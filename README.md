# Blurple Parrot

An async library for receiving and responding to Discord interactions via HTTPS.

Unlike other Python bot libraries such as [discord.py](https://github.com/Rapptz/discord.py), this library works using Discord's interactions webhooks instead of the gateway. It can't recieve events like the gateway, which is why it's better for "parrot" bots, which are simply call and response.

## Example Usage

### Basic slash command and usage
```py
from bparrot import Client

client = Client(bot_token="TOKEN")

@client.slash_command(name="mycommand", description="My Slash Command")
async def my_slash_command(inter):
    return inter.create_response("Hello World!")

client.run()
```

### User and Message commands
```py
@client.user_command(name="Say Hello!")
async def my_user_command(inter, user):
    return inter.create_response(f"{user.mention}")

@client.message_command(name="Read the message")
async def my_message_command(inter, message)
    return inter.create_response(f"This message says: `{message.content}`")
```

### Response followups
```py
@client.slash_command(name="mycommand", description="My Slash Command")
async def my_slash_command(inter):
    return inter.create_response("Hello World!")

@my_slash_command.after_response
async def after_my_slash_command(inter):
    followup = await inter.followup("This is a followup message!")
    await inter.edit_initial_response("Now the original message says something different!")

    await asyncio.sleep(5)
    await inter.delete_initial_response()
    await followup.delete()
```

### Component events
```py
@client.button(custom_id="my_button")
async def button_click(inter):
    return inter.create_response("You clicked my button!")

@client.select(custom_id="my_select_menu")
async def menu_select(inter, values):
    items = ', '.join(values)
    return inter.create_response(f"You selected the following items: {items}")
```

## Deployment
The client is an aiohttp web application, meaning it can be run using alternative web servers rather than the client's `run()` method. The aiohttp application can be fetched using the `run_factory()` method, and can be used for one of the [deployment options](https://docs.aiohttp.org/en/stable/deployment.html#server-deployment).

## Suggested resources

 - [ngrok](https://ngrok.com/) - Expose an HTTPS port to the internet without having to port forward
 - [Server Deployment Docs](https://docs.aiohttp.org/en/stable/deployment.html#server-deployment) - aiohttp documentation for all server deployment options