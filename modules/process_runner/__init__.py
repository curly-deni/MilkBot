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
            *["run.py", "-i", self.script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        return await self.process.communicate(b"\n")

    async def end_game(self):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["stop.py", "-i", self.script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        return await self.process.communicate(b"\n")

    async def next_round(self):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["next.py", "-i", self.script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        return await self.process.communicate(b"\n")

    async def deploy(self, script_id):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["deploy.py", "-i", script_id],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        return await self.process.communicate(b"\n")

    async def visit(self, link):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["fc.py", "-l", link],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        return await self.process.communicate(b"\n")

    async def set_gcp(self, script_id: str, gcp: int, path: str):
        self.process = await asyncio.create_subprocess_exec(
            self.cmd,
            *["firefox_control.py", "-i", script_id, "-g", str(gcp), "-p", path],
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=sys.stderr,  # asyncio.subprocess.DEVNULL,
            cwd=self.cwd,
        )
        return await self.process.communicate(b"\n")
