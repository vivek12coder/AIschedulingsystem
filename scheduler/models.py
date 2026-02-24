from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Subject(BaseModel):
    id: str
    name: str
    hours_per_week: int = Field(ge=1)
    subject_type: Literal["lecture", "lab"] = "lecture"


class Teacher(BaseModel):
    id: str
    name: str
    subjects: list[str]
    available_slots: list[str] = []
    preferred_day_off: str | None = None


class Room(BaseModel):
    id: str
    name: str
    capacity: int = Field(ge=1)
    room_type: Literal["classroom", "lab"] = "classroom"


class SchoolClass(BaseModel):
    id: str
    name: str
    num_students: int = Field(ge=1)
    required_subjects: list[str]


class TimeSlot(BaseModel):
    id: str
    day: str
    period: int = Field(ge=1)
    start_time: str
    end_time: str


class ScheduleEntry(BaseModel):
    time_slot_id: str
    teacher_id: str
    subject_id: str
    class_id: str
    room_id: str


class Schedule(BaseModel):
    entries: list[ScheduleEntry]
    score: float = 0.0
    violations: list[str] = []


class ScheduleInput(BaseModel):
    subjects: list[Subject]
    teachers: list[Teacher]
    rooms: list[Room]
    classes: list[SchoolClass]
    time_slots: list[TimeSlot]
