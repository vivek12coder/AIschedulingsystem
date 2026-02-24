from __future__ import annotations

from collections import defaultdict

from scheduler.models import ScheduleEntry, ScheduleInput, TimeSlot

_DEFAULT_HEAVY_KEYWORDS = ("math", "science")
_MAX_WORKLOAD_IMBALANCE = 2


def check_teacher_conflict(entries: list[ScheduleEntry]) -> list[str]:
    violations = []
    by_slot: dict[str, list[ScheduleEntry]] = defaultdict(list)
    for e in entries:
        by_slot[e.time_slot_id].append(e)
    for slot_id, group in by_slot.items():
        seen: dict[str, str] = {}
        for e in group:
            if e.teacher_id in seen:
                violations.append(
                    f"Teacher {e.teacher_id} double-booked in time slot {slot_id}"
                )
            else:
                seen[e.teacher_id] = e.class_id
    return violations


def check_class_conflict(entries: list[ScheduleEntry]) -> list[str]:
    violations = []
    by_slot: dict[str, list[ScheduleEntry]] = defaultdict(list)
    for e in entries:
        by_slot[e.time_slot_id].append(e)
    for slot_id, group in by_slot.items():
        seen: dict[str, str] = {}
        for e in group:
            if e.class_id in seen:
                violations.append(
                    f"Class {e.class_id} has multiple subjects in time slot {slot_id}"
                )
            else:
                seen[e.class_id] = e.subject_id
    return violations


def check_room_conflict(entries: list[ScheduleEntry]) -> list[str]:
    violations = []
    by_slot: dict[str, list[ScheduleEntry]] = defaultdict(list)
    for e in entries:
        by_slot[e.time_slot_id].append(e)
    for slot_id, group in by_slot.items():
        seen: dict[str, str] = {}
        for e in group:
            if e.room_id in seen:
                violations.append(
                    f"Room {e.room_id} double-booked in time slot {slot_id}"
                )
            else:
                seen[e.room_id] = e.class_id
    return violations


def check_room_capacity(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> list[str]:
    rooms = {r.id: r for r in schedule_input.rooms}
    classes = {c.id: c for c in schedule_input.classes}
    violations = []
    for e in entries:
        room = rooms.get(e.room_id)
        cls = classes.get(e.class_id)
        if room and cls and cls.num_students > room.capacity:
            violations.append(
                f"Room {e.room_id} (capacity {room.capacity}) too small for "
                f"class {e.class_id} ({cls.num_students} students)"
            )
    return violations


def check_all_hard_constraints(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> list[str]:
    violations = []
    violations.extend(check_teacher_conflict(entries))
    violations.extend(check_class_conflict(entries))
    violations.extend(check_room_conflict(entries))
    violations.extend(check_room_capacity(entries, schedule_input))
    return violations


def check_teacher_day_off(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> list[str]:
    teachers = {t.id: t for t in schedule_input.teachers}
    time_slots = {ts.id: ts for ts in schedule_input.time_slots}
    violations = []
    for e in entries:
        teacher = teachers.get(e.teacher_id)
        ts = time_slots.get(e.time_slot_id)
        if not teacher or not ts or not teacher.preferred_day_off:
            continue
        if ts.day == teacher.preferred_day_off:
            violations.append(
                f"Teacher {e.teacher_id} scheduled on preferred day off ({ts.day})"
            )
    return violations


def check_morning_preference(
    entries: list[ScheduleEntry],
    schedule_input: ScheduleInput,
    heavy_subjects: list[str] | None = None,
) -> list[str]:
    subjects = {s.id: s for s in schedule_input.subjects}
    time_slots = {ts.id: ts for ts in schedule_input.time_slots}

    if heavy_subjects is None:
        heavy_subjects = [
            s.id
            for s in schedule_input.subjects
            if any(kw in s.name.lower() for kw in _DEFAULT_HEAVY_KEYWORDS)
        ]

    violations = []
    for e in entries:
        if e.subject_id in heavy_subjects:
            ts = time_slots.get(e.time_slot_id)
            if ts and ts.period > 3:
                subj = subjects.get(e.subject_id)
                name = subj.name if subj else e.subject_id
                violations.append(
                    f"Heavy subject {name} scheduled in period {ts.period} "
                    f"(after morning) on {ts.day}"
                )
    return violations


def check_workload_balance(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> list[str]:
    time_slots = {ts.id: ts for ts in schedule_input.time_slots}
    class_day_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    for e in entries:
        ts = time_slots.get(e.time_slot_id)
        if ts:
            class_day_counts[e.class_id][ts.day] += 1

    violations = []
    for class_id, day_counts in class_day_counts.items():
        counts = list(day_counts.values())
        if counts:
            max_daily = max(counts)
            min_daily = min(counts)
            if max_daily - min_daily > _MAX_WORKLOAD_IMBALANCE:
                violations.append(
                    f"Class {class_id} has unbalanced workload: "
                    f"max {max_daily} - min {min_daily} = {max_daily - min_daily} (>2)"
                )
    return violations


def check_all_soft_constraints(
    entries: list[ScheduleEntry], schedule_input: ScheduleInput
) -> list[str]:
    violations = []
    violations.extend(check_teacher_day_off(entries, schedule_input))
    violations.extend(check_morning_preference(entries, schedule_input))
    violations.extend(check_workload_balance(entries, schedule_input))
    return violations
