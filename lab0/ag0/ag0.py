#!/usr/bin/env python3

import os
import tempfile

verbose = True
def system(cmd):
    if verbose:
        print("$ " + cmd)
    os.system(cmd)

print("================================================================")
print("grading lab0")
with tempfile.TemporaryDirectory() as tmpdir:
    print(tmpdir)

    # test harness
    system("cp ag0/ag0_runner.py {}".format(tmpdir))

    # student submission
    system("cp client.py {}/client.py".format(tmpdir))

    # unchanged files
    system("cp api.py {}".format(tmpdir))
    system("cp errors.py {}".format(tmpdir))
    system("cp codec.py {}/codec.py".format(tmpdir))
    system("cp crypto.py {}/crypto.py".format(tmpdir))
    system("cp dummy_server.py {}/dummy_server.py".format(tmpdir))
    system("cp util.py {}/util.py".format(tmpdir))

    system("cd {} && ./ag0_runner.py".format(tmpdir))
print("================================================================")
