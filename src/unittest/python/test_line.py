import json
import unittest

import unittest_utils
from aries.core.grid import grid_utils
from aries.core.grid.line import Line

NAME = "Line1"
RESISTANCE = 50
REACTANCE = 50
SHUNT_RESISTANCE = 60
SHUNT_REACTANCE = 70
GRID_ELEMENTS = 'grid_elements.json'

class TestLine(unittest.TestCase):
    def setUp(self):
        self.line = Line.from_properties(name=NAME, resistance=RESISTANCE, reactance=REACTANCE,
                                         shunt_resistance=SHUNT_RESISTANCE, shunt_reactance=SHUNT_REACTANCE)

    def test_pv_panel_assigned_properties(self):
        self.assertEqual(self.line.name, NAME, "name is not equal")
        self.assertEqual(self.line.resistance, RESISTANCE, "resistance is not equal")
        self.assertEqual(self.line.reactance, REACTANCE, "reactance is not equal")

        self.assertEqual(self.line.shunt_resistance, SHUNT_RESISTANCE, "shunt_resistance is not equal")
        self.assertEqual(self.line.shunt_reactance, SHUNT_REACTANCE, "shunt_reactance is not equal")

    def test_if_object_is_valid_in_grid_elements_schema(self):
        """Test lines schema validation for lines"""
        with unittest_utils.readfile(GRID_ELEMENTS, __file__) as f:
            j = json.load(f)
            agents,lines = grid_utils.create_grid_elements(j)
            self.assertEqual(len(lines), 4, 'Number of lines is not equal')
