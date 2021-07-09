from datetime import datetime, timedelta

from discord.ext import commands as cmds
from discord import Embed, Color

class AmongUs(cmds.Cog):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._message_id = None
		self._availabilities = dict()

	def _compose_timers() -> dict:
		"""Create a list of times remaining for each user in self._availabilities"""
		now = datetime.now()
		timers = dict()
		for uid, time in self._availabilities.items():
			if (diff := time - now).days >= 0:
				timers[uid] = diff
		return timers

	def _create_embed() -> Embed:
		embed = Embed(
			title="Game availability tracker",
			description="Whenever you're available to play, react below with the number of hours you'll be available for. If 5 or more people are available at the same time, I will @ you all and try to get a game going. If your availability changes, react again at any time to declare how many hours from the current time you are now available (potentially zero)."
			)

		for uid, time in self._compose_timers().items():
			embed.add_field(
				name=f"<@{uid}>:",
				value=f"Free for {time.seconds//3600}:{time.seconds%3600//60}"
				)

		return embed

	@cmds.command()
	async def init(self, ctx):
		pass

	@cmds.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		# only listen to reactions on the message we sent
		if self._message_id != reaction.message.id:
			return
