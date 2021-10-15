#!/usr/bin/env python3

import os
import tempfile

verbose = True
def system(cmd):
    if verbose:
        print("$ " + cmd)
    os.system(cmd)

# TODO put these in one place somewhere
targets = ['app.py', 'api.py', 'client.py', 'codec.py', 'crypto.py', 'dummy_server.py', 'errors.py', 'util.py', 'wordlist.py', 'static']

print("================================================================")
with tempfile.TemporaryDirectory() as tmpdir:
    print(tmpdir)

    for target in targets:
        system("cp -R {} {}".format(target, tmpdir))

    system(". venv/bin/activate && cd {} && flask run --port 65060".format(tmpdir))
print("================================================================")
