 # Blurple Parrot

 A library for reciving and responding to Discord interactions via HTTPS.

 ## Usage

```py
from bparrot import Client

client = Client("PUBLIC_KEY")

# Recieves and processes slash commands by name
@client.command(name="command")
async def my_command(inter):
    resp = inter.create_response(content="Hello World!")
    return resp

# Send followup messages and do other things after an interaction
# has been responded to
@my_command.after_response
async def after_my_command(inter):
    await inter.followup(content="This is a followup message")

# Values from options will be passed as keyword arguments
@client.command(name="args")
async def command_with_args(inter, arg1, arg2, arg3=None):
    return inter.create_response(content=f"{arg1}, {arg2}, and {arg3}")

client.run()
```