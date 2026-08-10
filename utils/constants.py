XP_VALUES = {
    'easy': 10,
    'medium': 25,
    'hard': 50,
    'topic_completed': 100,
    'flashcard_reviewed': 2,
    'logic_gate_passed': 15,
    'note_created': 5
}

DIFFICULTY_COLORS = {
    'easy': '#22C55E',
    'medium': '#F59E0B',
    'hard': '#EF4444'
}

LANGUAGES = {
    'Python': {
        'language': 'python',
        'version': '3.10.0',
        'filename': 'solution.py',
        'ace_mode': 'python'
    },
    'C++': {
        'language': 'c++',
        'version': '10.2.0',
        'filename': 'solution.cpp',
        'ace_mode': 'c_cpp'
    },
    'Java': {
        'language': 'java',
        'version': '15.0.2',
        'filename': 'Main.java',
        'ace_mode': 'java'
    }
}

STARTER_CODE = {
    'Python': 'def solve():\n    pass\n',
    'C++': '#include <iostream>\nusing namespace std;\n\nint main() {\n    return 0;\n}\n',
    'Java': 'public class Main {\n    public static void main(String[] args) {\n    }\n}\n'
}

AI_MODES = {
    'mentor': {
        'name': 'Mentor',
        'icon': '🎓',
        'system_prompt': 'You are a helpful DSA mentor. Guide the user step by step.'
    },
    'reviewer': {
        'name': 'Code Reviewer',
        'icon': '🔍',
        'system_prompt': 'You are a strict code reviewer. Focus on time/space complexity and best practices.'
    },
    'interviewer': {
        'name': 'Interviewer',
        'icon': '👔',
        'system_prompt': 'You are a FAANG interviewer. Ask clarifying questions and evaluate the approach.'
    }
}

SECTION_TYPES = ['introduction', 'algorithm', 'complexity', 'examples', 'implementation']

ACHIEVEMENT_CATEGORIES = ['problem_solving', 'consistency', 'learning']
