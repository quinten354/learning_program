import os

# get mod of dir or file
def get_permissions(path):
    x = 1
    w = 2
    r = 4
    x_permis = os.access(path, x)
    w_permis = os.access(path, w)
    r_permis = os.access(path, r)
    mod = 0
    if x_permis:
        mod = mod + x
    if w_permis:
        mod = mod + w
    if r_permis:
        mod = mod + r
    return mod

