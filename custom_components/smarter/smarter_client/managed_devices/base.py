import threading
from abc import ABCMeta
from collections.abc import Callable
from typing import Any

from ..domain.models import Device


class BaseDevice(metaclass=ABCMeta):
    device: Device
    friendly_name: str
    type: str
    user_id: str
    _status_subscriptions: set[Callable[[dict], None]] = set()
    refresh_timer: threading.Timer
    _logger = None

    def __init__(self, device: Device, friendly_name: str, device_type: str, user_id: str):
        device.fetch()
        self.device = device
        self.friendly_name = friendly_name
        self.user_id = user_id
        self.type = device_type

    def set_logger(self, logger):
        self._logger = logger

    def log(self, message):
        if self._logger is not None:
            self._logger.debug(message)

    @property
    def id(self):
        return self.device.identifier

    @property
    def model(self):
        return self.device.status.get("device_model")

    @property
    def firmware_version(self):
        return self.device.status.get("firmware_version")

    def _on_event(self, event):
        if "status" not in event.get("path", []):
            return

        for cb in self._status_subscriptions:
            cb(self.device.status)

    def send_command(self, command: str, value: Any):
        self.device.commands.get(command).execute(self.user_id, value)

    @property
    def status(self):
        return self.device.status

    @property
    def settings(self):
        return self.device.settings

    def _ensure_watching(self):
        if not self.device.is_watching:
            self.device.watch(self._on_event)
            refresh_after = self.device.client.session.expires_in * 0.95
            self.log(f"session to be refreshed in {refresh_after} seconds. duration: {
                     self.device.client.session.expires_in}, expiration time: {self.device.client.session.expires_at}")

            self.refresh_timer = threading.Timer(refresh_after, self.refresh_session)
            self.refresh_timer.start()

    def refresh_session(self):
        self.log("Refreshing session")
        self.device.unwatch()
        self.device.client.refresh()
        self._ensure_watching()

    def subscribe_status(self, handler: Callable[[dict], None] = lambda x: None):
        self._ensure_watching()
        self._status_subscriptions.add(handler)

    def unsubscribe_status(self, handler: Callable[[dict], None] = None):
        self._status_subscriptions.discard(handler)
        if len(self._status_subscriptions) == 0:
            self.refresh_timer.cancel()
            self.device.unwatch()

    def dispose(self):
        self.device.unwatch()

    def __str__(self):
        return f"Device ID: {self.id}, Device Name: {self.friendly_name} ({self.model}), Device Type: {self.type}"
