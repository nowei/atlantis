import json
import math
from collections import defaultdict, deque
import heapq
from .pearl import Pearl
from .worker import Worker

class Atlantis:
    """Coordinator for Pearl Processing.

    Main coordinator for how pearls should be processed
    as well as what action each worker should take.

    See Worker for information on how each worker chooses an action.
    """

    def __init__(self, mode="pq"):
        """ Constructor
        
        Keyword arguments:
        mode  -- Order of how workers will process the pearls (default "pq")
                 - "pq" for priority queue, see worker for priority computation
                 - "fifo" for first-in-first-out
                 - "rr" for round-robin
        """
        self.mode = mode                        # Mode for processing workers
        self.initialized = False                # Whether initialization has occurred or not
        self.worker_flavor = {}                 # flavor mappings for workers
        self.workers = {}                       # worker id to Worker mappings
        self.neighbors = defaultdict(set)       # Keeps track of neighboring nodes
        self.pearl_map = {}                     # pearl id to Pearl mappings
        self.workload = None                    # keeps track of current workload at nodes

        self.processing_rate = {
            "General": {
                "Red": 1,
                "Green": 1,
                "Blue": 1,
            },
            "Vector": {
                "Red": 1,
                "Green": 5,
                "Blue": 2,
            },
            "Matrix": {
                "Red": 1,
                "Green": 2,
                "Blue": 10,
            }
        }

        # penalize passing through the origin since it needs to 
        # address incoming pearls
        # origin is synonymous with gatekeeper id in this code
        self.origin_penalty = 10
        self.origin = 0

    
    def initialize(self, setting):
        """Initialize the workers and get the neighbor mappings.

        Keyword arguments:
        setting -- the initial state for the workers, e.g. flavor and id
                   along with the neighbor relationships.
        """

        # record type mappings 
        for worker in setting["workers"]:
            wid = worker["id"]
            flavor = worker["flavor"]
            self.worker_flavor[wid] = flavor
            self.workers[wid] = Worker(wid, self.mode)

        self.workload = [0 for _ in range(len(self.workers))]

        # record neighboring nodes 
        for u, v in setting["neighbor_map"]:
            self.neighbors[u].add(v) 
            self.neighbors[v].add(u)

        self.initialized = True

    def search(self, pid, start, layers):
        """Generate a plan for processing based on a greedy search on each layer

        The entire search considers:
        - layers to process
        - current workload at each worker
        - path from start of processing to the end

        Keyword arguments:
        pid    -- the id of the pearl we're processing
        start  -- the starting node (will be the origin each time)
        layers -- The different layers we need to process for the pearl

        Returns:
        plan     -- The plan for processing the pearl, Noms and Passes
        workload -- ~ The amount of turns needed to process the pearl
        start    -- The last worker id in the plan for processing the pearl
        """
        plan = []
        workload = [0 for _ in range(len(self.workers))]

        # each layer is a separate search for the worker to process the layer
        for i in range(len(layers)):
            layer = layers[i]
            target_color = layer["color"]
            target_thickness = layer["thickness"]
            processing_costs = {k: math.ceil(target_thickness / self.processing_rate[k][target_color]) for k in self.processing_rate}

            # Searches to find the cost of processing every node at each worker.
            # Cost consists of: Cost of the path 
            #                 + Existing workload cost 
            #                 + processing cost by the worker
            # 
            # Basically Dijkstra's.
            visited = set()
            path = {}
            path_costs = {}
            pq = [(0, start)]
            curr_costs = {}

            # Assumes single connected component 
            while len(visited) != len(self.workers):
                cost, curr = heapq.heappop(pq)
                if curr in visited: continue
                visited.add(curr)
                curr_costs[curr] = cost + processing_costs[self.worker_flavor[curr]] + self.workload[curr]
                if curr == self.origin:
                    curr_costs[curr] += self.origin_penalty
                for neighbor in self.neighbors[curr]:
                    if neighbor in visited: continue
                    cost_new = cost + 1 
                    if neighbor == self.origin:
                        cost_new += self.origin_penalty
                    if neighbor not in path_costs or cost_new < path_costs[neighbor]:
                        path_costs[neighbor] = cost_new
                        path[neighbor] = curr
                        heapq.heappush(pq, (cost_new, neighbor))

            # Get the best cost and candidate for processing the current layer
            best_cost = float("inf")
            best_cand = -1
            for cand in curr_costs:
                if curr_costs[cand] < best_cost:
                    best_cost = curr_costs[cand]
                    best_cand = cand

            # If the best candidate isn't the starting node, add the cost of the
            # path for future workload considerations
            if best_cand != start:
                # create the path 
                best_path = [best_cand]
                while best_path[-1] != start:
                    best_path.append(path[best_path[-1]])
                best_path = best_path[::-1]

                # Add the Pass operations to the plan
                prev = start 
                for curr in best_path[1:]:
                    workload[prev] += 1
                    plan.append([1, {"Pass":{"pearl_id":pid,"to_worker":curr}}])
                    prev = curr

            # Add the noms to the plan 
            workload[best_cand] += processing_costs[self.worker_flavor[best_cand]]
            plan.append([processing_costs[self.worker_flavor[best_cand]], {"Nom": pid}])

            # Set the last worker in the path as the start of the next search pass
            start = best_cand
        return plan, workload, start

    def return_path(self, start, target):
        """Finds best return path based on workload as cost.

        Finds the best path for getting from start to target, 
        using the workload as the cost of visiting each node.
        
        Basically Dijkstra's.

        Keyword arguments:
        start  -- Where the return path begins
        target -- Where we're trying to reach

        Returns:
        ret_path -- The path to from the start to the target
        """

        # return early if we don't need to go anywhere
        if start == target: return []

        # otherwise look for a path
        visited = set()
        path = {}
        costs = {}
        pq = [(0, start)]

        # Look until we find the target, dijkstra's guarantees
        # minimum cost path according to cost function.
        #
        # Cost function is: Cost to get to current worker + workload at worker
        while target not in visited:
            cost, curr = heapq.heappop(pq)
            if curr in visited: continue
            visited.add(curr)
            for neighbor in self.neighbors[curr]:
                if neighbor in visited: continue
                cost_new = cost + self.workload[neighbor] 
                if neighbor not in costs or cost_new < costs[neighbor]:
                    costs[neighbor] = cost_new
                    path[neighbor] = curr
                    heapq.heappush(pq, (cost_new, neighbor))

        ret_path = [0]
        while ret_path[-1] != start:
            ret_path.append(path[ret_path[-1]])

        return ret_path[::-1]

    def plan_pearl(self, pearl):
        """Create plan for processing pearl.

        Planning steps:
        1. Creates the plan for processing layers
        2. Adds work to workers for plan
        3. Compute return path
        4. Adds work to workers for return path

        Keyword arguments:
        pearl -- The pearl we need to create a plan for

        Returns:
        plan -- the plan for the pearl
        work -- the amount of work (~turns) necessary for processing the pearl
        """
        pid = pearl["id"]
        layers = pearl["layers"]
        start = 0

        # 1. Creates plan 
        plan, workload, last_id = self.search(pid, start, layers)

        # 2. Adds work for plan
        for i in range(len(workload)):
            self.workload[i] += workload[i]
        work = sum(workload)
        
        # 3. Compute return path
        path = self.return_path(last_id, start)

        # 4. if it's not already at the gatekeeper, add Pass operations
        if path: 
            prev = path[0]
            for curr in path[1:]:
                self.workload[prev] += 1
                plan.append([1, {"Pass":{"pearl_id":pid,"to_worker":curr}}])
                work += 1
                prev = curr
        return plan, work

    
    def process(self, state):
        """Processes the state and any associated state changes.

        Keyword arguments:
        state -- The current state of the system

        Returns:
        action_string -- The JSON string holding the actions for each worker
                         format: {[worker_id]:"Nom":[pearl_id]} or 
                                 {[worker_id]: "Pass": {"pearl_id":[pearl_id],"to_worker":[to_worker_id]}}

        """
        if not self.initialized:
            self.initialize(state)

        # for each new pearl, create a plan and create a pearl 
        # that tracks the plan 
        gatekeeper = state["workers"][0]
        for pearl in gatekeeper["desk"]:
            pid = pearl["id"]
            if pid not in self.pearl_map:
                plan, work = self.plan_pearl(pearl)
                self.pearl_map[pid] = Pearl(pid, plan, work, len(pearl["layers"]))

        # Designate the actions for each worker
        actions = {}
        for worker in state["workers"]:
            wid = worker["id"]
            desk = worker["desk"]
            act = self.workers[wid].process(desk, self.pearl_map)
            if act is not None:
                actions[wid] = act
                if self.workload[wid]:
                    self.workload[wid] -= 1

        # Clean up finished pearls
        finished_pearls = set()
        for pid in self.pearl_map:
            if self.pearl_map[pid].work == 0:
                finished_pearls.add(pid)
        for pid in finished_pearls:
            self.pearl_map.pop(pid, None)

        # Dump actions string so that atlantis output can be processed
        actions_string = json.dumps(actions)
        return actions_string

