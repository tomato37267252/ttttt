import discord
from discord.ext import commands

BOT_NAME = "Metal G3N"


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def emoji(self, name, default=''):
        return self.bot.config.get('emojis', {}).get(name, default)

    @commands.command(name='help')
    async def help_cmd(self, ctx):
        ice     = self.emoji('ice_cube',   '🧊')
        globe   = self.emoji('globe',      '🌐')
        gold    = self.emoji('gold',       '💰')
        booster = self.emoji('booster',    '🚀')
        paid    = self.emoji('paid',       '💎')
        stock_e = self.emoji('stock',      '📦')
        restock = self.emoji('restock',    '🔄')
        mod     = self.emoji('Moderation', '🛡️')
        hammer  = self.emoji('ban_hammer', '🔨')
        timer   = self.emoji('timer',      '⏱️')
        unlock  = self.emoji('unlock_s',   '🔓')
        stop    = self.emoji('stop_sign',  '🛑')
        books   = self.emoji('books',      '📚')
        search  = self.emoji('search',     '🔍')
        bans_e  = self.emoji('bans',       '🚫')
        notepad = self.emoji('notepad',    '📝')
        lock    = self.emoji('lock_key',   '🔒')
        star    = self.emoji('star',       '⭐')

        embed = discord.Embed(title=f"{ice} Metal G3N — Help Panel", color=0x001000)
        embed.description = "Use commands in the correct channel based on your access tier."

        embed.add_field(
            name=f"{gold}  Free Vault  {lock} *(G3N Access required)*",
            value=(
                "`$free minecraft` `$free steam` `$free crunchyroll`\n"
                "`$free mc_bedrock` `$free xbox` `$free cape`\n"
                "`$free xbox_codes` `$free ms_365`"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{booster}  Booster Vault",
            value=(
                "`$boost xbox_ultimate` `$boost xbox_pc`\n"
                "`$boost crunchyroll_mega` `$boost netflix_cookies`"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{paid}  Premium Vault",
            value="`$vip mcfa`",
            inline=False
        )
        embed.add_field(
            name=f"{lock}  Get G3N Access Role",
            value=(
                "Set `.gg/MetalDrops` as your **Custom Discord Status**\n"
                "then run `$cstatus` to get the role instantly!"
            ),
            inline=False
        )
        embed.add_field(
            name=f"⭐  Vouch System",
            value=(
                f"{star} `$vouch @user <reason>` → Vouch for a member\n"
                f"{star} `$vouches @user` → View all vouches for a member\n"
                f"{notepad} `$clearvouch @user` → Clear vouches *(admin)*"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{stock_e}  Stock & Management",
            value=(
                f"{stock_e} `$stock` → View all stock\n"
                f"{restock} `$restock <vault> <service>` → Add stock *(admin, attach .txt)*\n"
                f"{stop} `$removestock <service>` → Clear stock *(admin)*"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{mod}  Moderation",
            value=(
                f"{hammer} `$ban @user` · {timer} `$tempban @user <min>` · {unlock} `$unban @user`\n"
                f"{bans_e} `$bans` · {stop} `$setbantime <min>`"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{books}  Utilities",
            value=(
                f"{search} `$cstatus` → Verify status & get G3N Access\n"
                f"{notepad} `$checkroles` → Force re-check all members *(admin)*\n"
                f"{notepad} `$pending` → View pending vouches *(admin)*\n"
                f"{notepad} `$setstatus <text>` → Change required status *(admin)*"
            ),
            inline=False
        )

        embed.set_footer(text=f"{BOT_NAME} • Command Guide")
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
