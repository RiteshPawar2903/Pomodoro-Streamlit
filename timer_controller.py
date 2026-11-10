"""
State machine and timer logic for Zen Pomodoro Clock.
Supports Classic Pomodoro and the 4-Phase Cognitive Mastery Protocol (Learning Trio).
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Optional, Tuple

from models import (
    PomodoroSession,
    SessionType,
    TaskItem,
    TimerCycleMode,
    TimerStatus,
    UserSettings,
)
from storage import LocalStorage


class TimerController:
    """Manages timer transitions, session history logging, and cycle advances."""

    @staticmethod
    def get_initial_session_type(cycle_mode: TimerCycleMode) -> SessionType:
        if cycle_mode == TimerCycleMode.LEARNING_TRIO:
            return SessionType.VISUALIZATION
        return SessionType.FOCUS

    @staticmethod
    def get_session_duration(
        session_type: SessionType, settings: UserSettings
    ) -> int:
        """Returns duration in seconds for given session type."""
        if session_type == SessionType.VISUALIZATION:
            return settings.learningVisualizationDuration
        elif session_type == SessionType.FOCUS:
            if settings.cycleMode == TimerCycleMode.LEARNING_TRIO:
                return settings.learningFocusDuration
            return settings.focusDuration
        elif session_type == SessionType.ACTIVE_RECALL:
            return settings.learningRecallDuration
        elif session_type == SessionType.DIFFUSE_MODE:
            return settings.learningDiffuseDuration
        elif session_type == SessionType.SHORT_BREAK:
            return settings.shortBreakDuration
        elif session_type == SessionType.LONG_BREAK:
            return settings.longBreakDuration
        return settings.focusDuration

    @staticmethod
    def get_next_session_type(
        current_type: SessionType,
        cycle_mode: TimerCycleMode,
        completed_focus_sessions: int,
        sessions_before_long_break: int,
    ) -> Tuple[SessionType, int]:
        """Calculates next session type and updated completed session count."""
        next_count = completed_focus_sessions

        if cycle_mode == TimerCycleMode.LEARNING_TRIO:
            if current_type == SessionType.VISUALIZATION:
                return SessionType.FOCUS, next_count
            elif current_type == SessionType.FOCUS:
                next_count += 1
                return SessionType.ACTIVE_RECALL, next_count
            elif current_type == SessionType.ACTIVE_RECALL:
                return SessionType.DIFFUSE_MODE, next_count
            elif current_type == SessionType.DIFFUSE_MODE:
                return SessionType.VISUALIZATION, next_count
            else:
                return SessionType.VISUALIZATION, next_count

        # Classic Mode
        if current_type == SessionType.FOCUS:
            next_count += 1
            if next_count % sessions_before_long_break == 0:
                return SessionType.LONG_BREAK, next_count
            return SessionType.SHORT_BREAK, next_count
        else:
            return SessionType.FOCUS, next_count

    @staticmethod
    def record_completed_session(
        session_type: SessionType,
        planned_duration: int,
        actual_duration: int,
        cycle_number: int,
        active_task: Optional[TaskItem] = None,
    ) -> None:
        """Persists completed session and updates active task statistics."""
        now_str = datetime.now(timezone.utc).isoformat()
        session = PomodoroSession(
            type=session_type,
            status="completed",
            plannedDuration=planned_duration,
            actualDuration=actual_duration,
            startedAt=now_str,
            endedAt=now_str,
            cycleNumber=cycle_number,
            taskId=active_task.id if active_task else None,
            taskName=active_task.title if active_task else None,
        )
        LocalStorage.save_session(session)

        # Update task stats if focus session completed
        if active_task and session_type == SessionType.FOCUS:
            active_task.completedPomodoros += 1
            active_task.totalFocusSeconds += actual_duration
            LocalStorage.update_task(active_task)
