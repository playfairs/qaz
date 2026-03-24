from .imports import *
from config import DISCORD, COGS
from .events import setup_events

class ColoredFormatter(logging.Formatter):
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA,
    }
    
    def format(self, record):
        if hasattr(record, 'msg') and '┌─' in str(record.msg):
            return record.msg
        else:
            log_color = self.COLORS.get(record.levelname, Fore.WHITE)
            record.levelname = f"{log_color}{record.levelname}{Fore.RESET}"
            record.name = f"{Fore.BLUE}{record.name}{Fore.RESET}"
            return super().format(record)

class qaz(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(
            command_prefix=DISCORD.PREFIX,
            intents=intents,
            help_command=None,
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False, replied_user=True
            ),
        )

        self.owner_ids = DISCORD.OWNER_IDS
        self.cog_path = pathlib.Path("bot/ext")
        self.cog_skip = COGS.SKIP
        
        self.log = logging.getLogger(__name__)
        
        formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                   datefmt='%H:%M:%S')
        
        if not self.log.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            self.log.addHandler(handler)
            self.log.setLevel(logging.INFO)
        
        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
    
    def create_box(self, title, content_lines, color=Fore.GREEN):
        all_lines = [title] + content_lines
        max_content_length = max(len(line) for line in content_lines)
        title_length = len(title)
    
        box_width = max(max_content_length, title_length) + 2

        title_padding = box_width - title_length
        top_border = f"┌─ {title}{'─' * title_padding}┐"

        bottom_border = f"└{'─' * (box_width + 2)}┘"

        formatted_lines = []
        for line in content_lines:
            content_padding = box_width - len(line)
            formatted_line = f"│ {line}{' ' * content_padding} │"
            formatted_lines.append(formatted_line)

        box_lines = [f"{color}{top_border}{Fore.RESET}"] + [
            f"{Fore.CYAN if 'User:' in line else Fore.YELLOW if 'Guild:' in line else Fore.BLUE if 'Channel:' in line else Fore.MAGENTA if 'Command:' in line else Fore.RED if 'Error:' in line else Fore.WHITE}{line}{Fore.RESET}"
            for line in formatted_lines
        ] + [f"{color}{bottom_border}{Fore.RESET}"]

        return '\n'.join(box_lines)

    async def setup_hook(self):
        try:
            await self.load_extension("jishaku")
            print("[+] Loaded jishaku")
        except Exception as e:
            print(f"[!] Failed to load jishaku: {e}")

        for file in self.cog_path.glob("*.py"):
            if file.name.startswith("_"):
                continue

            if file.stem in self.cog_skip:
                print(f"[-] Skipped cog: {file.stem}")
                continue

            cog_name = f"bot.ext.{file.stem}"

            try:
                await self.load_extension(cog_name)
                print(f"[+] Loaded cog: {cog_name}")
            except Exception as e:
                print(f"[!] Failed to load {cog_name}: {e}")

        setup_events(self)
        self.log.info("Starting qaz bot.")
    
    async def get_prefix(self, message):
        prefixes = list(DISCORD.PREFIXES)
        return commands.when_mentioned_or(*prefixes)(self, message)
    
    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=commands.Context)
        await self.invoke(ctx)
    
    async def on_command(self, ctx):
        try:
            self.dispatch("usage", ctx)
        except Exception:
            import traceback
            traceback.print_exc()
            return
        
        if ctx.guild:
            location = f"#{ctx.channel.name} in {ctx.guild.name}"
            guild_id = ctx.guild.id
            channel_id = ctx.channel.id
        else:
            location = "DMs"
            guild_id = "N/A"
            channel_id = ctx.channel.id
        
        user_info = f"{ctx.author.name} ({ctx.author.id})"
        command_info = str(ctx.command)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        content_lines = [
            f"User: {user_info}",
            f"Guild: {guild_id}",
            f"Channel: {channel_id}",
            f"Command: {command_info}"
        ]
        
        box_message = self.create_box(f"✓ SUCCESS [{timestamp}]", content_lines, Fore.GREEN)
        self.log.info(box_message)
    
    async def on_command_error(self, ctx, exception):
        if ctx.guild:
            location = f"#{ctx.channel.name} in {ctx.guild.name}"
            guild_id = ctx.guild.id
            channel_id = ctx.channel.id
        else:
            location = "DMs"
            guild_id = "N/A"
            channel_id = ctx.channel.id
        
        user_info = f"{ctx.author.name} ({ctx.author.id})"
        command_info = str(ctx.command or ctx.invoked_with)
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        if isinstance(exception, commands.NotOwner):
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}"
            ]
            box_message = self.create_box(f"✗ OWNER_ONLY [{timestamp}]", content_lines, Fore.RED)
            self.log.info(box_message)
            return
        elif isinstance(exception, commands.CheckFailure):
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}"
            ]
            box_message = self.create_box(f"⚠ CHECK_FAILED [{timestamp}]", content_lines, Fore.YELLOW)
            self.log.info(box_message)
            return
        elif isinstance(exception, commands.BotMissingPermissions):
            error_msg = f"Missing permissions: {', '.join(p for p in exception.missing_permissions)}"
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}",
                f"Error: {error_msg}"
            ]
            box_message = self.create_box(f"✗ PERMISSION_ERROR [{timestamp}]", content_lines, Fore.RED)
            self.log.warning(box_message)
            embed = discord.Embed(
                description=f"> I'm **missing** permission: `{', '.join(p for p in exception.missing_permissions)}`",
                color=discord.Color(0x333333),
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(exception, commands.CommandNotFound):
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}"
            ]
            box_message = self.create_box(f"? NOT_FOUND [{timestamp}]", content_lines, Fore.YELLOW)
            self.log.info(box_message)
            embed = discord.Embed(
                description=f"> {ctx.author.mention}, Command **{ctx.invoked_with}** does not exist, run `help` for a list of commands.",
                color=discord.Color(0x333333),
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(exception, commands.CommandOnCooldown):
            error_msg = f"On cooldown: {exception.retry_after:.2f}s"
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}",
                f"Error: {error_msg}"
            ]
            box_message = self.create_box(f"⏱ COOLDOWN [{timestamp}]", content_lines, Fore.YELLOW)
            self.log.info(box_message)
            embed = discord.Embed(
                description=f"> {ctx.author.mention}, Command **{ctx.invoked_with}** is on cooldown, try again in {exception.retry_after:.2f} seconds.",
                color=discord.Color(0x333333),
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(exception, commands.MissingRequiredArgument):
            error_msg = f"Missing argument: {exception.param.name}"
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}",
                f"Error: {error_msg}"
            ]
            box_message = self.create_box(f"✗ MISSING_ARG [{timestamp}]", content_lines, Fore.RED)
            self.log.warning(box_message)
            embed = discord.Embed(
                description=f"> {ctx.author.mention}, Missing required argument for command **{ctx.invoked_with}**.",
                color=discord.Color(0x333333),
            )
            await ctx.send(embed=embed, delete_after=5)
        elif isinstance(exception, commands.MissingPermissions):
            error_msg = f"Missing permissions: {', '.join(p for p in exception.missing_permissions)}"
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}",
                f"Error: {error_msg}"
            ]
            box_message = self.create_box(f"✗ USER_PERM_ERROR [{timestamp}]", content_lines, Fore.RED)
            self.log.warning(box_message)
            embed = discord.Embed(
                description=f"> {ctx.author.mention}, You are **missing** permission: `{', '.join(p for p in exception.missing_permissions)}`",
                color=discord.Color(0x333333),
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            error_msg = str(exception)
            content_lines = [
                f"User: {user_info}",
                f"Guild: {guild_id}",
                f"Channel: {channel_id}",
                f"Command: {command_info}",
                f"Error: {error_msg}"
            ]
            box_message = self.create_box(f"✗ UNKNOWN_ERROR [{timestamp}]", content_lines, Fore.RED)
            self.log.error(box_message, exc_info=True)
    
    def format_number(self, number: int):
        """Convert larger numbers into a smaller condensed number."""
        if number >= 1000000000:
            return f"{number / 1000000000:.1f}B"
        elif number >= 1000000:
            return f"{number / 1000000:.1f}M"
        elif number >= 1000:
            return f"{number / 1000:.1f}K"
        return str(number)
