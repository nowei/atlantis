import unittest
import json
from atlantis.atlantis import Atlantis

class TestAtlantis(unittest.TestCase):

    def setUp(self):
        self.atlantis = Atlantis()
        self.state = {"workers": [{"id":0,"flavor":"General","desk":[]},
                                  {"id":1,"flavor":"Vector","desk":[]},
                                  {"id":2,"flavor":"Matrix","desk":[]}],
                                  "neighbor_map":[[0,1],[1,2],[0,2]],"score":0}
        self.atlantis.process(self.state)

    def test_initialized(self):
        assert(self.atlantis.mode == 'pq')
        assert(len(self.atlantis.workers) == 3)
        assert(not self.atlantis.pearl_map)
        assert(all([work == 0 for work in self.atlantis.workload]))
        nb = self.atlantis.neighbors
        assert(1 in nb[0] and 2 in nb[0])
        assert(0 in nb[1] and 2 in nb[1])
        assert(0 in nb[2] and 1 in nb[2])

    def test_search_move_simple_colors(self):
        plan, workload, end = self.atlantis.search(5, 0, [{"color":"Red","thickness":1},{"color":"Green","thickness":1},{"color":"Blue","thickness":1}])
        assert(workload[0] == 1)
        assert(workload[1] == 3)
        assert(workload[2] == 0)
        assert(end == 1)
        assert(plan[0][0] == 1)
        assert(plan[0][1]["Pass"]["pearl_id"] == 5)
        assert(plan[0][1]["Pass"]["to_worker"] == 1)
        assert(plan[1][0] == 1)
        assert(plan[1][1]["Nom"] == 5)
        assert(plan[2][0] == 1)
        assert(plan[2][1]["Nom"] == 5)
        assert(plan[3][0] == 1)
        assert(plan[3][1]["Nom"] == 5)

    def test_search_simple(self):
        plan, workload, end = self.atlantis.search(5, 0, [{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        assert(workload[0] == 1)
        assert(workload[1] == 15)
        assert(workload[2] == 0)
        assert(end == 1)
        assert(plan[0][0] == 1)
        assert(plan[0][1]["Pass"]["pearl_id"] == 5)
        assert(plan[0][1]["Pass"]["to_worker"] == 1)
        assert(plan[1][0] == 12)
        assert(plan[1][1]["Nom"] == 5)
        assert(plan[2][0] == 3)
        assert(plan[2][1]["Nom"] == 5)

    def test_search_simple2(self):
        state1 = {"workers": [{"id":0,"flavor":"General","desk":[{"id": 5,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]},
                             {"id":1,"flavor":"Vector","desk":[]},
                             {"id":2,"flavor":"Matrix","desk":[]}],
                             "neighbor_map":[[0,1],[1,2],[0,2]],"score":0}
        actions = json.loads(self.atlantis.process(state1))
        assert(actions["0"]["Pass"]["pearl_id"] == 5)
        assert(actions["0"]["Pass"]["to_worker"] == 1)

        state2 = {"workers": [{"id":0,"flavor":"General","desk":[]},
                             {"id":1,"flavor":"Vector","desk":[{"id": 5,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]},
                             {"id":2,"flavor":"Matrix","desk":[]}],
                             "neighbor_map":[[0,1],[1,2],[0,2]],"score":0}
        plan, workload, end = self.atlantis.search(5, 0, [{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        assert(workload[0] == 1)
        assert(workload[1] == 0)
        assert(workload[2] == 19)
        assert(end == 2)
        assert(plan[0][0] == 1)
        assert(plan[0][1]["Pass"]["pearl_id"] == 5)
        assert(plan[0][1]["Pass"]["to_worker"] == 2)
        assert(plan[1][0] == 12)
        assert(plan[1][1]["Nom"] == 5)
        assert(plan[2][0] == 7)
        assert(plan[2][1]["Nom"] == 5)

    def test_return_path_simple(self):
        plan, workload, end = self.atlantis.search(5, 0, [{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        assert(end == 1)
        path = self.atlantis.return_path(1, 0)
        assert(path[0] == 1)
        assert(path[1] == 0)

    def test_plan_pearl_simple(self):
        plan, work = self.atlantis.plan_pearl({"id": 5,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]})
        assert(work == 17)
        assert(plan[3][0] == 1)
        assert(plan[3][1]["Pass"]["pearl_id"] == 5)
        assert(plan[3][1]["Pass"]["to_worker"] == 0)

    def test_process_simple(self):
        state1 = {"workers": [{"id":0,"flavor":"General","desk":[{"id": 5,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]},
                             {"id":1,"flavor":"Vector","desk":[]},
                             {"id":2,"flavor":"Matrix","desk":[]}],
                             "neighbor_map":[[0,1],[1,2],[0,2]],"score":0}
        actions = json.loads(self.atlantis.process(state1))
        assert(actions["0"]["Pass"]["pearl_id"] == 5)
        assert(actions["0"]["Pass"]["to_worker"] == 1)

        state2 = {"workers": [{"id":0,"flavor":"General","desk":[]},
                             {"id":1,"flavor":"Vector","desk":[{"id": 5,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]},
                             {"id":2,"flavor":"Matrix","desk":[]}],
                             "neighbor_map":[[0,1],[1,2],[0,2]],"score":0}
        for i in range(15):
            actions = json.loads(self.atlantis.process(state2))
            assert(0 not in actions)
            assert(actions["1"]["Nom"] == 5)

        actions = json.loads(self.atlantis.process(state2))
        assert(actions["1"]["Pass"]["pearl_id"] == 5)
        assert(actions["1"]["Pass"]["to_worker"] == 0)

if __name__ == '__main__':
    unittest.main()