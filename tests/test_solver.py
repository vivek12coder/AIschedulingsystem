from scheduler.models import ScheduleEntry, ScheduleInput, Schedule
from scheduler.solver import generate_base_schedule, generate_schedule
from scheduler.constraints import check_all_hard_constraints


class TestGenerateBaseSchedule:
    def test_generate_base_schedule(self, sample_schedule_input):
        entries = generate_base_schedule(sample_schedule_input)
        assert len(entries) > 0
        for e in entries:
            assert isinstance(e, ScheduleEntry)

    def test_base_schedule_no_hard_violations(self, sample_schedule_input):
        entries = generate_base_schedule(sample_schedule_input)
        violations = check_all_hard_constraints(entries, sample_schedule_input)
        assert len(violations) == 0


class TestGenerateSchedule:
    def test_generate_schedule_with_optimization(self, sample_schedule_input):
        schedule = generate_schedule(
            sample_schedule_input, optimize=True, generations=5, population_size=5,
        )
        assert isinstance(schedule, Schedule)
        assert len(schedule.entries) > 0

    def test_generate_schedule_without_optimization(self, sample_schedule_input):
        schedule = generate_schedule(sample_schedule_input, optimize=False)
        assert isinstance(schedule, Schedule)
        assert len(schedule.entries) > 0

    def test_generate_schedule_returns_score(self, sample_schedule_input):
        schedule = generate_schedule(
            sample_schedule_input, optimize=False,
        )
        assert schedule.score > 0

    def test_empty_input(self):
        empty_input = ScheduleInput(
            subjects=[], teachers=[], rooms=[], classes=[], time_slots=[],
        )
        schedule = generate_schedule(empty_input, optimize=False)
        assert schedule.entries == []
