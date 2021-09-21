from collections import deque
import heapq

class Worker:
    """Worker object representing Nautiloids."""

    def __init__(self, wid, mode="pq"):
        """Constructor for Worker.

        Keyword arguments:
        wid  -- Worker id
        mode -- Order of how worker will process the pearls (default "pq")
                - "pq" for priority queue, see worker for priority computation
                - "fifo" for first-in-first-out
                - "rr"" for round-robin
        """
        
        self.wid = wid
        self.mode = mode if mode in ("pq", "fifo", "rr") else "pq"
        if mode == "pq":
            self.pearls = []
        else:
            self.pearls = deque()
        self.seen = set()

        # makes noms more costly to prioritize moving
        self.nom_penalty = 20 

    def compute_cost(self, pearl):
        """Compute the cost of processing the pearl based on the next action.

        Keyword argument:
        pearl -- The pearl we're computing the cost for

        Returns:
        cost -- Cost of processing pearl
                cost = Work left over for the 
                     + Nom penalty if next action is Nom
                     + Number of layers remaining if next action is Pass
        """

        cost = 0
        times, move = pearl.peek()

        # finished pearls only need to be moved and should be given priority
        if not pearl.finished:
            # base cost is number of turns to free pearl
            cost = pearl.work
            if "Nom" in move:
                cost += self.nom_penalty
            elif "Pass" in move: 
                cost += pearl.layers
        return cost

    def resolve(self, state, pearl_map):
        """Updates the worker if the pearl is incoming.
        
        Keyword arguments:
        state     -- Current state of the worker, i.e. the Desk
        pearl_map -- pearl id to Pearl object map used to access
                     pearl processing plan
        """

        for pearl in state:
            if pearl["id"] in self.seen:
                continue
            self.seen.add(pearl["id"])
            p = pearl_map[pearl["id"]]
            if self.mode == "rr" or self.mode == "fifo":
                self.pearls.append(p)
            else:
                cost = self.compute_cost(p)
                heapq.heappush(self.pearls, (cost, p.id))

    def process(self, state, pearl_map):
        """Resolves new state and redirects processing based on mode.

        Keyword arguments:
        state     -- State of worker
        pearl_map -- Pearl planning information

        Returns:
        ret -- Action for the current worker
        """

        self.resolve(state, pearl_map)
        if not self.pearls:
            return None
        ret = None
        if self.mode == "rr":
            ret = self.process_rr()
        elif self.mode == "fifo":
            ret = self.process_fifo()
        elif self.mode == "pq":
            ret = self.process_pq(pearl_map)
        return ret

    def process_rr(self):
        """Processes pearls in Round-Robin fashion."""

        if self.pearls:
            pearl = self.pearls.popleft()
            action = pearl.process()
            
            # If pearl is finished, we don't need to keep track of it anymore
            if pearl.finished: 
                self.seen.remove(pearl.id)
            else:
                # We only need to keep the pearl if it's not a Pass
                if "Pass" not in action:
                    self.pearls.append(pearl)
                else:
                    self.seen.remove(pearl.id)
            return action
        else:
            return None

    def process_fifo(self):
        """Processes pearls in FIFO fashion."""

        if self.pearls:
            pearl = self.pearls[0]
            action = pearl.process()

            # We are done processing the current pearl and can move on
            if pearl.finished:
                self.seen.remove(pearl.id)
                self.pearls.popleft()
            else: # Pearl is not done 
                # Passing the pearl means it's moved from the front of the queue
                if "Pass" in action:
                    self.pearls.popleft()
                    self.seen.remove(pearl.id)
            return action
        else:
            return None

    def process_pq(self, pearl_map):
        """Processes pearls in PriorityQueue fashion.

        Keyword arguments: 
        pearl_map -- map of current pearls, used to help compute cost
        """

        if self.pearls:
            # Get minimum cost move
            cost, pid = heapq.heappop(self.pearls)
            pearl = pearl_map[pid]
            action = pearl.process()
            
            # We are done processing the current pearl and can move on
            if pearl.finished:
                self.seen.remove(pearl.id)
            else:
                # If we still need to process the pearl, recompute the cost
                # and put it back into the priority queue
                if "Pass" not in action:
                    cost = self.compute_cost(pearl)
                    heapq.heappush(self.pearls, (cost, pearl.id))
                else:
                    self.seen.remove(pearl.id)
            return action
        else:
            return None
