from math import floor


def dmg_range(total):
    r = []
    for n in range(85, 101):
        r.append(floor(total * (n / 100)))
    print(r)
