import json
import unittest

import unittest_utils
from aries.core.config.config import Config
from aries.core.exceptions import ValidationError

CONFIG_EMPTY = 'config_empty.json'
CONFIG_NORMAL = 'config_normal.json'
CONFIG_WITH_MISSED_PARAMS = 'config_with_missed_params.json'


class TestConfig(unittest.TestCase):
    """Tests for checking State and update state behaviour"""

    def test_if_all_properties_set(self):
        """Test f all properties set for Config"""
        with unittest_utils.readfile(CONFIG_NORMAL, __file__) as f:
            j = json.load(f)
            config = Config.load(j)
        unittest_utils.check_if_properties_is_set_except(self, "Config", config, ['clusters'])

    def test_if_all_properties_set_from_missed_params(self):
        """Test if Config loaded with missed params"""
        with unittest_utils.readfile(CONFIG_WITH_MISSED_PARAMS, __file__) as f:
            j = json.load(f)
            config = Config.load(j)
            unittest_utils.check_if_properties_is_set_except(self, "Config", config, ['clusters'])

    def test_if_config_is_empty(self):
        """Test if Config loaded with missed params"""
        with unittest_utils.readfile(CONFIG_EMPTY, __file__) as f:
            j = json.load(f)
            self.assertRaises(ValidationError, Config.load, j)
