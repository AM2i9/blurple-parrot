from aiohttp import ClientSession

API_ENDPOINT = "https://discord.com/api/v9"

def build_inter_uri(inter):
    return f"{API_ENDPOINT}/webhooks/{inter.application_id}/{inter.token}"

async def interaction_followup(session: ClientSession, inter, resp):
    async with session.post(build_inter_uri(inter), json=resp) as r:
        return await r.json()