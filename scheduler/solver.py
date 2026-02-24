import random
from collections import defaultdict

from deap import base, creator, tools

from scheduler.models import ScheduleEntry, ScheduleInput, Schedule
from scheduler.scoring import score_schedule


def generate_base_schedule(
    schedule_input: ScheduleInput, max_attempts: int = 1000
) -> list[ScheduleEntry]:
    entries: list[ScheduleEntry] = []
    subjects = {s.id: s for s in schedule_input.subjects}
    teachers_by_subject: dict[str, list[str]] = defaultdict(list)
    for t in schedule_input.teachers:
        for s in t.subjects:
            teachers_by_subject[s].append(t.id)
    rooms = schedule_input.rooms
    slots = schedule_input.time_slots

    teacher_booked: set[tuple[str, str]] = set()
    class_booked: set[tuple[str, str]] = set()
    room_booked: set[tuple[str, str]] = set()

    for cls in schedule_input.classes:
        for subj_id in cls.required_subjects:
            subj = subjects.get(subj_id)
            if not subj:
                continue
            hours_needed = subj.hours_per_week
            assigned = 0

            shuffled_slots = list(slots)
            random.shuffle(shuffled_slots)

            for slot in shuffled_slots:
                if assigned >= hours_needed:
                    break
                if (cls.id, slot.id) in class_booked:
                    continue

                available_teachers = [
                    tid
                    for tid in teachers_by_subject.get(subj_id, [])
                    if (tid, slot.id) not in teacher_booked
                ]
                if not available_teachers:
                    continue

                suitable_rooms = [
                    r
                    for r in rooms
                    if r.capacity >= cls.num_students
                    and r.room_type == subj.subject_type
                    and (r.id, slot.id) not in room_booked
                ]
                if not suitable_rooms:
                    suitable_rooms = [
                        r
                        for r in rooms
                        if r.capacity >= cls.num_students
                        and (r.id, slot.id) not in room_booked
                    ]
                if not suitable_rooms:
                    continue

                teacher_id = random.choice(available_teachers)
                room = random.choice(suitable_rooms)

                entry = ScheduleEntry(
                    time_slot_id=slot.id,
                    teacher_id=teacher_id,
                    subject_id=subj_id,
                    class_id=cls.id,
                    room_id=room.id,
                )
                entries.append(entry)
                teacher_booked.add((teacher_id, slot.id))
                class_booked.add((cls.id, slot.id))
                room_booked.add((room.id, slot.id))
                assigned += 1

    return entries


def optimize_schedule(
    entries: list[ScheduleEntry],
    schedule_input: ScheduleInput,
    generations: int = 50,
    population_size: int = 30,
) -> list[ScheduleEntry]:
    if not entries:
        return entries

    n = len(entries)

    if not hasattr(creator, "FitnessMax"):
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    if not hasattr(creator, "Individual"):
        creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()

    def create_individual():
        return creator.Individual([e.time_slot_id for e in entries])

    def mutate_individual(individual):
        if len(individual) < 2:
            return (individual,)
        i, j = random.sample(range(len(individual)), 2)
        individual[i], individual[j] = individual[j], individual[i]
        return (individual,)

    def evaluate(individual):
        new_entries = [
            ScheduleEntry(
                time_slot_id=individual[idx],
                teacher_id=e.teacher_id,
                subject_id=e.subject_id,
                class_id=e.class_id,
                room_id=e.room_id,
            )
            for idx, e in enumerate(entries)
        ]
        sc, _ = score_schedule(new_entries, schedule_input)
        return (sc,)

    toolbox.register("individual", create_individual)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxUniform, indpb=0.3)
    toolbox.register("mutate", mutate_individual)
    toolbox.register("select", tools.selTournament, tournsize=3)

    pop = toolbox.population(n=population_size)

    for ind in pop:
        ind.fitness.values = toolbox.evaluate(ind)

    for _ in range(generations):
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for i in range(0, len(offspring) - 1, 2):
            if random.random() < 0.7:
                toolbox.mate(offspring[i], offspring[i + 1])
                del offspring[i].fitness.values
                del offspring[i + 1].fitness.values

        for i in range(len(offspring)):
            if random.random() < 0.2:
                toolbox.mutate(offspring[i])
                del offspring[i].fitness.values

        for ind in offspring:
            if not ind.fitness.valid:
                ind.fitness.values = toolbox.evaluate(ind)

        pop[:] = offspring

    best = tools.selBest(pop, 1)[0]

    result = [
        ScheduleEntry(
            time_slot_id=best[idx],
            teacher_id=e.teacher_id,
            subject_id=e.subject_id,
            class_id=e.class_id,
            room_id=e.room_id,
        )
        for idx, e in enumerate(entries)
    ]

    return result


def generate_schedule(
    schedule_input: ScheduleInput,
    optimize: bool = True,
    generations: int = 50,
    population_size: int = 30,
) -> Schedule:
    entries = generate_base_schedule(schedule_input)

    if optimize and entries:
        entries = optimize_schedule(entries, schedule_input, generations, population_size)

    score, violations = score_schedule(entries, schedule_input)
    return Schedule(entries=entries, score=score, violations=violations)
