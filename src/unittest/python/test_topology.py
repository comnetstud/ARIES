import unittest

from aries.core.grid.topology import Node, Path

BRANCHES_IN = ["IN1", "IN2"]
BRANCHES_OUT = ["OUT1", "OUT2", "OUT3"]
ADJACENCY = [["NAME1", "IN1"], ["NAME2", "OUT1"]]
AGENT = "agent"

PATHS = [{"active": 1, "path": ["A1", "A2"]}, {"active": 0, "path": ["A3", "A4"]}]


class TestNode(unittest.TestCase):
    """Test for Node"""

    def test_if_all_properties_set(self):
        node = Node.from_properties(branches_in=BRANCHES_IN, branches_out=BRANCHES_OUT, adjacency=ADJACENCY,
                                    agent=AGENT)

        self.assertEqual(node.branches_in, BRANCHES_IN, "branches_in is not equal")
        self.assertEqual(node.branches_out, BRANCHES_OUT, "branches_out is not equal")
        self.assertEqual(node.adjacency, ADJACENCY, "adjacency is not equal")
        self.assertEqual(node.agent, AGENT, "agent is not equal")


class TestPath(unittest.TestCase):
    """Test for Path"""

    def test_if_all_properties_are_set_and_valid(self):
        path = Path.load(PATHS)
        self.assertEqual(len(path.paths), 2, "number of paths is different")
        self.assertEqual(path.paths[0], PATHS[0], "paths is not equal")
        self.assertEqual(path.paths[1], PATHS[1], "paths is not equal")
