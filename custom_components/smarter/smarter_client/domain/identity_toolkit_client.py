import aiohttp

from .._consts import API_KEY


class IdentityToolkitClient:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def sign_in(self, email, password):
        request_body = {"email": email, "password": password, "returnSecureToken": True}

        async with self.session.post(
            # pylint: disable-next=line-too-long
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}",
            data=request_body,
        ) as resp:
            assert resp.status == 200
            return await resp.json()
