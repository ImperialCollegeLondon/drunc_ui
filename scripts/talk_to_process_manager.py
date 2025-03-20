"""Example script used to check communication with the process manager.

This is intended to be run within docker from the `app` service, i.e.:

```
docker compose exec app python scripts/talk_to_process_manager.py
```

and provides a basic proof of principle of communicating with the process manager via
gRPC.

The script starts a dummy session on the process manager and then retrieves the details
of all sessions and prints them to stdout.
"""

import asyncio
import random
import string

from drunc.process_manager.process_manager_driver import ProcessManagerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname
from druncschema.process_manager_pb2 import (
    ProcessInstance,
    ProcessInstanceList,
    ProcessQuery,
)


async def create_session(pmd: ProcessManagerDriver) -> list[ProcessInstance]:
    """Create a process manager session using the dummy_boot command."""
    return [
        item
        async for item in pmd.dummy_boot(
            user="root",
            session_name="".join(random.choices(string.ascii_lowercase, k=10)),
            n_processes=1,
            sleep=5,
            n_sleeps=4,
        )
    ]


async def get_session_info(pmd: ProcessManagerDriver) -> ProcessInstanceList:
    """Get info about all sessions from process manager."""
    query = ProcessQuery(names=[".*"])
    return await pmd.ps(query)


async def main() -> ProcessInstanceList:
    """Run the script."""
    token = create_dummy_token_from_uname()
    pmd = ProcessManagerDriver("drunc_pm:10054", token=token, aio_channel=True)

    await create_session(pmd)
    return await get_session_info(pmd)


if __name__ == "__main__":
    val = asyncio.run(main())
    print(val.data)
