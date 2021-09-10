from bparrot.application_commands import SlashOption
from bparrot import Client
from bparrot import components
from bparrot.client import slash_command, button
from bparrot.components import Button, ActionRow, SelectMenu, SelectOption

client = Client(
    application_id=852260416582451270,
    bot_token="ODUyMjYwNDE2NTgyNDUxMjcw.YMEPXQ.RavNhqsQAqhSAKx6Umc6_TPMQo0",
    public_key="f19c084216b9ac9137ee2518c461fd673542f49615dae7be3a3efb8aab0fa2eb"
)

@slash_command(name="command", description="This is a test command")
async def my_command(inter):
    select = SelectMenu(
        custom_id="test-select",
        options=[
            SelectOption(label="Test option #1", value="0"),
            SelectOption(label="Test option #2", value="1"),
            SelectOption(label="Test option #3", value="2"),
        ],
        placeholder="Select an option!"
    )
    return inter.create_response("Hello World!", components=[ActionRow([select])])

@client.user_command(name="User Info")
async def user_info(inter):
    return inter.create_response("User Info Command!")

@button(custom_id="test_button")
async def test_button_click(inter):
    return inter.create_response("Button Clicked!")

@client.select(custom_id="test-select")
async def test_select(inter, values):
    return inter.create_response(f"Selected option {values[0]}")

@my_command.after_response
async def after_my_command(inter):
    await inter.followup("Test Followup!")

@test_button_click.after_response
async def after_button_click(inter):
    await inter.followup("Button Clicked Followup!")

client.add_listener(my_command)
client.add_listener(test_button_click)
client.run()