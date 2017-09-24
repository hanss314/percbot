import datetime
from discord.ext import commands
import discord

from percbot.util.categories import category


class Misc():
    @category('info')
    @commands.command()
    async def help(self, ctx, *args):
        '''This help message :D'''
        cmds = {i for i in ctx.bot.all_commands.values()}

        if len(args) == 0:
            d = ''#'**PercBot help:**'

            cats = {}
            for cmd in cmds:
                if not hasattr(cmd, 'category'):
                    cmd.category = 'Misc'
                if cmd.category not in cats:
                    cats[cmd.category] = []
                cats[cmd.category].append(cmd)

            d += '\n**Categories:**\n'
            for cat in cats:
                d += '**`{}`**\n'.format(cat)
            d += '\nUse `{}help <category>` to list commands in a category'.format(ctx.prefix)
            d += '\nUse `{}help <command>` to get indepth help for a command\n'.format(ctx.prefix)
        elif len(args) == 1:
            cats = {}
            for cmd in cmds:
                if not hasattr(cmd, 'category'):
                    cmd.category = 'Misc'
                if cmd.category not in cats:
                    cats[cmd.category] = []
                cats[cmd.category].append(cmd)
            if args[0].title() in cats:
                d = 'Commands in caterogy **`{}`**:\n'.format(args[0])
                for cmd in sorted(cats[args[0].title()], key=lambda x:x.name):
                    d += '\n  `{}{}`'.format(ctx.prefix, cmd.name)

                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    if brief is not None:
                        d += ' - {}'.format(brief)
                d += '\n'
            else:
                if args[0] not in ctx.bot.all_commands:
                    d = 'Command not found.'
                else:
                    cmd = ctx.bot.all_commands[args[0]]
                    d = 'Help for command `{}`:\n'.format(cmd.name)
                    d += '\n**Usage:**\n'

                    if type(cmd) != commands.core.Group:
                        params = list(cmd.clean_params.items())
                        p_str = ''
                        for p in params:
                            if p[1].default == p[1].empty:
                                p_str += ' <{}>'.format(p[0])
                            else:
                                p_str += ' [{}]'.format(p[0])
                        d += '`{}{}{}`\n'.format(ctx.prefix, cmd.name, p_str)
                    else:
                        d += '`{}{} '.format(ctx.prefix, cmd.name)
                        if cmd.invoke_without_command:
                            d += '['
                        else:
                            d += '<'
                        d += '|'.join(cmd.all_commands.keys())
                        if cmd.invoke_without_command:
                            d += ']`\n'
                        else:
                            d += '>`\n'
                    
                    d += '\n**Description:**\n'
                    d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

                    if cmd.checks:
                        d += '\n**Checks:**'
                        for check in cmd.checks:
                            d += '\n{}'.format(check.__qualname__.split('.')[0])
                        d += '\n'

                    if cmd.aliases:
                        d += '\n**Aliases:**'
                        for alias in cmd.aliases:
                            d += '\n`{}{}`'.format(ctx.prefix, alias)

                        d += '\n'
        else:
            d = ''
            cmd = ctx.bot
            cmd_name = ''
            for i in args:
                i = i.replace('@', '@\u200b')
                if hasattr(cmd, 'all_commands') and i in cmd.all_commands:
                    cmd = cmd.all_commands[i]
                    cmd_name += cmd.name + ' '
                else:
                    if cmd == ctx.bot:
                        d += 'Command not found.'
                    else:
                        d += '`{}` has no sub-command `{}`.'.format(cmd.name, i)
                    break
            if cmd != ctx.bot:
                d = 'Help for command `{}`:\n'.format(cmd_name)
                d += '\n**Usage:**\n'

                if type(cmd) != commands.core.Group:
                    params = list(cmd.clean_params.items())
                    p_str = ''
                    for p in params:
                        if p[1].default == p[1].empty:
                            p_str += ' [{}]'.format(p[0])
                        else:
                            p_str += ' <{}>'.format(p[0])
                    d += '`{}{}{}`\n'.format(ctx.prefix, cmd_name, p_str)
                else:
                    d += '`{}{} '.format(ctx.prefix, cmd.name)
                    if cmd.invoke_without_command:
                        d += '['
                    else:
                        d += '<'
                    d += '|'.join(cmd.all_commands.keys())
                    if cmd.invoke_without_command:
                        d += ']`\n'
                    else:
                        d += '>`\n'

                d += '\n**Description:**\n'
                d += '{}\n'.format('None' if cmd.help is None else cmd.help.strip())

                if cmd.checks:
                    d += '\n**Checks:**'
                    for check in cmd.checks:
                        d += '\n{}'.format(check.__qualname__.split('.')[0])
                    d += '\n'

                if cmd.aliases:
                    d += '\n**Aliases:**'
                    for alias in cmd.aliases:
                        d += '\n`{}{}`'.format(ctx.prefix, alias)

                    d += '\n'

        d += '\n*Made by hanss314#0128*'
        await ctx.send(d)

    @category('info')
    @commands.command()
    async def ping(self, ctx):
        '''Ping the bot.'''
        await ctx.send('Pong!')
        
    @category('info')
    @commands.command()
    async def about(self, ctx):
        '''About the bot.'''
        d = 'This bot is a currency and shop bot for Nerd\'s Shop TWOW\n'
        d += 'This bot was made by hanss314#0128\n'
        d += 'You can see and contribute to the source code at <https://github.com/hanss314/percbot>\n'
        d += 'You can join Nerd\'s Shop TWOW here. https://discord.gg/A9DYC8C'
        await ctx.send(d)

    @category('info')
    @commands.command(aliases=['aboutme','boutme','\'boutme'])
    @commands.guild_only()
    async def me(self, ctx):
        '''Get info about yourself.'''
        member = ctx.author
        now = datetime.datetime.utcnow()
        joined_days = now - member.joined_at
        created_days = now - member.created_at
        avatar = member.avatar_url

        embed = discord.Embed(colour=member.colour)
        embed.add_field(name='Nickname', value=member.display_name)
        embed.add_field(name='User ID', value=member.id)
        embed.add_field(name='Avatar', value='[Click here to show]({})'.format(avatar))

        embed.add_field(name='Created', value=member.created_at.strftime('%x %X') + '\n{} days ago'.format(max(0, created_days.days)))
        embed.add_field(name='Joined', value=member.joined_at.strftime('%x %X') + '\n{} days ago'.format(max(0, joined_days.days)))
        roles = '\n'.join([r.mention for r in sorted(member.roles, key=lambda x:x.position, reverse=True) if r.name != '@everyone'])
        if roles == '': roles = '\@everyone'
        embed.add_field(name='Roles', value=roles)

        embed.set_author(name=member, icon_url=avatar)

        try:
            await ctx.channel.send(embed=embed)
        except discord.errors.Forbidden:
            pass

def setup(bot):
    bot.add_cog(Misc())
