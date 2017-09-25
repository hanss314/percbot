import discord

from discord.ext import commands

from percbot.util import checks
from percbot.util.categories import category
from percbot.util.converters import UserList, Item
from percbot.util.formatters import say_list, to_lower

class Users():
    
    @category('Info')
    @commands.command()
    async def percs(self, ctx, user: discord.User = None):
        '''See how many percs you have'''
        tried_other=False
        if user is not None:
            if not checks.is_owner(ctx):
                user = ctx.author
                tried_other=True
        else:
            user = ctx.author
        
        if user.id not in ctx.bot.people:
            if id == ctx.author.id:
                ctx.bot.add_user(user.id)
                await ctx.author.send('You have 0 percs.')
            else:
                await ctx.author.send('{} is not in the database.'.format(user.name))
            return
        
        percs = ctx.bot.people[user.id]['percs']
        
        d = ''
        if tried_other: d += 'You can only see how many percs you have. '
        
        if ctx.author.id == user.id: d += 'You have'
        else: d += '{} has'.format(user.name)
            
        if percs == 1: await ctx.author.send('{} 1 perc.'.format(d))
        else: await ctx.author.send('{} {} percs.'.format(d,percs))
        
    @category('Info')
    @commands.command()
    async def tier(self, ctx, user: discord.User = None):
        '''See your tier'''
        tried_other=False
        if user is not None:
            if not checks.is_owner(ctx):
                user = ctx.author
                tried_other=True
        else:
            user = ctx.author
        
        if user.id not in ctx.bot.people:
            if user.id == ctx.author.id:
                ctx.bot.add_user(user.id)
                await ctx.author.send('You are at tier 0.')
            else:
                await ctx.author.send('{} is not in the database.'.format(user.name))
            return

        d = ''
        tier = ctx.bot.people[user.id]['tier']
        
        if tried_other: d += 'You can only see your tier. '
        
        if ctx.author.id == user.id: d += 'You are at'
        else: d += user.name +' is at'
            
        await ctx.author.send('{} tier {}.'.format(d,tier))  
        
    @category('Info')
    @commands.command()
    async def transacinfo(self, ctx, user: discord.User = None):
        '''See your transaction history'''
        tried_other=False
        if user is not None:
            if not checks.is_owner(ctx):
                user = ctx.author
                tried_other=True
        else:
            user = ctx.author
        
        if user.id not in ctx.bot.people:
            if id == ctx.author.id: ctx.bot.add_user(user.id)
            else: await ctx.author.send('{} is not in the database.'.format(id))
        
        hist = ctx.bot.people[user.id]['transacts']
        gains = sum([x for x in hist if x>0])
        losses = sum([-x for x in hist if x<0])
        d = ''
        if tried_other:
            d += 'You can only see your history.\n'
        
        d += 'Perc History for **{}**\n'.format(user.name)
        d += 'Account: ¶{}\n'.format(sum(hist))
        d += 'Revenue: ¶{}\n'.format(gains)
        d += 'Payments: ¶{}\n'.format(losses)
        d += 'History: {}'.format(', '.join([str(x) for x in hist]))
            
        await ctx.author.send(d)   
        
    @category('Info')
    @commands.command()
    async def allitems(self, ctx):
        '''See all the items your tier and below'''
        item_tiers = {}
        d = ''
        try:
            tier = ctx.bot.people[ctx.author.id]['tier']
        except KeyError:
            tier = 0
            ctx.bot.add_user(ctx.author.id)
        
        for key, value in ctx.bot.items.items():
            if value['tier'] <= tier:
                stock = value['amount']
                if stock <0:
                    stock='Unlimited'
                item_str='*{}*: ¶{}. {} in stock.\n'.format(key,value['price'],stock)
                try: 
                    item_tiers[value['tier']].append(item_str)
                except KeyError:
                    item_tiers[value['tier']]=[item_str]
                    
        for key in sorted(item_tiers):
            d += '**Tier {}**\n'.format(key)
            d += ''.join(sorted(item_tiers[key]))
            d+='\n'
            
        if len(d)>0:
            await ctx.author.send(d)
        else:
            await ctx.author.send('There are no items you can view.')
    @category('Info')
    @commands.command()
    async def iteminfo(self, ctx, *, item: Item):
        '''Get info on an item'''
        tier = item[1]['tier']
        price = item[1]['price']
        aliases = list(item[1]['aliases']) if 'aliases' in item[1] else []
        stock = item[1]['amount']
        
        if stock<0:
            stock='Unlimited'
        description = item[1]['description']
        d = '**{}**\n'.format(item[0].title())
        if len(aliases) >0:
            d += 'Aliases: {}\n'.format(', '.join(aliases))
        d += 'Price: ¶{}\n'.format(price)
        d += 'Stock: {}\n'.format(stock)
        d += 'Tier: {}\n\n'.format(tier)
        d += description
        await ctx.author.send(d)
    
    @category('Info')
    @commands.command()
    async def canbuy(self, ctx):
        '''See all the items you can buy'''
        item_tiers = {}
        d = ''
        try:
            tier = ctx.bot.people[ctx.author.id]['tier']
        except KeyError:
            tier = 0
            ctx.bot.add_user(ctx.author.id)
        
        for key, value in ctx.bot.items.items():
            b = value['tier'] <= tier and value['amount'] > 0
            b = b and value['price'] <= ctx.bot.people[ctx.author.id]['percs']
            if 'maxtier' in value: b = b and tier <= value['maxtier']
            if 'minrev' in value: 
                rev = sum([x for x in ctx.bot.people[ctx.author.id]['transacts'] if x>0])
                b = b and rev >= value['minrev']
            if b:
                stock = value['amount']
                if stock <0:
                    stock='Unlimited'
                item_str='*{}*: ¶{}. {} in stock.\n'.format(key,value['price'],stock)
                try: 
                    item_tiers[value['tier']].append(item_str)
                except KeyError:
                    item_tiers[value['tier']]=[item_str]
                    
        for key in sorted(item_tiers):
            d += '**Tier {}**\n'.format(key)
            d += ''.join(sorted(item_tiers[key]))
            d+='\n'
            
        if len(d)>0:
            await ctx.author.send(d)
        else:
            await ctx.author.send('There are no items you can buy.')
    
    @category('Info')
    @commands.command()
    async def myitems(self, ctx, user: discord.User = None):
        '''See how many percs you have'''
        tried_other=False
        if user is not None:
            if not checks.is_owner(ctx):
                user = ctx.author
                tried_other=True
        else:
            user = ctx.author
        
        if user.id not in ctx.bot.people:
            if id == ctx.author.id:
                ctx.bot.add_user(user.id)
                await ctx.author.send('You have no items.')
            else:
                await ctx.author.send('{} is not in the database.'.format(user.name))
            return
        d = ''
        if tried_other:
            d += 'You can only see how many items you have. '
        d += 'Here are your items:\n'
        item_dict = ctx.bot.inventories[user.id]
        item_str = ''
        for key, value in item_dict.items():
            if value>0:
                item_str+='{}: {}\n'.format(key.title(),value)
            
        if len(item_str)==0:
            if ctx.author.id == user.id:
                d = 'You have no items.'
            else:
                d='{} has no items.'.format(user.name)
        
        d += item_str
        await ctx.author.send(d)
        
    @category('Shop')
    @commands.command()
    async def useitem(self, ctx, *, item: Item): 
        '''Use an item'''
        id = ctx.author.id
        try:
            item_dict = ctx.bot.inventories[id]
        except KeyError:
            ctx.bot.add_user(ctx.author.id)
            await ctx.user.send('You have no items.')
            return

        item_dict = ctx.bot.inventories[ctx.author.id]
        if item_dict[item[0]] > 0:
            item_dict[item[0]] -=1
        else:
            return await ctx.author.send('You don\'t have any {}. Use `{}myitems` to see your items.'.format(
                item[0].title(),ctx.prefix))

        await ctx.send('You have used {}. Nerd has been alerted'.format(item[0]))
        nerd = ctx.bot.get_user(210285266814894081)
        if nerd is not None: await nerd.send('{} has used {}'.format(ctx.author.name,item[0]))
       
    @category('Shop')
    @commands.command()
    async def buy(self, ctx, *, item: Item): 
        '''Buy an item'''
        price = item[1]['price']
        tier = item[1]['tier']
        
        if ctx.author.id not in ctx.bot.people:
            ctx.bot.add_user(ctx.author.id)
            return await ctx.send('You have no money.')
        
        if ctx.bot.people[ctx.author.id]['tier'] < tier:
            return await ctx.send('Your tier is too low!')
        
        if item[1]['amount'] == 0:
            return await ctx.send('{} is out of stock!'.format(item[0].title()))
        
        if item[1]['price'] > ctx.bot.people[ctx.author.id]['percs'] :
            return await ctx.send('You don\'t have enough percs!')
        
        if 'maxtier' in item[1] and item[1]['maxtier'] < ctx.bot.people[ctx.author.id]['tier']:
            return await ctx.send('Your tier is too high!')
        
        if 'minrev' in item[1]:
            rev = sum([x for x in ctx.bot.people[ctx.author.id]['transacts'] if x>0])
            if item[1]['minrev'] > rev:
                return await ctx.send('You need more revenue!')

        ctx.bot.inventories[ctx.author.id][item[0]] += 1
        ctx.bot.transac(ctx.author.id, -1*item[1]['price'])
        item[1]['amount'] -= 1
        
        await ctx.send('You have bought {}. Nerd has been alerted'.format(item[0].title()))
        nerd = ctx.bot.get_user(210285266814894081)
        if nerd is not None: await nerd.send('{} has bought {}'.format(ctx.author.name,item[0].title()))
        
def setup(bot):
    bot.add_cog(Users())
