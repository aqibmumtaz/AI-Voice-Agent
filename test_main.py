import unittest
from utils import Utils
from configs import Configs
import coverage
import sys


class TestUtils(unittest.TestCase):
    def test_print_api_key_runs(self):
        """Should run without raising exception (pass criteria: no exception)"""
        try:
            Utils.print_api_key()
        except Exception as e:
            self.fail(f"print_api_key() raised an exception: {e}")

    def test_utils_class_exists(self):
        """Utils class should exist (pass criteria: class is defined)"""
        self.assertTrue(hasattr(Utils, "print_api_key"))

    def test_utils_print_api_key_output(self):
        """print_api_key should print the correct API key (pass criteria: output contains API key)"""
        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            Utils.print_api_key()
        output = buf.getvalue()
        self.assertIn(Configs.RETELL_API_KEY, output)


class TestConfigs(unittest.TestCase):
    def test_retell_api_key_exists(self):
        """RETELL_API_KEY should not be None (pass criteria: not None)"""
        self.assertIsNotNone(Configs.RETELL_API_KEY)

    def test_retell_api_key_type(self):
        """RETELL_API_KEY should be a string (pass criteria: type is str)"""
        self.assertIsInstance(Configs.RETELL_API_KEY, str)

    def test_configs_class_has_types(self):
        """Configs class should have _TYPES attribute (pass criteria: attribute exists)"""
        self.assertTrue(hasattr(Configs, "_TYPES"))

    def test_configs_class_has_load_configs(self):
        """Configs class should have load_configs method (pass criteria: method exists)"""
        self.assertTrue(callable(getattr(Configs, "load_configs", None)))


def run_tests_with_coverage():
    cov = coverage.Coverage(source=["."])
    cov.start()
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    cov.stop()
    cov.save()
    percent = cov.report(show_missing=False)
    print("\nTest Summary Table:")
    print(
        "| Test Case Name                      | Description                                         | Criteria Tested                | Result |"
    )
    print(
        "|-------------------------------------|-----------------------------------------------------|-------------------------------|--------|"
    )
    print(
        "| test_print_api_key_runs             | Should run without raising exception                | Utility function, imports      | {}    |".format(
            "Pass" if result.wasSuccessful() else "Fail"
        )
    )
    print(
        "| test_utils_class_exists             | Utils class should exist                            | Class definition               | {}    |".format(
            "Pass" if result.wasSuccessful() else "Fail"
        )
    )
    print(
        "| test_utils_print_api_key_output     | print_api_key should print the correct API key      | Output correctness             | {}    |".format(
            "Pass" if result.wasSuccessful() else "Fail"
        )
    )
    print(
        "| test_retell_api_key_exists          | RETELL_API_KEY should not be None                   | Config loading, not None       | {}    |".format(
            "Pass" if result.wasSuccessful() else "Fail"
        )
    )
    print(
        "| test_retell_api_key_type            | RETELL_API_KEY should be a string                   | Config type, str               | {}    |".format(
            "Pass" if result.wasSuccessful() else "Fail"
        )
    )
    print(
        "| test_configs_class_has_types        | Configs class should have _TYPES attribute          | Attribute existence            | {}    |".format(
            "Pass" if result.wasSuccessful() else "Fail"
        )
    )
    print(
        "| test_configs_class_has_load_configs | Configs class should have load_configs method       | Method existence               | {}    |".format(
            "Pass" if result.wasSuccessful() else "Fail"
        )
    )
    print(f"\nCoverage: {percent:.2f}%\n")
    return result


if __name__ == "__main__":
    run_tests_with_coverage()
