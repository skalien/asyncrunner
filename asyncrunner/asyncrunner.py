import asyncio
import signal


class Runner:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self._stream = None
        self._stdout = []
        self._last_idx = 0

    async def run(self, stderr: bool = True):
        self.process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT if stderr else asyncio.subprocess.PIPE,
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
        current_idx = len(self._stdout)

        if last_idx == current_idx:
            return None
        else:
            self._last_idx = current_idx
            return self.stdout(last_idx)

    async def wait_till_finish(self, polling_rate=0.25, timeout=10, on_poll=None):
        for _ in range(int(timeout / polling_rate)):
            await asyncio.sleep(polling_rate)
            await on_poll()
            if not self.is_running():
                return
        self.terminate()

    def returncode(self):
        return self.process.returncode


async def main():
    cmd = "ping -c 3 google.com"
    cmd = cmd.split(" ")

    runner = Runner(cmd)
    await runner.run()

    async def dots():
        print(".", end="", flush=True)

    await runner.wait_till_finish(on_poll=dots)

    print(runner.stdout())


if __name__ == "__main__":
    asyncio.run(main())
