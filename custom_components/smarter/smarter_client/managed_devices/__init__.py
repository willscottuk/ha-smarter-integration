"""
Module containing wrappers for specific devices
"""

from collections.abc import Generator

from ..domain import Device, Network
from .base import BaseDevice
from .coffee_v2 import SmarterCoffeeV2
from .kettle_v3 import SmarterKettleV3


def load_from_network(network: Network, user_id: str) -> Generator[BaseDevice]:
    """
    Get devices from a given network
    """
    network.fetch()
    return (
        wrapper
        for wrapper in (get_device_wrapper(device, user_id) for device in network.associated_devices)
        if wrapper is not None
    )


def get_device_wrapper(device: Device, user_id: str) -> BaseDevice:
    """
    Get a device wrapper for a specific user by inferring the correct type
    from the device properties
    """
    device.fetch()
    model = device.status.get("device_model")
    managed: BaseDevice
    match model:
        case "SMKET01":
            managed = SmarterKettleV3.from_device(device, user_id)
            managed.subscribe_status()
            return managed
        case "SMCOF01":
            managed = SmarterCoffeeV2.from_device(device, user_id)
            managed.subscribe_status()
            return managed
        case _:
            raise ValueError(f"Unknown device model: {model}")
