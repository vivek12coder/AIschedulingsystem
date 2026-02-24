from __future__ import annotations

from collections import defaultdict

from scheduler.constraints import check_all_hard_constraints, check_all_soft_constraints
from scheduler.models import Schedule, ScheduleEntry, ScheduleInput
from scheduler.scoring import score_schedule


def detect_conflicts(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> dict:
    hard = check_all_hard_constraints(entries, schedule_input)
    soft = check_all_soft_constraints(entries, schedule_input)
    return {
        "hard_violations": hard,
        "soft_violations": soft,
        "is_valid": len(hard) == 0,
    }


def find_conflicting_entries(entries: list[ScheduleEntry]) -> list[tuple[int, int]]:
    conflicts: list[tuple[int, int]] = []
    for i in range(len(entries)):
        for j in range(i + 1, len(entries)):
            a, b = entries[i], entries[j]
            if a.time_slot_id != b.time_slot_id:
                continue
            if (
                a.teacher_id == b.teacher_id
                or a.class_id == b.class_id
                or a.room_id == b.room_id
            ):
                conflicts.append((i, j))
    return conflicts


def auto_fix_conflicts(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> list[ScheduleEntry]:
    result = list(entries)
    all_slot_ids = [ts.id for ts in schedule_input.time_slots]

    teacher_booked: dict[str, set[str]] = defaultdict(set)
    class_booked: dict[str, set[str]] = defaultdict(set)
    room_booked: dict[str, set[str]] = defaultdict(set)

    for e in result:
        teacher_booked[e.teacher_id].add(e.time_slot_id)
        class_booked[e.class_id].add(e.time_slot_id)
        room_booked[e.room_id].add(e.time_slot_id)

    conflicts = find_conflicting_entries(result)

    for i, j in conflicts:
        entry = result[j]
        for slot_id in all_slot_ids:
            if slot_id == entry.time_slot_id:
                continue
            if slot_id in teacher_booked[entry.teacher_id]:
                continue
            if slot_id in class_booked[entry.class_id]:
                continue
            if slot_id in room_booked[entry.room_id]:
                continue

            teacher_booked[entry.teacher_id].discard(entry.time_slot_id)
            class_booked[entry.class_id].discard(entry.time_slot_id)
            room_booked[entry.room_id].discard(entry.time_slot_id)

            result[j] = ScheduleEntry(
                time_slot_id=slot_id,
                teacher_id=entry.teacher_id,
                subject_id=entry.subject_id,
                class_id=entry.class_id,
                room_id=entry.room_id,
            )

            teacher_booked[entry.teacher_id].add(slot_id)
            class_booked[entry.class_id].add(slot_id)
            room_booked[entry.room_id].add(slot_id)
            break

    return result


def resolve_and_score(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> Schedule:
    fixed = auto_fix_conflicts(entries, schedule_input)
    final_score, violations = score_schedule(fixed, schedule_input)
    return Schedule(entries=fixed, score=final_score, violations=violations)
