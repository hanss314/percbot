import re

tired = """Okay, I\'m real tired of this shit {message.author.name}. This isn't funny. 
Go do something with your life. You're an asshole for constantly doing this. 
You need to get a life. And no, despite how many jokes you try to throw at me 
with all this SUCH FUNNY LMAO incorrect item naming, 
you'll still sound like, look like, hopefully feel like, and most of all, 
be an asshole. So you know what, do what you want. 
I'll just display the text like normal. For your sorry ass' information 
"Start Communist Revolution" is not an item. 
""".replace('\n', '')

eggs = {
    '(can.*|!)(buy|have|give|get).*start communist revolution': tired
}


class Eggs:

    def __init__(self, bot):
        self.bot = bot

    # basic easter egg item command
    '''
    @category('Seasonal')
    @commands.command()
    async def command_name(self, ctx):
        item = 'item name'
        gone_mess = 'I have no more stuff to give.'
        give_mess = 'Here have some stuff'

        if item not in ctx.bot.items or ctx.bot.items[item]['amount'] == 0:
            return await ctx.send(gone_mess)

        try:
            ctx.bot.inventories[ctx.author.id][item] += 1
        except KeyError:
            ctx.bot.inventories[ctx.author.id][item] = 1

        await ctx.send(give_mess)

    '''

    async def on_message(self, message):
        content = message.content.lower()
        for k, v in eggs.items():
            if re.match(k, content):
                return await message.channel.send(v.format(message=message))




def setup(bot):
    bot.add_cog(Eggs(bot))