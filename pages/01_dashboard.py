"""
Dashboard — Home page showing streak, XP, today's plan, and recent activity.
"""
import streamlit as st
from datetime import datetime, timedelta


def _safe_import():
    """Lazy imports to avoid circular deps and handle missing services gracefully."""
    services = {}
    try:
        from services.analytics_service import (
            get_streak_info, get_user_stats, get_heatmap_data, get_weekly_report, get_achievements
        )
        services["analytics"] = {
            "get_streak_info": get_streak_info,
            "get_user_stats": get_user_stats,
            "get_heatmap_data": get_heatmap_data,
            "get_weekly_report": get_weekly_report,
            "get_achievements": get_achievements,
        }
    except ImportError:
        services["analytics"] = None

    try:
        from services.flashcard_service import get_review_stats
        services["flashcard_stats"] = get_review_stats
    except ImportError:
        services["flashcard_stats"] = None

    try:
        from services.topic_service import get_user_progress
        services["topic_progress"] = get_user_progress
    except ImportError:
        services["topic_progress"] = None

    return services


def render_dashboard():
    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to view your dashboard.")
        return

    user_id = user["id"]
    display_name = user.get("display_name", user.get("user_metadata", {}).get("display_name", "Learner"))
    svcs = _safe_import()

    # ─── Header ─────────────────────────────────────────────────────
    col_welcome, col_streak, col_xp = st.columns([3, 1, 1])

    with col_welcome:
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
        st.markdown(f"""
        <div style="padding: 0.5rem 0;">
            <h1 style="margin:0; font-size:2rem; background: linear-gradient(135deg, #8B5CF6, #6366F1);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                {greeting}, {display_name}! 👋
            </h1>
            <p style="color: #94A3B8; margin-top: 0.25rem;">Ready to master DSA today?</p>
        </div>
        """, unsafe_allow_html=True)

    # Streak info
    streak_info = {"current": 0, "longest": 0}
    if svcs.get("analytics") and svcs["analytics"].get("get_streak_info"):
        try:
            streak_info = svcs["analytics"]["get_streak_info"](user_id)
        except Exception:
            pass

    with col_streak:
        streak = streak_info.get("current", 0)
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div class="streak-fire" style="font-size:2rem;">🔥</div>
            <div style="font-size:1.5rem; font-weight:700; color:#F59E0B;">{streak}</div>
            <div style="color:#94A3B8; font-size:0.8rem;">Day Streak</div>
        </div>
        """, unsafe_allow_html=True)

    with col_xp:
        xp = user.get("xp", 0)
        level = xp // 100
        xp_in_level = xp % 100
        st.markdown(f"""
        <div class="metric-card" style="text-align:center;">
            <div style="font-size:2rem;">⚡</div>
            <div style="font-size:1.5rem; font-weight:700; color:#8B5CF6;">{xp:,}</div>
            <div style="color:#94A3B8; font-size:0.8rem;">XP · Level {level}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ─── Stats Row ──────────────────────────────────────────────────
    stats = {"total_solved": 0, "acceptance_rate": 0, "topics_completed": 0}
    if svcs.get("analytics") and svcs["analytics"].get("get_user_stats"):
        try:
            stats = svcs["analytics"]["get_user_stats"](user_id)
        except Exception:
            pass

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#94A3B8; font-size:0.85rem;">Problems Solved</div>
            <div style="font-size:1.8rem; font-weight:700; color:#22C55E;">
                {stats.get('total_solved', 0)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        rate = stats.get("acceptance_rate", 0)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#94A3B8; font-size:0.85rem;">Acceptance Rate</div>
            <div style="font-size:1.8rem; font-weight:700; color:#8B5CF6;">
                {rate:.0f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#94A3B8; font-size:0.85rem;">Topics Completed</div>
            <div style="font-size:1.8rem; font-weight:700; color:#6366F1;">
                {stats.get('topics_completed', 0)}/19
            </div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        due_today = 0
        if svcs.get("flashcard_stats"):
            try:
                review_stats = svcs["flashcard_stats"](user_id)
                due_today = review_stats.get("due_today", 0)
            except Exception:
                pass
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#94A3B8; font-size:0.85rem;">Cards Due Today</div>
            <div style="font-size:1.8rem; font-weight:700; color:#F59E0B;">
                {due_today}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ─── Today's Plan & Activity ────────────────────────────────────
    col_plan, col_activity = st.columns([1, 1])

    with col_plan:
        st.markdown("### 📋 Today's Plan")

        tasks = []
        if due_today > 0:
            tasks.append(f"🃏 Review **{due_today}** flashcards due today")

        # Check topics in progress
        if svcs.get("topic_progress"):
            try:
                progress = svcs["topic_progress"](user_id)
                in_progress = [p for p in progress if p.get("status") == "in_progress"]
                if in_progress:
                    for tp in in_progress[:3]:
                        tasks.append(f"📖 Continue studying topic")
            except Exception:
                pass

        if not tasks:
            tasks = [
                "🗺️ Explore the **Roadmap** to start a new topic",
                "💻 Head to **Practice** to solve a problem",
                "🃏 Generate **Flashcards** for a topic you've studied",
            ]

        for task in tasks:
            st.markdown(f"""
            <div style="background: rgba(139,92,246,0.1); border-left: 3px solid #8B5CF6;
                padding: 0.75rem 1rem; margin-bottom: 0.5rem; border-radius: 0 8px 8px 0;">
                {task}
            </div>
            """, unsafe_allow_html=True)

    with col_activity:
        st.markdown("### 📈 Weekly Report")
        if svcs.get("analytics") and svcs["analytics"].get("get_weekly_report"):
            try:
                report = svcs["analytics"]["get_weekly_report"](user_id)
                st.markdown(f"""
                <div class="metric-card">
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1rem;">
                        <div>
                            <div style="color:#94A3B8; font-size:0.8rem;">Problems This Week</div>
                            <div style="font-size:1.3rem; font-weight:600; color:#22C55E;">
                                {report.get('problems_solved', 0)}
                            </div>
                        </div>
                        <div>
                            <div style="color:#94A3B8; font-size:0.8rem;">XP Earned</div>
                            <div style="font-size:1.3rem; font-weight:600; color:#8B5CF6;">
                                +{report.get('xp_earned', 0)}
                            </div>
                        </div>
                        <div>
                            <div style="color:#94A3B8; font-size:0.8rem;">Cards Reviewed</div>
                            <div style="font-size:1.3rem; font-weight:600; color:#F59E0B;">
                                {report.get('flashcards_reviewed', 0)}
                            </div>
                        </div>
                        <div>
                            <div style="color:#94A3B8; font-size:0.8rem;">Active Days</div>
                            <div style="font-size:1.3rem; font-weight:600; color:#6366F1;">
                                {report.get('active_days', 0)}/7
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.info("Complete some activities to see your weekly report!")
        else:
            st.info("Weekly report will appear once you start solving problems.")

    # ─── Activity Heatmap ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🟩 Activity Heatmap")
    if svcs.get("analytics") and svcs["analytics"].get("get_heatmap_data"):
        try:
            heatmap_data = svcs["analytics"]["get_heatmap_data"](user_id, days=90)
            if heatmap_data:
                from components.heatmap import render_heatmap
                render_heatmap(heatmap_data)
            else:
                st.info("Your activity heatmap will fill up as you learn! Start solving problems to see it grow. 🌱")
        except Exception:
            st.info("Start your learning journey to see your activity heatmap here!")
    else:
        st.info("Activity tracking will appear here once you start using the platform.")

    # ─── Recent Achievements ────────────────────────────────────────
    if svcs.get("analytics") and svcs["analytics"].get("get_achievements"):
        try:
            achievements = svcs["analytics"]["get_achievements"](user_id)
            earned = achievements.get("earned", [])
            if earned:
                st.markdown("---")
                st.markdown("### 🏆 Recent Achievements")
                cols = st.columns(min(len(earned), 5))
                for i, ach in enumerate(earned[:5]):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="text-align:center; padding:1rem;">
                            <div style="font-size:2rem;">{ach.get('icon', '🏆')}</div>
                            <div style="font-size:0.85rem; font-weight:600; color:#E2E8F0;">
                                {ach.get('name', 'Achievement')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
        except Exception:
            pass


# ─── Run ────────────────────────────────────────────────────────────────
render_dashboard()
