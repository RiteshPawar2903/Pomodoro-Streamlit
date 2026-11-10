"""
Interactive 3D Flip Clock & Web Audio Synthesizer Component for Streamlit.
Provides a client-side split-flap mechanical flip clock with Web Audio API soundscapes,
chime synthesis, and cognitive mastery cycle controls.
Built according to IEEE Std 730/1016 standards.
"""

from __future__ import annotations

import json
from typing import Optional
from models import (
    AmbientSound,
    ChimeSound,
    SessionType,
    TaskItem,
    ThemeType,
    TimerCycleMode,
    TimerStatus,
    UserSettings,
)
from themes import THEMES


def render_zen_flip_clock(
    session_type: SessionType,
    cycle_mode: TimerCycleMode,
    remaining_seconds: int,
    total_duration: int,
    timer_status: TimerStatus,
    completed_focus_sessions: int,
    settings: UserSettings,
    active_task: Optional[TaskItem] = None,
    is_focus_mode: bool = False,
) -> str:
    """Generate self-contained interactive 3D Flip Clock HTML/JS/CSS component."""
    theme_key = settings.theme.value if hasattr(settings.theme, "value") else str(settings.theme)
    t = THEMES.get(theme_key, THEMES["geometric-balance"])

    active_task_dict = {
        "id": active_task.id,
        "title": active_task.title,
        "category": active_task.category.value,
        "priority": active_task.priority.value,
        "completedPomodoros": active_task.completedPomodoros,
        "estimatedPomodoros": active_task.estimatedPomodoros,
    } if active_task else None

    # Calculate hours, minutes, seconds
    hours = remaining_seconds // 3600
    minutes = (remaining_seconds % 3600) // 60
    seconds = remaining_seconds % 60

    h_str = f"{hours:02d}"
    m_str = f"{minutes:02d}"
    s_str = f"{seconds:02d}"

    config_data = {
        "sessionType": session_type.value,
        "cycleMode": cycle_mode.value,
        "remainingSeconds": remaining_seconds,
        "totalDuration": total_duration,
        "timerStatus": timer_status.value,
        "completedFocusSessions": completed_focus_sessions,
        "sessionsBeforeLongBreak": settings.sessionsBeforeLongBreak,
        "autoStartBreaks": settings.autoStartBreaks,
        "autoStartFocus": settings.autoStartFocus,
        "autoAdvanceLearningCycle": settings.autoAdvanceLearningCycle,
        "soundEnabled": settings.soundEnabled,
        "soundVolume": settings.soundVolume,
        "chimeSound": settings.chimeSound.value,
        "tickSoundEnabled": settings.tickSoundEnabled,
        "ambientSound": settings.ambientSound.value,
        "ambientVolume": settings.ambientVolume,
        "flipAnimation": settings.flipAnimation,
        "showSeconds": settings.showSeconds,
        "showCycleIndicator": settings.showCycleIndicator,
        "durations": {
            "focus": settings.focusDuration,
            "shortBreak": settings.shortBreakDuration,
            "longBreak": settings.longBreakDuration,
            "visualization": settings.learningVisualizationDuration,
            "learningFocus": settings.learningFocusDuration,
            "recall": settings.learningRecallDuration,
            "diffuse": settings.learningDiffuseDuration,
        },
        "activeTask": active_task_dict,
        "isFocusMode": is_focus_mode,
        "theme": t,
    }

    config_json = json.dumps(config_data)

    card_width = "104px" if is_focus_mode else "82px"
    card_height = "138px" if is_focus_mode else "112px"
    font_size = "78px" if is_focus_mode else "62px"
    line_height = "138px" if is_focus_mode else "112px"
    half_height = "69px" if is_focus_mode else "56px"

    html_code = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;700;800&family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {{
    --bg-primary: {t["bg_primary"]};
    --bg-surface: {t["bg_surface"]};
    --bg-card-top: {t["bg_card_top"]};
    --bg-card-bottom: {t["bg_card_bottom"]};
    --text-primary: {t["text_primary"]};
    --text-secondary: {t["text_secondary"]};
    --text-muted: {t["text_muted"]};
    --accent: {t["accent"]};
    --border-color: {t["border_color"]};
    --hinge-color: {t["hinge_color"]};
    --shadow-card: {t["shadow_card"]};
}}

* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    user-select: none;
    -webkit-user-select: none;
}}

html, body {{
    background: transparent;
    color: var(--text-primary);
    font-family: 'Outfit', sans-serif;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4px 10px;
    overflow: hidden;
    height: 100%;
}}

.zen-card-panel {{
    width: 100%;
    max-width: 860px;
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 22px;
    padding: 16px 24px;
    box-shadow: 0 10px 30px var(--shadow-card);
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
}}

/* Top Status Banner */
.clock-header {{
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}}

.phase-pill-group {{
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    justify-content: center;
}}

.phase-btn {{
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 12px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 9999px;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
}}

.phase-btn:hover {{
    color: var(--text-primary);
    border-color: var(--accent);
    transform: translateY(-1px);
}}

.phase-btn.active {{
    background: var(--accent);
    color: var(--bg-surface);
    border-color: var(--accent);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}}

.phase-btn .dot {{
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: currentColor;
}}

/* Cycle Progress Dots */
.cycle-dots-container {{
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
}}

.cycle-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--border-color);
    transition: all 0.3s ease;
}}

.cycle-dot.filled {{
    background: var(--accent);
    box-shadow: 0 0 5px var(--accent);
}}

/* 3D Flip Clock Layout */
.flip-clock-stage {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 14px;
    margin: 8px 0 10px 0;
}}

.flip-group {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}}

.flip-digits {{
    display: flex;
    gap: 6px;
}}

/* Single 3D Flip Card */
.flip-card-container {{
    position: relative;
    width: {card_width};
    height: {card_height};
    perspective: 800px;
    -webkit-perspective: 800px;
    border-radius: 16px;
}}

.flip-unit {{
    position: relative;
    width: 100%;
    height: 100%;
    border-radius: inherit;
    box-shadow: 0 14px 28px var(--shadow-card), 0 2px 6px rgba(0,0,0,0.06);
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
}}

/* Static Top & Bottom halves */
.flip-card-static-top,
.flip-card-static-bottom,
.flip-flap-top,
.flip-flap-bottom {{
    position: absolute;
    left: 0;
    right: 0;
    overflow: hidden;
    text-align: center;
    color: var(--text-primary);
}}

.flip-card-static-top {{
    top: 0;
    height: {half_height};
    border-top-left-radius: inherit;
    border-top-right-radius: inherit;
    background: var(--bg-card-top);
    border-top: 1px solid var(--border-color);
    border-left: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
}}

.flip-card-static-bottom {{
    bottom: 0;
    height: {half_height};
    border-bottom-left-radius: inherit;
    border-bottom-right-radius: inherit;
    background: var(--bg-card-bottom);
    border-bottom: 1px solid var(--border-color);
    border-left: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
}}

.flip-digit-text {{
    position: absolute;
    left: 0;
    right: 0;
    width: 100%;
    font-size: {font_size};
    line-height: {line_height};
    text-align: center;
}}

.flip-card-static-top .flip-digit-text,
.flip-flap-top .flip-digit-text {{
    top: 0;
}}

.flip-card-static-bottom .flip-digit-text,
.flip-flap-bottom .flip-digit-text {{
    top: -{half_height};
}}

/* Flipping Flaps */
.flip-flap-top {{
    top: 0;
    height: {half_height};
    border-top-left-radius: inherit;
    border-top-right-radius: inherit;
    background: var(--bg-card-top);
    border-top: 1px solid var(--border-color);
    border-left: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    transform-origin: 50% 100%;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    z-index: 20;
}}

.flip-flap-bottom {{
    bottom: 0;
    height: {half_height};
    border-bottom-left-radius: inherit;
    border-bottom-right-radius: inherit;
    background: var(--bg-card-bottom);
    border-bottom: 1px solid var(--border-color);
    border-left: 1px solid var(--border-color);
    border-right: 1px solid var(--border-color);
    transform-origin: 50% 0%;
    backface-visibility: hidden;
    -webkit-backface-visibility: hidden;
    z-index: 30;
}}

/* 3D Keyframe Animations */
@keyframes flip-down-top {{
    0% {{ transform: rotateX(0deg); }}
    100% {{ transform: rotateX(-90deg); }}
}}

@keyframes flip-down-bottom {{
    0% {{ transform: rotateX(90deg); }}
    100% {{ transform: rotateX(0deg); }}
}}

.anim-flip-top {{
    animation: flip-down-top 0.22s cubic-bezier(0.37, 0, 0.63, 1) forwards;
}}

.anim-flip-bottom {{
    animation: flip-down-bottom 0.22s cubic-bezier(0.37, 0, 0.63, 1) 0.20s forwards;
}}

/* Glare & Shadows */
.flip-glare-top {{
    position: absolute;
    inset: 0;
    background: linear-gradient(to bottom, rgba(255,255,255,0.08), transparent);
    pointer-events: none;
}}

.flip-shadow-bottom {{
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.18), transparent);
    pointer-events: none;
}}

/* Center Divider Line & Notches */
.flip-divider {{
    position: absolute;
    left: 0;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    height: 2px;
    background: var(--hinge-color);
    z-index: 40;
    pointer-events: none;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
}}

.flip-notch-left {{
    position: absolute;
    left: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 5px;
    height: 10px;
    background: var(--bg-surface);
    border-top-right-radius: 5px;
    border-bottom-right-radius: 5px;
    z-index: 45;
}}

.flip-notch-right {{
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 5px;
    height: 10px;
    background: var(--bg-surface);
    border-top-left-radius: 5px;
    border-bottom-left-radius: 5px;
    z-index: 45;
}}

.flip-label {{
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--text-muted);
}}

.flip-colon {{
    font-family: 'Space Grotesk', sans-serif;
    font-size: 42px;
    font-weight: 300;
    color: var(--text-muted);
    margin-top: -18px;
    opacity: 0.5;
}}

/* Smooth Progress Bar */
.progress-container {{
    width: 100%;
    height: 5px;
    background: var(--bg-primary);
    border-radius: 9999px;
    overflow: hidden;
    margin: 6px 0 12px 0;
    position: relative;
    border: 1px solid var(--border-color);
}}

.progress-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, var(--text-muted), var(--accent));
    border-radius: 9999px;
    transition: width 0.35s ease;
    width: 0%;
}}

/* Interactive Controls Toolbar */
.controls-toolbar {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    width: 100%;
    flex-wrap: wrap;
}}

.ctrl-btn {{
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 600;
    font-size: 13px;
    padding: 8px 16px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    background: var(--bg-primary);
    color: var(--text-primary);
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}}

.ctrl-btn:hover {{
    transform: translateY(-1px);
    box-shadow: 0 4px 12px var(--shadow-card);
    border-color: var(--accent);
}}

.ctrl-btn.primary {{
    background: var(--accent);
    color: var(--bg-surface);
    border-color: var(--accent);
    padding: 9px 22px;
    font-size: 13px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15);
}}

.ctrl-btn.primary:hover {{
    filter: brightness(1.1);
}}

.task-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    max-width: 230px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

/* Ambient Sound Bar */
.ambient-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border-color);
    font-size: 12px;
    color: var(--text-muted);
}}

.ambient-select {{
    background: var(--bg-primary);
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 4px 8px;
    font-size: 12px;
    cursor: pointer;
}}

/* Keyboard shortcuts hint */
.shortcuts-hint {{
    font-size: 11px;
    color: var(--text-muted);
    display: flex;
    gap: 10px;
}}
kbd {{
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    padding: 1px 4px;
    border-radius: 4px;
    font-family: monospace;
}}
</style>
</head>
<body>

<div class="zen-card-panel">
    <!-- Top Bar: Phase Pills & Cycle Indicator -->
    <div class="clock-header">
        <div class="phase-pill-group" id="phase-pills"></div>

        <div class="cycle-dots-container" id="cycle-dots-box" title="Pomodoros until long break">
            <span>Cycle</span>
            <div class="cycle-dots" id="cycle-dots" style="display:flex; gap:4px;"></div>
        </div>
    </div>

    <!-- 3D Flip Clock View -->
    <div class="flip-clock-stage">
        <!-- Hours (if hours > 0) -->
        <div class="flip-group" id="hours-group" style="display: none;">
            <div class="flip-digits">
                <div class="flip-card-container" id="card-h0">
                    <div class="flip-unit">
                        <div class="flip-card-static-top"><div class="flip-digit-text" id="h0-top">{h_str[0]}</div><div class="flip-glare-top"></div></div>
                        <div class="flip-card-static-bottom"><div class="flip-digit-text" id="h0-bot">{h_str[0]}</div><div class="flip-shadow-bottom"></div></div>
                        <div class="flip-divider"></div><div class="flip-notch-left"></div><div class="flip-notch-right"></div>
                    </div>
                </div>
                <div class="flip-card-container" id="card-h1">
                    <div class="flip-unit">
                        <div class="flip-card-static-top"><div class="flip-digit-text" id="h1-top">{h_str[1]}</div><div class="flip-glare-top"></div></div>
                        <div class="flip-card-static-bottom"><div class="flip-digit-text" id="h1-bot">{h_str[1]}</div><div class="flip-shadow-bottom"></div></div>
                        <div class="flip-divider"></div><div class="flip-notch-left"></div><div class="flip-notch-right"></div>
                    </div>
                </div>
            </div>
            <span class="flip-label">Hours</span>
        </div>

        <div class="flip-colon" id="colon-h" style="display: none;">:</div>

        <!-- Minutes -->
        <div class="flip-group">
            <div class="flip-digits">
                <div class="flip-card-container" id="card-m0">
                    <div class="flip-unit">
                        <div class="flip-card-static-top"><div class="flip-digit-text" id="m0-top">{m_str[0]}</div><div class="flip-glare-top"></div></div>
                        <div class="flip-card-static-bottom"><div class="flip-digit-text" id="m0-bot">{m_str[0]}</div><div class="flip-shadow-bottom"></div></div>
                        <div class="flip-divider"></div><div class="flip-notch-left"></div><div class="flip-notch-right"></div>
                    </div>
                </div>
                <div class="flip-card-container" id="card-m1">
                    <div class="flip-unit">
                        <div class="flip-card-static-top"><div class="flip-digit-text" id="m1-top">{m_str[1]}</div><div class="flip-glare-top"></div></div>
                        <div class="flip-card-static-bottom"><div class="flip-digit-text" id="m1-bot">{m_str[1]}</div><div class="flip-shadow-bottom"></div></div>
                        <div class="flip-divider"></div><div class="flip-notch-left"></div><div class="flip-notch-right"></div>
                    </div>
                </div>
            </div>
            <span class="flip-label">Minutes</span>
        </div>

        <div class="flip-colon">:</div>

        <!-- Seconds -->
        <div class="flip-group">
            <div class="flip-digits">
                <div class="flip-card-container" id="card-s0">
                    <div class="flip-unit">
                        <div class="flip-card-static-top"><div class="flip-digit-text" id="s0-top">{s_str[0]}</div><div class="flip-glare-top"></div></div>
                        <div class="flip-card-static-bottom"><div class="flip-digit-text" id="s0-bot">{s_str[0]}</div><div class="flip-shadow-bottom"></div></div>
                        <div class="flip-divider"></div><div class="flip-notch-left"></div><div class="flip-notch-right"></div>
                    </div>
                </div>
                <div class="flip-card-container" id="card-s1">
                    <div class="flip-unit">
                        <div class="flip-card-static-top"><div class="flip-digit-text" id="s1-top">{s_str[1]}</div><div class="flip-glare-top"></div></div>
                        <div class="flip-card-static-bottom"><div class="flip-digit-text" id="s1-bot">{s_str[1]}</div><div class="flip-shadow-bottom"></div></div>
                        <div class="flip-divider"></div><div class="flip-notch-left"></div><div class="flip-notch-right"></div>
                    </div>
                </div>
            </div>
            <span class="flip-label">Seconds</span>
        </div>
    </div>

    <!-- Progress Bar -->
    <div class="progress-container">
        <div class="progress-bar-fill" id="progress-bar"></div>
    </div>

    <!-- Controls Toolbar -->
    <div class="controls-toolbar">
        <button class="ctrl-btn primary" id="btn-toggle">
            <span id="btn-toggle-icon">▶</span>
            <span id="btn-toggle-label">Start Focus</span>
        </button>
        <button class="ctrl-btn" id="btn-reset">
            <span>⏹</span> Reset
        </button>
        <button class="ctrl-btn" id="btn-skip">
            <span>⏭</span> Skip Phase
        </button>
        <button class="ctrl-btn" id="btn-complete-sync" style="background: rgba(16,185,129,0.12); border-color:#10b981; color:#10b981;" title="Record completed session into database">
            <span>⭐</span> Record Session
        </button>

        <div class="task-badge" id="task-badge">
            <span>🎯</span>
            <span id="task-badge-title">General Focus Session</span>
        </div>
    </div>

    <!-- Ambient Soundscape & Shortcuts Footer -->
    <div class="ambient-bar">
        <div style="display:flex; align-items:center; gap:8px;">
            <span id="sound-indicator" style="cursor:pointer;" title="Click to toggle mute">🔊</span>
            <select class="ambient-select" id="ambient-selector">
                <option value="none">Soundscape: Off</option>
                <option value="brown-noise">Brown Noise</option>
                <option value="gentle-rain">Gentle Rain</option>
                <option value="crackling-fireplace">Fireplace</option>
                <option value="forest-wind">Forest Wind</option>
                <option value="summer-night">Summer Night</option>
            </select>
            <input type="range" id="ambient-vol" min="0" max="1" step="0.05" value="0.5" style="width:65px; accent-color:var(--accent);" title="Ambient volume">
        </div>

        <div class="shortcuts-hint">
            <span><kbd>Space</kbd> Start/Pause</span>
            <span><kbd>R</kbd> Reset</span>
            <span><kbd>S</kbd> Skip</span>
            <span><kbd>M</kbd> Mute</span>
        </div>
    </div>
</div>

<script>
(function() {{
    const CFG = {config_json};

    let remainingSeconds = CFG.remainingSeconds;
    let totalDuration = CFG.totalDuration || remainingSeconds;
    let timerStatus = CFG.timerStatus;
    let currentSessionType = CFG.sessionType;
    let cycleMode = CFG.cycleMode;
    let completedSessions = CFG.completedFocusSessions;
    let intervalId = null;
    let audioCtx = null;
    let ambientSource = null;
    let ambientGain = null;
    let isMuted = !CFG.soundEnabled;

    let prevDigits = {{
        h0: "{h_str[0]}", h1: "{h_str[1]}",
        m0: "{m_str[0]}", m1: "{m_str[1]}",
        s0: "{s_str[0]}", s1: "{s_str[1]}"
    }};

    // DOM Elements
    const btnToggle = document.getElementById('btn-toggle');
    const btnToggleIcon = document.getElementById('btn-toggle-icon');
    const btnToggleLabel = document.getElementById('btn-toggle-label');
    const btnReset = document.getElementById('btn-reset');
    const btnSkip = document.getElementById('btn-skip');
    const btnCompleteSync = document.getElementById('btn-complete-sync');
    const progressBar = document.getElementById('progress-bar');
    const phasePills = document.getElementById('phase-pills');
    const cycleDots = document.getElementById('cycle-dots');
    const taskBadgeTitle = document.getElementById('task-badge-title');
    const ambientSelector = document.getElementById('ambient-selector');
    const ambientVol = document.getElementById('ambient-vol');
    const soundIndicator = document.getElementById('sound-indicator');

    if (CFG.activeTask) {{
        taskBadgeTitle.textContent = `${{CFG.activeTask.title}} (${{CFG.activeTask.completedPomodoros}}/${{CFG.activeTask.estimatedPomodoros}} poms)`;
    }} else {{
        taskBadgeTitle.textContent = "General Focus Session";
    }}

    ambientSelector.value = CFG.ambientSound || "none";
    ambientVol.value = CFG.ambientVolume || 0.5;

    function renderPhasePills() {{
        phasePills.innerHTML = '';
        let options = [];
        if (cycleMode === 'learning_trio') {{
            options = [
                {{ type: 'visualization', label: '1. Visualization' }},
                {{ type: 'focus', label: '2. Deep Focus' }},
                {{ type: 'active_recall', label: '3. Active Recall' }},
                {{ type: 'diffuse_mode', label: '4. Diffuse Mode' }}
            ];
        }} else {{
            options = [
                {{ type: 'focus', label: 'Focus' }},
                {{ type: 'short_break', label: 'Short Break' }},
                {{ type: 'long_break', label: 'Long Break' }}
            ];
        }}

        options.forEach(opt => {{
            const btn = document.createElement('button');
            btn.className = `phase-btn ${{currentSessionType === opt.type ? 'active' : ''}}`;
            btn.innerHTML = `<span class="dot"></span>${{opt.label}}`;
            btn.onclick = () => selectSessionType(opt.type);
            phasePills.appendChild(btn);
        }});
    }}

    function renderCycleDots() {{
        cycleDots.innerHTML = '';
        const total = CFG.sessionsBeforeLongBreak || 4;
        const currentMod = completedSessions % total;
        for (let i = 0; i < total; i++) {{
            const dot = document.createElement('div');
            dot.className = `cycle-dot ${{i < currentMod ? 'filled' : ''}}`;
            cycleDots.appendChild(dot);
        }}
    }}

    function getDuration(sType) {{
        const d = CFG.durations;
        if (sType === 'visualization') return d.visualization;
        if (sType === 'focus') return cycleMode === 'learning_trio' ? d.learningFocus : d.focus;
        if (sType === 'active_recall') return d.recall;
        if (sType === 'diffuse_mode') return d.diffuse;
        if (sType === 'short_break') return d.shortBreak;
        if (sType === 'long_break') return d.longBreak;
        return d.focus;
    }}

    function selectSessionType(sType) {{
        currentSessionType = sType;
        totalDuration = getDuration(sType);
        remainingSeconds = totalDuration;
        pauseTimer();
        renderPhasePills();
        updateDisplay(remainingSeconds, true);

        // Sync with parent Streamlit workspace
        try {{
            if (window.parent && window.parent.location) {{
                window.parent.location.search = `?action=switch_phase&type=${{sType}}`;
            }}
        }} catch(e) {{}}
    }}

    function flipDigitCard(cardId, newVal, oldVal) {{
        const container = document.getElementById(cardId);
        if (!container) return;
        const unit = container.querySelector('.flip-unit');
        if (!unit) return;

        if (!CFG.flipAnimation) {{
            const topVal = container.querySelector('.flip-card-static-top .flip-digit-text');
            const botVal = container.querySelector('.flip-card-static-bottom .flip-digit-text');
            if (topVal) topVal.textContent = newVal;
            if (botVal) botVal.textContent = newVal;
            return;
        }}

        const staticTopVal = unit.querySelector('.flip-card-static-top .flip-digit-text');
        if (staticTopVal) staticTopVal.textContent = newVal;

        const oldFlapTop = unit.querySelector('.flip-flap-top');
        const oldFlapBot = unit.querySelector('.flip-flap-bottom');
        if (oldFlapTop) oldFlapTop.remove();
        if (oldFlapBot) oldFlapBot.remove();

        const flapTop = document.createElement('div');
        flapTop.className = 'flip-flap-top anim-flip-top';
        flapTop.innerHTML = `<div class="flip-digit-text">${{oldVal}}</div><div class="flip-glare-top"></div>`;

        const flapBot = document.createElement('div');
        flapBot.className = 'flip-flap-bottom anim-flip-bottom';
        flapBot.innerHTML = `<div class="flip-digit-text" style="top:-${{container.offsetHeight / 2}}px;">${{newVal}}</div><div class="flip-shadow-bottom"></div>`;

        unit.appendChild(flapTop);
        unit.appendChild(flapBot);

        setTimeout(() => {{
            const staticBotVal = unit.querySelector('.flip-card-static-bottom .flip-digit-text');
            if (staticBotVal) staticBotVal.textContent = newVal;
            flapTop.remove();
            flapBot.remove();
        }}, 420);
    }}

    function updateDisplay(remSecs, force = false) {{
        const h = Math.floor(remSecs / 3600);
        const m = Math.floor((remSecs % 3600) / 60);
        const s = remSecs % 60;

        const h0 = String(Math.floor(h / 10));
        const h1 = String(h % 10);
        const m0 = String(Math.floor(m / 10));
        const m1 = String(m % 10);
        const s0 = String(Math.floor(s / 10));
        const s1 = String(s % 10);

        const hoursGroup = document.getElementById('hours-group');
        const colonH = document.getElementById('colon-h');
        if (h > 0) {{
            hoursGroup.style.display = 'flex';
            colonH.style.display = 'block';
            if (h0 !== prevDigits.h0 || force) flipDigitCard('card-h0', h0, prevDigits.h0);
            if (h1 !== prevDigits.h1 || force) flipDigitCard('card-h1', h1, prevDigits.h1);
            prevDigits.h0 = h0;
            prevDigits.h1 = h1;
        }} else {{
            hoursGroup.style.display = 'none';
            colonH.style.display = 'none';
        }}

        if (m0 !== prevDigits.m0 || force) flipDigitCard('card-m0', m0, prevDigits.m0);
        if (m1 !== prevDigits.m1 || force) flipDigitCard('card-m1', m1, prevDigits.m1);
        if (s0 !== prevDigits.s0 || force) flipDigitCard('card-s0', s0, prevDigits.s0);
        if (s1 !== prevDigits.s1 || force) flipDigitCard('card-s1', s1, prevDigits.s1);

        prevDigits.m0 = m0;
        prevDigits.m1 = m1;
        prevDigits.s0 = s0;
        prevDigits.s1 = s1;

        const ratio = totalDuration > 0 ? Math.max(0, Math.min(1, 1 - (remSecs / totalDuration))) : 0;
        progressBar.style.width = `${{(ratio * 100).toFixed(1)}}%`;

        if (CFG.tickSoundEnabled && timerStatus === 'running') {{
            playTickSound();
        }}
    }}

    function initAudio() {{
        try {{
            if (!audioCtx) {{
                const AudioCtx = window.AudioContext || window.webkitAudioContext;
                if (AudioCtx) audioCtx = new AudioCtx();
            }}
            if (audioCtx && audioCtx.state === 'suspended') {{
                audioCtx.resume();
            }}
        }} catch(e) {{
            console.warn("Audio note:", e);
        }}
    }}

    function playChime(chimeType = CFG.chimeSound, vol = CFG.soundVolume) {{
        if (isMuted || chimeType === 'none' || vol <= 0) return;
        initAudio();
        if (!audioCtx) return;

        const now = audioCtx.currentTime;
        if (chimeType === 'singing-bowl' || chimeType === 'zen-gong') {{
            const baseFreq = chimeType === 'zen-gong' ? 130.81 : 261.63;
            const freqs = [baseFreq, baseFreq * 2, baseFreq * 3.01];
            freqs.forEach((f, idx) => {{
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(f, now);
                gain.gain.setValueAtTime(0, now);
                gain.gain.linearRampToValueAtTime((vol * 0.45) / (idx + 1), now + 0.08);
                gain.gain.exponentialRampToValueAtTime(0.0001, now + (chimeType === 'zen-gong' ? 4.0 : 3.5));
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now);
                osc.stop(now + 4.0);
            }});
        }} else if (chimeType === 'soft-bell' || chimeType === 'crystal-chime') {{
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = chimeType === 'crystal-chime' ? 'sine' : 'triangle';
            osc.frequency.setValueAtTime(chimeType === 'crystal-chime' ? 1760 : 880, now);
            osc.frequency.exponentialRampToValueAtTime(chimeType === 'crystal-chime' ? 880 : 440, now + 1.2);
            gain.gain.setValueAtTime(vol * 0.5, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 1.8);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 1.8);
        }} else if (chimeType === 'wooden-clack') {{
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'square';
            osc.frequency.setValueAtTime(320, now);
            gain.gain.setValueAtTime(vol * 0.6, now);
            gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.12);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.15);
        }} else if (chimeType === 'gentle-marimba') {{
            [523.25, 659.25, 783.99].forEach((f, i) => {{
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(f, now + (i * 0.1));
                gain.gain.setValueAtTime(0, now + (i * 0.1));
                gain.gain.linearRampToValueAtTime(vol * 0.45, now + (i * 0.1) + 0.02);
                gain.gain.exponentialRampToValueAtTime(0.001, now + (i * 0.1) + 0.9);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start(now + (i * 0.1));
                osc.stop(now + (i * 0.1) + 0.95);
            }});
        }}
    }}

    function playTickSound() {{
        if (isMuted) return;
        initAudio();
        if (!audioCtx) return;
        const now = audioCtx.currentTime;
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(1200, now);
        gain.gain.setValueAtTime(0.04, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.02);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(now);
        osc.stop(now + 0.025);
    }}

    function startAmbientSound(ambientType, volume) {{
        stopAmbientSound();
        if (isMuted || ambientType === 'none' || volume <= 0) return;
        initAudio();
        if (!audioCtx) return;

        try {{
            const bufferSize = audioCtx.sampleRate * 2;
            const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const data = buffer.getChannelData(0);
            let lastOut = 0.0;

            for (let i = 0; i < bufferSize; i++) {{
                const white = Math.random() * 2 - 1;
                if (ambientType === 'brown-noise') {{
                    lastOut = (lastOut + (0.02 * white)) / 1.02;
                    data[i] = lastOut * 3.5;
                }} else if (ambientType === 'gentle-rain') {{
                    lastOut = (lastOut + (0.08 * white)) / 1.08;
                    const drop = Math.random() < 0.001 ? (Math.random() * 1.5) : 0;
                    data[i] = (lastOut * 2.2) + drop;
                }} else if (ambientType === 'crackling-fireplace') {{
                    lastOut = (lastOut + (0.015 * white)) / 1.015;
                    const pop = Math.random() < 0.003 ? (Math.random() * 2.5 - 1.25) : 0;
                    data[i] = (lastOut * 3.0) + pop;
                }} else {{
                    lastOut = (lastOut + (0.03 * white)) / 1.03;
                    data[i] = lastOut * 2.8;
                }}
            }}

            const noise = audioCtx.createBufferSource();
            noise.buffer = buffer;
            noise.loop = true;

            const filter = audioCtx.createBiquadFilter();
            filter.type = 'lowpass';
            filter.frequency.value = ambientType === 'brown-noise' ? 380 : (ambientType === 'gentle-rain' ? 850 : 500);

            ambientGain = audioCtx.createGain();
            ambientGain.gain.setValueAtTime(volume * 0.18, audioCtx.currentTime);

            noise.connect(filter);
            filter.connect(ambientGain);
            ambientGain.connect(audioCtx.destination);
            noise.start();
            ambientSource = noise;
        }} catch(e) {{
            console.warn("Ambient generation note:", e);
        }}
    }}

    function stopAmbientSound() {{
        if (ambientSource) {{
            try {{ ambientSource.stop(); ambientSource.disconnect(); }} catch(e) {{}}
            ambientSource = null;
        }}
    }}

    function startTimer() {{
        initAudio();
        timerStatus = 'running';
        btnToggleIcon.textContent = '⏸';
        btnToggleLabel.textContent = 'Pause Timer';

        startAmbientSound(ambientSelector.value, parseFloat(ambientVol.value));

        if (intervalId) clearInterval(intervalId);
        intervalId = setInterval(() => {{
            if (remainingSeconds > 0) {{
                remainingSeconds--;
                updateDisplay(remainingSeconds);
            }}

            if (remainingSeconds === 0) {{
                handleSessionComplete();
            }}
        }}, 1000);
    }}

    function pauseTimer() {{
        timerStatus = 'paused';
        btnToggleIcon.textContent = '▶';
        btnToggleLabel.textContent = 'Resume Timer';
        if (intervalId) {{
            clearInterval(intervalId);
            intervalId = null;
        }}
        stopAmbientSound();
    }}

    function resetTimer() {{
        pauseTimer();
        btnToggleIcon.textContent = '▶';
        btnToggleLabel.textContent = 'Start Focus';
        remainingSeconds = totalDuration;
        updateDisplay(remainingSeconds, true);
    }}

    function handleSessionComplete() {{
        pauseTimer();
        playChime();

        const actualDur = totalDuration;
        const sType = currentSessionType;
        const taskId = CFG.activeTask ? CFG.activeTask.id : '';

        if (cycleMode === 'learning_trio') {{
            if (sType === 'focus') completedSessions++;
        }} else {{
            if (sType === 'focus') completedSessions++;
        }}

        renderCycleDots();

        // Sync with parent Streamlit workspace to record into SQLite
        setTimeout(() => {{
            syncSessionToParent(sType, actualDur, taskId);
        }}, 1000);
    }}

    function syncSessionToParent(sType, dur, taskId) {{
        try {{
            const search = `?action=complete_session&type=${{sType}}&duration=${{dur}}&task_id=${{taskId}}`;
            if (window.parent && window.parent.location) {{
                window.parent.location.search = search;
            }}
        }} catch(e) {{
            console.log("Sync note:", e);
        }}
    }}

    function skipSession() {{
        pauseTimer();
        let nextType = 'focus';
        if (cycleMode === 'learning_trio') {{
            if (currentSessionType === 'visualization') nextType = 'focus';
            else if (currentSessionType === 'focus') nextType = 'active_recall';
            else if (currentSessionType === 'active_recall') nextType = 'diffuse_mode';
            else nextType = 'visualization';
        }} else {{
            if (currentSessionType === 'focus') nextType = 'short_break';
            else nextType = 'focus';
        }}
        selectSessionType(nextType);
    }}

    // Event Handlers
    btnToggle.onclick = () => {{
        if (timerStatus === 'running') {{
            pauseTimer();
        }} else {{
            startTimer();
        }}
    }};

    btnReset.onclick = resetTimer;
    btnSkip.onclick = skipSession;
    btnCompleteSync.onclick = handleSessionComplete;

    ambientSelector.onchange = () => {{
        if (timerStatus === 'running') {{
            startAmbientSound(ambientSelector.value, parseFloat(ambientVol.value));
        }}
    }};

    ambientVol.oninput = () => {{
        if (ambientGain && audioCtx) {{
            ambientGain.gain.setValueAtTime(parseFloat(ambientVol.value) * 0.18, audioCtx.currentTime);
        }}
    }};

    soundIndicator.onclick = () => {{
        isMuted = !isMuted;
        soundIndicator.textContent = isMuted ? '🔇' : '🔊';
        if (isMuted) stopAmbientSound();
        else if (timerStatus === 'running') startAmbientSound(ambientSelector.value, parseFloat(ambientVol.value));
    }};

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {{
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        if (e.code === 'Space') {{
            e.preventDefault();
            btnToggle.click();
        }} else if (e.code === 'KeyR') {{
            e.preventDefault();
            btnReset.click();
        }} else if (e.code === 'KeyS') {{
            e.preventDefault();
            btnSkip.click();
        }} else if (e.code === 'KeyM') {{
            e.preventDefault();
            soundIndicator.click();
        }}
    }});

    // Initial Renders
    renderPhasePills();
    renderCycleDots();
    updateDisplay(remainingSeconds, true);

    if (CFG.timerStatus === 'running') {{
        startTimer();
    }}
}})();
</script>
</body>
</html>
    """
    return html_code
