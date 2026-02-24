from scheduler.models import ScheduleEntry
from scheduler.constraints import (
    check_teacher_conflict,
    check_class_conflict,
    check_room_conflict,
    check_room_capacity,
    check_teacher_day_off,
    check_morning_preference,
    check_workload_balance,
    check_all_hard_constraints,
    check_all_soft_constraints,
)


def _entry(slot="mon_p1", teacher="t1", subject="math", cls="c1", room="r1"):
    return ScheduleEntry(
        time_slot_id=slot, teacher_id=teacher,
        subject_id=subject, class_id=cls, room_id=room,
    )


class TestTeacherConflict:
    def test_no_teacher_conflict(self):
        entries = [_entry(slot="mon_p1", teacher="t1"), _entry(slot="mon_p2", teacher="t1")]
        assert check_teacher_conflict(entries) == []

    def test_teacher_conflict_detected(self):
        entries = [
            _entry(slot="mon_p1", teacher="t1", cls="c1"),
            _entry(slot="mon_p1", teacher="t1", cls="c2"),
        ]
        violations = check_teacher_conflict(entries)
        assert len(violations) == 1
        assert "t1" in violations[0]


class TestClassConflict:
    def test_no_class_conflict(self):
        entries = [_entry(slot="mon_p1", cls="c1"), _entry(slot="mon_p2", cls="c1")]
        assert check_class_conflict(entries) == []

    def test_class_conflict_detected(self):
        entries = [
            _entry(slot="mon_p1", cls="c1", subject="math"),
            _entry(slot="mon_p1", cls="c1", subject="eng", teacher="t2", room="r2"),
        ]
        violations = check_class_conflict(entries)
        assert len(violations) == 1
        assert "c1" in violations[0]


class TestRoomConflict:
    def test_no_room_conflict(self):
        entries = [_entry(slot="mon_p1", room="r1"), _entry(slot="mon_p2", room="r1")]
        assert check_room_conflict(entries) == []

    def test_room_conflict_detected(self):
        entries = [
            _entry(slot="mon_p1", room="r1", cls="c1", teacher="t1"),
            _entry(slot="mon_p1", room="r1", cls="c2", teacher="t2"),
        ]
        violations = check_room_conflict(entries)
        assert len(violations) == 1
        assert "r1" in violations[0]


class TestRoomCapacity:
    def test_room_capacity_ok(self, sample_schedule_input):
        entries = [_entry(room="r1", cls="c1")]
        assert check_room_capacity(entries, sample_schedule_input) == []

    def test_room_capacity_violation(self, sample_schedule_input):
        from scheduler.models import Room
        si = sample_schedule_input.model_copy()
        si.rooms = list(si.rooms) + [Room(id="r_small", name="Small Room", capacity=10)]
        entries = [_entry(room="r_small", cls="c1")]
        violations = check_room_capacity(entries, si)
        assert len(violations) == 1


class TestTeacherDayOff:
    def test_teacher_day_off_respected(self, sample_schedule_input):
        entries = [_entry(slot="mon_p1", teacher="t3")]
        assert check_teacher_day_off(entries, sample_schedule_input) == []

    def test_teacher_day_off_violated(self, sample_schedule_input):
        entries = [_entry(slot="fri_p1", teacher="t3")]
        violations = check_teacher_day_off(entries, sample_schedule_input)
        assert len(violations) == 1
        assert "t3" in violations[0]


class TestMorningPreference:
    def test_morning_preference_ok(self, sample_schedule_input):
        entries = [_entry(slot="mon_p2", subject="math")]
        assert check_morning_preference(entries, sample_schedule_input) == []

    def test_morning_preference_violated(self, sample_schedule_input):
        entries = [_entry(slot="mon_p4", subject="math")]
        violations = check_morning_preference(entries, sample_schedule_input)
        assert len(violations) == 1
        assert "Mathematics" in violations[0]


class TestWorkloadBalance:
    def test_workload_balance_ok(self, sample_schedule_input):
        entries = [
            _entry(slot="mon_p1", cls="c1"),
            _entry(slot="tue_p1", cls="c1", teacher="t2", room="r2"),
        ]
        assert check_workload_balance(entries, sample_schedule_input) == []


class TestAllConstraints:
    def test_all_hard_constraints(self, sample_schedule_input):
        entries = [_entry(slot="mon_p1"), _entry(slot="mon_p2", teacher="t2", room="r2")]
        violations = check_all_hard_constraints(entries, sample_schedule_input)
        assert violations == []

    def test_all_soft_constraints(self, sample_schedule_input):
        entries = [_entry(slot="mon_p1", teacher="t1")]
        violations = check_all_soft_constraints(entries, sample_schedule_input)
        assert isinstance(violations, list)
