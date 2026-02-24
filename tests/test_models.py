import pytest
from pydantic import ValidationError
from scheduler.models import (
    Subject, Teacher, Room, SchoolClass, TimeSlot,
    ScheduleEntry, Schedule, ScheduleInput,
)


class TestSubject:
    def test_valid_subject(self):
        s = Subject(id="math", name="Mathematics", hours_per_week=3)
        assert s.id == "math"
        assert s.name == "Mathematics"
        assert s.hours_per_week == 3
        assert s.subject_type == "lecture"

    def test_invalid_hours_per_week(self):
        with pytest.raises(ValidationError):
            Subject(id="math", name="Mathematics", hours_per_week=0)


class TestTeacher:
    def test_valid_teacher(self):
        t = Teacher(id="t1", name="Mr. Smith", subjects=["math", "sci"])
        assert t.id == "t1"
        assert t.name == "Mr. Smith"
        assert t.subjects == ["math", "sci"]
        assert t.preferred_day_off is None


class TestRoom:
    def test_invalid_capacity(self):
        with pytest.raises(ValidationError):
            Room(id="r1", name="Room 101", capacity=0)


class TestSchoolClass:
    def test_valid_class(self):
        c = SchoolClass(id="c1", name="Grade 10-A", num_students=30, required_subjects=["math"])
        assert c.id == "c1"
        assert c.num_students == 30


class TestTimeSlot:
    def test_valid_time_slot(self):
        ts = TimeSlot(id="mon_p1", day="Monday", period=1, start_time="08:00", end_time="09:00")
        assert ts.day == "Monday"
        assert ts.period == 1


class TestScheduleEntry:
    def test_valid_entry(self):
        e = ScheduleEntry(
            time_slot_id="mon_p1", teacher_id="t1",
            subject_id="math", class_id="c1", room_id="r1",
        )
        assert e.time_slot_id == "mon_p1"
        assert e.teacher_id == "t1"


class TestSchedule:
    def test_defaults(self):
        s = Schedule(entries=[])
        assert s.score == 0.0
        assert s.violations == []
        assert s.entries == []


class TestScheduleInput:
    def test_creation(self, sample_schedule_input):
        si = sample_schedule_input
        assert len(si.subjects) == 4
        assert len(si.teachers) == 3
        assert len(si.rooms) == 3
        assert len(si.classes) == 2
        assert len(si.time_slots) == 30
