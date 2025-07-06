"""Module contains implementation of Smarter Firebase API."""

from __future__ import annotations

from ...pyrebase import pyrebase

from .decorators.session import refreshsession

from .._consts import API_KEY
from .models import LoginSession


class SmarterClient:  # pragma: no cover
    """A client for interacting with the Smarter API."""

    session: LoginSession

    def __init__(self):
        config = {
            "apiKey": API_KEY,
            "authDomain": "smarter-live.firebaseapp.com",
            "databaseURL": "https://smarter-live.firebaseio.com",
            "projectId": "smarter-live",
            "storageBucket": "smarter-live.appspot.com",
            "messagingSenderId": "41919779740",
        }
        app = pyrebase.initialize_app(config)
        self.app = app
        self.token = None

    def sign_in(self, email, password) -> LoginSession:
        auth = self.app.auth()

        user = auth.sign_in_with_email_and_password(email, password)
        self.token = user.get("idToken")
        self.session = LoginSession(user)
        return self.session

    def refresh(self):
        auth = self.app.auth()
        refresh_response = auth.refresh(self.session.refresh_token)
        self.token = refresh_response.get("idToken")
        self.session.update(refresh_response)
        return self.session

    @refreshsession
    def get_user(self, user_id: str):
        database = self.app.database()
        return database.child("users").child(user_id).get(self.token).val()

    @refreshsession
    def get_network(self, network_id: str):
        database = self.app.database()
        return database.child("networks").child(network_id).get(self.token).val()

    @refreshsession
    def get_device(self, device_id: str):
        database = self.app.database()
        return database.child("devices").child(device_id).get(self.token).val()

    @refreshsession
    def get_status(self, device_id: str):
        database = self.app.database()
        return database.child("devices").child(device_id).child("status").get(self.token).val()

    def get_db(self):
        return self.app.database()

    @refreshsession
    def send_command(self, device_id: str, command: str, data: dict):
        database = self.app.database()

        return database.child("devices").child(device_id).child("commands").child(command).push(data, self.token)

    # TODO fix leaky abstraction
    @refreshsession
    def watch_device_attribute(self, device_id: str, callback):
        database = self.app.database()
        return database.child("devices").child(device_id).stream(callback, self.token)
