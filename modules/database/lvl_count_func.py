def new_lvl(lvl) -> int:
    if lvl != 0:
        return (5 * lvl**2 + 50 * lvl + 100) + new_lvl(lvl - 1)
    else:
        return 5 * lvl**2 + 50 * lvl + 100


def count_new_lvl(lvl, xp) -> int:
    nxp = new_lvl(lvl)
    if xp > nxp:
        return count_new_lvl(lvl + 1, xp)
    else:
        return lvl
