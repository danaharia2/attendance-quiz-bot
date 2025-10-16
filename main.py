# main.py (Railway version - kembali ke polling)
import logging
import traceback
import os
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from datetime import time
from telegram import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def setup_bot_commands(application):
    """Setup bot commands menu untuk semua user"""
    try:
        # Commands untuk private chats
        private_commands = [
            BotCommand("start", "Memulai Bot"),
            BotCommand("help", "Membuka pesan bantuan"),
            BotCommand("mulai", "Memulai permainan"),
            BotCommand("nyerah", "Menyerah dari pertanyaan"),
            BotCommand("next", "Pertanyaan berikutnya"),
            BotCommand("skor", "Melihat skor saat ini"),
            BotCommand("poin", "Melihat poin kamu"),
            BotCommand("topskor", "Melihat 10 pemain teratas"),
            BotCommand("aturan", "Melihat aturan bermain"),
            BotCommand("donasi", "Dukungan untuk bot"),
            BotCommand("lapor", "Laporkan pertanyaan"),
            BotCommand("quiz", "Menu utama tebak-tebakan"),
        ]
        # Commands untuk group chats
        group_commands = [
            BotCommand("mulai", "Memulai permainan"),
            BotCommand("skor", "Melihat skor saat ini"),
            BotCommand("topskor", "Melihat 10 pemain teratas"),
            BotCommand("aturan", "Melihat aturan bermain"),
            BotCommand("help", "Membuka pesan bantuan"),
            BotCommand("quiz", "Menu utama tebak-tebakan"),
        ]
        # Admin commands
        admin_commands = private_commands + [BotCommand("buat", "Buat pertanyaan (Admin)")]

        # Set commands untuk private chats
        await application.bot.set_my_commands(
            private_commands,
            scope=BotCommandScopeAllPrivateChats()
        )
        logger.info("✅ Private chat commands setup completed")

        # Set commands untuk group chats
        await application.bot.set_my_commands(
            group_commands,
            scope=BotCommandScopeAllGroupChats()
        )
        logger.info("✅ Group chat commands setup completed")

        # Set commands khusus untuk admin
        from config import ADMIN_IDS
        from telegram import BotCommandScopeChat
        
        for admin_id in ADMIN_IDS:
            try:
                await application.bot.set_my_commands(
                    admin_commands,
                    scope=BotCommandScopeChat(admin_id)
                )
                logger.info(f"✅ Admin commands setup for {admin_id}")
                
            except Exception as e:
                logger.warning(f"⚠️ Could not set admin commands for {admin_id}: {e}")
    except Exception as e:
        logger.error(f"❌ Error setting bot commands: {e}")

def main():
    """Main function - Railway version (polling)"""
    try:
        # Import config
        from config import validate_config, BOT_TOKEN
        if not validate_config():
            logger.error("❌ Config validation failed")
            return
        
        # Test connections
        logger.info("🔧 Testing connections...")
        try:
            from fiturBot.attendance_bot import AttendanceBot
            bot = AttendanceBot()
            df = bot.get_student_data()
            logger.info(f"✅ Connected to Google Sheets - {len(df)} records")
        except Exception as e:
            logger.error(f"❌ Error testing connections: {e}")
            # Continue anyway, as some features might still work
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Setup bot commands menu
        application.post_init = setup_bot_commands
        
        # Import handlers
        try:
            from fiturBot.handlers import (
                start, status, test_connection, get_my_info, register, absen, test_classroom, get_all_member_ids, get_simple_member_ids,
                admin_help, admin_stats, reset_attendance, force_attendance_check, export_data,
                manual_kick, list_warnings, list_kehadiran, classroom_reminder_now, class_reminder_now, check_topics, 
                materi, materi1, materi2, start_auto_reminder, stop_auto_reminder, test_auto_reminder, materi3
            )
            
            # Add command handlers
            commands = [
                ("start", start),
                ("absen", absen),
                ("status", status),
                ("test", test_connection),
                ("myinfo", get_my_info),
                ("register", register),
                ("materi", materi),
                ("materi1", materi1),
                ("materi2", materi2),
                ("materi3", materi3),
                ("admin_help", admin_help),
                ("admin_stats", admin_stats),
                ("reset_attendance", reset_attendance),
                ("force_check", force_attendance_check),
                ("export_data", export_data),
                ("manual_kick", manual_kick),
                ("list_warnings", list_warnings),
                ("list_kehadiran", list_kehadiran),
                ("classroom_reminder", classroom_reminder_now),
                ("test_classroom", test_classroom),
                ("class_reminder", class_reminder_now),
                ("check_topics", check_topics),
                ("start_reminder", start_auto_reminder),
                ("stop_reminder", stop_auto_reminder),
                ("test_reminder", test_auto_reminder),
                ("get_all_member", get_all_member_ids),
                ("get_ids", get_simple_member_ids),
            ]
            
            for command, handler in commands:
                application.add_handler(CommandHandler(command, handler))
                logger.info(f"✅ Added handler: /{command}")
                
        except ImportError as e:
            logger.error(f"❌ Error importing handlers: {e}")
            return
        except Exception as e:
            logger.error(f"❌ Error setting up handlers: {e}")
            logger.error(traceback.format_exc())
        
        # Import dan setup quiz handlers
        try:
            from fiturBot.quiz_handler import (
                start_command, help_command, quiz, quiz_callback_handler, handle_quiz_message,
                quiz_help, start_quiz, surrender_quiz, next_question, 
                show_score, show_points, top_score, quiz_rules, 
                quiz_donate, quiz_report, create_question_start, quiz_stats, add_question_handler
            )
            
            # Add quiz command handlers
            quiz_commands = [
                 ("start", start_command),
                 ("help", help_command),
                 ("quiz", quiz),
                 ("mulai", start_quiz),
                 ("nyerah", surrender_quiz),
                 ("next", next_question),
                 ("skor", show_score),
                 ("poin", show_points),
                 ("topskor", top_score),
                 ("aturan", quiz_rules),
                 ("stats", quiz_stats),
                 ("tambah_pertanyaan", add_question_handler),
                 ("donasi", quiz_donate),
                 ("lapor", quiz_report),
                 ("buat", create_question_start),
             ]
            
            for command, handler in quiz_commands:
                application.add_handler(CommandHandler(command, handler))
                logger.info(f"✅ Added quiz handler: /{command}")

            application.add_handler(MessageHandler(
                filters.TEXT & ~filters.COMMAND, 
                handle_quiz_message
            ), group=1)
            logger.info("✅ Added quiz message handler")
            
            application.add_handler(CallbackQueryHandler(quiz_callback_handler, pattern="^quiz_"))
            logger.info("✅ Added quiz callback handler")
        
        except Exception as e:
            logger.error(f"❌ Error setting up quiz handlers: {e}")
        
        # Setup job queue for scheduled tasks
        if application.job_queue:
            try:
                from auto_functions import periodic_check, send_classroom_reminder, send_class_reminder
                
                # Schedule tasks
                application.job_queue.run_daily(periodic_check, time=time(hour=8, minute=0))
                application.job_queue.run_daily(periodic_check, time=time(hour=18, minute=0))
                application.job_queue.run_daily(send_classroom_reminder, time=time(hour=10, minute=0))
                application.job_queue.run_daily(send_class_reminder, time=time(hour=18, minute=0), days=(6,))
                application.job_queue.run_daily(send_class_reminder, time=time(hour=10, minute=0), days=(0,))
                
                logger.info("✅ Scheduled tasks configured")
            except Exception as e:
                logger.error(f"❌ Error setting up scheduled tasks: {e}")
        
        logger.info("🚄 Starting bot on Railway (polling mode)...")
        
        # Start polling - Railway works best with polling
        application.run_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot failed: {e}")
        logger.error(traceback.format_exc())

if __name__ == '__main__':
    main()