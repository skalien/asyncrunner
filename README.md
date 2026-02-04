# AsyncRunner

AsyncRunner is an asynchronous terminal command launcher from a python script. You can launch any program in the background and have its stdout read whenever you want for however long you want. You can have it run the background continuously and then launch another task simultaneously. You can monitor the stdouts of many programs at the same time and take decisions like pause / resume any process in any order.

## Installation

```
git clone <this repo>
cd asyncrunner
pip install -e .
```

## Usage

```
import asyncio
from asyncrunner import Runner


async def main():
    runner = Runner("ping -c 5 google.com".split(" "))
    await runner.run()

    for _ in range(10):
        print(runner.stdout())  # stdout and stderr is merged
        await asyncio.sleep(1)  # Do other stuff

    await runner.terminate()


if __name__ == "__main__":
    asyncio.run(main())
```

## Features

```
runner.pause()          # pauses the running process

runner.resume()         # resumes a paused process

runner.terminate()      # terminates the process, returns returncode
```

## License

MIT
