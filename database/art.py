import pygsheets
import xml.etree.ElementTree as ET
from .serversettings import getArtTable
from random import choice


def gcAuthorize():
    gc = pygsheets.authorize()
    return gc


def getArt(gc, session, guildid, title):

    x = getArtTable(session, guildid)
    if x is not None:
        spr = gc.open_by_key(x)
        sp = spr.worksheet_by_title(title)
        g = sp.get_values("A2", "B1001")

        gx = choice(g)
        gxi = g.index(gx) + 2

        updateArtInfo(gc, session, guildid, title, gxi)

        return gx[0]
    else:
        return None


def updateArtInfo(gc, session, guildid, title, num):

    x = getArtTable(session, guildid)
    if x is not None:
        spr = gc.open_by_key(x)
        sp = spr.worksheet_by_title(title)

        e = sp.get_value(f"B{num}")
        if e == "":
            e = 0
        else:
            e = int(e)
        sp.update_value(f"B{num}", e + 1)


def createArtTable(gc, guildid, mastertable):
    spr = gc.create(f"Art-{guildid}", template=mastertable)

    spr.share("", role="writer", type="anyone")
    sp = spr.sheet1
    sp.update_value("D1", f"{guildid}")

    return spr.id
