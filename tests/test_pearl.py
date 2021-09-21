import unittest
from atlantis.pearl import Pearl

# Tests moving pearl
class TestPearlMoving(unittest.TestCase):
    def setUp(self):
        pid = 3076927177
        layers = len([{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        plan = [[1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 8}}], 
                [12, {'Nom': 3076927177}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 9}}], 
                [3, {'Nom': 3076927177}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 10}}], 
                [1, {'Pass': {'pearl_id': 3076927177, 'to_worker': 0}}]]
        work = sum([p[0] for p in plan])
        self.pearl = Pearl(pid, plan, work, layers)

    def test_creation(self):
        assert(self.pearl.id == 3076927177)
        assert(self.pearl.layers == 2)
        assert(self.pearl.work == 19)
        assert(len(self.pearl.plan) == 6)

    def test_peek_doesnt_change(self):
        times, action = self.pearl.peek()
        assert(times == 1)
        assert('Pass' in action)
        times, action = self.pearl.peek()
        assert(times == 1)
        assert('Pass' in action)

    def test_peek_after_process(self):
        action = self.pearl.process()
        times, action = self.pearl.peek()
        assert(times == 12)
        assert('Nom' in action)

    def test_process(self):
        start_work = self.pearl.work
        action = self.pearl.process()
        assert('Pass' in action)
        end_work = self.pearl.work
        assert(start_work == end_work + 1)

    def test_layers(self):
        assert(self.pearl.layers == 2)
        action = self.pearl.process()
        assert(action['Pass']['to_worker'] == 8)
        for _ in range(12): action = self.pearl.process(); assert(action['Nom'] == 3076927177)
        assert(self.pearl.layers == 1)

    def test_full(self):
        assert(not self.pearl.finished)
        assert(self.pearl.layers == 2)
        action = self.pearl.process()
        assert(action['Pass']['to_worker'] == 8)
        assert(self.pearl.work == 18)

        for _ in range(12): action = self.pearl.process(); assert(action['Nom'] == 3076927177)
        assert(self.pearl.layers == 1)
        assert(self.pearl.work == 6)
        
        action = self.pearl.process()
        assert(action['Pass']['to_worker'] == 9)
        assert(self.pearl.work == 5)
        
        for _ in range(3): action = self.pearl.process(); assert(action['Nom'] == 3076927177)
        assert(self.pearl.work == 2)
        assert(self.pearl.layers == 0)
        assert(self.pearl.finished)

        action = self.pearl.process()
        assert(action['Pass']['to_worker'] == 10)
        assert(self.pearl.work == 1)
        
        action = self.pearl.process()
        assert(action['Pass']['to_worker'] == 0)
        assert(self.pearl.work == 0)

# Tests pearls that don't move
class TestPearlStationary(unittest.TestCase):
    def setUp(self):
        pid = 3076927176
        layers = len([{"color":"Red","thickness":12},{"color":"Green","thickness":13}])
        plan = [[12, {'Nom': 3076927176}], 
                [3, {'Nom': 3076927176}]]
        work = sum([p[0] for p in plan])
        self.pearl = Pearl(pid, plan, work, layers)

    def test_creation(self):
        assert(self.pearl.id == 3076927176)
        assert(self.pearl.layers == 2)
        assert(self.pearl.work == 15)
        assert(len(self.pearl.plan) == 2)

    def test_peek_doesnt_change(self):
        times, action = self.pearl.peek()
        assert(times == 12)
        assert('Nom' in action)
        times, action = self.pearl.peek()
        assert(times == 12)
        assert('Nom' in action)

    def test_peek_after_process(self):
        action = self.pearl.process()
        times, action = self.pearl.peek()
        assert(times == 11)
        assert('Nom' in action)

    def test_process(self):
        start_work = self.pearl.work
        action = self.pearl.process()
        assert('Nom' in action)
        end_work = self.pearl.work
        assert(start_work == end_work + 1)

    def test_layers(self):
        assert(self.pearl.layers == 2)
        for _ in range(12): action = self.pearl.process(); assert(action['Nom'] == 3076927176)
        assert(self.pearl.layers == 1)

    def test_full(self):
        assert(not self.pearl.finished)
        assert(self.pearl.layers == 2)
        for _ in range(12): action = self.pearl.process(); assert(action['Nom'] == 3076927176)
        assert(self.pearl.layers == 1)
        assert(self.pearl.work == 3)
        
        for _ in range(3): action = self.pearl.process(); assert(action['Nom'] == 3076927176)
        assert(self.pearl.layers == 0)
        assert(self.pearl.finished)

if __name__ == '__main__':
    unittest.main()