import os

from discord.ext import commands as cmds

from cogs.amongus import AmongUs

gus = cmds.Bot(command_prefix = "!")
puck.add_cog(AmongUs())
gus.help_command.cog = gus.cogs["AmongUs"]

@gus.command(aliases=["stop", "exit"], hidden=True)
@cmds.is_owner()
async def quit(ctx):
	await gus.close()

# change the working directory to the bot root directory
os.chdir(os.path.dirname(__file__) or ".")

# get the token from the config file
try:
	with open("configs/token.txt", "r") as file:
		token = file.readline()
# if no token has been set, tell the user
except:
	print("Please create the file \"configs/token.txt\", and place the bot token within it.")
# if the token is gathered successfully, run the bot
else:
	gus.run(token)
