from scheduler.models import ScheduleEntry, Schedule
from scheduler.conflict_resolver import (
    detect_conflicts,
    find_conflicting_entries,
    auto_fix_conflicts,
    resolve_and_score,
)
from scheduler.solver import generate_base_schedule


def _entry(slot="mon_p1", teacher="t1", subject="math", cls="c1", room="r1"):
    return ScheduleEntry(
        time_slot_id=slot, teacher_id=teacher,
        subject_id=subject, class_id=cls, room_id=room,
    )


class TestDetectConflicts:
    def test_detect_conflicts_valid(self, sample_schedule_input):
        entries = generate_base_schedule(sample_schedule_input)
        result = detect_conflicts(entries, sample_schedule_input)
        assert result["is_valid"] is True
        assert result["hard_violations"] == []

    def test_detect_conflicts_with_hard(self, sample_schedule_input):
        entries = [
            _entry(slot="mon_p1", teacher="t1", cls="c1"),
            _entry(slot="mon_p1", teacher="t1", cls="c2", room="r2"),
        ]
        result = detect_conflicts(entries, sample_schedule_input)
        assert result["is_valid"] is False
        assert len(result["hard_violations"]) > 0


class TestFindConflictingEntries:
    def test_find_conflicting_entries(self):
        entries = [
            _entry(slot="mon_p1", teacher="t1", cls="c1", room="r1"),
            _entry(slot="mon_p1", teacher="t1", cls="c2", room="r2"),
        ]
        conflicts = find_conflicting_entries(entries)
        assert len(conflicts) == 1
        assert conflicts[0] == (0, 1)


class TestAutoFix:
    def test_auto_fix_resolves_conflict(self, sample_schedule_input):
        entries = [
            _entry(slot="mon_p1", teacher="t1", cls="c1", room="r1"),
            _entry(slot="mon_p1", teacher="t1", cls="c2", room="r2"),
        ]
        fixed = auto_fix_conflicts(entries, sample_schedule_input)
        result = detect_conflicts(fixed, sample_schedule_input)
        assert result["is_valid"] is True


class TestResolveAndScore:
    def test_resolve_and_score(self, sample_schedule_input):
        entries = generate_base_schedule(sample_schedule_input)
        schedule = resolve_and_score(entries, sample_schedule_input)
        assert isinstance(schedule, Schedule)
        assert schedule.score > 0
