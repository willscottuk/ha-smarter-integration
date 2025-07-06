from __future__ import annotations  # noqa: I001

from abc import ABCMeta
from abc import abstractmethod
from typing import Any, Self
from collections.abc import Callable
from pprint import pprint
from ...pyrebase.pyrebase import Stream

import datetime
from ..dict_util import delete_dict, patch_dict, put_dict
from . import smarter_client
import logging


_LOGGER = logging.getLogger(__name__)


class BaseEntity(metaclass=ABCMeta):
    identifier: str
    _data: dict
    client: smarter_client.SmarterClient
    is_stub: bool = True

    # Class methods
    @classmethod
    def from_id(cls, client: smarter_client.SmarterClient, identifier: str) -> Self:
        self = cls(client)
        self.client = client
        self.is_stub = True
        self.identifier = identifier

        return self

    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict, identifier: str | None = None) -> Self:
        self = cls(client)
        self._data = data or {}
        self.identifier = identifier
        self._init_data()

        return self

    def __init__(self, client: smarter_client.SmarterClient):
        self.client = client

    # Public methods
    def fetch(self):
        if self.is_stub:
            self._data = self._fetch()
            _LOGGER.info("Fetched network %o", self._data)
            self._init_data()
            self.is_stub = False

    # Private methods

    def _get_handler(self, event: dict):
        event_name: str = event.get("event")
        data: dict = event.get("data")

        if event_name == "patch":
            return patch_dict
        if event_name == "put" and data is None:
            return delete_dict
        if event_name == "put":
            return put_dict

        return lambda: None

    def _on_event(self, event):
        event_name: str = event.get("event")
        path: str = event.get("path")
        data: dict = event.get("data")

        if event_name not in ("put", "patch"):
            print(f"Unexpected event: {event_name}")
            pprint(event)
            return

        handler = self._get_handler(event)

        try:
            self._data = handler(self._data, path, data)
            self._init_data()
        except BaseException as e:
            print(f"Error handling update: {e}")
            pprint((event_name, path, data))

    @abstractmethod
    def _fetch(self) -> dict:
        pass

    @abstractmethod
    def _init_data(self) -> None:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}({self.identifier})"


# </BaseEntiy>


class Commands(BaseEntity, dict[str, "Command"]):
    device: Device

    # Class methods
    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict, device: Device) -> Self:
        self = Commands(client, device)
        self._data = data
        self._init_data()

        return self

    @classmethod
    def from_id(cls) -> Self:
        raise RuntimeError("Cannot create Commands from id")

    def __init__(self, client: smarter_client.SmarterClient, device: Device):
        super().__init__(client)
        self.device: Device = device

    # Private methods
    def _init_data(self) -> None:
        self._build_commands()

    def _build_commands(self):
        super().clear()
        super().update(
            {key: Command.from_data(self.client, value, key, self.device) for key, value in self._data.items()}
        )

    def _fetch(self) -> dict:  # pragma: no cover
        raise NotImplementedError()


# </Commands>


class CommandInstance(BaseEntity):
    command: Command
    device: Device
    value: dict[str, Any]
    state: str
    response: dict[str, Any]
    user_id: str

    # Class Methods
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)

    def _init_data(self) -> None:
        self.user_id = self._data.get("user_id")
        self.value = self._data.get("value")
        self.state = self._data.get("state")
        self.response = self._data.get("response")

    def _fetch(self) -> dict:  # pragma: no cover
        raise NotImplementedError()

    @classmethod
    def from_data(
        cls, client: smarter_client.SmarterClient, data: dict, identifier: str, command: Command, device: Device
    ) -> Self:
        self = CommandInstance(client)
        self.command = command
        self.identifier = identifier
        self._data = data
        self.device = device
        self._init_data()

        return self


# </CommandInstance>


class Command(BaseEntity):
    name: str
    device: Device
    instances: dict[str, CommandInstance] = {}
    example: dict
    # Class methods

    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict, name: str, device: Device) -> Self:
        self = Command(client)
        self._data = data
        self.identifier = name
        self.device = device
        self._init_data()

        return self

    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)

    def execute(self, user_id: str, value: any):
        return self.client.send_command(self.device.identifier, self.name, {"user_id": user_id, "value": value})

    def _init_data(self) -> None:
        self.name = self.identifier
        self.example = self._data.get("example")
        self.instances = {
            key: CommandInstance.from_data(self.client, value, key, self, self.device)
            for key, value in self._data.items()
            if key != "example"
        }

    def _fetch(self) -> dict:  # pragma: no cover
        raise NotImplementedError()


# </Command>


class Device(BaseEntity):
    commands: Commands
    settings: Settings | None
    status: Status | None
    _stream: Stream | None = None

    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)

    # Public methods
    def watch(self, callback: Callable[[dict], None]):
        if self._stream is not None:
            raise RuntimeError(
                "Already watching device. Call unwatch() first. Support for multiple callbacks may be implemented in a later version"  # noqa: E501
            )

        def on_data(event):
            self._on_event(event)
            callback(event)

        self._stream = self.client.watch_device_attribute(self.identifier, on_data)

    def unwatch(self):
        if self._stream is not None:
            try:
                self._stream.close()
            except Exception as e:
                print(f"Error closing stream: {e}")
                # TODO: log
                return e
            self._stream = None
        return None

    @property
    def is_watching(self):
        """Returns True if the device is being watched."""
        return self._stream is not None

    @property
    def is_stream_active(self):
        """Experimental: Returns True if the stream connection is active."""
        return self.is_watching and self._stream.sse.running

    # Private methods
    def _init_data(self):
        self.commands = Commands.from_data(self.client, self._data.get("commands"), self)

        self.settings = Settings.from_data(self.client, self._data.get("settings"))

        # Status(client: smarter_client.SmarterClient, data.get('status'))
        self.status = Status.from_data(self.client, self._data.get("status"), self)

    def _fetch(self) -> dict:
        return self.client.get_device(self.identifier)


# </Device>


class LoginSession:
    kind: str | None
    local_id: str
    email: str
    display_name: str
    id_token: str
    registered: bool
    refresh_token: str
    session_duration: int
    expires_at: datetime.datetime

    def __init__(self, data: dict[str, str]):
        self.kind = data.get("kind")
        self.local_id = data.get("localId")
        self.email = data.get("email")
        self.display_name = data.get("displayName")
        self.id_token = data.get("idToken")
        self.registered = data.get("registered")
        self.refresh_token = data.get("refreshToken")
        self.session_duration = int(data.get("expiresIn"))

        self.expires_at = self._get_expiration_datetime()

    def _get_expiration_datetime(self):
        return datetime.datetime.now() + datetime.timedelta(0, self.session_duration)

    def is_expired(self) -> bool:
        """Returns True if the session has expired."""
        return self.expires_at <= datetime.datetime.now()

    @property
    def expires_in(self) -> float:
        """Returns the number of seconds until the session expires."""
        return (self.expires_at - datetime.datetime.now()).total_seconds()

    def update(self, data: dict):
        self.id_token = data.get("idToken")
        self.refresh_token = data.get("refreshToken")
        self.local_id = data.get("userId")
        self.expires_at = self._get_expiration_datetime()


# </LoginSession>


class Network(BaseEntity):
    access_tokens_fcm: dict[str, str]
    associated_devices: list[Device]
    name: str
    owner: User

    def __init__(self, client):
        super().__init__(client)
        self.access_tokens_fcm = None
        self.associated_devices = None
        self.name = None
        self.owner = None

    def _fetch(self) -> dict:
        return self.client.get_network(self.identifier)

    def _init_data(self) -> None:
        try:
            self.access_tokens_fcm = self._data.get("access_tokens_fcm")
            self.associated_devices = [Device.from_id(self.client, key) for key in self._data.get("associated_devices")]

            self.name = self._data.get("name")
            self.owner = User.from_id(self.client, self._data.get("owner"))
        except Exception as ex:
            _LOGGER.error(ex)
            _LOGGER.info(self._data)
            raise ex


# </Network>


class Settings(BaseEntity):
    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)
        self.identifier = "/"
        self.network: Network
        self.network_ssid: str

    def _fetch(self) -> dict:
        return dict()

    def _init_data(self) -> None:
        self.network = Network.from_id(self.client, self._data.get("network"))
        self.network_ssid = self._data.get("network_ssid")


# </Settings>


class Status(BaseEntity, dict):
    device: Device

    # Class methods
    @classmethod
    def from_data(cls, client: smarter_client.SmarterClient, data: dict, device: Device) -> Self:
        self = super().from_data(client, data, f"{device.identifier}/status")
        self.device = device

        return self

    def __init__(self, client: smarter_client.SmarterClient):
        super().__init__(client)

    def _init_data(self) -> None:
        self.clear()
        self.update(self._data)

    def _fetch(self) -> dict:
        self.client.get_status(self.device.identifier)


# </Status>


class User(BaseEntity):
    email: str
    accepted: int
    first_name: str
    last_name: str
    location_accepted: int
    networks_index: dict[str, str]
    temperature_unit: int
    networks: dict[str, Network] = dict()

    def __init__(self, client):
        super().__init__(client)

    def _init_data(self) -> None:
        self.accepted: int = datetime.datetime.fromtimestamp(self._data.get("accepted") / 1000.0)
        self.email: str = self._data.get("email")
        self.first_name: str = self._data.get("first_name")
        self.last_name: str = self._data.get("last_name")
        self.location_accepted: int = self._data.get("locationAccepted")
        self.networks_index: dict = self._data.get("networks_index")
        self.temperature_unit: int = self._data.get("temperature_unit")

        self.networks = {value: Network.from_id(self.client, key) for key, value in self.networks_index.items()}

    def _fetch(self) -> dict:
        return self.client.get_user(self.identifier)
