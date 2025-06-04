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

class TestStaticAnalysisCpp(unittest.TestCase):

    """Unit tests for static_analysis_cpp"""

    maxDiff = None

    @classmethod
    def mock_env(self, mp: MonkeyPatch):
        mp.setenv("GITHUB_WORKSPACE", f"{PROJECT_PATH}{os.sep}test{os.sep}utils{os.sep}dummy_project")
        mp.setenv("INPUT_VERBOSE", "True")
        mp.setenv("INPUT_REPORT_PR_CHANGES_ONLY", "False")
        mp.setenv("INPUT_REPO", "RepoName")
        mp.setenv("GITHUB_SHA", "1234")
        mp.setenv("INPUT_COMMENT_TITLE", "title")

    def test_create_comment_for_output(self):
        with MonkeyPatch.context() as mp:
            self.mock_env(mp)

            from src import static_analysis_cpp

            cppcheck_content = [
                f"{os.getenv("GITHUB_WORKSPACE")}{os.sep}DummyFile.cpp:8:23: style: Error message\n",
                "    Part of code\n",
                "               ^\n",
                f"{os.getenv("GITHUB_WORKSPACE")}{os.sep}DummyFile.cpp:6:12: note: Note message\n",
                "    Part of code\n",
                "               ^\n",
                f"{os.getenv("GITHUB_WORKSPACE")}{os.sep}DummyFile.cpp:7:4: note: Another note message\n",
                "    Part of code\n",
                "               ^\n",
                f"{os.getenv("GITHUB_WORKSPACE")}{os.sep}DummyFile.cpp:3:0: style: Error message\n",
                "    Part of code\n",
                "               ^\n",
            ]

            files_changed_in_pr = {
                f"{os.getenv("GITHUB_WORKSPACE")}{os.sep}DummyFile.hpp": ("added", (1, 10)),
                f"{os.getenv("GITHUB_WORKSPACE")}{os.sep}DummyFile.cpp": ("added", (1, 10)),
            }
            result = static_analysis_cpp.create_comment_for_output(
                cppcheck_content, os.getenv("GITHUB_WORKSPACE"), files_changed_in_pr, False
            )

            sha = os.getenv("GITHUB_SHA")
            repo_name = os.getenv("INPUT_REPO")
            expected = (
                f"\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L8-L9 \n"
                f"```diff\n!Line: 8 - style: Error message"
                f"\n\n!Line: 6 - note: Note message"
                f"\n!Line: 7 - note: Another note message\n``` "
                f"\n\n\n\nhttps://github.com/{repo_name}/blob/{sha}/DummyFile.cpp#L3-L8 \n"
                f"```diff\n!Line: 3 - style: Error message\n\n``` \n <br>\n"
            )

            print(result)

            self.assertEqual(result, (expected, 2))

    def test_prepare_comment_body_empty(self):
        with MonkeyPatch.context() as mp:
            self.mock_env(mp)

            from src import static_analysis_cpp
            from utils import helper_functions as utils

            comment_title = os.getenv("INPUT_COMMENT_TITLE")
            comment_body = static_analysis_cpp.prepare_comment_body("", "", "", "", 0, 0, 0, 0)

            # Empty results
            expected_comment_body = utils.generate_comment(comment_title, "", 0, "cppcheck")

            self.assertEqual(expected_comment_body, comment_body)

    def test_prepare_comment_body_single_cppcheck(self):
        with MonkeyPatch.context() as mp:
            self.mock_env(mp)

            from src import static_analysis_cpp
            from utils import helper_functions as utils

            comment_title = os.getenv("INPUT_COMMENT_TITLE")

            cppcheck_issues_found = 1
            cppcheck_comment = "dummy issue"
            expected_comment_body = utils.generate_comment(
                comment_title, cppcheck_comment, cppcheck_issues_found,
                "cppcheck"
            )

            comment_body = static_analysis_cpp.prepare_comment_body(
                "", cppcheck_comment, "", "",
                0, cppcheck_issues_found, 0, 0
            )

            self.assertEqual(expected_comment_body, comment_body)

    def test_prepare_comment_body_multi_cppcheck(self):
        with MonkeyPatch.context() as mp:
            self.mock_env(mp)

            from src import static_analysis_cpp
            from utils import helper_functions as utils

            comment_title = os.getenv("INPUT_COMMENT_TITLE")

            cppcheck_issues_found = 4
            cppcheck_comment = "dummy issues"
            expected_comment_body = utils.generate_comment(
                comment_title, cppcheck_comment, cppcheck_issues_found,
                "cppcheck"
            )

            comment_body = static_analysis_cpp.prepare_comment_body(
                "", cppcheck_comment, "", "",
                0, cppcheck_issues_found, 0, 0
            )

            self.assertEqual(expected_comment_body, comment_body)

    def test_prepare_comment_body_single_clang_tidy(self):
        with MonkeyPatch.context() as mp:
            self.mock_env(mp)

            from src import static_analysis_cpp
            from utils import helper_functions as utils

            comment_title = os.getenv("INPUT_COMMENT_TITLE")

            clang_tidy_issues_found = 1
            clang_tidy_comment = "dummy issue"
            expected_comment_body = utils.generate_comment(
                comment_title, clang_tidy_comment, clang_tidy_issues_found, "clang-tidy"
            )

            comment_body = static_analysis_cpp.prepare_comment_body(
                "", "", "", clang_tidy_comment,
                0, 0, 0, clang_tidy_issues_found
            )

            self.assertEqual(expected_comment_body, comment_body)

    def test_prepare_comment_body_multi_clang_tidy(self):
        with MonkeyPatch.context() as mp:
            self.mock_env(mp)

            from src import static_analysis_cpp
            from utils import helper_functions as utils

            comment_title = os.getenv("INPUT_COMMENT_TITLE")

            clang_tidy_issues_found = 4
            clang_tidy_comment = "dummy issues"
            expected_comment_body = utils.generate_comment(
                comment_title, clang_tidy_comment, clang_tidy_issues_found, "clang-tidy"
            )

            comment_body = static_analysis_cpp.prepare_comment_body(
                "", "", "", clang_tidy_comment,
                0, 0, 0, clang_tidy_issues_found
            )

            self.assertEqual(expected_comment_body, comment_body)

if __name__ == "__main__":
    unittest.main()
