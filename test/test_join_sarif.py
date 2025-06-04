import filecmp
import itertools
import json
import jsonpickle
import os
import sys
import tempfile
import unittest

try:
    PROJECT_PATH = f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-2])
    sys.path.append(PROJECT_PATH)

except Exception as exception:
    print(f"Can not add project path to system path! Exiting!\nERROR: {exception}")
    raise SystemExit(1) from exception

from pathlib import Path
from src import join_sarif as sarops
from utils import helper_functions as utils

class TestJoinSarif(unittest.TestCase):
    """Unit tests for join_sarif module"""

    @classmethod
    def setUpClass(cls):
        dir = f"{f"{os.sep}".join(os.path.abspath(__file__).split(os.sep)[:-1])}{os.sep}data{os.sep}sarif{os.sep}join"
        cls.to_join_tjs_js, cls.to_join_tjs_gh, cls.to_join_twjs_jsw, cls.to_join_twjs_jsjd = itertools.tee(
            Path(dir).rglob("cppcheck__mnt_c_code_project_src_Type*.cpp.sarif"),
            4
        )

    def test_join_sarif(self):
        joined = sarops.join_sarif(self.to_join_tjs_js)
        hashes = utils.genhashes(self.to_join_tjs_gh)

        for run in joined.runs:
            run_hash = hash(json.dumps(run, sort_keys=True, ensure_ascii=True, default=lambda v: repr(v) + str(hash(v))))
            self.assertIn(run_hash, hashes)
    
    def test_write_joined_sarif(self):
        with tempfile.NamedTemporaryFile("w", delete_on_close=False) as written_file:
            written_file.close()
            sarops.write_joined_sarif(sarops.join_sarif(self.to_join_twjs_jsw), written_file.name)

            with tempfile.NamedTemporaryFile("w", delete_on_close=False) as joined_file:
                joined_file.close()
                json_sarif = jsonpickle.encode(sarops.join_sarif(self.to_join_twjs_jsjd))
                open(joined_file.name, "w").write(json_sarif)
                self.assertTrue(filecmp.cmp(written_file.name, joined_file.name, False))

if __name__ == "__main__":
    unittest.main()
