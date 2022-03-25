import pygsheets
import xml.etree.ElementTree as ET
from .serversettings import getEmbTable


def gcAuthorize():
    gc = pygsheets.authorize()
    return gc


def getEmbed(gc, session, guildid):

    x = getEmbTable(session, guildid)
    if x != None:
        spr = gc.open_by_key(x)
        sp = spr.sheet1
        g = sp.get_values("O2", "V1000")

        return g
    else:
        return None


def updateEmbed(gc, session, guildid, messageid, num):

    x = getEmbTable(session, guildid)
    if x != None:
        spr = gc.open_by_key(x)
        sp = spr.sheet1

        sp.update_value(f"A{num}", f"{messageid}")
        sp.update_value(f"I{num}", False)


def createEmbedTable(gc, guildid, mastertable):
    spr = gc.create(f"Emb-{guildid}", template=mastertable)

    spr.share("", role="writer", type="anyone")
    sp = spr.sheet1
    sp.update_value("B1", f"{guildid}")

    return spr.id
