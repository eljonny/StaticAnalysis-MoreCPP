import unittest
import os
import sys

try:
    PROJECT_PATH = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    sys.path.append(PROJECT_PATH)
except Exception as exception:
    print(f"Can not add project path to system path! Exiting!\nERROR: {exception}")
    raise SystemExit(1) from exception

from pytest import MonkeyPatch

class TestUtils(unittest.TestCase):
    """Unit tests for utils_sa module"""

    maxDiff = None

    @classmethod
    def mock_env(self, mp: MonkeyPatch):
        mp.setenv("GITHUB_WORKSPACE", f"{PROJECT_PATH}{os.sep}test{os.sep}utils{os.sep}dummy_project")
        mp.setenv("INPUT_VERBOSE", "True")
        mp.setenv("INPUT_REPORT_PR_CHANGES_ONLY", "False")
        mp.setenv("INPUT_REPO", "RepoName")
        mp.setenv("GITHUB_SHA", "1234")
        mp.setenv("INPUT_COMMENT_TITLE", "title")

    def test_get_lines_changed_from_patch(self):
        with MonkeyPatch.context() as mp:
            self.mock_env(mp)

            from src import sa_utils

            patch = "@@ -43,6 +48,8 @@\n@@ -0,0 +1 @@"

            lines = sa_utils.get_lines_changed_from_patch(patch)
            self.assertEqual(lines, [(48, 56), (1, 1)])

if __name__ == "__main__":
    unittest.main()
