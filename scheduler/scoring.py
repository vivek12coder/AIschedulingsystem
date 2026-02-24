"""Schedule scoring based on constraint violations."""

from scheduler.models import ScheduleEntry, ScheduleInput
from scheduler.constraints import check_all_hard_constraints, check_all_soft_constraints

HARD_CONSTRAINT_PENALTY = 100.0
SOFT_CONSTRAINT_PENALTY = 10.0
BASE_SCORE = 1000.0


def score_schedule(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> tuple[float, list[str]]:
    """Score a schedule by penalizing constraint violations."""
    score = BASE_SCORE

    hard_violations = check_all_hard_constraints(entries, schedule_input)
    score -= HARD_CONSTRAINT_PENALTY * len(hard_violations)

    soft_violations = check_all_soft_constraints(entries, schedule_input)
    score -= SOFT_CONSTRAINT_PENALTY * len(soft_violations)

    all_violations = hard_violations + soft_violations
    score = max(0.0, score)

    return score, all_violations
