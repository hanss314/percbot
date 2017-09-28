import sys
import asyncio
import subprocess
import discord
import inspect

from discord.ext import commands

from percbot.util import checks
from percbot.util.categories import category
from percbot.util.converters import UserList
from percbot.util.formatters import say_list

class Core():
    async def __local_check(self, ctx):
        return checks.is_owner(ctx)    
    
    @category('Bot')
    @commands.command()
    async def blacklist(self, ctx, *users: UserList):
        '''Blacklist users'''
        users = [m for s in users for m in s]
        users = list(set(users))
        
        if not users:
            users = []
            for id in ctx.bot.blacklist:
                user = ctx.bot.get_user(id)
                if user: users.append(user.name)
            if users: await ctx.send(', '.join(users))
            else: await ctx.send('No one is blacklisted')
        else:
            success = []
            for user in users:
                if user.id not in ctx.bot.blacklist and user.id not in ctx.bot.config['owners']:
                    ctx.bot.blacklist.append(user.id)
                    success.append(user.name)

            await ctx.send('Blacklisted {}.'.format(say_list(success)))
        
    @category('Bot')
    @commands.command()
    async def whitelist(self, ctx, *users: UserList):   
        '''Unblacklist users'''
        users = [m for s in users for m in s]
        users = list(set(users))
        
        success = []
        for user in users:
            if user.id in ctx.bot.blacklist:
                ctx.bot.blacklist.remove(user.id)
                success.append(user.name)

        await ctx.send('Whitelisted {}.'.format(say_list(success)))
    
    @category('Bot')
    @commands.command()
    async def exception(self, ctx):
        '''Raise an exception'''
        raise Exception('WOOOOOO! EXCEPTIONS!!!!!!')
    
    @category('Bot')
    @commands.command(aliases=['kill'])
    async def die(self, ctx):
        '''Shutdown the bot'''
        await ctx.bot.logout()
        
    @category('Bot')
    @commands.command()
    async def say(self, ctx, channel: int, *, message):
        '''Say something'''
        c = ctx.bot.get_channel(channel)
        if not c:
            c = ctx.bot.get_user(channel)
        if c: await c.send(message)
        else: await ctx.send('Could not find channel')
    
    @category('Bot')
    @commands.group(invoke_without_command=True)
    async def reload(self, ctx, *, cog: str):
        '''Reloads an extension'''
        try:
            ctx.bot.unload_extension(cog)
            ctx.bot.load_extension(cog)
        except Exception as e:
            await ctx.send('Failed to load: `{}`\n```py\n{}\n```'.format(cog, e))
        else:
            await ctx.send('\N{OK HAND SIGN} Reloaded cog {} successfully'.format(cog))

    @category('Bot')
    @reload.command(name='all')
    async def reload_all(self, ctx):
        '''Reloads all extensions'''
        import importlib
        modules = ['percbot.util.'+d for d in dir(sys.modules['percbot.util']) if not d.startswith('_')]
        for module in modules:
            importlib.reload(sys.modules[module])
        for extension in ctx.bot.extensions.copy():
            ctx.bot.unload_extension(extension)
            try:
                ctx.bot.load_extension(extension)
            except Exception as e:
                await ctx.send('Failed to load `{}`:\n```py\n{}\n```'.format(extension, e))
                return

        await ctx.send('\N{OK HAND SIGN} Reloaded {} cogs successfully'.format(len(ctx.bot.extensions)))
        
    @category('Bot')
    @commands.command()
    async def update(self, ctx):
        '''Pulls from git'''
        async with ctx.channel.typing():
            if sys.platform == 'win32':
                subprocess.run('git stash', shell=True)
                process = subprocess.run('git pull', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.stdout, process.stderr
            else:
                await asyncio.create_subprocess_exec('git', 'stash')
                process = await asyncio.create_subprocess_exec('git', 'pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = await process.communicate()

            stdout = stdout.decode().splitlines()
            stdout = '\n'.join('+ ' + i for i in stdout)
            stderr = stderr.decode().splitlines()
            stderr = '\n'.join('- ' + i for i in stderr)

        await ctx.send('```diff\n{}\n{}```'.format(stdout.replace('```', '`\u200b`\u200b`'), stderr.replace('```', '`\u200b`\u200b`')))
            

    @category('Bot')
    @commands.command(aliases=['eval'])
    async def evaluate(self, ctx, *, code:str):
        '''Run some code.'''
        embed = None
        async with ctx.channel.typing():
            result = None
            env = {
                'channel': ctx.channel,
                'author': ctx.author,
                'bot': ctx.bot,
                'message': ctx.message,
                'channel': ctx.channel,
                'inventories': ctx.bot.inventories,
                'items': ctx.bot.items,
                'people': ctx.bot.people,
                'ctx': ctx,
            }
            env.update(globals())

            try:
                result = eval(code, env)
                if inspect.isawaitable(result):
                    result = await result

                colour = 0x00FF00
            except Exception as e:
                result = type(e).__name__ + ': ' + str(e)
                colour = 0xFF0000

            embed = discord.Embed(colour=colour, title=code, description='```py\n{}```'.format(result))
            embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        try:
            await ctx.send(embed=embed)
        except discord.errors.Forbidden:
            pass
        
def setup(bot):
    @bot.event
    async def on_ready():
        game = discord.Game(name='{}help'.format(bot.command_prefix))
        asyncio.ensure_future(bot.change_presence(game=game))
    bot.add_cog(Core())
