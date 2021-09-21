from collections import deque

class Pearl:
    """Pearl object holding pearl planning information"""
    def __init__(self, pid, plan, work, layers):
        """Constructor for Pearl.

        Keyword arguments: 
        pid    -- id of pearl
        plan   -- computed plan for dissolving layers of pearl
        work   -- amount of turns necessary for finishing work on the pearl based on plan
        layers -- number of layers to dissolve for the pearl
        """
        self.id = pid
        self.plan = deque(plan)
        # import sys
        # print(self.plan, file=sys.stderr)
        self.work = work
        self.finished = False
        self.layers = layers

    def peek(self):
        """Look at the next step of the plan."""
        return self.plan[0]

    def process(self):
        """Gets the next action.

        Returns the next action that needs to be taken.
        Moves plan forward as necessary. 
        If all the layers are removed, then the pearl is marked as finished.

        Also keeps track of the amount of work left for the pearl, 
        mostly for debugging purposes.
        
        Returns:
        action -- next action to perform for the Pearl,
                  type is either Nom or Pass
        """
        action = self.peek()
        action[0] -= 1
        if action[0] == 0:
            self.plan.popleft()
            if "Nom" in action[1]:
                self.layers -= 1

                # No more layers: we're done with the plan or we're just passing the 
                # pearl back to the gatekeeper
                if self.layers == 0:
                    self.finished = True
        self.work -= 1
        return action[1]