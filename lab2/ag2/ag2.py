#!/usr/bin/env python3

import os
import tempfile

verbose = True
def system(cmd):
    if verbose:
        print("$ " + cmd)
    os.system(cmd)

print("================================================================")
print("grading lab2")
with tempfile.TemporaryDirectory() as tmpdir:
    print(tmpdir)

    # # test harness
    system("cp ag2/ag2_runner.py {}".format(tmpdir))

    # student submission
    system("cp client.py {}/client.py".format(tmpdir))

    # unchanged files
    system("cp api.py {}".format(tmpdir))
    system("cp errors.py {}".format(tmpdir))
    system("cp util.py {}".format(tmpdir))
    system("cp policy.py {}".format(tmpdir))

    # # special autograder files
    system("cp ag2/ag2_codec.py {}/codec.py".format(tmpdir))
    system("cp ag2/ag2_crypto.py {}/crypto.py".format(tmpdir))
    system("cp ag2/ag2_dummy_server.py {}/dummy_server.py".format(tmpdir))

    system("cd {} && ./ag2_runner.py".format(tmpdir))
print("================================================================")
