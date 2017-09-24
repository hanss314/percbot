import discord
import inspect

from discord.ext import commands

from percbot.util import checks
from percbot.util.categories import category
from percbot.util.converters import UserList, Item
from percbot.util.formatters import say_list, to_lower

class Owner():
    
    async def __local_check(self, ctx):
        return checks.is_owner(ctx)
    
    @category('People')
    @commands.command()
    async def transac(self, ctx, amount: int, *members: UserList):
        '''Give or take percs from users'''
        db = ctx.bot
        members = [m for s in members for m in s]
        members = list(set(members))
        success = []
        not_enough = []
        
        for member in members:
            if member.id in db.people:
                if -1*amount > db.people[member.id]['percs']:
                    not_enough.append(member.name)
                else:
                    db.people[member.id]['percs'] += amount
                    db.people[member.id]['transacts'].append(amount)
                    success.append(member.name)
        
        if ctx.message.mention_everyone: name_str = 'Everyone'
        else: name_str = say_list(success, 'No one')
        
        if amount < 0: action = 'lost'
        else: action = 'gained'
        
        d = '{} {} {} perc{}.'.format(name_str, action, amount, '' if amount == 1 else 's')
        if not_enough: d += ' {} did not have enough percs.'.format(say_list(not_enough))

        await ctx.send(d)
    
    @category('Shop')
    @commands.command(aliases=['additem'])
    async def add_item(self, ctx, name: to_lower, price: int, amount: int, tier: int, *, description:str):
        '''Create an item'''
        success = False
        db = ctx.bot
        if name in db.items: return await ctx.send('{} is already an item!'.format(name.title()))
        db.items[name]={
            'price':price,
            'amount':amount,
            'tier':tier,
            'description':description
            }
        for user in db.inventories.values():
            user[name] = 0
            
        await ctx.send('`{}`x {} added to tier {}. It costs ¶{}.'.format(
            'Unlimited' if amount<0 else amount, name, tier, price))
    
    @category('Shop')
    @commands.command(aliases=['setprice'])
    async def set_price(self, ctx, price: int, *, item: Item):
        '''Set the price for an item'''
        item[1]['price'] = price
        await ctx.send('{} now costs ¶{}.'.format(item[0].title(), price))
        
    @category('Shop')
    @commands.command(aliases=['setstock'])
    async def set_stock(self, ctx, amount: int, *, item: Item):
        '''Set how many items are in stock'''
        item[1]['amount'] = amount
        await ctx.send('Set stock for {} to {}.'.format(item[0].title(), 'Unlimited' if amount<0 else amount))
        
    @category('Shop')
    @commands.command(aliases=['itemtier'])
    async def item_tier(self, ctx, tier: int, *, item: Item):
        '''Set the tier for an item'''
        item[1]['tier'] = tier
        await ctx.send('{} is now at tier {}.'.format(item[0].title(), tier))
        
    @category('Shop')
    @commands.command(aliases=['setdescription', 'setdescrip'])
    async def set_description(self, ctx, item: Item, *, descrip: str):
        '''Set the tier for an item'''
        item[1]['description'] = description
        await ctx.send('Description for {} is {}.'.format(
            item[0].title(), 
            descrip[:1900] + '...' if len(descrip) > 1900 else descrip
            ))
    
    @category('Shop')
    @commands.command()
    async def alias(self, ctx, item: Item, action, *aliases: to_lower):
        '''Add an alias for an item'''
        if action not in ['add', 'remove', '+', '-', 'list']:
            return await ctx.send('Action must be <add|remove|+|-|list>')
        
        aliases=set(aliases)

        if 'aliases' not in item[1]:
            item[1]['aliases'] = set()
            
        if action in['add','+']:
            item[1]['aliases'] |= aliases
        elif action in ['remove','-']:
            item[1]['aliases'] -= aliases
            
        await ctx.send('Aliases for {}: `{}`'.format(item[0].title(), ', '.join(item[1]['aliases']) or ' '))

    @category('Shop')
    @commands.command()
    async def nexttier(self, ctx, tier: int, *, item: Item):   
        '''For items that tier you up after buying'''
        item[1]['nexttier'] = tier
        await ctx.send('Anyone who buys {} will be set to at least tier {}.'.format(item[0].title(), tier))

    @category('Shop')
    @commands.command()
    async def maxtier(self, ctx, tier: int, *, item: Item):
        '''Sets a maximum tier to buy an item'''
        item[1]['maxtier']=tier
        await ctx.send('The highest tier to buy {} will be {}.'.format(item[0].title(), tier))
        
    @category('Shop')
    @commands.command(aliases=['minrev'])
    async def setminrev(self, ctx, revenue: int, *, item: Item):
        '''Sets the revenue required to buy an item'''
        item[1]['minrev']=revenue
        await ctx.send('People will need ¶{} to buy {}.'.format(revenue, item[0].title()))
        
    @category('Info')
    @commands.command()
    async def usertiers(self, ctx, tier: int):
        '''Get all users at a tier'''
        
        to_send = ''
        await ctx.send('These people are at tier {}:'.format(tier))
        for id, person in ctx.bot.people.items():
            if person['tier']==tier:
                if len(person['name'])+len(to_send)>1990:
                    await ctx.send(to_send)
                    to_send = ''
                user = ctx.bot.get_user(id)
                if user: to_send += '{}\n'.format(user.name)
                
        if to_send != '':
            await ctx.send(to_send)
    
    @category('Shop')
    @commands.command()
    async def remove(self, ctx, item: Item):
        '''Remove an item from the shop'''
        items = ctx.bot.items
        inventories = ctx.bot.inventories
        items.pop(item[0])
        for user in inventories.values():
            if item[0] in user:
                user.pop(item[0])
                
        await ctx.send('Removed {} from shop.'.format(item[0].title()))

    @category('Shop')
    @commands.command(aliases=['readshop'])
    async def read_shop(self, ctx):
        '''Update the shop with any changes you've made'''
        bot = ctx.bot
        with open('bot_data/items.yml') as data_file:
            bot.items = bot.yaml.load(data_file)
        with open('bot_data/inventories.yml') as data_file:
            bot.inventories = bot.yaml.load(data_file)
        with open('bot_data/people.yml') as data_file:
            bot.people = bot.yaml.load(data_file)
        with open('bot_data/blacklist.yml') as data_file:
            bot.blacklist = bot.yaml.load(data_file)
        await ctx.send('Shop updated.')
    
    @category('People')
    @commands.command()
    async def give(self, ctx, user: discord.User, item: Item):
        '''Give an item to a user. Ignore stock and tiers.'''
        if user.id not in ctx.bot.inventories:
            ctx.bot.inventories[user.id] = {i:0 for i in ctx.bot.items.keys()}
        ctx.bot.inventories[user.id][item[0]] += 1
        await ctx.send('Gave one {} to {}.'.format(item[0].title(), user.name))
            
    @category('People')
    @commands.command()
    async def take(self, ctx, user: discord.User, item: Item):
        '''Take an item from a user.'''
        if user.id not in ctx.bot.inventories:
            ctx.bot.inventories[user.id] = {i:0 for i in ctx.bot.items.keys()}
        if ctx.bot.inventories[user.id][item[0]] <= 0:
            return await ctx.send('{} doesn\'t have any {}.'.format(user.name, item[0].title()))
        else:
            ctx.bot.inventories[user.id][item[0]] -= 1
            await ctx.send('Took one {} from {}.'.format(item[0].title(), user.name))
        
    @category('People')
    @commands.command()
    async def settier(self, ctx, tier: int, *members: UserList):
        '''Sets tiers for users.'''
        success = []
        db = ctx.bot
        members = [m for s in members for m in s]
        members = list(set(members))
        for member in members:
            if member.id in db.people:
                db.people[member.id]['tier'] = tier
                success.append(member.name)
        
        if ctx.message.mention_everyone: name_str = 'Everyone'
        else: name_str = say_list(success, 'No one')
        
        await ctx.send('{} has had their tier set to {}.'.format(name_str, tier))
        
    @category('People')
    @commands.command()
    async def addtier(self, ctx, amount: int, *members: UserList):
        '''Sets tiers for users.'''
        success = []
        db = ctx.bot
        members = [m for s in members for m in s]
        members = list(set(members))
        for member in members:
            if member.id in db.people:
                db.people[member.id]['tier'] += amount
                success.append(member.name)
        
        if ctx.message.mention_everyone: name_str = 'Everyone'
        else: name_str = say_list(success, 'No one')
        
        await ctx.send('{} has had {} added to their their tier.'.format(name_str, amount))
        
    @category('Bot')
    @commands.command()
    async def remind(self, ctx, role: UserList, *, message: str):
        '''Send a DM reminder to a role, user, or whatever'''
        if ctx.guild.large: await ctx.bot.request_offline_members(shopmtwow)
        for user in role:
            await user.send('Reminder! {}'.format(message))

def setup(bot):
    bot.add_cog(Owner())
