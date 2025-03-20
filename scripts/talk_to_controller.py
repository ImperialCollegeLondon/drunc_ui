"""Example script used to check communication with the controller.

This is intended to be run within docker from the `app` service, i.e.:

```
docker compose exec app python scripts/talk_to_controller.py
```

and provides a basic proof of principle of communicating with the controller via
gRPC.
"""

from drunc.connectivity_service.client import ConnectivityServiceClient
from drunc.controller.controller_driver import ControllerDriver
from drunc.utils.shell_utils import create_dummy_token_from_uname

if __name__ == "__main__":
    # find where the root controller is running via the connectivity service
    csc = ConnectivityServiceClient("local-1x1-config", "drunc_pm:5000")
    uris = csc.resolve("root-controller_control", "RunControlMessage")
    uri = uris[0]["uri"].removeprefix("grpc://")

    # connect to and query the root controller
    token = create_dummy_token_from_uname()
    controller = ControllerDriver(uri, token=token)
    val = controller.status()
    print(val)
