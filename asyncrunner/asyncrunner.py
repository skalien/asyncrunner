import asyncio
import signal


class Runner:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self._stream = None
        self._stdout = []
        self._last_idx = 0

    async def run(self):
        self.process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self._stream = self.process.stdout
        asyncio.create_task(self.stream_reader())

    async def stream_reader(self):
        async for line in self._stream:
            decoded = line.decode().strip()
            self._stdout.append(f"{decoded}")

    def stdout(self, idx=0):
        return "\n".join(self._stdout[idx:])

    async def terminate(self):
        try:
            self.process.kill()
            await self.process.wait()
            return self.process.returncode
        except ProcessLookupError:
            pass

    def pause(self):
        self.process.send_signal(signal.SIGSTOP)

    def resume(self):
        self.process.send_signal(signal.SIGCONT)

    def is_running(self):
        return self.process.returncode is None

    def last_stdout(self):
        last_idx = self._last_idx
        self._last_idx = len(self._stdout)
        return self.stdout(last_idx)


async def main():
    cmd = "ping -c 5 google.com"
    cmd = cmd.split(" ")

    runner = Runner(cmd)
    await runner.run()

    while runner.is_running():
        print(runner.last_stdout())
        await asyncio.sleep(1)
    print(runner.last_stdout())


if __name__ == "__main__":
    asyncio.run(main())
