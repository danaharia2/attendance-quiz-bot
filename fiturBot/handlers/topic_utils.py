import logging
from telegram.ext import ContextTypes
from config import GROUP_CHAT_ID, ANNOUNCEMENT_TOPIC_ID, ASSIGNMENT_TOPIC_ID, ATTENDANCE_TOPIC_ID

logger = logging.getLogger(__name__)

async def send_to_announcement_topic(context: ContextTypes.DEFAULT_TYPE, message: str, parse_mode='Markdown'):
    """Mengirim pesan ke topik PENGUMUMAN & INFO"""
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=ANNOUNCEMENT_TOPIC_ID,
            text=message,
            parse_mode=parse_mode
        )
        logger.info(f"✅ Pesan terkirim ke topik PENGUMUMAN & INFO")
    except Exception as e:
        logger.error(f"Error sending to announcement topic: {e}")
        # Fallback ke regular message
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=message,
            parse_mode=parse_mode
        )

async def send_to_assignment_topic(context: ContextTypes.DEFAULT_TYPE, message: str, parse_mode='Markdown'):
    """Mengirim pesan ke topik TUGAS"""
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=ASSIGNMENT_TOPIC_ID,
            text=message,
            parse_mode=parse_mode
        )
        logger.info(f"✅ Pesan terkirim ke topik TUGAS")
    except Exception as e:
        logger.error(f"Error sending to assignment topic: {e}")
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=message,
            parse_mode=parse_mode
        )

async def send_to_attendance_topic(context: ContextTypes.DEFAULT_TYPE, message: str, parse_mode='Markdown'):
    """Mengirim pesan ke topik Perihal Absensi Kelas"""
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=ATTENDANCE_TOPIC_ID,
            text=message,
            parse_mode=parse_mode
        )
        logger.info(f"✅ Pesan terkirim ke topik Absensi")
    except Exception as e:
        logger.error(f"Error sending to attendance topic: {e}")
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=message,
            parse_mode=parse_mode
        )

