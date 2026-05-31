"""Messaging channels for Agents Claw Mini."""

import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable, Set
from dataclasses import dataclass
from .config import ChannelConfig
from .exceptions import ChannelException

logger = logging.getLogger("AgentsClawMini.Channel")

@dataclass
class ChannelMessage:
    """Message from a channel."""
    platform: str
    chat_id: str
    user_id: str
    username: str
    text: str
    timestamp: str
    raw_data: Dict[str, Any]

class ChannelManager:
    """
    Messaging channel manager.

    Supported platforms:
    - Telegram (via python-telegram-bot) - dengan Bot ID & User ID tracking
    - Discord (via discord.py)
    - Slack (via slack-sdk)
    - WhatsApp (coming soon)

    Features:
    - Multi-platform support
    - Message handling dengan filter by user ID
    - Command parsing (/start, /help, /status)
    - Admin/authorized user filtering
    - Webhook support
    - Bot ID tracking
    """

    def __init__(self, config: Optional[ChannelConfig] = None):
        self.config = config or ChannelConfig()
        self._telegram_bot = None
        self._telegram_app = None
        self._telegram_bot_id: Optional[str] = None
        self._discord_bot = None
        self._slack_client = None
        self._handlers: List[Callable] = []
        self._connected = False

        # Authorized users (whitelist)
        self._authorized_users: Set[str] = set()
        self._admin_users: Set[str] = set()

        # Command handlers
        self._command_handlers: Dict[str, Callable] = {}

    def on_message(self, handler: Callable):
        """Register message handler."""
        self._handlers.append(handler)
        return handler

    def on_command(self, command: str):
        """Decorator untuk register command handler."""
        def decorator(func: Callable):
            self._command_handlers[command] = func
            return func
        return decorator

    def add_authorized_user(self, user_id: str):
        """Add authorized user ID."""
        self._authorized_users.add(str(user_id))
        logger.info("✅ User %s authorized", user_id)

    def add_admin(self, user_id: str):
        """Add admin user ID."""
        self._admin_users.add(str(user_id))
        self._authorized_users.add(str(user_id))
        logger.info("👑 Admin %s added", user_id)

    def is_authorized(self, user_id: str) -> bool:
        """Check if user is authorized."""
        if not self._authorized_users:
            return True  # No whitelist = all allowed
        return str(user_id) in self._authorized_users

    def is_admin(self, user_id: str) -> bool:
        """Check if user is admin."""
        return str(user_id) in self._admin_users

    async def _notify_handlers(self, message: ChannelMessage):
        """Notify all handlers."""
        # Check authorization
        if not self.is_authorized(message.user_id):
            logger.warning("❌ Unauthorized user: %s", message.user_id)
            return

        # Check commands
        if message.text.startswith("/"):
            parts = message.text.split()
            cmd = parts[0][1:].split("@")[0]  # Remove @botname
            if cmd in self._command_handlers:
                try:
                    handler = self._command_handlers[cmd]
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message, parts[1:])
                    else:
                        handler(message, parts[1:])
                    return
                except Exception as e:
                    logger.error("Command handler error: %s", e)

        # Notify general handlers
        for handler in self._handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                logger.error("Handler error: %s", e)

    # ========== TELEGRAM ==========

    async def start_telegram(self):
        """Start Telegram bot dengan Bot ID & User ID tracking."""
        if not self.config.telegram_token:
            raise ChannelException("Telegram token tidak diatur. Set TELEGRAM_BOT_TOKEN atau config.channel.telegram_token")

        try:
            from telegram import Update
            from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

            async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
                if not update.effective_message or not update.effective_message.text:
                    return

                # Extract IDs
                bot_id = str(update.effective_message.bot.id) if update.effective_message.bot else None
                chat_id = str(update.effective_chat.id) if update.effective_chat else "0"
                user_id = str(update.effective_user.id) if update.effective_user else "0"
                username = update.effective_user.username or update.effective_user.first_name or "Unknown"

                # Store bot ID
                if bot_id and not self._telegram_bot_id:
                    self._telegram_bot_id = bot_id
                    logger.info("🤖 Telegram Bot ID: %s", bot_id)

                logger.info("📩 [Telegram] Bot:%s | Chat:%s | User:%s(@%s): %s",
                           bot_id or "?", chat_id, user_id, username, update.effective_message.text)

                msg = ChannelMessage(
                    platform="telegram",
                    chat_id=chat_id,
                    user_id=user_id,
                    username=username,
                    text=update.effective_message.text,
                    timestamp=str(update.effective_message.date),
                    raw_data={
                        "bot_id": bot_id,
                        "chat_id": chat_id,
                        "user_id": user_id,
                        "username": username,
                        "message_id": update.effective_message.message_id,
                        "is_group": update.effective_chat.type in ["group", "supergroup"] if update.effective_chat else False,
                    }
                )
                await self._notify_handlers(msg)

            async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                bot_info = await update.effective_message.bot.get_me()
                welcome = f"""🤖⚡ *Agents Claw Mini Bot*

Halo {update.effective_user.first_name}!

*Bot Info:*
🆔 Bot ID: `{bot_info.id}`
👤 Your ID: `{update.effective_user.id}`
💬 Chat ID: `{update.effective_chat.id}`

*Commands:*
/help - Show help
/status - Bot status
/id - Show your ID
/ping - Test connection

Powered by Agents Claw Mini 🐾"""
                await update.message.reply_text(welcome, parse_mode="Markdown")

            async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                help_text = """🤖 *Agents Claw Mini - Help*

*User Commands:*
/start - Start bot
/help - Show this help
/status - Check bot status
/id - Show your Telegram ID
/ping - Test connection

*Admin Commands:*
/users - List authorized users
/adduser <id> - Add authorized user
/removeuser <id> - Remove user

Just chat with me for AI responses!"""
                await update.message.reply_text(help_text, parse_mode="Markdown")

            async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                bot_info = await update.effective_message.bot.get_me()
                status_text = f"""📊 *Bot Status*

🆔 Bot ID: `{bot_info.id}`
🤖 Bot Name: @{bot_info.username}
👤 Your ID: `{update.effective_user.id}`
💬 Chat ID: `{update.effective_chat.id}`

✅ Bot is running normally!"""
                await update.message.reply_text(status_text, parse_mode="Markdown")

            async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                user = update.effective_user
                chat = update.effective_chat
                text = f"""🆔 *Your Info*

👤 User ID: `{user.id}`
📛 Name: {user.first_name} {user.last_name or ''}
🔖 Username: @{user.username or 'N/A'}

💬 Chat ID: `{chat.id}`
📁 Chat Type: {chat.type}"""
                await update.message.reply_text(text, parse_mode="Markdown")

            async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                await update.message.reply_text("🏓 Pong! Bot is active.")

            # Admin commands
            async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                if not self.is_admin(str(update.effective_user.id)):
                    await update.message.reply_text("❌ Admin only!")
                    return

                users_list = "\n".join([f"👤 `{uid}`" for uid in self._authorized_users]) or "No authorized users"
                await update.message.reply_text(f"📋 *Authorized Users*:\n\n{users_list}", parse_mode="Markdown")

            async def adduser_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                if not self.is_admin(str(update.effective_user.id)):
                    await update.message.reply_text("❌ Admin only!")
                    return

                if not context.args:
                    await update.message.reply_text("Usage: /adduser <user_id>")
                    return

                new_user = context.args[0]
                self.add_authorized_user(new_user)
                await update.message.reply_text(f"✅ User `{new_user}` authorized!", parse_mode="Markdown")

            async def removeuser_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
                if not self.is_admin(str(update.effective_user.id)):
                    await update.message.reply_text("❌ Admin only!")
                    return

                if not context.args:
                    await update.message.reply_text("Usage: /removeuser <user_id>")
                    return

                rem_user = context.args[0]
                self._authorized_users.discard(rem_user)
                await update.message.reply_text(f"🗑️ User `{rem_user}` removed!", parse_mode="Markdown")

            # Build application
            self._telegram_app = Application.builder().token(self.config.telegram_token).build()

            # Add handlers
            self._telegram_app.add_handler(CommandHandler("start", start_cmd))
            self._telegram_app.add_handler(CommandHandler("help", help_cmd))
            self._telegram_app.add_handler(CommandHandler("status", status_cmd))
            self._telegram_app.add_handler(CommandHandler("id", id_cmd))
            self._telegram_app.add_handler(CommandHandler("ping", ping_cmd))
            self._telegram_app.add_handler(CommandHandler("users", users_cmd))
            self._telegram_app.add_handler(CommandHandler("adduser", adduser_cmd))
            self._telegram_app.add_handler(CommandHandler("removeuser", removeuser_cmd))
            self._telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

            await self._telegram_app.initialize()
            await self._telegram_app.start()

            # Get bot info
            bot_info = await self._telegram_app.bot.get_me()
            self._telegram_bot_id = str(bot_info.id)

            self._connected = True
            logger.info("📱 Telegram bot started")
            logger.info("🤖 Bot ID: %s | Username: @%s", bot_info.id, bot_info.username)
            logger.info("👑 Add admin with: claw.channels.add_admin("YOUR_USER_ID")")

        except ImportError:
            raise ChannelException("python-telegram-bot tidak terinstall. Run: pip install python-telegram-bot")

    async def send_telegram(self, chat_id: str, text: str, parse_mode: str = "Markdown"):
        """Send message to Telegram chat."""
        if self._telegram_app:
            from telegram import Bot
            bot = Bot(token=self.config.telegram_token)
            await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            logger.info("📤 Sent to Telegram Chat %s: %s...", chat_id, text[:50])

    async def send_telegram_to_user(self, user_id: str, text: str, parse_mode: str = "Markdown"):
        """Send message to specific Telegram user by ID."""
        await self.send_telegram(user_id, text, parse_mode)

    def get_telegram_bot_id(self) -> Optional[str]:
        """Get Telegram Bot ID."""
        return self._telegram_bot_id

    # ========== DISCORD ==========

    async def start_discord(self):
        """Start Discord bot."""
        if not self.config.discord_token:
            raise ChannelException("Discord token tidak diatur")

        try:
            import discord

            intents = discord.Intents.default()
            intents.message_content = True

            client = discord.Client(intents=intents)

            @client.event
            async def on_ready():
                logger.info("🎮 Discord bot logged in as %s (ID: %s)", client.user, client.user.id)

            @client.event
            async def on_message(message):
                if message.author == client.user:
                    return

                msg = ChannelMessage(
                    platform="discord",
                    chat_id=str(message.channel.id),
                    user_id=str(message.author.id),
                    username=message.author.name,
                    text=message.content,
                    timestamp=str(message.created_at),
                    raw_data={
                        "bot_id": str(client.user.id),
                        "guild_id": str(message.guild.id) if message.guild else None,
                        "is_dm": message.guild is None,
                    }
                )
                await self._notify_handlers(msg)

            self._discord_bot = client
            asyncio.create_task(client.start(self.config.discord_token))
            self._connected = True

        except ImportError:
            raise ChannelException("discord.py tidak terinstall. Run: pip install discord.py")

    # ========== SLACK ==========

    async def start_slack(self):
        """Start Slack bot."""
        if not self.config.slack_token:
            raise ChannelException("Slack token tidak diatur")

        try:
            from slack_sdk.web.async_client import AsyncWebClient
            self._slack_client = AsyncWebClient(token=self.config.slack_token)
            logger.info("💬 Slack client initialized")
        except ImportError:
            raise ChannelException("slack-sdk tidak terinstall. Run: pip install slack-sdk")

    async def send_slack(self, channel: str, text: str):
        """Send message to Slack channel."""
        if self._slack_client:
            await self._slack_client.chat_postMessage(channel=channel, text=text)

    # ========== UTILITIES ==========

    def connected_count(self) -> int:
        """Count connected channels."""
        count = 0
        if self._telegram_app:
            count += 1
        if self._discord_bot:
            count += 1
        if self._slack_client:
            count += 1
        return count

    async def disconnect_all(self):
        """Disconnect all channels."""
        if self._telegram_app:
            await self._telegram_app.stop()
            self._telegram_app = None
            self._telegram_bot_id = None

        if self._discord_bot:
            await self._discord_bot.close()
            self._discord_bot = None

        self._slack_client = None
        self._connected = False
        logger.info("📴 All channels disconnected")

    def __repr__(self):
        return f"ChannelManager(connected={self.connected_count()}, bot_id={self._telegram_bot_id})"
