# AI Timetable Scheduling System

## Overview

The AI Timetable Scheduling System is an intelligent scheduling engine that automatically generates conflict-free timetables for educational institutions. It combines constraint programming (Google OR-Tools) with evolutionary algorithms (DEAP) to produce optimized schedules that satisfy hard constraints (no room or instructor conflicts) and maximize soft constraints (preferred time slots, balanced workloads).

## Development Phases

### Phase 1 — Data Modeling
Define core entities: courses, instructors, rooms, time slots, and sections. Build Pydantic models for validation and serialization.

### Phase 2 — Constraint Engine
Implement hard and soft constraints using Google OR-Tools CP-SAT solver. Hard constraints prevent double-booking of rooms and instructors. Soft constraints handle preferences like preferred time slots and room capacities.

### Phase 3 — Solver Integration
Wire the constraint engine into a scheduling solver that takes input data, builds the constraint model, solves it, and returns a complete timetable.

### Phase 4 — Conflict Resolution
Use DEAP genetic algorithms to iteratively improve schedules, resolve edge-case conflicts, and optimize the overall fitness of the timetable.

### Phase 5 — Scoring & Evaluation
Score generated timetables against quality metrics: constraint satisfaction rate, instructor preference fulfillment, room utilization, and schedule compactness.

### Phase 6 — REST API
Expose the scheduling engine through a FastAPI REST API, allowing clients to submit scheduling requests and retrieve optimized timetables.

## Tech Stack

| Component              | Technology            |
|------------------------|-----------------------|
| Language               | Python 3.10+          |
| Constraint Solving     | Google OR-Tools       |
| Evolutionary Algorithm | DEAP                  |
| API Framework          | FastAPI + Uvicorn     |
| Data Validation        | Pydantic              |
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
│  Input Data  │  Courses, Instructors, Rooms, Time Slots
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validation  │  Pydantic models validate and parse input
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Constraint Model │  OR-Tools CP-SAT builds hard & soft constraints
└──────┬───────────┘
       │
       ▼
┌──────────────┐
│    Solver    │  CP-SAT solver finds feasible timetable
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│ Conflict Resolver  │  DEAP genetic algorithm refines solution
└──────┬─────────────┘
       │
       ▼
┌──────────────┐
│   Scoring    │  Evaluate timetable quality metrics
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
  constraints.py        # Hard & soft constraint definitions
  solver.py             # OR-Tools CP-SAT solver integration
  conflict_resolver.py  # DEAP-based conflict resolution
  scoring.py            # Timetable quality scoring
  api.py                # FastAPI endpoints
tests/
  __init__.py
  test_models.py
  test_constraints.py
  test_solver.py
  test_conflict_resolver.py
requirements.txt
README.md
.gitignore
```
