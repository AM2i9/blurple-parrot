from aiohttp import ClientSession

API_ENDPOINT = "https://discord.com/api/v9"


def build_inter_uri(inter):
    return f"{API_ENDPOINT}/webhooks/{inter.application_id}/{inter.token}"


async def interaction_followup(session: ClientSession, inter, data):
    async with session.post(build_inter_uri(inter), json=data) as r:
        return await r.json()


async def interaction_edit_followup(session: ClientSession, inter, id, data):
    async with session.patch(f"{build_inter_uri(inter)}/messages/{id}", json=data) as r:
        return await r.json()


async def interaction_delete_followup(session: ClientSession, inter, id):
    async with session.delete(f"{build_inter_uri(inter)}/messages/{id}") as r:
        if r.status != 204:
            raise Exception(f"Failed to delete response: {await r.text()}")


async def interaction_edit_response(session: ClientSession, inter, data):
    async with session.patch(
        f"{build_inter_uri(inter)}/messages/@original", json=data
    ) as r:
        return await r.json()


async def interaction_delete_response(session: ClientSession, inter):
    async with session.delete(f"{build_inter_uri(inter)}/messages/@original") as r:
        if r.status != 204:
            raise Exception(f"Failed to delete response: {await r.text()}")
