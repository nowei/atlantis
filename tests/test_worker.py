import unittest
from atlantis.worker import Worker
from atlantis.pearl import Pearl

class TestWorker(unittest.TestCase):
    def setUp(self):
        self.worker = Worker(0)

    def test_resolve_state(self):
        assert(1==1)

    def test_worker(self):
        assert(self.worker.mode == 'pq')
        assert(self.worker.wid == 0)
        worker = Worker(0, mode='af')
        assert(worker.mode == 'pq')
        worker = Worker(0, mode='rr')
        assert(worker.mode == 'rr')
        worker = Worker(0, mode='fifo')
        assert(worker.mode == 'fifo')

    def test_compute_cost(self):
        pid = 3076927177
        layers = len([{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        plan = [[1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 8}}], 
                [12, {'Nom': 3076927177}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 9}}], 
                [3, {'Nom': 3076927177}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 10}}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 0}}]]
        work = sum([p[0] for p in plan])
        pearl = Pearl(pid, plan, work, layers)
        cost = self.worker.compute_cost(pearl)
        assert(cost == 21)
        plan = [[12, {'Nom': 3076927177}], 
                [3, {'Nom': 3076927177}]]
        work = sum([p[0] for p in plan])
        pearl = Pearl(pid, plan, work, layers)
        cost = self.worker.compute_cost(pearl)
        assert(cost == self.worker.nom_penalty + 15)


class TestWorkerProcess(unittest.TestCase):
    def setUp(self):
        pid1 = 3076927177
        layers1 = len([{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        plan1 = [[1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 8}}], 
                [12, {'Nom': 3076927177}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 9}}], 
                [3, {'Nom': 3076927177}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 10}}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 0}}]]
        work1 = sum([p[0] for p in plan1])
        pearl1 = Pearl(pid1, plan1, work1, layers1)
        pid2 = 3076927176
        layers2 = len([{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        plan2 = [[12, {'Nom': 3076927176}], 
                 [3, {'Nom': 3076927176}]]
        work2 = sum([p[0] for p in plan2])
        pearl2 = Pearl(pid2, plan2, work2, layers2)
        self.pearl_map = {pid1: pearl1, pid2: pearl2}
        self.state = [{"id":3076927176,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}, {"id":3076927177,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]

class TestWorkerProcessPQ(TestWorkerProcess):
    def setUp(self):
        super(TestWorkerProcessPQ, self).setUp()
        wid = 0
        self.worker = Worker(wid, mode='pq')

    def test_process(self):
        action = self.worker.process(self.state, self.pearl_map)
        assert(action['Pass']['pearl_id'] == 3076927177)
        assert(action['Pass']['to_worker'] == 8)
        assert(3076927176 in self.worker.seen)
        assert(3076927177 not in self.worker.seen)
        new_state = [{"id":3076927176,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]
        assert(len(self.worker.seen) == 1)
        for _ in range(15): 
            action = self.worker.process(new_state, self.pearl_map)
            assert(action['Nom'] == 3076927176)
        assert(not self.worker.seen)

class TestWorkerProcessRR(TestWorkerProcess):
    def setUp(self):
        super(TestWorkerProcessRR, self).setUp()
        wid = 0
        self.worker = Worker(wid, mode='rr')

    def test_process(self):
        action = self.worker.process(self.state, self.pearl_map)
        assert(action['Nom'] == 3076927176)
        assert(3076927176 in self.worker.seen)
        assert(3076927177 in self.worker.seen)

        action = self.worker.process(self.state, self.pearl_map)
        assert(action['Pass']['pearl_id'] == 3076927177)
        assert(action['Pass']['to_worker'] == 8)
        assert(3076927176 in self.worker.seen)
        assert(3076927177 not in self.worker.seen)
        assert(len(self.worker.seen) == 1)

        new_state = [{"id":3076927176,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]
        for _ in range(14): 
            action = self.worker.process(new_state, self.pearl_map)
            assert(action['Nom'] == 3076927176)
        assert(not self.worker.seen)


class TestWorkerProcessFIFO(TestWorkerProcess):
    def setUp(self):
        super(TestWorkerProcessFIFO, self).setUp()
        wid = 0
        self.worker = Worker(wid, mode='fifo')

    def test_process(self):
        action = self.worker.process(self.state, self.pearl_map)
        assert(action['Nom'] == 3076927176)
        assert(3076927176 in self.worker.seen)
        assert(3076927177 in self.worker.seen)

        for _ in range(14): 
            action = self.worker.process(self.state, self.pearl_map)
            assert(action['Nom'] == 3076927176)
        assert(3076927176 not in self.worker.seen)
        assert(3076927177 in self.worker.seen)

        new_state = [{"id":3076927177,"layers":[{"color":"Red","thickness":12},{"color":"Green","thickness":13}]}]
        action = self.worker.process(new_state, self.pearl_map)
        assert(action['Pass']['pearl_id'] == 3076927177)
        assert(action['Pass']['to_worker'] == 8)
        assert(not self.worker.seen)

if __name__ == '__main__':
    unittest.main()