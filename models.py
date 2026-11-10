"""
Zen-Style Pomodoro Clock - Domain Models and Data Structures
Strict type hints, Pydantic dataclasses/models, and SemVer 2.0.0 compliance.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SessionType(str, Enum):
    VISUALIZATION = "visualization"
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    ACTIVE_RECALL = "active_recall"
    DIFFUSE_MODE = "diffuse_mode"


class TimerCycleMode(str, Enum):
    CLASSIC = "classic"
    LEARNING_TRIO = "learning_trio"


class TimerStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"


class ThemeType(str, Enum):
    GEOMETRIC_BALANCE = "geometric-balance"
    ZEN_DARK = "zen-dark"
    OBSIDIAN = "obsidian"
    MINIMAL_LIGHT = "minimal-light"
    AMBER_GLOW = "amber-glow"
    FOREST_MOSS = "forest-moss"
    MIDNIGHT_INDIGO = "midnight-indigo"


class ChimeSound(str, Enum):
    SINGING_BOWL = "singing-bowl"
    ZEN_GONG = "zen-gong"
    SOFT_BELL = "soft-bell"
    CRYSTAL_CHIME = "crystal-chime"
    WOODEN_CLACK = "wooden-clack"
    GENTLE_MARIMBA = "gentle-marimba"
    NONE = "none"


class AmbientSound(str, Enum):
    NONE = "none"
    BROWN_NOISE = "brown-noise"
    GENTLE_RAIN = "gentle-rain"
    CRACKLING_FIREPLACE = "crackling-fireplace"
    FOREST_WIND = "forest-wind"
    SUMMER_NIGHT = "summer-night"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCategory(str, Enum):
    WORK = "Work"
    STUDY = "Study"
    CODING = "Coding"
    READING = "Reading"
    CREATIVE = "Creative"
    PERSONAL = "Personal"
    OTHER = "Other"


class UserProfile(BaseModel):
    uid: str
    email: Optional[str] = ""
    displayName: Optional[str] = "Zen User"
    photoURL: Optional[str] = None
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class RecallFlashcard(BaseModel):
    id: str = Field(default_factory=lambda: f"card_{uuid.uuid4().hex[:8]}")
    userId: Optional[str] = None
    taskId: Optional[str] = None
    question: str
    answer: str
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    reviewedCount: int = 0
    lastReviewedAt: Optional[str] = None
    mastered: bool = False


class TaskItem(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid.uuid4().hex[:8]}")
    userId: Optional[str] = None
    title: str
    description: Optional[str] = ""
    category: TaskCategory = TaskCategory.WORK
    priority: TaskPriority = TaskPriority.MEDIUM
    estimatedPomodoros: int = 2
    completedPomodoros: int = 0
    totalFocusSeconds: int = 0
    completed: bool = False
    createdAt: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completedAt: Optional[str] = None


class PomodoroSession(BaseModel):
    id: str = Field(default_factory=lambda: f"sess_{uuid.uuid4().hex[:8]}")
    userId: Optional[str] = None
    type: SessionType
    status: str = "completed"  # 'completed' | 'cancelled' | 'interrupted'
    plannedDuration: int  # in seconds
    actualDuration: int  # in seconds
    startedAt: str
    endedAt: str
    cycleNumber: int = 1
    taskId: Optional[str] = None
    taskName: Optional[str] = None


class UserSettings(BaseModel):
    userId: Optional[str] = None
    cycleMode: TimerCycleMode = TimerCycleMode.CLASSIC
    focusDuration: int = 1500  # 25 min in seconds
    shortBreakDuration: int = 300  # 5 min in seconds
    longBreakDuration: int = 900  # 15 min in seconds
    sessionsBeforeLongBreak: int = 4

    # 4-Step Learning Cycle (Cognitive Mastery Protocol)
    learningVisualizationDuration: int = 120  # 2 min in seconds
    learningFocusDuration: int = 1200  # 20 min in seconds
    learningRecallDuration: int = 180  # 3 min in seconds
    learningDiffuseDuration: int = 300  # 5 min in seconds
    autoAdvanceLearningCycle: bool = True

    autoStartBreaks: bool = False
    autoStartFocus: bool = False
    focusModeEnabled: bool = False
    keepScreenAwake: bool = True

    soundEnabled: bool = True
    soundVolume: float = 0.6  # 0.0 to 1.0
    chimeSound: ChimeSound = ChimeSound.SINGING_BOWL
    tickSoundEnabled: bool = False

    ambientSound: AmbientSound = AmbientSound.NONE
    ambientVolume: float = 0.5

    theme: ThemeType = ThemeType.GEOMETRIC_BALANCE
    flipAnimation: bool = True
    reducedMotion: bool = False
    showSeconds: bool = True
    showCycleIndicator: bool = True
    dailyGoalSessions: int = 8
