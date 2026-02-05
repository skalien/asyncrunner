import asyncio
import signal


class Runner:
    def __init__(self, cmd):
        self.cmd = cmd
        self.process = None
        self.stream = None
        self._stdout = []

    async def run(self):
        self.process = await asyncio.create_subprocess_exec(
            *self.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self.stream = self.process.stdout
        asyncio.create_task(self.stream_reader())

    async def stream_reader(self):
        async for line in self.stream:
            decoded = line.decode().strip()
            self._stdout.append(f"{decoded}")

    def stdout(self):
        return "\n".join(self._stdout)

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


async def main():
    cmd = "ping -c 5 google.com"
    cmd = cmd.split(" ")

    runner = Runner(cmd)
    await runner.run()

    for i in range(10):
        print("====")
        print(f"i={i}")
        print("====")
        print(runner.stdout())
        print()
        await asyncio.sleep(1)

        if i == 1:
            runner.pause()
        if i == 5:
            runner.resume()


if __name__ == "__main__":
    asyncio.run(main())
