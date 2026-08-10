-- ============================================================================
-- DSA Mastery Platform — Full Supabase Schema
-- Run this in the Supabase SQL Editor (Dashboard → SQL → New Query)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. PROFILES (extends Supabase auth.users)
-- ============================================================================
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT NOT NULL DEFAULT 'Learner',
    avatar_url TEXT,
    joined_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    xp INTEGER NOT NULL DEFAULT 0 CHECK (xp >= 0),
    current_streak INTEGER NOT NULL DEFAULT 0 CHECK (current_streak >= 0),
    longest_streak INTEGER NOT NULL DEFAULT 0 CHECK (longest_streak >= 0),
    last_active_date DATE,
    theme TEXT NOT NULL DEFAULT 'dark' CHECK (theme IN ('dark', 'light', 'system')),
    notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    preferences JSONB NOT NULL DEFAULT '{}'::JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_profiles_display_name ON public.profiles(display_name);

-- ============================================================================
-- 2. TOPICS (DSA topic tree with hierarchy)
-- ============================================================================
CREATE TABLE public.topics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    parent_id UUID REFERENCES public.topics(id) ON DELETE SET NULL,
    sort_order INTEGER NOT NULL DEFAULT 0,
    icon TEXT,
    difficulty_level TEXT CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),
    estimated_hours NUMERIC(4,1),
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_topics_parent ON public.topics(parent_id);
CREATE INDEX idx_topics_sort ON public.topics(sort_order);
CREATE INDEX idx_topics_slug ON public.topics(slug);

-- ============================================================================
-- 3. TOPIC_NOTES (AI-generated notes per topic, cached)
-- ============================================================================
CREATE TABLE public.topic_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    section_type TEXT NOT NULL CHECK (section_type IN (
        'detailed_notes', 'visual_explanation', 'worked_examples',
        'reference_code', 'complexity_notes', 'cheat_sheet',
        'interview_questions', 'practice_questions', 'common_mistakes'
    )),
    content TEXT NOT NULL,
    generated_by TEXT DEFAULT 'gemini-2.0-flash',
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_stale BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::JSONB,
    UNIQUE(topic_id, section_type)
);
CREATE INDEX idx_topic_notes_topic ON public.topic_notes(topic_id);
CREATE INDEX idx_topic_notes_section ON public.topic_notes(section_type);

-- ============================================================================
-- 4. PROBLEMS (problem bank)
-- ============================================================================
CREATE TABLE public.problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    difficulty TEXT NOT NULL CHECK (difficulty IN ('easy', 'medium', 'hard')),
    topic_id UUID NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    tags TEXT[] DEFAULT '{}',
    companies TEXT[] DEFAULT '{}',
    hints JSONB DEFAULT '[]'::JSONB,
    test_cases JSONB NOT NULL DEFAULT '[]'::JSONB,
    expected_output TEXT,
    time_complexity TEXT,
    space_complexity TEXT,
    starter_code JSONB DEFAULT '{}'::JSONB,
    solution_code JSONB DEFAULT '{}'::JSONB,
    solution_explanation TEXT,
    created_by UUID REFERENCES auth.users(id),
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    is_published BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_problems_topic ON public.problems(topic_id);
CREATE INDEX idx_problems_difficulty ON public.problems(difficulty);
CREATE INDEX idx_problems_tags ON public.problems USING GIN(tags);
CREATE INDEX idx_problems_companies ON public.problems USING GIN(companies);
CREATE INDEX idx_problems_slug ON public.problems(slug);

-- ============================================================================
-- 5. SUBMISSIONS
-- ============================================================================
CREATE TABLE public.submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    code TEXT NOT NULL,
    language TEXT NOT NULL CHECK (language IN ('python', 'cpp', 'java')),
    status TEXT NOT NULL CHECK (status IN (
        'accepted', 'wrong_answer', 'runtime_error',
        'time_limit', 'compilation_error', 'pending'
    )),
    runtime_ms INTEGER,
    memory_kb INTEGER,
    test_results JSONB DEFAULT '[]'::JSONB,
    tests_passed INTEGER DEFAULT 0,
    tests_total INTEGER DEFAULT 0,
    console_output TEXT,
    submitted_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_submissions_user ON public.submissions(user_id);
CREATE INDEX idx_submissions_problem ON public.submissions(problem_id);
CREATE INDEX idx_submissions_user_problem ON public.submissions(user_id, problem_id);
CREATE INDEX idx_submissions_status ON public.submissions(status);
CREATE INDEX idx_submissions_submitted ON public.submissions(submitted_at DESC);

-- ============================================================================
-- 6. LOGIC_GATE_RESPONSES (pre-coding reasoning)
-- ============================================================================
CREATE TABLE public.logic_gate_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    problem_understanding TEXT,
    input_output TEXT,
    brute_force_approach TEXT,
    optimal_approach TEXT,
    edge_cases TEXT,
    dry_run TEXT,
    pseudocode TEXT,
    ai_feedback TEXT,
    ai_validated BOOLEAN NOT NULL DEFAULT FALSE,
    validated_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, problem_id)
);
CREATE INDEX idx_logic_gate_user ON public.logic_gate_responses(user_id);
CREATE INDEX idx_logic_gate_problem ON public.logic_gate_responses(problem_id);

-- ============================================================================
-- 7. FLASHCARDS
-- ============================================================================
CREATE TABLE public.flashcards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    topic_id UUID NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    difficulty TEXT DEFAULT 'medium' CHECK (difficulty IN ('easy', 'medium', 'hard')),
    tags TEXT[] DEFAULT '{}',
    generated_by TEXT DEFAULT 'gemini-2.0-flash',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_flashcards_topic ON public.flashcards(topic_id);

-- ============================================================================
-- 8. USER_FLASHCARD_PROGRESS (spaced repetition)
-- ============================================================================
CREATE TABLE public.user_flashcard_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    flashcard_id UUID NOT NULL REFERENCES public.flashcards(id) ON DELETE CASCADE,
    next_review_date DATE NOT NULL DEFAULT CURRENT_DATE,
    interval_days INTEGER NOT NULL DEFAULT 0,
    ease_factor NUMERIC(4,2) NOT NULL DEFAULT 2.50,
    repetitions INTEGER NOT NULL DEFAULT 0,
    last_quality INTEGER,
    last_reviewed_at TIMESTAMPTZ,
    times_reviewed INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, flashcard_id)
);
CREATE INDEX idx_flashcard_progress_user ON public.user_flashcard_progress(user_id);
CREATE INDEX idx_flashcard_progress_review ON public.user_flashcard_progress(user_id, next_review_date);

-- ============================================================================
-- 9. USER_TOPIC_PROGRESS
-- ============================================================================
CREATE TABLE public.user_topic_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID NOT NULL REFERENCES public.topics(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'not_started' CHECK (status IN (
        'not_started', 'in_progress', 'completed', 'revision'
    )),
    notes_read BOOLEAN NOT NULL DEFAULT FALSE,
    problems_attempted INTEGER NOT NULL DEFAULT 0,
    problems_solved INTEGER NOT NULL DEFAULT 0,
    flashcards_reviewed INTEGER NOT NULL DEFAULT 0,
    last_accessed_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, topic_id)
);
CREATE INDEX idx_topic_progress_user ON public.user_topic_progress(user_id);
CREATE INDEX idx_topic_progress_status ON public.user_topic_progress(user_id, status);

-- ============================================================================
-- 10. USER_NOTES (personal annotations)
-- ============================================================================
CREATE TABLE public.user_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id UUID REFERENCES public.topics(id) ON DELETE SET NULL,
    problem_id UUID REFERENCES public.problems(id) ON DELETE SET NULL,
    title TEXT NOT NULL DEFAULT 'Untitled Note',
    content TEXT NOT NULL DEFAULT '',
    tags TEXT[] DEFAULT '{}',
    is_pinned BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_user_notes_user ON public.user_notes(user_id);
CREATE INDEX idx_user_notes_topic ON public.user_notes(topic_id);
CREATE INDEX idx_user_notes_search ON public.user_notes
    USING GIN(to_tsvector('english', title || ' ' || content));

-- ============================================================================
-- 11. BOOKMARKS
-- ============================================================================
CREATE TABLE public.bookmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    problem_id UUID NOT NULL REFERENCES public.problems(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, problem_id)
);
CREATE INDEX idx_bookmarks_user ON public.bookmarks(user_id);

-- ============================================================================
-- 12. MISTAKE_JOURNAL
-- ============================================================================
CREATE TABLE public.mistake_journal (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES public.problems(id) ON DELETE SET NULL,
    topic_id UUID REFERENCES public.topics(id) ON DELETE SET NULL,
    mistake_type TEXT CHECK (mistake_type IN (
        'logic', 'syntax', 'edge_case', 'complexity', 'approach', 'other'
    )),
    description TEXT NOT NULL,
    lesson_learned TEXT,
    code_snippet TEXT,
    frequency INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_mistakes_user ON public.mistake_journal(user_id);
CREATE INDEX idx_mistakes_type ON public.mistake_journal(user_id, mistake_type);

-- ============================================================================
-- 13. ACHIEVEMENTS
-- ============================================================================
CREATE TABLE public.achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    icon TEXT NOT NULL,
    category TEXT CHECK (category IN ('streak', 'problems', 'topics', 'xp', 'special')),
    requirement JSONB NOT NULL,
    xp_reward INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE public.user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    achievement_id UUID NOT NULL REFERENCES public.achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, achievement_id)
);
CREATE INDEX idx_user_achievements_user ON public.user_achievements(user_id);

-- ============================================================================
-- 14. ACTIVITY_LOG (heatmap / streak tracking)
-- ============================================================================
CREATE TABLE public.activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    activity_type TEXT NOT NULL CHECK (activity_type IN (
        'problem_solved', 'problem_attempted', 'notes_read',
        'flashcard_reviewed', 'topic_completed', 'code_submitted',
        'logic_gate_completed', 'note_created', 'login'
    )),
    reference_id UUID,
    reference_type TEXT,
    xp_earned INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_activity_user ON public.activity_log(user_id);
CREATE INDEX idx_activity_date ON public.activity_log(user_id, created_at);
CREATE INDEX idx_activity_type ON public.activity_log(activity_type);
CREATE INDEX idx_activity_heatmap ON public.activity_log(user_id, (created_at::date));

-- ============================================================================
-- 15. AI_CACHE
-- ============================================================================
CREATE TABLE public.ai_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cache_key TEXT NOT NULL UNIQUE,
    prompt_hash TEXT NOT NULL,
    model TEXT NOT NULL DEFAULT 'gemini-2.0-flash',
    response TEXT NOT NULL,
    token_count INTEGER,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    hit_count INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_ai_cache_key ON public.ai_cache(cache_key);
CREATE INDEX idx_ai_cache_expires ON public.ai_cache(expires_at);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.topic_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.problems ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.logic_gate_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flashcards ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_flashcard_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_topic_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bookmarks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mistake_journal ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ai_cache ENABLE ROW LEVEL SECURITY;

-- Profiles
CREATE POLICY "Profiles: read all" ON public.profiles
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "Profiles: update own" ON public.profiles
    FOR UPDATE TO authenticated USING (auth.uid() = id);
CREATE POLICY "Profiles: insert own" ON public.profiles
    FOR INSERT TO authenticated WITH CHECK (auth.uid() = id);

-- Shared content: topics, notes, flashcards, achievements, problems, ai_cache
CREATE POLICY "Topics: read all" ON public.topics
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "Topic Notes: read all" ON public.topic_notes
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "Topic Notes: insert" ON public.topic_notes
    FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Topic Notes: update" ON public.topic_notes
    FOR UPDATE TO authenticated USING (true);
CREATE POLICY "Flashcards: read all" ON public.flashcards
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "Flashcards: insert" ON public.flashcards
    FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Achievements: read all" ON public.achievements
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "Problems: read all" ON public.problems
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "Problems: insert" ON public.problems
    FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "Problems: update" ON public.problems
    FOR UPDATE TO authenticated USING (true);
CREATE POLICY "AI Cache: read all" ON public.ai_cache
    FOR SELECT TO authenticated USING (true);
CREATE POLICY "AI Cache: insert" ON public.ai_cache
    FOR INSERT TO authenticated WITH CHECK (true);
CREATE POLICY "AI Cache: update" ON public.ai_cache
    FOR UPDATE TO authenticated USING (true);

-- User-owned data
CREATE POLICY "Submissions: own only" ON public.submissions
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Logic Gate: own only" ON public.logic_gate_responses
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Flashcard Progress: own only" ON public.user_flashcard_progress
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Topic Progress: own only" ON public.user_topic_progress
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "User Notes: own only" ON public.user_notes
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Bookmarks: own only" ON public.bookmarks
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Mistake Journal: own only" ON public.mistake_journal
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "User Achievements: own only" ON public.user_achievements
    FOR ALL TO authenticated USING (auth.uid() = user_id);
CREATE POLICY "Activity Log: own only" ON public.activity_log
    FOR ALL TO authenticated USING (auth.uid() = user_id);

-- ============================================================================
-- TRIGGERS & FUNCTIONS
-- ============================================================================

-- Auto-create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, display_name)
    VALUES (
        NEW.id,
        COALESCE(NEW.raw_user_meta_data->>'display_name', 'Learner')
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_profiles_updated BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER trg_topics_updated BEFORE UPDATE ON public.topics
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER trg_problems_updated BEFORE UPDATE ON public.problems
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER trg_logic_gate_updated BEFORE UPDATE ON public.logic_gate_responses
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER trg_topic_progress_updated BEFORE UPDATE ON public.user_topic_progress
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER trg_user_notes_updated BEFORE UPDATE ON public.user_notes
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER trg_mistakes_updated BEFORE UPDATE ON public.mistake_journal
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- Update streak function
CREATE OR REPLACE FUNCTION public.update_streak(p_user_id UUID)
RETURNS void AS $$
DECLARE
    v_last_active DATE;
    v_current_streak INTEGER;
    v_longest_streak INTEGER;
BEGIN
    SELECT last_active_date, current_streak, longest_streak
    INTO v_last_active, v_current_streak, v_longest_streak
    FROM public.profiles WHERE id = p_user_id;

    IF v_last_active = CURRENT_DATE THEN
        RETURN;
    ELSIF v_last_active = CURRENT_DATE - 1 THEN
        v_current_streak := v_current_streak + 1;
    ELSE
        v_current_streak := 1;
    END IF;

    v_longest_streak := GREATEST(v_longest_streak, v_current_streak);

    UPDATE public.profiles
    SET current_streak = v_current_streak,
        longest_streak = v_longest_streak,
        last_active_date = CURRENT_DATE,
        updated_at = NOW()
    WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- SEED DATA: DSA Topic Tree
-- ============================================================================
INSERT INTO public.topics (title, slug, description, parent_id, sort_order, icon, difficulty_level, estimated_hours) VALUES
('Arrays & Strings',        'arrays-strings',        'Fundamental data structures for sequential data storage and manipulation',           NULL, 1,  '📊', 'beginner',     8),
('Hashing',                 'hashing',               'Hash maps, hash sets, and hashing techniques',                                      NULL, 2,  '#️⃣', 'beginner',     5),
('Two Pointers',            'two-pointers',          'Technique using two pointers to solve array/string problems efficiently',            NULL, 3,  '👆', 'beginner',     4),
('Sliding Window',          'sliding-window',        'Technique for processing subarrays/substrings of fixed or variable length',         NULL, 4,  '🪟', 'beginner',     4),
('Sorting & Searching',     'sorting-searching',     'Fundamental algorithms for organizing and finding data',                            NULL, 5,  '🔍', 'beginner',     8),
('Linked Lists',            'linked-lists',          'Linear data structures with pointer-based connections',                              NULL, 6,  '🔗', 'beginner',     6),
('Stacks',                  'stacks',                'LIFO data structure and its applications',                                           NULL, 7,  '📚', 'beginner',     5),
('Queues',                  'queues',                'FIFO data structure including deques and priority queues',                           NULL, 8,  '🚶', 'beginner',     5),
('Recursion & Backtracking','recursion-backtracking','Recursive problem-solving and systematic exploration',                               NULL, 9,  '🔄', 'intermediate', 8),
('Trees',                   'trees',                 'Hierarchical data structures including BSTs and balanced trees',                     NULL, 10, '🌳', 'intermediate', 10),
('Heaps & Priority Queues', 'heaps',                 'Heap data structure and priority-based processing',                                  NULL, 11, '⛰️', 'intermediate', 5),
('Graphs',                  'graphs',                'Non-linear data structures with BFS, DFS, and shortest paths',                      NULL, 12, '🕸️', 'intermediate', 12),
('Dynamic Programming',     'dynamic-programming',   'Optimization technique using overlapping subproblems',                               NULL, 13, '🧩', 'advanced',     15),
('Greedy Algorithms',       'greedy',                'Making locally optimal choices for global solutions',                                NULL, 14, '💰', 'intermediate', 6),
('Bit Manipulation',        'bit-manipulation',      'Operations at the binary level',                                                     NULL, 15, '🔢', 'intermediate', 4),
('Math & Number Theory',    'math',                  'Mathematical concepts used in competitive programming',                              NULL, 16, '🔣', 'intermediate', 5),
('Tries',                   'tries',                 'Prefix tree data structure for string operations',                                   NULL, 17, '🔤', 'advanced',     4),
('Segment Trees & BIT',     'segment-trees',         'Advanced tree structures for range queries',                                         NULL, 18, '📐', 'advanced',     6),
('System Design Basics',    'system-design',         'Introduction to system design concepts and patterns',                                NULL, 19, '🏗️', 'advanced',     8);

-- ============================================================================
-- SEED DATA: Achievements
-- ============================================================================
INSERT INTO public.achievements (name, description, icon, category, requirement, xp_reward) VALUES
('First Steps',     'Solve your first problem',            '🎯', 'problems', '{"type": "problems_solved", "count": 1}',    10),
('Problem Solver',  'Solve 10 problems',                   '💪', 'problems', '{"type": "problems_solved", "count": 10}',   50),
('Century Club',    'Solve 100 problems',                  '💯', 'problems', '{"type": "problems_solved", "count": 100}',  200),
('On Fire',         'Maintain a 7-day streak',             '🔥', 'streak',   '{"type": "streak", "count": 7}',             50),
('Unstoppable',     'Maintain a 30-day streak',            '⚡', 'streak',   '{"type": "streak", "count": 30}',            200),
('Explorer',        'Complete 5 different topics',         '🗺️', 'topics',   '{"type": "topics_completed", "count": 5}',   100),
('Scholar',         'Complete all topics',                 '🎓', 'topics',   '{"type": "topics_completed", "count": 19}',  500),
('XP Hunter',       'Earn 1000 XP',                        '⭐', 'xp',       '{"type": "xp_earned", "count": 1000}',       100),
('Logic Master',    'Complete 20 Logic Gate exercises',    '🧠', 'special',  '{"type": "logic_gates", "count": 20}',       100),
('Flash Learner',   'Review 100 flashcards',               '📸', 'special',  '{"type": "flashcards_reviewed", "count": 100}', 75);

-- ============================================================================
-- STORAGE: Create avatars bucket (run via Supabase Dashboard or API)
-- ============================================================================
-- INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
-- VALUES ('avatars', 'avatars', true, 5242880, ARRAY['image/jpeg','image/png','image/webp'])
-- ON CONFLICT (id) DO NOTHING;
