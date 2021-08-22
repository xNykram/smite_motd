import unittest
from crons.motd import get_motd_names

class TestMotd(unittest.TestCase):
    
    def test_get_motd_names(self):
        self.assertNotEqual(get_motd_names(), {}, "Shouldn't be empty")


if __name__ == '__main__':
    unittest.main()

