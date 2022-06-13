from nextcord import VoiceChannel, Member
import datetime


class StatVoiceChannel(object):
    """Simple voice object for stat"""

    def __init__(self, ch: VoiceChannel, bot):
        self.id: int = ch.id
        self.bot = bot
        self.channel: VoiceChannel = ch
        self.members: list[Member] = ch.members
        self.multiplier: float = 1.0

        self.activemember: list[StatVoiceMember] = []
        for member in self.members:
            self.add_active_user(member)

    def add_active_user(self, member: Member):
        self.add_xp()
        if member.voice is not None:
            if (
                not member.voice.mute
                and not member.voice.self_mute
                and not member.voice.deaf
                and not member.voice.self_deaf
            ):
                self.activemember.append(StatVoiceMember(member, self.bot))

    def del_active_user(self, member: Member):
        self.add_xp()
        for m in self.activemember:
            if m.member.id == member.id:
                self.activemember.remove(m)

    def add_xp(self):
        users: int = len(self.activemember)
        t: datetime.datetime = datetime.datetime.now()
        if users != 0 and users != 1:
            for mem in self.activemember:
                xp = (
                    0.1
                    * users
                    * int((t - mem.voice_entered_at).total_seconds().__round__())
                    * self.multiplier
                )
                self.bot.database.add_xp(mem.member.id, mem.member.guild.id, xp)
                self.bot.database.add_voice_time(
                    mem.member.id,
                    mem.member.guild.id,
                    int((t - mem.voice_entered_at).total_seconds().__round__()),
                )
                mem.reset_voice_connect_time()


class StatVoiceMember(object):
    """Simple member object for stat"""

    def __init__(self, m: Member, bot):
        self.id: int = m.id
        self.bot = bot
        self.member: Member = m
        self.voice_entered_at: datetime.datetime = datetime.datetime.now()

    def reset_voice_connect_time(self):
        self.voice_entered_at = datetime.datetime.now()
