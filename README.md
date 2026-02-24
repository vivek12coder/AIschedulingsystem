# AI Timetable Scheduling System

## Overview

The AI Timetable Scheduling System is an intelligent scheduling engine that automatically generates conflict-free timetables for educational institutions. It combines a greedy Constraint Satisfaction Problem (CSP) solver with evolutionary optimization (DEAP Genetic Algorithm) to produce optimized schedules that satisfy hard constraints (no room, teacher, or class conflicts) and maximize soft constraints (preferred day off, morning scheduling for heavy subjects, balanced workloads).

## Development Phases

### Phase 1 — Data Modeling
Define core entities: subjects, teachers, rooms, time slots, and classes. Build Pydantic v2 models for validation and serialization.

### Phase 2 — Constraint Engine
Implement hard and soft constraint checking functions in Python. Hard constraints prevent double-booking of rooms, teachers, and classes. Soft constraints handle preferences like teacher day-off, morning scheduling for heavy subjects, and balanced weekly workload.

### Phase 3 — AI Solver (CSP + Genetic Algorithm)
Hybrid approach: a greedy CSP solver generates a valid base schedule by assigning subjects to time slots while respecting hard constraints. A DEAP Genetic Algorithm then optimizes the schedule by swapping time slot assignments to improve soft constraint satisfaction.

### Phase 4 — Conflict Detection & Resolution
Detect remaining conflicts in the generated schedule, find specific conflicting entries, and auto-fix them by reassigning to available time slots. Re-score the schedule after resolution.

### Phase 5 — Scoring & Evaluation
Score generated timetables using a penalty-based system: hard constraint violations receive heavy penalties (100 points each), soft constraint violations receive lighter penalties (10 points each), starting from a base score of 1000.

### Phase 6 — REST API
Expose the scheduling engine through a FastAPI REST API, allowing clients to submit scheduling requests, validate schedules, and resolve conflicts.

## Tech Stack

| Component              | Technology            |
|------------------------|-----------------------|
| Language               | Python 3.10+          |
| CSP Solver             | Custom greedy solver  |
| Evolutionary Algorithm | DEAP                  |
| API Framework          | FastAPI + Uvicorn     |
| Data Validation        | Pydantic v2           |
| Testing                | pytest + httpx        |

## Installation

```bash
git clone <repository-url>
cd AIschedulingsystem
pip install -r requirements.txt
```

## Running the API

```bash
uvicorn scheduler.api:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs are at `http://127.0.0.1:8000/docs`.

## Running Tests

```bash
pytest
```

## System Flow

```
┌──────────────┐
│  Input Data  │  Subjects, Teachers, Rooms, Classes, Time Slots
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validation  │  Pydantic models validate and parse input
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  CSP Solver      │  Greedy algorithm generates valid base schedule
└──────┬───────────┘
       │
       ▼
┌────────────────────┐
│  Genetic Algorithm │  DEAP optimizes soft constraint satisfaction
└──────┬─────────────┘
       │
       ▼
┌────────────────────┐
│ Conflict Resolver  │  Detects and auto-fixes remaining conflicts
└──────┬─────────────┘
       │
       ▼
┌──────────────┐
│   Scoring    │  Penalty-based timetable quality scoring
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   REST API   │  FastAPI returns optimized timetable
└──────────────┘
```

## Project Structure

```
scheduler/
  __init__.py
  models.py             # Pydantic data models
  constraints.py        # Hard & soft constraint checking
  solver.py             # Greedy CSP + DEAP Genetic Algorithm
  conflict_resolver.py  # Conflict detection and auto-fix
  scoring.py            # Penalty-based schedule scoring
  api.py                # FastAPI endpoints
tests/
  __init__.py
  conftest.py
  test_models.py
  test_constraints.py
  test_solver.py
  test_conflict_resolver.py
requirements.txt
README.md
.gitignore
```
