import asyncio
from datetime import datetime, timedelta

from discord.ext import commands as cmds
from discord import Embed, Color

class AmongUs(cmds.Cog):
	emojis = {
		0: "\u0030\ufe0f\u20e3",
		1: "\u0031\ufe0f\u20e3",
		2: "\u0032\ufe0f\u20e3",
		3: "\u0033\ufe0f\u20e3",
		4: "\u0034\ufe0f\u20e3",
		5: "\u0035\ufe0f\u20e3",
		6: "\u0036\ufe0f\u20e3",
		7: "\u0037\ufe0f\u20e3",
		8: "\u0038\ufe0f\u20e3",
		9: "\u0039\ufe0f\u20e3"
	}

	def __init__(self, bot):
		self.bot = bot
		self._message_id = None
		self._alert_id = None
		self._availabilities = dict()

	def _compose_timers(self) -> dict:
		"""Create a list of times remaining for each user in self._availabilities still available"""
		now = datetime.now()
		timers = dict()
		for uid, time in self._availabilities.items():
			diff = time - now
			if diff.days >= 0:
				timers[uid] = diff
		return timers

	def _create_embed(self) -> Embed:
		"""Create the embed to be sent/edited to display availabilities"""
		return Embed(
			title = "Game availability tracker",
			description = "Whenever you have a bit of time when you could be available to play a game, react below with the number of hours you'll be available for. If 5 or more people are available at the same time, I will @ you all and try to get a game going. If your availability changes, react again at any time to declare how many hours from the current time you're available (potentially zero).",
			color = Color.from_rgb(9, 21, 142)
		).add_field(
			name = "Currently available:",
			value = "\n".join(
				f"<@{uid}> is free for {time.seconds//3600}:{time.seconds%3600//60:0>2}"
				for uid, time in self._compose_timers().items()
			) or "Nobody"
		)

	@cmds.command(brief="Send initial message")
	@cmds.is_owner()
	async def init(self, ctx):
		"""Send the message used to track availabilities"""
		await ctx.message.delete()
		msg = await ctx.send(embed=self._create_embed())
		self._message_id = msg.id
		for emoji in self.emojis.values():
			await msg.add_reaction(emoji)

		# now periodically refresh the timers
		while True:
			await asyncio.sleep(60)
			await msg.edit(embed=self._create_embed())

	@cmds.Cog.listener()
	async def on_reaction_add(self, reaction, user):
		# only listen to reactions on the message we sent
		if self._message_id != reaction.message.id:
			return

		# ignore our own reactions
		if user.id == self.bot.user.id:
			return

		# update availability end time, and edit message to reflect this
		msg = reaction.message
		await msg.remove_reaction(reaction.emoji, user)
		value = next(k for k, v in self.emojis.items() if v == reaction.emoji)
		self._availabilities[user.id] = datetime.now() + timedelta(hours=value, seconds=59)
		await msg.edit(embed=self._create_embed())

		# if there's already an active alert, don't send another
		if self._alert_id is not None:
			return

		# if there's now five people available, ping them
		users = list(self._compose_timers().keys())
		if len(users) >= 5:
			embed = Embed(
				title = "That's five people!",
				description = "Hey " + ", ".join(f"<@{uid}>" for uid in users[:-1]) + f", and <@{users[-1]}>, you've all indicated that you're available for a game now! If that's still true, react with a \u2705. If nobody (besides me) reacts with an \u274c, and everyone *does* react with a \u2705, then join the voice channel and have fun!",
				color = Color.from_rgb(9, 21, 142)
			).set_footer(
				text = "This message will self destruct in 5 minutes."
			)
			alert = await msg.channel.send(embed=embed)
			self._alert_id = alert.id
			await alert.add_reaction("\u2705")
			await alert.add_reaction("\u274c")

			# wait five minutes, then delete the alert
			await asyncio.sleep(300)
			await alert.delete()
			self._alert_id = None
