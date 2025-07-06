from __future__ import annotations


def refreshsession(func):
    def wrapper(self, *args, **kwargs):
        if self.session is None:
            raise ValueError("No session")
        if self.session.expires_in < 30:
            self.refresh()
        return func(self, *args, **kwargs)

    return wrapper
