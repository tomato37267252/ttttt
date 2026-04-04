import discord
from discord.ext import commands
import os
import aiohttp

BOT_NAME = "Metal G3N"

STOCK_PATHS = {
    "🆓 Free Vault": {
        "Minecraft":   "stock/Minecraft.txt",
        "Steam":       "stock/Steam.txt",
        "Crunchyroll": "stock/Crunchyroll.txt",
        "Mc_Bedrock":  "stock/Mc_Bedrock.txt",
        "Xbox":        "stock/Xbox.txt",
        "Cape":        "stock/Cape.txt",
        "Xbox_Codes":  "stock/XboxCodes.txt",
        "MS_365":      "stock/MS365.txt",
    },
    "🚀 Booster Vault": {
        "Xbox_Ultimate":    "bosststock/XboxUltimate.txt",
        "Xbox_PC":          "bosststock/XboxPC.txt",
        "Crunchyroll_Mega": "bosststock/CrunchyrollMega.txt",
        "Netflix_Cookies":  "bosststock/NetflixCookies.txt",
    },
    "💎 Premium Vault": {
        "Mcfa": "paidstock/Mcfa.txt",
    }
}


class InventoryCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def emoji(self, name, default='📦'):
        return self.bot.config.get('emojis', {}).get(name, default)

    def count(self, path):
        try:
            if not os.path.exists(path):
                return 0
            with open(path, 'r', encoding='utf-8') as f:
                return len([l for l in f.read().splitlines() if l.strip()])
        except Exception:
            return 0

    @commands.command(name='stock')
    async def stock(self, ctx):
        """$stock — View available stock"""
        warden = self.emoji('warden', '🛡️')
        embed = discord.Embed(
            title=f"{warden} Metal G3N — Inventory",
            color=0x001000
        )
        embed.description = "```Current stock status```"

        for vault, services in STOCK_PATHS.items():
            lines = ""
            for name, path in services.items():
                n   = self.count(path)
                bar = "🟢" if n > 10 else ("🟡" if n > 0 else "🔴")
                lines += f"{bar} `{name:<18}` → **{n}** units\n"
            embed.add_field(name=vault, value=lines or "Empty", inline=False)

        embed.set_footer(text=f"{BOT_NAME} • Stock System")
        await ctx.send(embed=embed)

    @commands.command(name='restock')
    @commands.has_permissions(administrator=True)
    async def restock(self, ctx, vault: str = None, service: str = None):
        """$restock <vault> <service> + attach .txt — Add stock (admin)"""
        tick  = self.emoji('tick',  '✅')
        cross = self.emoji('cross', '❌')

        if not vault or not service:
            e = discord.Embed(title=f"{cross} Incorrect Usage", color=0xff0000)
            e.description = (
                "**Usage:** `$restock <vault> <service>` + attach a `.txt` file\n\n"
                "**Vaults:** `free` | `booster` | `premium`"
            )
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        vault_map = {
            "free":    "🆓 Free Vault",
            "booster": "🚀 Booster Vault",
            "premium": "💎 Premium Vault",
        }
        vault_key = vault_map.get(vault.lower())
        if not vault_key:
            e = discord.Embed(title=f"{cross} Unknown Vault", color=0xff0000)
            e.description = "Valid vaults: `free`, `booster`, `premium`"
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        service_path = None
        for sname, spath in STOCK_PATHS[vault_key].items():
            if sname.lower() == service.lower().replace('-', '_'):
                service_path = spath
                break

        if not service_path:
            available = ', '.join(f'`{s}`' for s in STOCK_PATHS[vault_key])
            e = discord.Embed(title=f"{cross} Unknown Service", color=0xff0000)
            e.description = f"Available in **{vault_key}**: {available}"
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        if not ctx.message.attachments:
            e = discord.Embed(title=f"{cross} Missing File", color=0xff0000)
            e.description = "Please attach a `.txt` file containing accounts (one per line)."
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        att = ctx.message.attachments[0]
        if not att.filename.endswith('.txt'):
            e = discord.Embed(title=f"{cross} Wrong Format", color=0xff0000)
            e.description = "The file must be a `.txt` file."
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        async with aiohttp.ClientSession() as session:
            async with session.get(att.url) as r:
                text = await r.text(encoding='utf-8', errors='ignore')

        lines = [l.strip() for l in text.splitlines() if l.strip()]
        os.makedirs(os.path.dirname(service_path), exist_ok=True)
        with open(service_path, 'a', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')

        restock_ch = int(self.bot.config.get('botConfig', {}).get('restockChannelId', 0))
        if restock_ch:
            ch = self.bot.get_channel(restock_ch)
            if ch:
                ann = discord.Embed(
                    title="🔄 Restock Alert!",
                    description=f"**{service}** has been restocked with **{len(lines)}** entries!",
                    color=0x00ff00
                )
                ann.set_footer(text=BOT_NAME)
                await ch.send(embed=ann)

        e = discord.Embed(title=f"{tick} Restock Successful!", color=0x00ff00)
        e.description = f"**{len(lines)}** entry/entries added to `{service}` in **{vault_key}**."
        e.set_footer(text=BOT_NAME)
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(name='removestock')
    @commands.has_permissions(administrator=True)
    async def removestock(self, ctx, service: str = None):
        """$removestock <service|all> — Clear stock (admin)"""
        tick  = self.emoji('tick',  '✅')
        cross = self.emoji('cross', '❌')

        if not service:
            e = discord.Embed(title=f"{cross} Incorrect Usage", color=0xff0000)
            e.description = "**Usage:** `$removestock <service>` or `$removestock all`"
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        paths = []
        if service.lower() == 'all':
            for vs in STOCK_PATHS.values():
                paths.extend(vs.values())
        else:
            for vs in STOCK_PATHS.values():
                for sname, spath in vs.items():
                    if sname.lower() == service.lower().replace('-', '_'):
                        paths.append(spath)

        if not paths:
            e = discord.Embed(title=f"{cross} Not Found", color=0xff0000)
            e.description = f"No stock file found for `{service}`."
            e.set_footer(text=BOT_NAME)
            return await ctx.reply(embed=e, mention_author=False)

        for p in paths:
            if os.path.exists(p):
                with open(p, 'w', encoding='utf-8') as f:
                    f.truncate(0)

        e = discord.Embed(title=f"{tick} Stock Cleared", color=0x00ff00)
        e.description = f"**{len(paths)}** stock file(s) cleared."
        e.set_footer(text=BOT_NAME)
        await ctx.reply(embed=e, mention_author=False)


async def setup(bot):
    await bot.add_cog(InventoryCommands(bot))
