# Atlantis - Coding challenge from OctoML

## Main idea
When the gatekeeper receives a new pearl, create a plan for processing the pearl based on the workload of each worker. Then at each step, each worker will choose to process pearls based on which mode they're in. `pq` prioritizes moving pearls and pearls that need less work (number of turns to process). Better to plan the work for a pearl all at once because the coordinator has all the information as opposed to making local decisions about each pearl at each worker. 

## How to run the code
`usage: process_pearls.py [-h] [mode]`
e.g.
```bash
./atlantis.ubuntu-latest single-run python process_pearls.py
./atlantis.ubuntu-latest average-run python process_pearls.py
```

### Modes:
- PriorityQueue: pq (default) (averages around 15) 
- Round-Robin: rr (averages around 9) 
- First-In-First-Out: fifo (averages around 8)

### Example of running with a mode
```bash
./atlantis.ubuntu-latest single-run python process_pearls.py rr
./atlantis.ubuntu-latest average-run python process_pearls.py rr
```

## How to run tests
```bash
python -m unittest -v
```
from the root directory of the project.

## Folder structure
```
atlantis/
│
├── atlantis/               - source code
│   ├── __init__.py
│   ├── atlantis.py         - coordinator and planner for pearls 
│   ├── pearl.py            - Pearl object, holds plan information
│   └── worker.py           - Worker object, abstracts handling of pearls
|
├── tests/
|   ├── __init__.py
|   ├── test_atlantis.py
|   ├── test_pearl.py
|   └── test_worker.py
|
├── .gitignore
├── atlantis.ubuntu-latest  - run script
├── process_pearls.py       - entry point for running code
└── README.md

```

## Time 
- `atlantis/pearl.py` - 10 min
- `atlantis/worker.py` - 30 min
- `atlantis/atlantis.py` - 2 hours
- `process_pearls.py` - 20 min
- `tests/*` - 1 hour and 30 minutes
- `comments` - 30 minutes 

Total time: approx. 5 hours

## Optional improvements
- Add debug/logging information (previously debugged with prints to stderr)
  - Log run information to a file
  - Add info on action per turn by each worker
  - Add planning information 
  - Add messages for when pearls are resolved 
- Tune the cost functions for:
  - Plan to dissolve outer layers
  - Return path of clean pearl
- Tune constants:
  - Origin penalty: Penalty for Passing across/to the origin
  - Nom penalty: Penalty for choosing to Nom instead of Pass
- Create better planning
- Add more rigorous testing, i.e. more complicated paths 
- Structure classes/fields better
  - e.g. using getters instead of directly accessing the fields, especially immutable ones
- Better code reuse
  - I implemented Dijkstra's twice with slightly different cost functions