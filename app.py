import streamlit as st
import datetime
import random
import json
import httpx
import pandas as pd
from supabase import create_client, Client
import google.generativeai as genai

# --- 1. SYSTEM GATEWAY INITIALIZATION ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    ai_coach = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    st.error("⚠️ Infrastructure configuration secrets tokens missing inside Streamlit Secrets panel.")
    st.stop()

# --- 2. SEQUENTIAL DIFFICULTY PROGRESSION CURRICULUM MAP ---
TOPIC_PROGRESSION = {
    1: "Arrays & Hashing", 2: "Two Pointers", 3: "Sliding Window", 4: "Stack",
    5: "Binary Search", 6: "Linked List", 7: "Trees", 8: "Tries",
    9: "Backtracking", 10: "Graphs", 11: "Advanced Graphs", 12: "1-D Dynamic Programming",
    13: "2-D Dynamic Programming", 14: "Greedy", 15: "Intervals", 16: "Math & Geometry",
    17: "Bit Manipulation"
}

API_TAG_MAPPING = {
    "Arrays & Hashing": "array", "Two Pointers": "two-pointers", "Sliding Window": "sliding-window",
    "Stack": "stack", "Binary Search": "binary-search", "Linked List": "linked-list", "Trees": "tree",
    "Tries": "trie", "Backtracking": "backtracking", "Graphs": "graph", "Advanced Graphs": "shortest-path",
    "1-D Dynamic Programming": "dynamic-programming", "2-D Dynamic Programming": "dynamic-programming",
    "Greedy": "greedy", "Intervals": "array", "Math & Geometry": "math", "Bit Manipulation": "bit-manipulation"
}

# --- 3. LIVE CLOUD LEETCODE API STREAMER ---
@st.cache_data(ttl=3600)
def fetch_leetcode_questions_by_tag(tag: str):
    url = f"https://onrender.com{tag}&limit=50"
    try:
        response = httpx.get(url, timeout=12.0)
        if response.status_code == 200:
            return response.json().get("problemsetQuestionList", [])
    except Exception:
        pass
    return [
        {"questionId": "1", "title": "Two Sum", "titleSlug": "two-sum", "difficulty": "Easy", "content": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target."},
        {"questionId": "217", "title": "Contains Duplicate", "titleSlug": "contains-duplicate", "difficulty": "Easy", "content": "Return true if any value appears at least twice in the array."}
    ]

# --- 4. ENGINE CORE OPERATIONS SECURITY HANDLERS ---
def log_activity_points(username: str, points: int):
    today = str(datetime.date.today())
    check = supabase.table("user_contributions").select("*").eq("username", username).eq("activity_date", today).execute()
    if check.data:
        current_pts = check.data[0]["points_earned"] if isinstance(check.data, list) else check.data.get("points_earned", 0)
        supabase.table("user_contributions").update({"points_earned": current_pts + points}).eq("username", username).eq("activity_date", today).execute()
    else:
        supabase.table("user_contributions").insert({"username": username, "activity_date": today, "points_earned": points}).execute()


def sync_secure_user_session(username: str):
    user_res = supabase.table("dsa_users").select("*").eq("username", username).execute()
    if not user_res.data:
        supabase.table("dsa_users").insert({"username": username, "streak": 0, "total_xp": 0, "signup_date": str(datetime.date.today())}).execute()
        user_res = supabase.table("dsa_users").select("*").eq("username", username).execute()

    for topic in TOPIC_PROGRESSION.values():
        check = supabase.table("topic_mastery").select("*").eq("username", username).eq("topic_name", topic).execute()
        if not check.data:
            supabase.table("topic_mastery").insert({"username": username, "topic_name": topic, "mastery_score": 0}).execute()
    return user_res.data[0]

# --- 5. RUNTIME STATE MACHINE MANAGEMENT ---
if "logic_approved" not in st.session_state:
    st.session_state.logic_approved = False
if "active_cloud_prob" not in st.session_state:
    st.session_state.active_cloud_prob = None
if "practice_approved" not in st.session_state:
    st.session_state.practice_approved = False

st.sidebar.title("🛡️ CoreEngine Workspace")
username = st.sidebar.text_input("🔑 Sign In with Username Account Profile:", value="").strip().lower()

if not username:
    st.title("👨‍💻 Welcome to CoreEngine Unified LeetCode Portal")
    st.info("💡 Share this live URL with your friends! Each username creates an independent tracking profile inside our cloud database.")
    st.stop()

profile = sync_secure_user_session(username)
mastery_records = supabase.table("topic_mastery").select("*").eq("username", username).execute().data
mastery_map = {r["topic_name"]: r["mastery_score"] for r in mastery_records}

st.sidebar.markdown(f"### 👤 Profile User: **{username}**")
st.sidebar.markdown(f"🔥 Continuous Streak: **{profile['streak']} Days**")
st.sidebar.markdown(f"🏆 System Mastery: **{profile['total_xp']} XP**")
st.sidebar.divider()

# --- 6. ELEVATED INTERACTIVE 7-DAY MILESTONE POPUP ---
signup_dt = datetime.datetime.strptime(profile["signup_date"], "%Y-%m-%d").date() if isinstance(profile["signup_date"], str) else profile["signup_date"]
days_since_reg = (datetime.date.today() - signup_dt).days

if days_since_reg >= 7:
    latest_report = supabase.table("weekly_reports").select("*").eq("username", username).order("generated_at", desc=True).limit(1).execute().data
    if not latest_report or not latest_report[0]["was_alerted_popup"]:

        st.error("📊 **WEEKLY PROGRESS INFRASTRUCTURE SUMMARY**")
        st.markdown(f"### ⚙️ Interactive Performance Dashboard Ready for **{username}**")
        st.write("The platform has generated an analytical breakdown of your core learning vectors and historical execution bugs.")

        core_logs = supabase.table("problem_attempts").select("*").eq("username", username).execute().data

        if core_logs:
            df_logs = pd.DataFrame(core_logs)
            mc1, mc2 = st.columns(2)
            with mc1:
                st.metric(label="Total Logged Problem Attempts", value=len(df_logs))
            with mc2:
                failed_count = len(df_logs[df_logs["status"] == "FAILED"]) if "status" in df_logs.columns else 0
                st.metric(label="System Error/Failure Interceptions", value=failed_count)

            st.markdown("#### 🔍 Error Density Metrics Across DSA Patterns")
            if "topic" in df_logs.columns and failed_count > 0:
                failed_df = df_logs[df_logs["status"] == "FAILED"]
                chart_data = failed_df["topic"].value_counts().reset_index()
                chart_data.columns = ["DSA Topic Pattern", "Failure Count"]
                st.bar_chart(data=chart_data, x="DSA Topic Pattern", y="Failure Count", use_container_width=True)
            else:
                st.info("💡 Zero failure logs recorded. Your operational efficiency parameters are performing perfectly.")
        else:
            st.info("💡 Not enough problem metrics recorded this week to generate detailed chart data vectors.")

        with st.expander("📖 Read Detailed AI Socratic Diagnostic Text Breakdown"):
            with st.spinner("🤖 AI Coach is compiling text report vectors..."):
                prompt_meta = f"User: {username}. Core History: {str(core_logs)[:1000]}."
                ai_eval_report = ai_coach.generate_content(f"{prompt_meta} Evaluate this student's progress. Write a strict 3-paragraph assessment split into 1. Submission Success Metrics, 2. Conceptual Blind Spots, and 3. A 3-step action plan for next week.").text
                st.markdown(ai_eval_report)

        if st.button("🎯 Finalize and Dismiss Weekly Audit Gateway"):
            supabase.table("weekly_reports").insert({"username": username, "report_text": ai_eval_report if 'ai_eval_report' in locals() else "Dashboard Checked", "was_alerted_popup": True}).execute()
            st.success("Audit filed to your permanent diagnostic studio tab!")
            st.rerun()
        st.stop()

# Build navigation dynamically based on performance gates
unlocked_practice_tracks = [t for t, score in mastery_map.items() if score >= 40]
nav_matrix = ["📊 1. User Metrics Control Dashboard", "🚀 2. Adaptive Curriculum Arena"]
if unlocked_practice_tracks:
    nav_matrix.append("♾️ 3. Infinite LeetCode Practice (Unlocked)")
nav_matrix.extend(["👥 4. Multiplayer Friend Lobbies", "📋 5. Weekly AI Diagnostic Studio"])
view_selector = st.sidebar.radio("🎛️ Navigation Dashboards Panel:", nav_matrix)

# --- VIEW 1: DASHBOARD METRICS CONTROLLER (GITHUB + LEETCODE STYLE) ---
if view_selector == "📊 1. User Metrics Control Dashboard":
    st.header(f"📊 Live Progression Dashboard for {username}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🎯 Pattern Mastery Track")
        for idx, topic in sorted(TOPIC_PROGRESSION.items()):
            score = mastery_map.get(topic, 0)
            st.markdown(f"**Lvl {idx}. {topic}**: `{score} / 100 XP`")
            st.progress(score / 100)
    with col2:
        st.subheader("🔥 Consistency Parameters")
        st.metric("Continuous Study Days", f"{profile['streak']} Days")
    with col3:
        st.subheader("🏆 Global Status")
        st.metric("Total Experience Points", f"{profile['total_xp']} XP")
    st.divider()

    st.subheader("🟩 System Contribution Activity Matrix (Past 14 Days)")
    cont_records = supabase.table("user_contributions").select("*").eq("username", username).order("activity_date", desc=True).limit(14).execute().data
    cont_map = {str(r["activity_date"]): r["points_earned"] for r in cont_records}

    grid_cols = st.columns(14)
    for index in range(14):
        target_date = datetime.date.today() - datetime.timedelta(days=(13 - index))
        date_str = str(target_date)
        pts = cont_map.get(date_str, 0)
        with grid_cols[index]:
            if pts > 0:
                st.markdown(f"🟩")
            else:
                st.markdown(f"⬜")
            st.caption(target_date.strftime("%d"))

# --- VIEW 2: ADAPTIVE CURRICULUM ARENA ---
elif view_selector == "🚀 2. Adaptive Curriculum Arena":
    st.header("🚀 Adaptive Curriculum Arena")

    # Determine current topic based on mastery
    current_topic_idx = 1
    for idx in sorted(TOPIC_PROGRESSION.keys()):
        topic = TOPIC_PROGRESSION[idx]
        if mastery_map.get(topic, 0) >= 100:
            current_topic_idx = idx + 1
        else:
            break
    current_topic_idx = min(current_topic_idx, max(TOPIC_PROGRESSION.keys()))
    current_topic = TOPIC_PROGRESSION[current_topic_idx]

    st.info(f"📌 Current Focus Topic: **Level {current_topic_idx} — {current_topic}**")

    # Fetch questions for the current topic
    api_tag = API_TAG_MAPPING.get(current_topic, "array")
    questions = fetch_leetcode_questions_by_tag(api_tag)

    if not st.session_state.active_cloud_prob:
        st.session_state.active_cloud_prob = random.choice(questions) if questions else None

    prob = st.session_state.active_cloud_prob
    if prob:
        st.subheader(f"📝 Problem: {prob['title']}")
        st.markdown(f"**Difficulty:** {prob.get('difficulty', 'N/A')}")
        st.markdown(f"**Description:** {prob.get('content', 'No description available.')}")
        st.markdown(f"🔗 [Open on LeetCode](https://leetcode.com/problems/{prob.get('titleSlug', '')}/)")

        user_code = st.text_area("💻 Paste your solution code here:", height=250)

        if st.button("🚀 Submit Solution for AI Review"):
            if user_code.strip():
                with st.spinner("🤖 AI Coach is reviewing your solution..."):
                    review_prompt = f"""You are a strict DSA coach. The student is working on the topic "{current_topic}".
Problem: {prob['title']}
Description: {prob.get('content', '')}
Student's Code:
```
{user_code}
```
Provide:
1. Is the solution correct? (YES/NO)
2. Time complexity analysis
3. Space complexity analysis
4. If incorrect, explain what's wrong and give hints (NOT the answer)
5. Rate the solution quality out of 10"""
                    review = ai_coach.generate_content(review_prompt).text
                    st.markdown("### 🤖 AI Coach Review")
                    st.markdown(review)

                    # Determine if passed
                    passed = "YES" in review.upper().split("\n")[0] if review else False
                    status = "PASSED" if passed else "FAILED"
                    xp_earned = 20 if passed else 5

                    # Log attempt
                    supabase.table("problem_attempts").insert({
                        "username": username,
                        "topic": current_topic,
                        "problem_title": prob["title"],
                        "status": status,
                        "code_submitted": user_code[:2000]
                    }).execute()

                    # Update XP
                    supabase.table("dsa_users").update({"total_xp": profile["total_xp"] + xp_earned}).eq("username", username).execute()
                    log_activity_points(username, xp_earned)

                    # Update mastery
                    if passed:
                        new_mastery = min(mastery_map.get(current_topic, 0) + 20, 100)
                        supabase.table("topic_mastery").update({"mastery_score": new_mastery}).eq("username", username).eq("topic_name", current_topic).execute()

                    st.success(f"{'✅ Correct!' if passed else '❌ Not quite.'} +{xp_earned} XP earned.")
            else:
                st.warning("⚠️ Please paste your solution code before submitting.")

        if st.button("🔄 Get New Problem"):
            st.session_state.active_cloud_prob = random.choice(questions) if questions else None
            st.rerun()

# --- VIEW 3: INFINITE LEETCODE PRACTICE ---
elif view_selector == "♾️ 3. Infinite LeetCode Practice (Unlocked)":
    st.header("♾️ Infinite LeetCode Practice Mode")

    selected_topic = st.selectbox("Choose a topic to practice:", unlocked_practice_tracks)
    api_tag = API_TAG_MAPPING.get(selected_topic, "array")
    practice_questions = fetch_leetcode_questions_by_tag(api_tag)

    if practice_questions:
        if st.button("🎲 Roll Random Problem"):
            st.session_state.active_cloud_prob = random.choice(practice_questions)
            st.session_state.practice_approved = True

        if st.session_state.practice_approved and st.session_state.active_cloud_prob:
            prob = st.session_state.active_cloud_prob
            st.subheader(f"📝 {prob['title']}")
            st.markdown(f"**Difficulty:** {prob.get('difficulty', 'N/A')}")
            st.markdown(f"**Description:** {prob.get('content', 'No description available.')}")
            st.markdown(f"🔗 [Open on LeetCode](https://leetcode.com/problems/{prob.get('titleSlug', '')}/)")

            user_code = st.text_area("💻 Your solution:", height=250, key="practice_code")
            if st.button("📤 Submit Practice Solution"):
                if user_code.strip():
                    with st.spinner("🤖 Reviewing..."):
                        review_prompt = f"""Review this solution for "{prob['title']}" ({selected_topic}):
```
{user_code}
```
Give: correctness, time/space complexity, and improvement suggestions."""
                        review = ai_coach.generate_content(review_prompt).text
                        st.markdown(review)

                        supabase.table("problem_attempts").insert({
                            "username": username,
                            "topic": selected_topic,
                            "problem_title": prob["title"],
                            "status": "PRACTICE",
                            "code_submitted": user_code[:2000]
                        }).execute()

                        log_activity_points(username, 5)
                        st.success("+5 XP for practice effort!")
    else:
        st.warning("No practice problems available for this topic.")

# --- VIEW 4: MULTIPLAYER FRIEND LOBBIES ---
elif view_selector == "👥 4. Multiplayer Friend Lobbies":
    st.header("👥 Multiplayer Friend Lobbies")
    st.info("🔧 Challenge your friends! Compare progress and compete on the leaderboard.")

    st.subheader("🏅 Global Leaderboard")
    all_users = supabase.table("dsa_users").select("username, total_xp, streak").order("total_xp", desc=True).limit(20).execute().data
    if all_users:
        lb_df = pd.DataFrame(all_users)
        lb_df.index = lb_df.index + 1
        lb_df.columns = ["Username", "Total XP", "Streak (Days)"]
        st.table(lb_df)
    else:
        st.info("No users found on the leaderboard yet.")

    st.divider()
    st.subheader("🔍 Look Up a Friend's Progress")
    friend_name = st.text_input("Enter a friend's username:").strip().lower()
    if friend_name:
        friend_data = supabase.table("dsa_users").select("*").eq("username", friend_name).execute().data
        if friend_data:
            f = friend_data[0]
            st.markdown(f"**{f['username']}** — 🏆 {f['total_xp']} XP | 🔥 {f['streak']} Day Streak")
            friend_mastery = supabase.table("topic_mastery").select("*").eq("username", friend_name).execute().data
            for fm in friend_mastery:
                st.markdown(f"- {fm['topic_name']}: `{fm['mastery_score']} / 100`")
        else:
            st.warning(f"User '{friend_name}' not found.")

# --- VIEW 5: WEEKLY AI DIAGNOSTIC STUDIO ---
elif view_selector == "📋 5. Weekly AI Diagnostic Studio":
    st.header("📋 Weekly AI Diagnostic Studio")

    past_reports = supabase.table("weekly_reports").select("*").eq("username", username).order("generated_at", desc=True).limit(10).execute().data
    if past_reports:
        for rpt in past_reports:
            with st.expander(f"📄 Report — {rpt.get('generated_at', 'N/A')}"):
                st.markdown(rpt.get("report_text", "No content available."))
    else:
        st.info("No weekly reports generated yet. Your first report will appear after 7 days of activity.")

    st.divider()
    if st.button("🔄 Generate Fresh AI Diagnostic Report Now"):
        with st.spinner("🤖 Generating comprehensive diagnostic..."):
            all_attempts = supabase.table("problem_attempts").select("*").eq("username", username).execute().data
            diag_prompt = f"""User: {username}. Total XP: {profile['total_xp']}. Streak: {profile['streak']}.
Mastery: {json.dumps(mastery_map)}.
Recent attempts: {str(all_attempts)[:1500]}.
Generate a comprehensive weekly diagnostic report covering:
1. Overall performance assessment
2. Strongest and weakest topics
3. Recommended study plan for the next week
4. Motivational insights"""
            diag_report = ai_coach.generate_content(diag_prompt).text
            st.markdown("### 📊 Fresh Diagnostic Report")
            st.markdown(diag_report)

            supabase.table("weekly_reports").insert({
                "username": username,
                "report_text": diag_report,
                "was_alerted_popup": False
            }).execute()
            st.success("Report saved to your diagnostic studio!")
