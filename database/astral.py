import pygsheets
import asyncio
import xml.etree.ElementTree as ET
from .serversettings import getEmbTable
from time import sleep
from datetime import datetime

# for processing
import numpy as np
from random import randint


def gcAuthorize():
    gc = pygsheets.authorize()
    return gc


def connectToSpreadsheet():
    return gcAuthorize()


def inputCastersName(playersList, spreadsheetId, service):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Настройки")

    for count, value in enumerate(playersList):
        sp.update_value(f"A{count+2}", value.name)


def getCastersName(spreadsheetId, service):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Настройки")
    return list(np.array(sp.get_values("A2", "A6")).ravel())


def getCastersSpreadsheetsLinks(spreadsheetId, service):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Настройки")
    return list(np.array(sp.get_values("D2", "D6")).ravel())


def sendCastersMove(service, spreadsheetId, playersList):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Основная")
    for count, value in enumerate(playersList):
        sp.update_value(f"C{count+2}", value.move)
        sp.update_value(f"D{count+2}", value.movedirection)


def getCastersMove(service, spreadsheetId, AstralPlayer):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title(AstralPlayer)
    try:
        x = sp.get_value("Q90")
        if x is None or x == "":
            raise Exception
    except:
        return getCastersMove(service, spreadsheetId, AstralPlayer)
    Move = x.split(", ")
    return Move


def getGameStepMessange(spreadsheetId, service, time):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Основная")
    try:
        x = sp.get_value("I6")
        if x is None or x == "":
            raise Exception
    except:
        if (datetime.now() - time).total_seconds() <= 15:
            return getGameStepMessange(spreadsheetId, service, time)
        else:
            return False
    Info_Array = ["", []]
    g = x.split("\n")
    l = g[0].split(" ")
    for i in l:
        if i != "":
            Info_Array[1].append(i)
    for i in range(4):
        g.pop(0)
    Info_Array[0] = ("\n").join(g)
    return Info_Array


def setArena(Arena, spreadsheetId, service):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Настройки")
    sp.update_value("I3", Arena)


def setDM(DM, spreadsheetId, service):
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Настройки")
    sp.update_value("K2", DM)


def getEffects(spreadsheetId, service, player):
    spr = service.open_by_key(spreadsheetId)
    main = spr.worksheet_by_title("Основная")
    try:
        gameRound = main.get_value("H2")
        if gameRound is None or gameRound == "":
            raise Exception
    except:
        return getEffects(spreadsheetId, service, player)

    playert = spr.worksheet_by_title(player)
    try:
        EffFst = playert.get_value("O3")
        if EffFst is None or EffFst == "":
            raise Exception
    except:
        return getEffects(spreadsheetId, service, player)

    try:
        eff = playert.get_value(f"U{2+(int(gameRound)-int(EffFst)+1)}")
        return eff if eff is not None else ""
    except Exception as el:
        return ""


def getCastersMP(spreadsheetId, service, player):
    players = getCastersName(spreadsheetId, service)
    for i in range(len(players)):
        if players[i] == player:
            num = i
    spr = service.open_by_key(spreadsheetId)
    sp = spr.worksheet_by_title("Основная")

    try:
        MPSheet = list(np.array(sp.get_values("G2", "G6")).ravel())
        if MPSheet is None or MPSheet == []:
            return getCastersMP(spreadsheetId, service, player)
    except:
        return getCastersMP(spreadsheetId, service, player)

    return MPSheet[num]


def createAstralTable(gc, guildid, mastertable):
    spr = gc.create(f"astral-{guildid}", template=mastertable)

    spr.share("", role="writer", type="anyone")
    sp = spr.worksheet_by_title("Инфо")
    sp.update_value("A2", f"{guildid}")

    return spr.id
