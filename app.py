"""
Zen Flip Focus - Streamlit Desktop & Web Application
A faithful, aesthetic rewrite of the Zen-Style Pomodoro Clock.
Built according to IEEE Software Engineering Standards (IEEE Std 730/828/1012/1016/12207/42010).
Includes Firebase Google Authentication, Multi-Tenancy, and Production Retention Lifecycle.
"""

from __future__ import annotations

import io
import time
from datetime import datetime, timezone
from typing import Optional

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from auth_component import render_firebase_auth_button
from clock_component import render_zen_flip_clock
from health import perform_health_check
from models import (
    AmbientSound,
    ChimeSound,
    RecallFlashcard,
    SessionType,
    TaskCategory,
    TaskItem,
    TaskPriority,
    ThemeType,
    TimerCycleMode,
    TimerStatus,
    UserProfile,
    UserSettings,
)
from storage import LocalStorage
from themes import THEMES, get_theme_css
from timer_controller import TimerController

# 1. Page Configuration
st.set_page_config(
    page_title="Zen Flip Focus | Aesthetic Pomodoro",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None

current_uid = st.session_state.user.uid if st.session_state.user else None

if "settings" not in st.session_state:
    st.session_state.settings = LocalStorage.get_settings(user_id=current_uid)

if "timer_status" not in st.session_state:
    st.session_state.timer_status = TimerStatus.IDLE

if "cycle_mode" not in st.session_state:
    st.session_state.cycle_mode = st.session_state.settings.cycleMode

if "session_type" not in st.session_state:
    st.session_state.session_type = TimerController.get_initial_session_type(
        st.session_state.cycle_mode
    )

if "remaining_seconds" not in st.session_state:
    st.session_state.remaining_seconds = TimerController.get_session_duration(
        st.session_state.session_type, st.session_state.settings
    )

if "completed_focus_sessions" not in st.session_state:
    sessions = LocalStorage.get_sessions(user_id=current_uid)
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    today_sessions = [
        s for s in sessions if s.type == SessionType.FOCUS and s.startedAt.startswith(today_str)
    ]
    st.session_state.completed_focus_sessions = len(today_sessions)

if "active_task_id" not in st.session_state:
    st.session_state.active_task_id = None

if "is_focus_mode" not in st.session_state:
    st.session_state.is_focus_mode = False

if "last_tick_time" not in st.session_state:
    st.session_state.last_tick_time = time.time()


# 3. Synchronize Actions from Client Component (Firebase Auth & Session Sync via query params)
if "auth_action" in st.query_params:
    auth_act = st.query_params.get("auth_action")
    if auth_act == "login":
        uid = st.query_params.get("uid")
        email = st.query_params.get("email", "")
        name = st.query_params.get("name", "Zen User")
        photo = st.query_params.get("photo", None)
        if uid:
            user_obj = UserProfile(
                uid=uid,
                email=email,
                displayName=name,
                photoURL=photo if photo else None,
            )
            st.session_state.user = user_obj
            st.session_state.settings = LocalStorage.get_settings(user_id=uid)
            st.toast(f"Welcome back, {name}! 🌟", icon="👤")
    elif auth_act == "logout":
        st.session_state.user = None
        st.session_state.settings = LocalStorage.get_settings(user_id=None)
        st.toast("Signed out successfully. Switched to Guest mode.", icon="👋")

    st.query_params.clear()
    st.rerun()

if "action" in st.query_params:
    action = st.query_params.get("action")
    if action == "complete_session":
        sess_type_raw = st.query_params.get("type", SessionType.FOCUS.value)
        duration_raw = int(st.query_params.get("duration", "1500"))
        task_id_raw = st.query_params.get("task_id", "")

        active_task_obj: Optional[TaskItem] = None
        if task_id_raw:
            tasks_list = LocalStorage.get_tasks(user_id=current_uid)
            for t_item in tasks_list:
                if t_item.id == task_id_raw:
                    active_task_obj = t_item
                    break

        try:
            s_type = SessionType(sess_type_raw)
        except Exception:
            s_type = SessionType.FOCUS

        TimerController.record_completed_session(
            session_type=s_type,
            planned_duration=duration_raw,
            actual_duration=duration_raw,
            cycle_number=st.session_state.completed_focus_sessions + 1,
            active_task=active_task_obj,
        )

        next_s_type, updated_count = TimerController.get_next_session_type(
            current_type=s_type,
            cycle_mode=st.session_state.cycle_mode,
            completed_focus_sessions=st.session_state.completed_focus_sessions,
            sessions_before_long_break=st.session_state.settings.sessionsBeforeLongBreak,
        )
        st.session_state.session_type = next_s_type
        st.session_state.completed_focus_sessions = updated_count
        st.session_state.remaining_seconds = TimerController.get_session_duration(
            next_s_type, st.session_state.settings
        )

        st.query_params.clear()
        st.toast("🎉 Session recorded successfully to KPI Dashboard!", icon="🏆")
        st.rerun()

    elif action == "switch_phase":
        phase_raw = st.query_params.get("type", SessionType.FOCUS.value)
        try:
            st.session_state.session_type = SessionType(phase_raw)
            st.session_state.remaining_seconds = TimerController.get_session_duration(
                st.session_state.session_type, st.session_state.settings
            )
        except Exception:
            pass
        st.query_params.clear()
        st.rerun()


# 4. Helper Functions
def get_active_task() -> Optional[TaskItem]:
    if not st.session_state.active_task_id:
        return None
    tasks = LocalStorage.get_tasks(user_id=current_uid)
    for t in tasks:
        if t.id == st.session_state.active_task_id:
            return t
    return None


active_task = get_active_task()

# 5. Apply Active Theme CSS
active_theme_key = st.session_state.settings.theme.value
st.markdown(get_theme_css(active_theme_key), unsafe_allow_html=True)


# -------------------------------------------------------------
# 6. FOCUS SANCTUARY MODE (DISTRACTION-FREE VIEW)
# -------------------------------------------------------------
if st.session_state.is_focus_mode:
    f_bar1, f_bar2 = st.columns([3, 1])
    with f_bar1:
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; gap:12px; padding:8px 0;">
                <div style="width:10px; height:10px; border-radius:50%; background:var(--accent);"></div>
                <span style="font-family:'Space Grotesk',sans-serif; font-weight:700; letter-spacing:0.2em; text-transform:uppercase; font-size:14px;">
                    Zen Focus Sanctuary
                </span>
                <span style="font-size:12px; color:var(--text-muted);">
                    &bull; {active_task.title if active_task else 'General Focus'}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with f_bar2:
        if st.button("🧘 Exit Focus Sanctuary", key="exit_focus_mode", type="primary", use_container_width=True):
            st.session_state.is_focus_mode = False
            st.rerun()

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    total_dur = TimerController.get_session_duration(
        st.session_state.session_type, st.session_state.settings
    )
    clock_html = render_zen_flip_clock(
        session_type=st.session_state.session_type,
        cycle_mode=st.session_state.cycle_mode,
        remaining_seconds=st.session_state.remaining_seconds,
        total_duration=total_dur,
        timer_status=st.session_state.timer_status,
        completed_focus_sessions=st.session_state.completed_focus_sessions,
        settings=st.session_state.settings,
        active_task=active_task,
        is_focus_mode=True,
    )
    components.html(clock_html, height=440, scrolling=False)
    st.stop()


# -------------------------------------------------------------
# 7. STANDARD WORKSPACE VIEW
# -------------------------------------------------------------

# Top Header Bar with Firebase Google Auth Integration
header_col1, header_col2 = st.columns([1.1, 2.9])
with header_col1:
    st.markdown(
        """
        <div style="display:flex; align-items:center; gap:10px; padding: 6px 0;">
            <div style="width:12px; height:12px; border-radius:50%; background:var(--text-primary);"></div>
            <h1 style="margin:0; font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:700; letter-spacing:0.18em; text-transform:uppercase;">
                Zen Flip Focus
            </h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

with header_col2:
    btn_c1, btn_c2, btn_c3, btn_c4, btn_auth = st.columns([0.8, 1.0, 1.2, 0.8, 1.4])
    with btn_c1:
        sound_label = "🔊 On" if st.session_state.settings.soundEnabled else "🔇 Mute"
        if st.button(sound_label, key="toggle_sound", use_container_width=True):
            st.session_state.settings.soundEnabled = not st.session_state.settings.soundEnabled
            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.rerun()

    with btn_c2:
        if st.button("🎯 Focus", key="enter_focus_mode", use_container_width=True):
            st.session_state.is_focus_mode = True
            st.rerun()

    with btn_c3:
        mode_btn = "⚡ Learning" if st.session_state.cycle_mode == TimerCycleMode.CLASSIC else "⏱️ Classic"
        if st.button(mode_btn, key="toggle_cycle_mode", use_container_width=True):
            if st.session_state.cycle_mode == TimerCycleMode.CLASSIC:
                st.session_state.cycle_mode = TimerCycleMode.LEARNING_TRIO
                st.session_state.settings.cycleMode = TimerCycleMode.LEARNING_TRIO
            else:
                st.session_state.cycle_mode = TimerCycleMode.CLASSIC
                st.session_state.settings.cycleMode = TimerCycleMode.CLASSIC
            st.session_state.session_type = TimerController.get_initial_session_type(st.session_state.cycle_mode)
            st.session_state.remaining_seconds = TimerController.get_session_duration(
                st.session_state.session_type, st.session_state.settings
            )
            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.rerun()

    with btn_c4:
        theme_names = list(THEMES.keys())
        current_idx = theme_names.index(st.session_state.settings.theme.value)
        if st.button("🎨 Theme", key="quick_theme", use_container_width=True):
            next_idx = (current_idx + 1) % len(theme_names)
            new_theme = theme_names[next_idx]
            st.session_state.settings.theme = ThemeType(new_theme)
            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.rerun()

    with btn_auth:
        auth_widget_html = render_firebase_auth_button(
            user=st.session_state.user,
            theme_key=active_theme_key,
        )
        components.html(auth_widget_html, height=42, scrolling=False)


# Render 3D Flip Clock Component (Precisely fitted to 350px height with zero clipping)
total_dur = TimerController.get_session_duration(
    st.session_state.session_type, st.session_state.settings
)
clock_html = render_zen_flip_clock(
    session_type=st.session_state.session_type,
    cycle_mode=st.session_state.cycle_mode,
    remaining_seconds=st.session_state.remaining_seconds,
    total_duration=total_dur,
    timer_status=st.session_state.timer_status,
    completed_focus_sessions=st.session_state.completed_focus_sessions,
    settings=st.session_state.settings,
    active_task=active_task,
    is_focus_mode=False,
)
components.html(clock_html, height=350, scrolling=False)


# -------------------------------------------------------------
# 8. PHASE-SPECIFIC GUIDANCE CONSOLES
# -------------------------------------------------------------
if st.session_state.session_type == SessionType.VISUALIZATION:
    with st.container():
        st.markdown(
            """
            <div class="zen-container" style="border-left: 4px solid #8b5cf6;">
                <h3 style="margin-top:0; color:#8b5cf6; font-size:18px;">Phase 1 · Mental Visualization & Box Breathing</h3>
                <p style="font-size:13px; color:var(--text-secondary); margin-bottom:0;">
                    Prime your prefrontal cortex, reduce task friction, and rehearse flawless execution before starting work.
                </p>
                <div class="breathe-sphere" style="background: radial-gradient(circle, rgba(139,92,246,0.35) 0%, rgba(139,92,246,0.06) 72%);">
                    <span style="font-family:'Space Grotesk',sans-serif; font-weight:700; color:#8b5cf6; font-size:16px;">Box Breathing</span>
                    <span style="font-size:11px; color:var(--text-muted); margin-top:4px;">4s In &bull; 4s Hold &bull; 4s Out &bull; 4s Hold</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        vis_c1, vis_c2 = st.columns([3, 1])
        with vis_c1:
            st.checkbox("1. Prime Frictionless Launch: Mentally picture executing the very first keystroke.", key="vis_step1")
            st.checkbox("2. Distraction Inoculation: Anticipate tab-switching impulse and breathe past it.", key="vis_step2")
            st.checkbox("3. Envision Milestone Victory: Visualize completing the focus session.", key="vis_step3")
        with vis_c2:
            if st.button("Proceed to Deep Focus ▶", key="vis_to_focus", type="primary", use_container_width=True):
                st.session_state.session_type = SessionType.FOCUS
                st.session_state.remaining_seconds = TimerController.get_session_duration(
                    SessionType.FOCUS, st.session_state.settings
                )
                st.rerun()

elif st.session_state.session_type == SessionType.DIFFUSE_MODE:
    with st.container():
        st.markdown(
            """
            <div class="zen-container" style="border-left: 4px solid #10b981;">
                <h3 style="margin-top:0; color:#10b981; font-size:18px;">Phase 4 · Diffuse Mode Relaxation</h3>
                <p style="font-size:13px; color:var(--text-secondary);">
                    Default Mode Network (DMN) active: Allow subconscious neural synthesis through physical and mental disengagement.
                </p>
                <div style="display:flex; justify-content:space-around; text-align:center; font-size:13px; margin: 16px 0; gap:12px;">
                    <div style="flex:1; background:var(--bg-primary); padding:14px 18px; border-radius:14px; border:1px solid var(--border-color);">
                        👀 <b>20-20-20 Rule</b><br><span style="font-size:11px; color:var(--text-muted);">Look 20 feet away for 20 seconds to relax ciliary eye muscles</span>
                    </div>
                    <div style="flex:1; background:var(--bg-primary); padding:14px 18px; border-radius:14px; border:1px solid var(--border-color);">
                        🚶 <b>Physical Movement</b><br><span style="font-size:11px; color:var(--text-muted);">Stand up, roll shoulders, take 3 deep belly breaths</span>
                    </div>
                    <div style="flex:1; background:var(--bg-primary); padding:14px 18px; border-radius:14px; border:1px solid var(--border-color);">
                        💧 <b>Hydration</b><br><span style="font-size:11px; color:var(--text-muted);">Drink a glass of fresh water</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# -------------------------------------------------------------
# 9. TABS: TASK MANAGER, ACTIVE RECALL, KPI DASHBOARD & PREFERENCES
# -------------------------------------------------------------
st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
tab_tasks, tab_recall, tab_metrics, tab_settings = st.tabs(
    ["📋 Task Manager", "🧠 Active Recall & Flashcards", "📊 KPI Dashboard", "⚙️ Preferences"]
)


# =============================================================
# TAB 1: TASK MANAGER
# =============================================================
with tab_tasks:
    st.subheader("Task Manager & Execution Queue")
    tasks = LocalStorage.get_tasks(user_id=current_uid)

    with st.expander("➕ Add New Task", expanded=False):
        with st.form("new_task_form"):
            t_col1, t_col2 = st.columns([2, 1])
            with t_col1:
                t_title = st.text_input("Task Title", placeholder="e.g. Implement OAuth2 authentication flow")
                t_desc = st.text_area("Description (Optional)", placeholder="Notes or specifications...")
            with t_col2:
                t_cat = st.selectbox("Category", [c.value for c in TaskCategory])
                t_prio = st.selectbox("Priority", [p.value for p in TaskPriority], index=1)
                t_est = st.number_input("Estimated Pomodoros", min_value=1, max_value=20, value=2)

            submitted = st.form_submit_button("Create Task", use_container_width=True, type="primary")
            if submitted and t_title.strip():
                new_task = TaskItem(
                    userId=current_uid,
                    title=t_title.strip(),
                    description=t_desc.strip(),
                    category=TaskCategory(t_cat),
                    priority=TaskPriority(t_prio),
                    estimatedPomodoros=int(t_est),
                )
                LocalStorage.add_task(new_task)
                st.success(f"Task '{t_title.strip()}' created!")
                st.rerun()

    # Filter controls
    f_c1, f_c2 = st.columns([2, 2])
    with f_c1:
        cat_filter = st.selectbox("Filter Category", ["All"] + [c.value for c in TaskCategory])
    with f_c2:
        status_filter = st.selectbox("Filter Status", ["All", "Active Only", "Completed Only"])

    filtered_tasks = tasks
    if cat_filter != "All":
        filtered_tasks = [t for t in filtered_tasks if t.category.value == cat_filter]
    if status_filter == "Active Only":
        filtered_tasks = [t for t in filtered_tasks if not t.completed]
    elif status_filter == "Completed Only":
        filtered_tasks = [t for t in filtered_tasks if t.completed]

    if not filtered_tasks:
        st.info("No matching tasks found. Create a task above to begin tracking.")
    else:
        for t in filtered_tasks:
            is_active = t.id == st.session_state.active_task_id
            border_style = "2px solid var(--accent)" if is_active else "1px solid var(--border-color)"
            prio_badge_class = f"badge-{t.priority.value.lower()}"

            with st.container():
                st.markdown(
                    f"""
                    <div style="background:var(--bg-surface); border:{border_style}; border-radius:16px; padding:16px 20px; margin-bottom:12px; box-shadow:0 2px 10px var(--shadow-card);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <div style="font-weight:700; font-size:16px; text-decoration:{'line-through' if t.completed else 'none'};">
                                    {'✅ ' if t.completed else ''}{t.title}
                                </div>
                                <div style="font-size:12px; color:var(--text-muted); margin-top:6px; display:flex; gap:8px; align-items:center;">
                                    <span class="zen-badge {prio_badge_class}">{t.priority.value.upper()}</span>
                                    <span>Category: <b>{t.category.value}</b></span>
                                    <span>&bull;</span>
                                    <span>Focus: <b>{t.completedPomodoros}/{t.estimatedPomodoros} poms</b> ({t.totalFocusSeconds // 60}m)</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                t_actions1, t_actions2, t_actions3 = st.columns([1.2, 1, 1])
                with t_actions1:
                    sel_label = "🎯 Select for Focus" if not is_active else "⭐ Active in Timer"
                    if st.button(sel_label, key=f"sel_{t.id}", use_container_width=True):
                        st.session_state.active_task_id = t.id if not is_active else None
                        st.rerun()
                with t_actions2:
                    toggle_label = "↩ Reopen Task" if t.completed else "✔ Mark Completed"
                    if st.button(toggle_label, key=f"tog_{t.id}", use_container_width=True):
                        t.completed = not t.completed
                        t.completedAt = datetime.now(timezone.utc).isoformat() if t.completed else None
                        LocalStorage.update_task(t)
                        st.rerun()
                with t_actions3:
                    if st.button("🗑 Delete", key=f"del_{t.id}", use_container_width=True):
                        LocalStorage.delete_task(t.id)
                        if st.session_state.active_task_id == t.id:
                            st.session_state.active_task_id = None
                        st.rerun()


# =============================================================
# TAB 2: ACTIVE RECALL & RETRIEVAL FLASHCARDS (PHASE 3)
# =============================================================
with tab_recall:
    st.subheader("Active Recall & Retrieval Console (Phase 3)")
    st.write("Strengthen neural retention by quizzing yourself from memory immediately after deep work sessions.")

    cards = LocalStorage.get_flashcards(user_id=current_uid)

    with st.expander("➕ Create New Recall Flashcard", expanded=False):
        with st.form("new_card_form"):
            c_q = st.text_input("Question / Retrieval Prompt", placeholder="e.g. What is the difference between CQRS and Event Sourcing?")
            c_a = st.text_area("Answer / Core Insight", placeholder="Concise explanation or key bullet points...")
            c_sub = st.form_submit_button("Save Flashcard", use_container_width=True, type="primary")
            if c_sub and c_q.strip() and c_a.strip():
                card = RecallFlashcard(
                    userId=current_uid,
                    question=c_q.strip(),
                    answer=c_a.strip(),
                    taskId=active_task.id if active_task else None,
                )
                LocalStorage.add_flashcard(card)
                st.success("Recall Flashcard saved!")
                st.rerun()

    if not cards:
        st.info("No flashcards created yet. Add flashcards above to strengthen memory retention.")
    else:
        mastered_count = len([c for c in cards if c.mastered])
        st.write(f"**Deck Status**: {mastered_count} Mastered &bull; {len(cards) - mastered_count} Needs Review")

        for c in cards:
            mastered_icon = "⭐ Mastered" if c.mastered else "🔄 In Review"
            card_border = "1px solid #10b981" if c.mastered else "1px solid var(--border-color)"

            with st.container():
                st.markdown(
                    f"""
                    <div style="background:var(--bg-surface); border:{card_border}; border-radius:14px; padding:16px 20px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div style="font-weight:700; font-size:15px;">Q: {c.question}</div>
                            <span style="font-size:12px; color:var(--text-muted);">{mastered_icon} (Reviewed {c.reviewedCount}x)</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander("Reveal Answer"):
                    st.write(c.answer)
                    rc_col1, rc_col2, rc_col3 = st.columns([1, 1, 1])
                    with rc_col1:
                        if st.button("⭐ Mark Mastered", key=f"master_{c.id}", use_container_width=True):
                            c.mastered = True
                            c.reviewedCount += 1
                            c.lastReviewedAt = datetime.now(timezone.utc).isoformat()
                            LocalStorage.update_flashcard(c)
                            st.rerun()
                    with rc_col2:
                        if st.button("🔄 Review Again", key=f"review_{c.id}", use_container_width=True):
                            c.mastered = False
                            c.reviewedCount += 1
                            c.lastReviewedAt = datetime.now(timezone.utc).isoformat()
                            LocalStorage.update_flashcard(c)
                            st.rerun()
                    with rc_col3:
                        if st.button("🗑 Delete Card", key=f"del_card_{c.id}", use_container_width=True):
                            LocalStorage.delete_flashcard(c.id)
                            st.rerun()


# =============================================================
# TAB 3: KPI DASHBOARD & SESSIONS HISTORY
# =============================================================
with tab_metrics:
    st.subheader("Performance & Task KPI Metrics")
    all_tasks = LocalStorage.get_tasks(user_id=current_uid)
    all_sessions = LocalStorage.get_sessions(user_id=current_uid)

    total_tasks = len(all_tasks)
    completed_tasks = len([t for t in all_tasks if t.completed])
    completion_rate = int((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)

    total_est_poms = sum(t.estimatedPomodoros for t in all_tasks)
    total_actual_poms = sum(t.completedPomodoros for t in all_tasks)
    total_focus_mins = sum(t.totalFocusSeconds for t in all_tasks) // 60

    comp_t = [t for t in all_tasks if t.completed]
    spot_on = len([t for t in comp_t if t.completedPomodoros == t.estimatedPomodoros])
    accuracy = int((spot_on / len(comp_t) * 100) if comp_t else 0)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Task Velocity", f"{completion_rate}%", f"{completed_tasks}/{total_tasks} Tasks")
    m2.metric("Focus Investment", f"{total_focus_mins}m", f"{len(all_sessions)} Total Sessions")
    m3.metric("Pomodoro Burn", f"{total_actual_poms}", f"vs {total_est_poms} Est")
    m4.metric("Estimation Accuracy", f"{accuracy}%", f"{spot_on} Spot-on")

    st.markdown("---")
    st.write("### Session Log History")
    if all_sessions:
        s_data = [
            {
                "Type": s.type.value if hasattr(s.type, "value") else str(s.type),
                "Planned (s)": s.plannedDuration,
                "Actual (s)": s.actualDuration,
                "Task": s.taskName or "General Focus",
                "Timestamp": s.startedAt[:19].replace("T", " "),
            }
            for s in all_sessions[:50]
        ]
        df_sessions = pd.DataFrame(s_data)
        st.dataframe(df_sessions, use_container_width=True)

        csv_buffer = io.StringIO()
        df_sessions.to_csv(csv_buffer, index=False)
        st.download_button(
            "📥 Export Sessions CSV",
            data=csv_buffer.getvalue(),
            file_name=f"zen_pomodoro_sessions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

        if st.button("🗑 Clear Session History"):
            LocalStorage.clear_sessions(user_id=current_uid)
            st.session_state.completed_focus_sessions = 0
            st.success("Session history cleared!")
            st.rerun()
    else:
        st.info("No sessions recorded yet. Start a focus session to build history.")

    # Production Live Data Retention & Archival
    with st.expander("📦 Production Data Retention & Storage Policy (GDPR / Tiered Storage)", expanded=False):
        ret_summary = LocalStorage.get_retention_summary(user_id=current_uid)
        st.write(f"**Active Retention Window**: `{ret_summary['retention_policy_days']}` days (Rolling Hot Tier)")
        st.write(f"**Total Tracked Sessions**: `{ret_summary['total_sessions']}` | **Oldest Timestamp**: `{ret_summary['oldest_session_timestamp'] or 'N/A'}`")

        p_col1, p_col2 = st.columns(2)
        with p_col1:
            retention_days_input = st.number_input("Purge records older than (days)", min_value=7, max_value=365, value=90)
            if st.button("🧹 Enforce Retention Purge Now", use_container_width=True):
                pruned = LocalStorage.prune_expired_sessions(retention_days=int(retention_days_input), user_id=current_uid)
                st.success(f"Pruned {pruned} sessions older than {retention_days_input} days!")
                st.rerun()

        with p_col2:
            if current_uid:
                st.warning("Right to Erasure (GDPR Art. 17)")
                if st.button("⚠️ Permanently Erase All My Data", use_container_width=True):
                    LocalStorage.delete_user_data(current_uid)
                    st.session_state.user = None
                    st.session_state.settings = LocalStorage.get_settings(user_id=None)
                    st.success("All personal records purged!")
                    st.rerun()
            else:
                st.info("Sign in with Google to manage personal data erasure compliance.")

    with st.expander("🛠️ Production System Health & Diagnostics", expanded=False):
        health = perform_health_check()
        st.json(health)


# =============================================================
# TAB 4: PREFERENCES & PROTOCOL SETTINGS
# =============================================================
with tab_settings:
    st.subheader("Preferences & Protocol Settings")

    st.write("#### ⚡ Quick Preset Durations")
    p_c1, p_c2, p_c3, p_c4 = st.columns(4)
    with p_c1:
        if st.button("Classic 25/5", use_container_width=True):
            st.session_state.settings.focusDuration = 25 * 60
            st.session_state.settings.shortBreakDuration = 5 * 60
            st.session_state.settings.longBreakDuration = 15 * 60
            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.rerun()
    with p_c2:
        if st.button("Deep Sprint 50/10", use_container_width=True):
            st.session_state.settings.focusDuration = 50 * 60
            st.session_state.settings.shortBreakDuration = 10 * 60
            st.session_state.settings.longBreakDuration = 25 * 60
            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.rerun()
    with p_c3:
        if st.button("Ultradian 90/20", use_container_width=True):
            st.session_state.settings.focusDuration = 90 * 60
            st.session_state.settings.shortBreakDuration = 20 * 60
            st.session_state.settings.longBreakDuration = 30 * 60
            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.rerun()
    with p_c4:
        if st.button("Cognitive Protocol 2/20/3/5", use_container_width=True):
            st.session_state.settings.learningVisualizationDuration = 2 * 60
            st.session_state.settings.learningFocusDuration = 20 * 60
            st.session_state.settings.learningRecallDuration = 3 * 60
            st.session_state.settings.learningDiffuseDuration = 5 * 60
            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.rerun()

    st.markdown("---")
    with st.form("settings_form"):
        st.write("#### ⏳ Durations (Minutes)")
        d_col1, d_col2, d_col3 = st.columns(3)
        with d_col1:
            cfg_focus = st.number_input("Classic Focus (min)", min_value=1, max_value=120, value=st.session_state.settings.focusDuration // 60)
            cfg_short = st.number_input("Short Break (min)", min_value=1, max_value=60, value=st.session_state.settings.shortBreakDuration // 60)
            cfg_long = st.number_input("Long Break (min)", min_value=1, max_value=120, value=st.session_state.settings.longBreakDuration // 60)
        with d_col2:
            cfg_vis = st.number_input("Phase 1: Visualization (min)", min_value=1, max_value=30, value=st.session_state.settings.learningVisualizationDuration // 60)
            cfg_learn_focus = st.number_input("Phase 2: Learning Focus (min)", min_value=1, max_value=120, value=st.session_state.settings.learningFocusDuration // 60)
            cfg_rec = st.number_input("Phase 3: Active Recall (min)", min_value=1, max_value=30, value=st.session_state.settings.learningRecallDuration // 60)
        with d_col3:
            cfg_diffuse = st.number_input("Phase 4: Diffuse Mode (min)", min_value=1, max_value=60, value=st.session_state.settings.learningDiffuseDuration // 60)
            cfg_cycles = st.number_input("Sessions Before Long Break", min_value=1, max_value=10, value=st.session_state.settings.sessionsBeforeLongBreak)

        st.write("#### 🔊 Audio & Ambient Atmosphere")
        a_col1, a_col2 = st.columns(2)
        with a_col1:
            cfg_sound_en = st.checkbox("Sound Effects Enabled", value=st.session_state.settings.soundEnabled)
            cfg_chime = st.selectbox("Chime Sound", [s.value for s in ChimeSound], index=[s.value for s in ChimeSound].index(st.session_state.settings.chimeSound.value))
            cfg_vol = st.slider("Chime Volume", 0.0, 1.0, float(st.session_state.settings.soundVolume), 0.05)
            cfg_tick = st.checkbox("Tick Sound on Flips", value=st.session_state.settings.tickSoundEnabled)
        with a_col2:
            cfg_ambient = st.selectbox("Ambient Soundscape", [a.value for a in AmbientSound], index=[a.value for a in AmbientSound].index(st.session_state.settings.ambientSound.value))
            cfg_amb_vol = st.slider("Ambient Volume", 0.0, 1.0, float(st.session_state.settings.ambientVolume), 0.05)

        st.write("#### 🎨 Theme Selection")
        cfg_theme = st.selectbox("Aesthetic Theme", list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state.settings.theme.value))

        st.write("#### ⚙️ Automation & Behavior")
        b_c1, b_c2 = st.columns(2)
        with b_c1:
            cfg_auto_breaks = st.checkbox("Auto-start Breaks", value=st.session_state.settings.autoStartBreaks)
        with b_c2:
            cfg_auto_focus = st.checkbox("Auto-start Focus", value=st.session_state.settings.autoStartFocus)

        save_cfg = st.form_submit_button("Save Preferences", use_container_width=True, type="primary")
        if save_cfg:
            st.session_state.settings.focusDuration = int(cfg_focus * 60)
            st.session_state.settings.shortBreakDuration = int(cfg_short * 60)
            st.session_state.settings.longBreakDuration = int(cfg_long * 60)
            st.session_state.settings.learningVisualizationDuration = int(cfg_vis * 60)
            st.session_state.settings.learningFocusDuration = int(cfg_learn_focus * 60)
            st.session_state.settings.learningRecallDuration = int(cfg_rec * 60)
            st.session_state.settings.learningDiffuseDuration = int(cfg_diffuse * 60)
            st.session_state.settings.sessionsBeforeLongBreak = int(cfg_cycles)

            st.session_state.settings.soundEnabled = cfg_sound_en
            st.session_state.settings.chimeSound = ChimeSound(cfg_chime)
            st.session_state.settings.soundVolume = cfg_vol
            st.session_state.settings.tickSoundEnabled = cfg_tick

            st.session_state.settings.ambientSound = AmbientSound(cfg_ambient)
            st.session_state.settings.ambientVolume = cfg_amb_vol
            st.session_state.settings.theme = ThemeType(cfg_theme)

            st.session_state.settings.autoStartBreaks = cfg_auto_breaks
            st.session_state.settings.autoStartFocus = cfg_auto_focus

            LocalStorage.save_settings(st.session_state.settings, user_id=current_uid)
            st.session_state.remaining_seconds = TimerController.get_session_duration(
                st.session_state.session_type, st.session_state.settings
            )
            st.success("Preferences updated successfully!")
            st.rerun()
