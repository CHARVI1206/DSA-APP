import streamlit as stimport datetimeimport randomimport jsonimport httpximport pandas as pdfrom supabase import create_client, Clientimport google.generativeai as genai
# --- 1. SYSTEM GATEWAY INITIALIZATION ---try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    genai.configure(api_key=GEMINI_API_KEY)
    ai_coach = genai.GenerativeModel('gemini-1.5-flash')except Exception:
    st.error("⚠️ Infrastructure configuration secrets tokens missing inside Streamlit Secrets panel.")
    st.stop()
# --- 2. SEQUENTIAL DIFFICULTY PROGRESSION CURRICULUM MAP ---TOPIC_PROGRESSION = {
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
@st.cache_data(ttl=3600)def fetch_leetcode_questions_by_tag(tag: str):
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
# --- 4. ENGINE CORE OPERATIONS SECURITY HANDLERS ---def log_activity_points(username: str, points: int):
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
# --- 5. RUNTIME STATE MACHINE MANAGEMENT ---if "logic_approved" not in st.session_state: st.session_state.logic_approved = Falseif "active_cloud_prob" not in st.session_state: st.session_state.active_cloud_prob = Noneif "practice_approved" not in st.session_state: st.session_state.practice_approved = False

st.sidebar.title("🛡️ CoreEngine Workspace")username = st.sidebar.text_input("🔑 Sign In with Username Account Profile:", value="").strip().lower()
if not username:
    st.title("👨‍💻 Welcome to CoreEngine Unified LeetCode Portal")
    st.info("💡 Share this live URL with your friends! Each username creates an independent tracking profile inside our cloud database.")
    st.stop()
profile = sync_secure_user_session(username)mastery_records = supabase.table("topic_mastery").select("*").eq("username", username).execute().datamastery_map = {r["topic_name"]: r["mastery_score"] for r in mastery_records}

st.sidebar.markdown(f"### 👤 Profile User: **{username}**")
st.sidebar.markdown(f"🔥 Continuous Streak: **{profile['streak']} Days**")
st.sidebar.markdown(f"🏆 System Mastery: **{profile['total_xp']} XP**")
st.sidebar.divider()
# --- 6. ELEVATED INTERACTIVE 7-DAY MILESTONE POPUP ---signup_dt = datetime.datetime.strptime(profile["signup_date"], "%Y-%m-%d").date() if isinstance(profile["signup_date"], str) else profile["signup_date"]days_since_reg = (datetime.date.today() - signup_dt).days
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
# Build navigation dynamically based on performance gatesunlocked_practice_tracks = [t for t, score in mastery_map.items() if score >= 40]
nav_matrix = ["📊 1. User Metrics Control Dashboard", "🚀 2. Adaptive Curriculum Arena"]if unlocked_practice_tracks: nav_matrix.append("♾️ 3. Infinite LeetCode Practice (Unlocked)")
nav_matrix.extend(["👥 4. Multiplayer Friend Lobbies", "📋 5. Weekly AI Diagnostic Studio"])
view_selector = st.sidebar.radio("🎛️ Navigation Dashboards Panel:", nav_matrix)
# --- VIEW 1: DASHBOARD METRICS CONTROLLER (GITHUB + LEETCODE STYLE) ---if view_selector == "📊 1. User Metrics Control Dashboard":
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
