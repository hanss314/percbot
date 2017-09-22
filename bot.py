import traceback
import datetime
import logging
import sys
import re
import os
import base64

from discord.ext import commands
from discord.ext.commands.errors import CommandError, CommandNotFound
import ruamel.yaml as yaml
import discord

class PercBot(commands.Bot):
    class ErrorAlreadyShown(Exception): pass

    def __init__(self, log_file=None, *args, **kwargs):
        self.config = {}
        self.board = None
        self.yaml = yaml.YAML(typ='safe')
        
        with open('config.yml') as data_file:
            self.config = self.yaml.load(data_file)
        
        with open('bot_data/items.yml') as data_file:
            self.items = self.yaml.load(data_file)
            
        with open('bot_data/inventories.yml') as data_file:
            self.inventories = self.yaml.load(data_file)
            
        with open('bot_data/people.yml') as data_file:
            self.people = self.yaml.load(data_file)
            
        with open('bot_data/blacklist.yml') as data_file:
            self.blacklist = self.yaml.load(data_file)
            
        logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s] %(message)s')
        self.logger = logging.getLogger('bot')

        super().__init__(
            command_prefix=self.config['prefix'],
            *args,
            **kwargs
        )
        
    def add_user(self, id):
        self.people[user.id] = {
            'name':user.name,
            'tier':0,
            'percs':0,
            'transacts':[]
        }
        self.inventories[user.id] = {item:0 for item in self.items.keys()}
        
    def save_data(self):
        with open('bot_data/items.yml', 'w') as data_file:
            self.yaml.dump(self.items, data_file)
            
        with open('bot_data/inventories.yml', 'w') as data_file:
            self.yaml.dump(self.inventories, data_file)
            
        with open('bot_data/people.yml', 'w') as data_file:
            self.yaml.dump(self.people, data_file)
            
        with open('bot_data/blacklist.yml', 'w') as data_file:
            self.yaml.dump(self.blacklist, data_file)

    async def on_message(self, message):
        await self.process_commands(message)

    async def close(self):
        await super().close()

    async def on_command_error(self, ctx: commands.Context, exception: Exception):
        if isinstance(exception, commands.CommandInvokeError):
            if isinstance(exception.original, discord.Forbidden):
                try: await ctx.send('Permissions error: `{}`'.format(exception))
                except discord.Forbidden: pass
                return
            
            lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
            self.logger.error(''.join(lines))
            await self.notify_devs(''.join(lines))
        elif isinstance(exception, commands.CheckFailure):
            await ctx.send('You can\'t do that.')
        elif isinstance(exception, commands.CommandNotFound):
            pass
        elif isinstance(exception, commands.UserInputError):
            error = ' '.join(exception.args)
            error_data = re.findall('Converting to \"(.*)\" failed for parameter \"(.*)\"\.', error)
            if not error_data:
                await ctx.send('Error: {}'.format(' '.join(exception.args)))
            else:
                await ctx.send('Got to say, I *was* expecting `{1}` to be an `{0}`..'.format(*error_data[0]))
        else:
            info = traceback.format_exception(type(exception), exception, exception.__traceback__, chain=False)
            self.logger.error('Unhandled command exception - {}'.format(''.join(info)))
            await self.notify_devs(''.join(info))
            
    async def on_error(self, event_method, *args, **kwargs):
        info = sys.exc_info()
        info = traceback.format_exception(*info, chain=False)
        self.logger.error('Unhandled exception - {}'.format(''.join(info)))
        await self.notify_devs(''.join(info))
    
    async def notify_devs(self, info):
        with open('error.txt', 'w') as error_file:
            error_file.write(info)
        
        for dev_id in self.config['developers']:
            dev = self.get_user(dev_id)
            if dev is None:
                self.logger.warning('Could not get developer with an ID of {0.id}, skipping.'.format(dev))
                continue
            try:
                with open('error.txt', 'r') as error_file:
                    await dev.send(file=discord.File(error_file))
            except Exception as e:
                self.logger.error('Couldn\'t send error embed to developer {0.id}. {1}'
                                .format(dev, type(e).__name__ + ': ' + str(e)))
            
        os.remove('error.txt')

    async def on_ready(self):
        self.logger.info('Connected to Discord')
        self.logger.info('Guilds  : {}'.format(len(self.guilds)))
        self.logger.info('Users   : {}'.format(len(set(self.get_all_members()))))
        self.logger.info('Channels: {}'.format(len(list(self.get_all_channels()))))

    async def close(self):
        await super().close()

    def run(self):
        self.remove_command("help")
        token = self.config['token']
        cogs = self.config.get('cogs', [])
        for cog in cogs:
            try:
                self.load_extension(cog)
            except Exception as e:
                self.logger.exception('Failed to load cog {}.'.format(cog))
            else:
                self.logger.info('Loaded cog {}.'.format(cog))
        async def coro(ctx): ctx.bot.save_data()
        self.after_invoke(coro)
        self.logger.info('Loaded {} cogs'.format(len(self.cogs)))
        super().run(token)

if __name__ == '__main__':
    bot = PercBot()        
    bot.run()