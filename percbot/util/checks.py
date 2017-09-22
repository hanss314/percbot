import inspect
import discord

from discord.ext import commands


def is_owner(ctx):
    return ctx.author.id in ctx.bot.config['owners']

    
