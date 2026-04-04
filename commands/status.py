import discord
from discord.ext import commands
from discord.ext import tasks

BOT_NAME    = "Metal G3N"
STATUS_TEXT = ".gg/MetalDrops"


class StatusRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        cfg = self.bot.config.get('botConfig', {})
        self.gen_access_role_id = int(cfg.get('genAccessRoleId', 0))
        self.log_ch_id          = int(cfg.get('logsChannelId',   0))
        self.status_text        = cfg.get('statusText', STATUS_TEXT)
        self.check_loop.start()

    def cog_unload(self):
        self.check_loop.cancel()

    def emoji(self, name, default=''):
        return self.bot.config.get('emojis', {}).get(name, default)

    def get_custom_status(self, member) -> str:
        for activity in member.activities:
            if isinstance(activity, discord.CustomActivity):
                return activity.state or ""
        return ""

    def member_has_status(self, member) -> bool:
        return self.status_text in self.get_custom_status(member)

    async def log(self, message: str):
        if not self.log_ch_id:
            return
        ch = self.bot.get_channel(self.log_ch_id)
        if ch:
            try:
                await ch.send(message)
            except Exception as e:
                print(f"[{BOT_NAME}] Log error: {e}")

    async def sync_member(self, member, source="Auto"):
        if not self.gen_access_role_id:
            print(f"[{BOT_NAME}] genAccessRoleId is 0 — not configured!")
            return
        role = member.guild.get_role(self.gen_access_role_id)
        if not role:
            print(f"[{BOT_NAME}] Role ID {self.gen_access_role_id} not found in guild!")
            return

        has_status = self.member_has_status(member)
        has_role   = role in member.roles

        print(f"[{BOT_NAME}] [{source}] {member} | status='{self.get_custom_status(member)}' | has_status={has_status} | has_role={has_role}")

        try:
            if has_status and not has_role:
                await member.add_roles(role, reason=f"Metal G3N: {source}")
                await self.log(f"✅ **[{source}]** {member.mention} (`{member}`) → **G3N Access** granted.")
                print(f"[{BOT_NAME}] Granted G3N Access to {member}")
                try:
                    dm = discord.Embed(title="✅ G3N Access Granted!", color=0x2ecc71)
                    dm.description = (
                        f"Hey **{member.display_name}**! 👋\n\n"
                        f"Your status `{self.status_text}` was verified on **{member.guild.name}**.\n"
                        f"You now have the **G3N Access** role!\n\n"
                        f"Use `$free <service>` in the generator channel. Type `$help` for all services."
                    )
                    dm.set_footer(text=BOT_NAME)
                    await member.send(embed=dm)
                except discord.Forbidden:
                    pass

            elif not has_status and has_role:
                await member.remove_roles(role, reason=f"Metal G3N: {source}")
                await self.log(f"❌ **[{source}]** {member.mention} (`{member}`) → **G3N Access** removed.")
                print(f"[{BOT_NAME}] Removed G3N Access from {member}")
                try:
                    dm = discord.Embed(title="❌ G3N Access Removed", color=0xff0000)
                    dm.description = (
                        f"Hey **{member.display_name}**,\n\n"
                        f"Your **G3N Access** role was removed because `{self.status_text}` "
                        f"is no longer in your Custom Status.\n\n"
                        f"Set it back to get the role again!"
                    )
                    dm.set_footer(text=BOT_NAME)
                    await member.send(embed=dm)
                except discord.Forbidden:
                    pass

        except discord.Forbidden:
            print(f"[{BOT_NAME}] MISSING PERMISSIONS to manage roles for {member}! Check role hierarchy.")
        except Exception as e:
            print(f"[{BOT_NAME}] sync_member error for {member}: {e}")

    # ── on_presence_update ───────────────────────

    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if after.bot or not after.guild:
            return
        await self.sync_member(after, source="Live")

    # ── Loop every 2 min ─────────────────────────

    @tasks.loop(minutes=2)
    async def check_loop(self):
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    continue
                await self.sync_member(member, source="Auto")

    @check_loop.before_loop
    async def before_check_loop(self):
        await self.bot.wait_until_ready()
        for guild in self.bot.guilds:
            try:
                await guild.chunk()
                print(f"[{BOT_NAME}] Chunked {guild.member_count} members in '{guild.name}'")
            except Exception as e:
                print(f"[{BOT_NAME}] Chunk error: {e}")

    # ── $cstatus ─────────────────────────────────
    # KEY FIX: fetch_member() gets fresh presence data from Discord API

    @commands.command(name='cstatus')
    async def cstatus(self, ctx):
        """$cstatus — Verify your status and get the G3N Access role"""
        role    = ctx.guild.get_role(self.gen_access_role_id)
        warning = self.emoji('warning',     '⚠️')
        tick    = self.emoji('tick',        '✅')
        hearts  = self.emoji('hearts_blue', '💙')
        cross   = self.emoji('cross',       '❌')

        if not role:
            e = discord.Embed(title=f"{warning} Role Not Configured", color=0xff0000)
            e.description = (
                "The G3N Access role is not set up.\n"
                "Admin: set `genAccessRoleId` in `config.json`."
            )
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        # Fetch fresh member data so activities/presence are up to date
        try:
            member = await ctx.guild.fetch_member(ctx.author.id)
        except Exception:
            member = ctx.author

        has_status   = self.member_has_status(member)
        current_text = self.get_custom_status(member)

        print(f"[{BOT_NAME}] $cstatus — {member} | raw status: '{current_text}' | match: {has_status}")

        if has_status:
            if role not in member.roles:
                await member.add_roles(role, reason="Metal G3N: $cstatus manual verify")
                await self.log(f"✅ **[Manual]** {member.mention} verified via `$cstatus` → **G3N Access** granted.")
            e = discord.Embed(color=0x2ecc71)
            e.description = (
                f"{hearts} **Status Verified!**\n\n"
                f"{tick} `{self.status_text}` detected.\n"
                f"**G3N Access** role has been granted!\n\n"
                f"Keep this status to keep the role."
            )
        else:
            if role in member.roles:
                await member.remove_roles(role, reason="Metal G3N: $cstatus — status not found")
                await self.log(f"❌ **[Manual]** {member.mention} ran `$cstatus` without status → **G3N Access** removed.")
            e = discord.Embed(title=f"{cross} Verification Failed", color=0xff0000)
            e.description = (
                f"**To get the G3N Access role:**\n"
                f"1. Be **Online, Idle or Do Not Disturb** *(not Invisible)*\n"
                f"2. Set this **exact** text as your Custom Status:\n"
                f"```\n{self.status_text}\n```"
                f"3. Run `$cstatus` again.\n\n"
            )
            if current_text:
                e.description += f"*(Your current status: `{current_text}`)*"
            else:
                e.description += "*(No custom status detected — make sure you are not Invisible)*"

        e.set_footer(text=BOT_NAME)
        await ctx.reply(embed=e, mention_author=False)

    # ── $checkroles ──────────────────────────────

    @commands.command(name='checkroles')
    @commands.has_permissions(administrator=True)
    async def checkroles(self, ctx):
        """$checkroles — Force sync all members (admin)"""
        role = ctx.guild.get_role(self.gen_access_role_id)
        if not role:
            return await ctx.reply("❌ `genAccessRoleId` is not configured.", mention_author=False)

        msg = await ctx.reply("🔄 Checking all members...", mention_author=False)
        added = removed = 0

        for member in ctx.guild.members:
            if member.bot:
                continue
            has_status = self.member_has_status(member)
            try:
                if has_status and role not in member.roles:
                    await member.add_roles(role, reason="Metal G3N: $checkroles")
                    await self.log(f"✅ **[Force]** {member.mention} → **G3N Access** granted.")
                    added += 1
                elif not has_status and role in member.roles:
                    await member.remove_roles(role, reason="Metal G3N: $checkroles")
                    await self.log(f"❌ **[Force]** {member.mention} → **G3N Access** removed.")
                    removed += 1
            except Exception as e:
                print(f"[{BOT_NAME}] checkroles error for {member}: {e}")

        e = discord.Embed(title="✅ Check Complete", color=0x00ff00)
        e.description = f"**{added}** granted · **{removed}** removed"
        e.set_footer(text=BOT_NAME)
        await msg.edit(content=None, embed=e)

    # ── $setstatus ───────────────────────────────

    @commands.command(name='setstatus')
    @commands.has_permissions(administrator=True)
    async def setstatus(self, ctx, *, text: str = None):
        """$setstatus <text> — Change required status text (admin)"""
        cross = self.emoji('cross', '❌')
        if not text:
            e = discord.Embed(title=f"{cross} Incorrect Usage", color=0xff0000)
            e.description = "**Usage:** `$setstatus <status text>`"
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        self.status_text     = text
        self.bot.status_text = text
        e = discord.Embed(title="✅ Status Updated", color=0x00ff00)
        e.description = f"New required status:\n```\n{text}\n```"
        e.set_footer(text=BOT_NAME)
        await ctx.reply(embed=e, mention_author=False)


async def setup(bot):
    await bot.add_cog(StatusRole(bot))
