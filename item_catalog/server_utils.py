import os
from os.path import dirname, abspath

def full_path(file, *args):
    return os.path.join(
        abspath(dirname(file)),
        *args
    )