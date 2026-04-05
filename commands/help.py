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
            name="⚙️  Custom Vault  👑 *(Owner managed)*",
            value=(
                "`$custom <service>` → Generate from a custom service\n"
                "`$genlist` → List all custom services\n"
                "👑 `$genadd <service> [channel:#ch] [role:@role] [filter:no]`\n"
                "👑 `$genedit <service> [channel:#ch] [role:@role] [filter:yes/no]`\n"
                "👑 `$genremove <service>` → Remove a custom service"
            ),
            inline=False
        )
        embed.add_field(
            name="🆓🚀  Vault Management  👑 *(Owner only)*",
            value=(
                "👑 `$freeadd <service> [filter:no]` → Add a service to the Free Vault\n"
                "👑 `$boostadd <service> [filter:no]` → Add a service to the Booster Vault\n"
                "Then restock with `$restock free/booster <service>` + attach `.txt`"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{lock}  Get G3N Access Role — Automatic!",
            value=(
                "Set `.gg/MetalDrops` as your **Custom Discord Status**.\n"
                "The role will be given **automatically** — no command needed! 🤖"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{star}  Vouch System",
            value=(
                "`$vouch @user <reason>` → Vouch for a member\n"
                "`$vouches @user` → View vouches for a member\n"
                "`$clearvouch @user` → Clear vouches *(admin)*"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{stock_e}  Stock Management  *(admin)*",
            value=(
                f"`$stock` → View stock\n"
                f"`$stocklive` → Pin a live auto-updating stock message in this channel\n"
                f"`$restock <vault> <service>` → Add stock *(attach .txt)*\n"
                f"┗ Vaults: `free` `booster` `premium` `custom`\n"
                f"`$removestock <service>` → Clear stock"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{mod}  Moderation  *(admin)*",
            value=(
                f"{hammer} `$ban @user` · {timer} `$tempban @user <min>` · {unlock} `$unban @user`\n"
                f"{bans_e} `$bans` · {stop} `$setbantime <min>` · `$pending`"
            ),
            inline=False
        )
        embed.add_field(
            name=f"{books}  Utilities",
            value=(
                f"`$checkroles` → Force re-check all members *(admin)*\n"
                f"`$setstatus <text>` → Change required status *(admin)*"
            ),
            inline=False
        )

        embed.set_footer(text=f"{BOT_NAME} • Command Guide")
        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
