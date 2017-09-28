from discord.ext import commands

class UserList(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            ids = set()
            if ctx.guild is not None:
                try: member = await commands.MemberConverter().convert(ctx, argument)
                except commands.BadArgument:
                    try: role = await commands.RoleConverter().convert(ctx, argument)
                    except commands.BadArgument as e: raise e
                    else:
                        if role.guild.large: await role.bot.request_offline_member(ctx.guild)
                        for member in role.guild.members:
                            if role in member.roles:
                                ids.add(member)
                else: ids.add(member)
                    
            else:
                try: user = await commands.UserConverter().convert(ctx, argument)
                except commands.BadArgument as e: raise e
                else: ids.add(user)
            if len(ids) == 0:
                raise commands.BadArgument('{} is not a role or user.'.format(argument))
            return ids
        except Exception as e:
            await ctx.author.send(traceback.format_exception(type(e), e, e.__traceback__, chain=True))

class Item(commands.Converter):
    async def convert(self, ctx, argument):
        
        items = ctx.bot.items
        argument = argument.lower().strip('"')
        if argument in items: return (argument, items[argument])
        for k, v in items.items():
            if 'aliases' in v and argument in v['aliases']:
                return (k, v)
            
        raise commands.BadArgument('`{}` is not an Item.'.format(argument.title()))

