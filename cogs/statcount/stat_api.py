from nextcord import VoiceChannel, Member
from database.stat import addXp, addVoiceTime
import datetime


class StatVoiceChannel(object):
    """Simple voice object for stat"""

    def __init__(self, ch: VoiceChannel, session):
        self.id: int = ch.id
        self.channel = ch
        self.members = ch.members

        self.activemember = []
        for memb in self.members:
            self.addActiveUser(memb, session)

    def addActiveUser(self, member, session):
        self.addXp(session)
        if member.voice != None:
            if (
                member.voice.mute == False
                and member.voice.self_mute == False
                and member.voice.deaf == False
                and member.voice.self_deaf == False
            ):
                self.activemember.append(StatVoiceMember(member))

    def delActiveUser(self, member, session):
        self.addXp(session)
        for m in self.activemember:
            if m.member.id == member.id:
                self.activemember.remove(m)

    def addXp(self, session):
        users = len(self.activemember)
        t = datetime.datetime.now()
        if users != 0 and users != 1:
            for mem in self.activemember:
                xp = (
                    0.1
                    * users
                    * int((t - mem.voice_entered_at).total_seconds().__round__())
                )
                addXp(session, mem.member.guild.id, mem.member.id, xp)
                addVoiceTime(
                    session,
                    mem.member.guild.id,
                    mem.member.id,
                    int((t - mem.voice_entered_at).total_seconds().__round__()),
                )
                mem.resetVoiceConnectTime()


class StatVoiceMember(object):
    """Simple member object for stat"""

    def __init__(self, m: Member):
        self.id: int = m.id
        self.member: Member = m
        self.voice_entered_at = datetime.datetime.now()

    def resetVoiceConnectTime(self):
        self.voice_entered_at = datetime.datetime.now()
