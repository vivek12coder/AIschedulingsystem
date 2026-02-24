import pytest
from scheduler.models import (
    Subject, Teacher, Room, SchoolClass, TimeSlot,
    ScheduleEntry, Schedule, ScheduleInput,
)


@pytest.fixture
def sample_subjects():
    return [
        Subject(id="math", name="Mathematics", hours_per_week=3),
        Subject(id="sci", name="Science", hours_per_week=2),
        Subject(id="eng", name="English", hours_per_week=2, subject_type="lecture"),
        Subject(id="cs", name="Computer Science", hours_per_week=1, subject_type="lab"),
    ]


@pytest.fixture
def sample_teachers():
    return [
        Teacher(id="t1", name="Mr. Smith", subjects=["math", "sci"]),
        Teacher(id="t2", name="Ms. Johnson", subjects=["eng"]),
        Teacher(id="t3", name="Dr. Lee", subjects=["cs", "math"], preferred_day_off="Friday"),
    ]


@pytest.fixture
def sample_rooms():
    return [
        Room(id="r1", name="Room 101", capacity=40),
        Room(id="r2", name="Room 102", capacity=35),
        Room(id="r3", name="Lab 1", capacity=30, room_type="lab"),
    ]


@pytest.fixture
def sample_classes():
    return [
        SchoolClass(id="c1", name="Grade 10-A", num_students=30, required_subjects=["math", "eng"]),
        SchoolClass(id="c2", name="Grade 10-B", num_students=28, required_subjects=["math", "sci"]),
    ]


@pytest.fixture
def sample_time_slots():
    slots = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    for day in days:
        for period in range(1, 7):
            hour = 7 + period
            slot_id = f"{day.lower()[:3]}_p{period}"
            slots.append(TimeSlot(
                id=slot_id,
                day=day,
                period=period,
                start_time=f"{hour:02d}:00",
                end_time=f"{hour + 1:02d}:00",
            ))
    return slots


@pytest.fixture
def sample_schedule_input(sample_subjects, sample_teachers, sample_rooms, sample_classes, sample_time_slots):
    return ScheduleInput(
        subjects=sample_subjects,
        teachers=sample_teachers,
        rooms=sample_rooms,
        classes=sample_classes,
        time_slots=sample_time_slots,
    )
