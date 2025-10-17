import logging
from telegram.ext import ContextTypes
from datetime import datetime, timedelta, timezone
from fiturBot.attendance_bot import AttendanceBot
from fiturBot.handlers.topic_utils import send_to_announcement_topic, send_to_assignment_topic
from config import GROUP_CHAT_ID, GOOGLE_MEET_LINK
from config import ANNOUNCEMENT_TOPIC_ID, TOPIC_NAMES, ASSIGNMENT_TOPIC_ID, ATTENDANCE_TOPIC_ID


logger = logging.getLogger(__name__)

WIB = timezone(timedelta(hours=7))

async def auto_check_attendance(context: ContextTypes.DEFAULT_TYPE):
    """Fungsi otomatis untuk mengecek dan mengeluarkan murid"""
    try:
        # Validasi GROUP_CHAT_ID
        if not GROUP_CHAT_ID or not isinstance(GROUP_CHAT_ID, int):
            logger.error("❌ GROUP_CHAT_ID tidak valid untuk auto_check_attendance")
        bot = AttendanceBot()
        students_to_kick, students_to_warn = bot.check_auto_kick_conditions()
        
        # Kirim peringatan ke grup
        if students_to_warn and len(students_to_warn) > 0:
            warning_message = "🚨 **PERINGATAN KEHADIRAN** 🚨\n\n"
            for student in students_to_warn:
                warning_message += (
                    f"👤 {student['nama']} - Izin: {student['total_izin']}x, Alpha: {student['total_alpha']}x\n"
                )
            warning_message += "\n⚠️ Hadiri pertemuan selanjutnya!\nKarena 3x Alpha atau 3x Izin akan otomatis dikeluarkan dari grup"
            
            await context.bot.send_message(
                chat_id=GROUP_CHAT_ID,
                text=warning_message
            )
        
        # Keluarkan murid yang memenuhi syarat
        for student in students_to_kick:
            try:
                await context.bot.ban_chat_member(
                    chat_id=GROUP_CHAT_ID,
                    user_id=int(student['telegram_id'])
                )
                logger.info(f"Murid {student['nama']} dikeluarkan: {student['alasan']}")
            except Exception as e:
                logger.error(f"Error kicking student {student['nama']}: {e}")
                
    except Exception as e:
        logger.error(f"Error in auto_check_attendance: {e}")

async def periodic_check(context: ContextTypes.DEFAULT_TYPE):
    """Pengecekan periodik"""
    await auto_check_attendance(context)

async def send_classroom_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Mengirim reminder untuk tugas yang belum dikumpulkan"""
    try:
        bot = AttendanceBot()
        
        if bot.classroom_manager is None:
            logger.warning("Google Classroom tidak tersedia, skip reminder")
            return
        
        unsubmitted_assignments = bot.classroom_manager.get_unsubmitted_assignments()
        
        if not unsubmitted_assignments:
            message = "✅ **SEMUA TUGAS TELAH DIKUMPULKAN!**\n\nSelamat! Semua siswa telah mengumpulkan tugas mereka. 🎉"
        else:
            message = "📚 **REMINDER TUGAS GOOGLE CLASSROOM**\n\n"
            message += "⚠️ **Siswa yang belum mengumpulkan tugas:**\n\n"
            
            for student, assignments in unsubmitted_assignments.items():
                message += f"👤 **{student}**\n"
                for assignment in assignments:
                    message += f"   • {assignment}\n"
                message += "\n"
            
            message += "📌 **Segera kumpulkan sebelum deadline!**"

        logger.info(f"🔔 Sending class reminder to topic: {ASSIGNMENT_TOPIC_ID} ({TOPIC_NAMES.get(ASSIGNMENT_TOPIC_ID, 'Unknown')})")

        # Kirim ke topik TUGAS
        await send_to_assignment_topic(context, message)
        logger.info("✅ Classroom reminder sent successfully")
        
    except Exception as e:
        logger.error(f"Error sending classroom reminder: {e}")


async def send_class_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Mengirim reminder kelas hari Senin ke topik PENGUMUMAN & INFO"""
    try:
        # Dapatkan tanggal Senin ini dan Senin depan
        today = datetime.now(WIB)

        # Cek apakah hari ini Senin (0 = Monday, 6 = Sunday)
        is_monday = today.weekday() == 0
        
        # Cari Senin terdekat (hari ini jika Senin, atau Senin depan)
        days_ahead = 0 - today.weekday()  # 0 = Monday
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        
        next_monday = today + timedelta(days=days_ahead)
        
        # Format tanggal Indonesia
        month_names = {
            1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
            7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
        }
        
        formatted_date = f"{next_monday.day:02d} {month_names[next_monday.month]} {next_monday.year}"
        
        #Pilih pesan berdasarkan hari
        if is_monday:
            message = f"""🎉 Reminder!

🇷🇺✨ Привет, друзья!

Jangan lupa hari ini ada Kelas!  🥰

📅 Senin, {formatted_date}
🕖 Pukul 19.00 WIB (zona waktu lain menyesuaikan)
📍 Google Meet : {GOOGLE_MEET_LINK}

G-Meet akan dibuka 15 menit sebelum kelas dimulai

Siap kan buku catatan, semangat belajar, dan pastikan koneksi yang stabil!

До встречи в классе!
Have a nice day & спасибо! 🌟"""
            
        else: 
            message = f"""🎉 Reminder!

🇷🇺✨ Привет, друзья!

Jangan lupa Besok ada Kelas!  🥰

📅 Senin, {formatted_date}
🕖 Pukul 19.00 WIB (zona waktu lain menyesuaikan)
📍 Google Meet : {GOOGLE_MEET_LINK}

\033G-Meet akan dibuka 15 menit sebelum kelas dimulai\033 

Siap kan buku catatan, semangat belajar, dan pastikan koneksi yang stabil!

До встречи в классе!
Have a nice day & спасибо! 🌟"""
        
        # DEBUG: Log topic yang digunakan
        logger.info(f"🔔 Sending class reminder to topic: {ANNOUNCEMENT_TOPIC_ID} ({TOPIC_NAMES.get(ANNOUNCEMENT_TOPIC_ID, 'Unknown')})")

        # Kirim ke topik PENGUMUMAN & INFO
        await send_to_announcement_topic(context, message)
        logger.info(f"✅ Class reminder sent to PENGUMUMAN & INFO topic (ID: {ANNOUNCEMENT_TOPIC_ID})")
        
    except Exception as e:
        logger.error(f"Error sending class reminder: {e}")

async def reminder_tugas_classroom(context: ContextTypes.DEFAULT_TYPE):
    """Fungsi reminder tugas classroom yang dijalankan setiap hari"""
    try:
        bot = AttendanceBot()
        
        if bot.classroom_manager is None:
            logger.warning("Google Classroom tidak tersedia, skip daily reminder")
            return
        
        # Dapatkan tugas yang mendekati deadline
        upcoming_assignments = bot.classroom_manager.get_upcoming_assignments()
        
        # Dapatkan tugas yang terlambat
        overdue_assignments = bot.classroom_manager.get_overdue_assignments()
        
        current_time = datetime.now(WIB)
        current_date = current_time.strftime("%d %B %Y")
        current_hour = current_time.strftime("%H:%M WIB")
        
        message = f"📚 **REMINDER TUGAS HARIAN** 📚\n\n"
        message += f"🕐 {current_date} - {current_hour}\n\n"
        
        if not upcoming_assignments and not overdue_assignments:
            message += "✅ **Tidak ada tugas yang perlu diingatkan!**\n\n"
            message += "Semua tugas sudah dikumpulkan atau tidak ada deadline mendatang. Tetap semangat belajar! 🎉"
        else:
            # Tugas yang terlambat
            if overdue_assignments:
                message += "🔴 **TUGAS TERLAMBAT**\n"
                message += "Segera kumpulkan tugas-tugas berikut:\n\n"
                
                for assignment in overdue_assignments:
                    message += f"📌 **{assignment['title']}**\n"
                    message += f"   ⏰ Deadline: {assignment['due_date']}\n"
                    message += f"   📝 Deskripsi: {assignment['description'][:100]}...\n\n"
            
            # Tugas yang mendekati deadline
            if upcoming_assignments:
                message += "🟡 **TUGAS MENDATANG**\n"
                message += "Persiapkan tugas-tugas berikut:\n\n"
                
                for assignment in upcoming_assignments:
                    message += f"📌 **{assignment['title']}**\n"
                    message += f"   ⏰ Deadline: {assignment['due_date']}\n"
                    message += f"   📝 Deskripsi: {assignment['description'][:100]}...\n\n"
            
            # Tips motivasi
            motivation_tips = [
                "💡 **Tips**: Kerjakan tugas sedikit demi sedikit setiap hari!",
                "🎯 **Motivasi**: Jangan tunda sampai besok, mulailah hari ini!",
                "🌟 **Pengingat**: Kumpulkan tepat waktu untuk nilai maksimal!",
                "📖 **Saran**: Baca ulang instruksi tugas sebelum mengerjakan!"
            ]
            
            import random
            message += random.choice(motivation_tips)
        
        # Kirim reminder ke topik TUGAS
        logger.info(f"🔔 Sending daily classroom reminder to topic: {ASSIGNMENT_TOPIC_ID}")
        await send_to_assignment_topic(context, message)
        logger.info("✅ Daily classroom reminder sent successfully")
        
    except Exception as e:
        logger.error(f"Error in reminder_tugas_classroom: {e}")

async def reminder_tugas_mingguan(context: ContextTypes.DEFAULT_TYPE):
    """Fungsi reminder tugas mingguan (setiap Senin)"""
    try:
        bot = AttendanceBot()
        
        if bot.classroom_manager is None:
            logger.warning("Google Classroom tidak tersedia, skip weekly reminder")
            return
        
        # Dapatkan semua tugas aktif
        all_assignments = bot.classroom_manager.get_all_active_assignments()
        
        current_time = datetime.now(WIB)
        current_date = current_time.strftime("%d %B %Y")
        
        message = f"📋 **REKAP TUGAS MINGGU INI** 📋\n\n"
        message += f"📅 {current_date}\n\n"
        
        if not all_assignments:
            message += "🎉 **Tidak ada tugas untuk minggu ini!**\n\n"
            message += "Gunakan waktu luang untuk review materi atau istirahat yang cukup! 😊"
        else:
            # Kelompokkan tugas berdasarkan status
            upcoming = [a for a in all_assignments if a.get('status') == 'upcoming']
            ongoing = [a for a in all_assignments if a.get('status') == 'ongoing']
            overdue = [a for a in all_assignments if a.get('status') == 'overdue']
            
            total_tugas = len(all_assignments)
            
            message += f"📊 **Statistik Tugas:**\n"
            message += f"   • Total: {total_tugas} tugas\n"
            message += f"   • Mendatang: {len(upcoming)} tugas\n"
            message += f"   • Berjalan: {len(ongoing)} tugas\n"
            message += f"   • Terlambat: {len(overdue)} tugas\n\n"
            
            if overdue:
                message += "🔴 **PRIORITAS TINGGI (Terlambat)**\n"
                for assignment in overdue[:3]:  # Tampilkan max 3
                    message += f"   ⚠️ {assignment['title']}\n"
                message += "\n"
            
            if ongoing:
                message += "🟡 **SEDANG BERJALAN**\n"
                for assignment in ongoing[:3]:  # Tampilkan max 3
                    message += f"   📌 {assignment['title']}\n"
                    if assignment.get('due_date'):
                        message += f"     ⏰ {assignment['due_date']}\n"
                message += "\n"
            
            if upcoming:
                message += "🟢 **AKAN DATANG**\n"
                for assignment in upcoming[:3]:  # Tampilkan max 3
                    message += f"   📌 {assignment['title']}\n"
                    if assignment.get('due_date'):
                        message += f"     ⏰ {assignment['due_date']}\n"
            
            message += "\n💪 **Semangat mengerjakan tugas! Jangan menunda-nunda!**"
        
        # Kirim reminder mingguan ke topik TUGAS
        logger.info(f"🔔 Sending weekly classroom reminder to topic: {ASSIGNMENT_TOPIC_ID}")
        await send_to_assignment_topic(context, message)
        logger.info("✅ Weekly classroom reminder sent successfully")
        
    except Exception as e:
        logger.error(f"Error in reminder_tugas_mingguan: {e}")


async def periodic_check(context: ContextTypes.DEFAULT_TYPE):
    """Pengecekan periodik"""
    await auto_check_attendance(context)

