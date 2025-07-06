from __future__ import annotations

from typing import Any

from ..domain import Device, SmarterClient
from .base import BaseDevice


class SmarterCoffeeV2(BaseDevice):
    @classmethod
    def from_id(cls, client: SmarterClient, device_id: str, user_id: str) -> SmarterCoffeeV2:
        device = Device.from_id(client, device_id)
        device.fetch()
        return cls(device, user_id)

    @classmethod
    def from_device(cls, device: Device, user_id: str) -> SmarterCoffeeV2:
        device.fetch()
        return cls(device, user_id)

    def __init__(self, device: Device, user_id: str):
        super().__init__(device, "Smarter Coffee V2", "coffee", user_id)

    def add_alarm(self, value: Any):
        self.send_command("add_alarm", value)

    def change_alarm(self, value: Any):
        self.send_command("change_alarm", value)

    def remove_alarm(self, value: Any):
        self.send_command("remove_alarm", value)

    def reset_settings(self, value: Any):
        self.send_command("reset_settings", value)

    def send_notification(self, value: Any):
        self.send_command("send_notification", value)

    def send_ping(self, value: Any):
        self.send_command("send_ping", value)

    def server_restart(self, value: Any):
        self.send_command("server_restart", value)

    def set_auto_coffee_strength(self, value: Any):
        self.send_command("set_auto_coffee_strength", value)

    def set_auto_grind_enable(self, value: Any):
        self.send_command("set_auto_grind_enable", value)

    def set_auto_keep_warm_time(self, value: Any):
        self.send_command("set_auto_keep_warm_time", value)

    def set_auto_number_of_cups(self, value: Any):
        self.send_command("set_auto_number_of_cups", value)

    def set_auto_preheat_time(self, value: Any):
        self.send_command("set_auto_preheat_time", value)

    def set_coffee_soak_percentage(self, value: Any):
        self.send_command("set_coffee_soak_percentage", value)

    def set_coffee_soak_percentage_medium(self, value: Any):
        self.send_command("set_coffee_soak_percentage_medium", value)

    def set_coffee_soak_percentage_strong(self, value: Any):
        self.send_command("set_coffee_soak_percentage_strong", value)

    def set_coffee_soak_percentage_weak(self, value: Any):
        self.send_command("set_coffee_soak_percentage_weak", value)

    def set_coffee_strength(self, value: Any):
        self.send_command("set_coffee_strength", value)

    def set_coffee_strength_medium(self, value: Any):
        self.send_command("set_coffee_strength_medium", value)

    def set_coffee_strength_strong(self, value: Any):
        self.send_command("set_coffee_strength_strong", value)

    def set_coffee_strength_weak(self, value: Any):
        self.send_command("set_coffee_strength_weak", value)

    def set_cup_mode_enable(self, value: Any):
        self.send_command("set_cup_mode_enable", value)

    def set_default_coffee_strength_selected(self, value: Any):
        self.send_command("set_default_coffee_strength_selected", value)

    def set_default_grind_enable(self, value: Any):
        self.send_command("set_default_grind_enable", value)

    def set_default_keep_warm_time(self, value: Any):
        self.send_command("set_default_keep_warm_time", value)

    def set_default_number_of_cups(self, value: Any):
        self.send_command("set_default_number_of_cups", value)

    def set_default_preheat_time(self, value: Any):
        self.send_command("set_default_preheat_time", value)

    def set_grind_enable(self, value: Any):
        self.send_command("set_grind_enable", value)

    def set_hotplate_enable(self, value: Any):
        self.send_command("set_hotplate_enable", value)

    def set_keep_warm(self, value: Any):
        self.send_command("set_keep_warm", value)

    def set_keep_warm_time(self, value: Any):
        self.send_command("set_keep_warm_time", value)

    def set_lcd_backlight_brightness(self, value: Any):
        self.send_command("set_lcd_backlight_brightness", value)

    def set_lcd_backlight_timeout(self, value: Any):
        self.send_command("set_lcd_backlight_timeout", value)

    def set_max_keep_warm_time(self, value: Any):
        self.send_command("set_max_keep_warm_time", value)

    def set_minimum_cups(self, value: Any):
        self.send_command("set_minimum_cups", value)

    def set_no_carafe_mode_enable(self, value: Any):
        self.send_command("set_no_carafe_mode_enable", value)

    def set_number_of_cups(self, value: Any):
        self.send_command("set_number_of_cups", value)

    def set_options(self, value: Any):
        self.send_command("set_options", value)

    def set_pause_and_brew_enable(self, value: Any):
        self.send_command("set_pause_and_brew_enable", value)

    def set_pause_and_serve_enable(self, value: Any):
        self.send_command("set_pause_and_serve_enable", value)

    def set_preheat_time(self, value: Any):
        self.send_command("set_preheat_time", value)

    def set_region(self, value: Any):
        self.send_command("set_region", value)

    def set_user(self, value: Any):
        self.send_command("set_user", value)

    def start_auto_brew(self, value: Any):
        self.send_command("start_auto_brew", value)

    def start_brew(self, value: Any):
        self.send_command("start_brew", value)

    def stats_update(self, value: Any):
        self.send_command("stats_update", value)

    def stop_brew(self, value: Any):
        self.send_command("stop_brew", value)

    def turn_off_wifi(self, value: Any):
        self.send_command("turn_off_wifi", value)
