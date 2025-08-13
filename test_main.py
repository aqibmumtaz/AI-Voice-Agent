import unittest
from utils import Utils
from configs import Configs


class TestUtils(unittest.TestCase):
    def test_print_api_key(self):
        # This just checks that the method runs without error
        try:
            Utils.print_api_key()
        except Exception as e:
            self.fail(f"print_api_key() raised an exception: {e}")


class TestConfigs(unittest.TestCase):
    def test_retell_api_key(self):
        self.assertIsNotNone(Configs.RETELL_API_KEY)
        self.assertIsInstance(Configs.RETELL_API_KEY, str)


if __name__ == "__main__":
    unittest.main()
