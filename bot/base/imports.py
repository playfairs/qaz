"""
Centralized imports for this bot.
"""

import discord
from discord.ext import commands
from discord.ext.commands import (
    BotMissingPermissions,
    Context,
    CommandError,
    NotOwner,
    CheckFailure,
    CommandNotFound,
    CommandOnCooldown,
    MissingRequiredArgument,
    MissingPermissions,
    CooldownMapping,
    BucketType,
)
import logging
import ssl
import os
import asyncio
from pathlib import Path
import pathlib

try:
    import colorama
    from colorama import Fore, Back, Style
    colorama.init()
    HAS_COLORAMA = True
except ImportError:
    class Fore:
        GREEN = '\033[92m'
        RED = '\033[91m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    HAS_COLORAMA = False

try:
    import asyncpg
    HAS_ASYNCPG = True
except ImportError:
    asyncpg = None
    HAS_ASYNCPG = False

Intents = discord.Intents
AllowedMentions = discord.AllowedMentions
Embed = discord.Embed
Color = discord.Color

log = logging.getLogger(__name__)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

__all__ = [
    'discord',
    'commands',
    'BotMissingPermissions',
    'Context',
    'CommandError',
    'NotOwner',
    'CheckFailure',
    'CommandNotFound',
    'CommandOnCooldown',
    'MissingRequiredArgument',
    'MissingPermissions',
    'CooldownMapping',
    'BucketType',
    'Intents',
    'AllowedMentions',
    'Embed',
    'Color',
    'logging',
    'ssl',
    'os',
    'asyncio',
    'asyncpg',
    'HAS_ASYNCPG',
    'Path',
    'pathlib',
    'log',
    'ssl_context',
    'colorama',
    'Fore',
    'Back',
    'Style',
    'HAS_COLORAMA',
]
