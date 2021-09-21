import sys
import json
from atlantis import atlantis 
import argparse

# Entrypoint for processing pearls
parser = argparse.ArgumentParser(description="Entrypoint for processing pearls", formatter_class=argparse.RawTextHelpFormatter)
mode_help_text = "mode for worker, either PriorityQueue (pq), Round-Robin (rr), or First-In-First-Out (fifo) (default=\"pq\")\n\
  pq - processes pearls in priority queue fashion, priority based on type of action and work remaining\n\
  rr - processes pearls in round-robin fashion\n\
fifo - processes pearls in first in, first out fashion"
parser.add_argument("mode", nargs='?', default="pq", help=mode_help_text)
args = parser.parse_args()

# Set mode, default is pq
mode = "pq"
if args.mode == "rr":
    mode = "rr"
elif args.mode == "fifo":
    mode = "fifo"

atlan = atlantis.Atlantis(mode=mode)

for line in sys.stdin:
    state = json.loads(line)
    actions = atlan.process(state)
    print(actions, flush=True)
