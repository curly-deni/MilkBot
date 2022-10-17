import sys
import asyncio


class AstralScriptRunner:
    def __init__(self, cmd, cwd, script_id):
        self.cmd = cmd
        self.cwd = cwd
        self.script_id = script_id

    async def start_game(self):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["astral_script.py", "-r", "-i", self.script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        stdout, _ = await self.process.communicate(b"\n")
        return (stdout.decode("utf-8"))[:-1]

    async def end_game(self):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["astral_script.py", "-s", "-i", self.script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        stdout, _ = await self.process.communicate(b"\n")
        return (stdout.decode("utf-8"))[:-1]

    async def next_round(self):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["astral_script.py", "-n", "-i", self.script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        stdout, _ = await self.process.communicate(b"\n")
        return (stdout.decode("utf-8"))[:-1]

    async def deploy(self, script_id):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["astral_script.py", "-d", "-i", script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        return await self.process.communicate(b"\n")

    async def visit(self, link):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["browser_script.py", "-l", link],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        stdout, _ = await self.process.communicate(b"\n")
        return (stdout.decode("utf-8"))[:-1]

    async def set_gcp(self, script_id: str, gcp: int, path: str):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["browser_script.py", "-i", script_id, "-g", str(gcp), "-p", path],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        stdout, _ = await self.process.communicate(b"\n")
        return (stdout.decode("utf-8"))[:-1]
