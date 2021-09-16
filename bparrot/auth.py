import asyncio
import aiohttp

from bparrot.http import API_ENDPOINT


def get_application_token(client_id: int, client_secret: str, scopes: list = []) -> str:
    """
    Get a Bearer token for the application owner via your application's OAuth2
    credentials.

    By default, this function uses the `applications.commands` scope for
    accessing your application commands. Aditional scopes can be added using
    the `scopes` parameter

    OAuth2 credentials are possible more dangerous to have exposed  than
    a normal bot token, so take Discord's warning as said in their docs:
    https://discord.com/developers/docs/topics/oauth2#client-credentials-grant
    """

    scopes = set(scopes)
    scopes.add("applications.commands")

    data = aiohttp.FormData(
        {
            "grant_type": "client_credentials",
            "scope": " ".join(scopes),
        }
    )

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    auth = aiohttp.BasicAuth(str(client_id), client_secret)

    async def _make_request():
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{API_ENDPOINT}/oauth2/token",
                data=data,
                headers=headers,
                auth=auth,
            ) as resp:
                return await resp.json()

    _loop = asyncio.get_event_loop()
    _resp_data = _loop.run_until_complete(_make_request())

    return _resp_data["access_token"]
