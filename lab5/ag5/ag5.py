#!/usr/bin/env python3

import os
import tempfile

verbose = True
def system(cmd):
    if verbose:
        print("$ " + cmd)
    os.system(cmd)

print("================================================================")
print("grading lab5")
with tempfile.TemporaryDirectory() as tmpdir:
    print(tmpdir)

    # # test harness
    system("cp ag5/ag5_runner.py {}".format(tmpdir))

    # student submission
    system("cp attacker.py {}/attacker.py".format(tmpdir))

    # unchanged files
    system("cp api.py {}".format(tmpdir))
    system("cp secure_server.py {}".format(tmpdir))

    system("cd {} && ./ag5_runner.py".format(tmpdir))
print("================================================================")
