#!/usr/bin/env python3

import os
import tempfile

verbose = True
def system(cmd):
    if verbose:
        print("$ " + cmd)
    os.system(cmd)

print("================================================================")
print("grading lab4")
with tempfile.TemporaryDirectory() as tmpdir:
    print(tmpdir)

    # # test harness
    system("cp ag4/ag4_runner.py {}".format(tmpdir))

    # student submission
    system("cp photobox.py {}/photobox.py".format(tmpdir))

    # unchanged files
    system("cp clientdb.py {}".format(tmpdir))
    system("cp *.wasm {}".format(tmpdir))

    system("cd {} && ./ag4_runner.py".format(tmpdir))
print("================================================================")
