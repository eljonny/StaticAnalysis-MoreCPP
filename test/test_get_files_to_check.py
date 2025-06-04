import os
import sys
import unittest

try:
    PROJECT_PATH = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    sys.path.append(PROJECT_PATH)

except Exception as exception:
    print(f"Can not add project path to system path! Exiting!\nERROR: {exception}")
    raise SystemExit(1) from exception

from src import get_files_to_check as gftc
from utils import helper_functions as util

class TestGetFilesToCheck(unittest.TestCase):
    """Unit tests for get_files_to_check module"""

    def test_get_files_to_check(self):
        """
        Test the `get_files_to_check()` function.

        This test case checks whether the `get_files_to_check()` function correctly generates a
        list of file paths to check for static analysis issues in a given directory, excluding
        any directories that should be skipped.

        The test case creates a mock directory structure and a set of directories to skip,
        and expects the generated list of file paths to match a pre-defined expected list of
        file paths.
        """

        pwd = os.path.dirname(os.path.realpath(__file__))

        # Excludes == None
        expected = [
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.cpp",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.hpp",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_1{os.sep}ExcludedFile1.hpp",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_2{os.sep}ExcludedFile2.hpp",
        ]
        result = gftc.get_files_to_check(
            f"{pwd}{os.sep}utils{os.sep}dummy_project", None, "", "c++"
        )

        self.assertEqual(util.to_list_and_sort(result), expected)

        # Single exclude_dir
        expected = [
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.cpp",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.hpp",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_2{os.sep}ExcludedFile2.hpp",
        ]
        result = gftc.get_files_to_check(
            f"{pwd}{os.sep}utils{os.sep}dummy_project",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_1",
            "",
            "c++",
        )

        self.assertEqual(util.to_list_and_sort(result), expected)

        # Multiple exclude_dir
        expected = [
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.cpp",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.hpp",
        ]
        result = gftc.get_files_to_check(
            f"{pwd}{os.sep}utils{os.sep}dummy_project",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_1 {pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_2",
            "",
            "c++",
        )

        # Preselected files present
        expected = [f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.cpp"]
        result = gftc.get_files_to_check(
            f"{pwd}{os.sep}utils{os.sep}dummy_project",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_1 {pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_2",
            f"{pwd}{os.sep}utils{os.sep}dummy_project{os.sep}DummyFile.cpp {pwd}{os.sep}utils{os.sep}dummy_project{os.sep}exclude_dir_1{os.sep}ExcludedFile1.hpp",
            "c++",
        )

if __name__ == "__main__":
    unittest.main()
