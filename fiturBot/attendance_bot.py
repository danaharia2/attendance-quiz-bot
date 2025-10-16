import gspread
import pandas as pd
import os
import logging
import schedule
import time
from google.oauth2.service_account import Credentials
from config import SCOPES, CREDENTIALS_FILE, SPREADSHEET_URL, WORKSHEET_NAME, CLASSROOM_COURSE_ID
from .classroom_manager import ClassroomManager
from datetime import datetime
from threading import Thread
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class AttendanceBot:
    def __init__(self):
        self.gc = None
        self.worksheet = None
        self.classroom_manager = None
        self.classroom_service = None
        self.setup_sheets()
        self.setup_classroom()
    
    def setup_sheets(self):
        """Setup koneksi ke Google Sheets"""
        try:
            logger.info("Memulai koneksi ke Google Sheets...")
            
            # Validasi file credentials
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"File {CREDENTIALS_FILE} tidak ditemukan!")
            
            # Setup credentials dan koneksi
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            self.gc = gspread.authorize(creds)
            self.worksheet = self.gc.open_by_url(SPREADSHEET_URL).worksheet(WORKSHEET_NAME)
            
            logger.info("✅ Berhasil terhubung ke Google Sheets!")
            
        except Exception as e:
            logger.error(f"❌ Error connecting to Google Sheets: {e}")
            raise
    
    def setup_classroom(self):
        """Setup koneksi ke Google Classroom"""
        try:
            self.classroom_manager = ClassroomManager()
        except Exception as e:
            logger.warning(f"Google Classroom tidak tersedia: {e}")
            self.classroom_manager = None
    
    def get_credentials(self):
        """Mendapatkan credentials untuk Google API"""
        try:
            return Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            return None
    
    def get_student_data(self):
        """Mengambil data murid dari spreadsheet dan konversi tipe data"""
        try:
            data = self.worksheet.get_all_records()
            df = pd.DataFrame(data)

            # Konversi kolom numerik dari string ke integer
            numeric_columns = ['Total Alpha', 'Total Izin', 'Telegram ID']

            for col in numeric_columns:
                if col in df.columns:
                    try:
                        # Coba konversi langsung ke numeric
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
                    except:
                        # Jika gagal, bersihkan string terlebih dahulu
                        df[col] = pd.to_numeric(
                            df[col].astype(str).str.replace('[^0-9.-]', '', regex=True), 
                            errors='coerce'
                        ).fillna(0).astype(int)

            logger.info(f"📊 Berhasil membaca {len(df)} records")
            logger.info(f"📈 Sample data - Alpha: {df['Total Alpha'].iloc[0] if len(df) > 0 else 'N/A'}, Izin: {df['Total Izin'].iloc[0] if len(df) > 0 else 'N/A'}")
            return df
        
        except Exception as e:
            logger.error(f"Error getting student data: {e}")
            return pd.DataFrame()
    
    def update_student_record(self, telegram_id, status):
        """Update record kehadiran murid (simpan data angka)"""
        try:
            df = self.get_student_data()
            if df.empty:
                return False
            
            # Cari baris berdasarkan Telegram ID
            for idx, row in df.iterrows():
                if str(row['Telegram ID']) == str(telegram_id):
                    # Konversi nilai saat ini ke integer (pastikan angka)
                    current_alpha = int(row['Total Alpha']) if pd.notna(row['Total Alpha']) else 0
                    current_izin = int(row['Total Izin']) if pd.notna(row['Total Izin']) else 0

                    # Update total alpha atau izin berdasarkan status
                    if status == 'Alpha':
                        # Update Total Alpha (angka) dan Status Terakhir (teks)
                        new_alpha = current_alpha + 1
                        self.worksheet.update_cell(idx + 2, 5, new_alpha)  # Kolom D: Total Alpha (angka)
                        self.worksheet.update_cell(idx + 2, 7, 'Alpha')     # Kolom F: Status Terakhir (teks)
                        logger.info(f"✅ Updated Alpha for {row['Nama']}: {current_alpha} → {new_alpha}")

                    elif status == 'Izin':
                        # Update Total Izin (angka) dan Status Terakhir (teks)
                        new_izin = current_izin + 1
                        self.worksheet.update_cell(idx + 2, 6, new_izin)   # Kolom E: Total Izin (angka)
                        self.worksheet.update_cell(idx + 2, 7, 'Izin')     # Kolom F: Status Terakhir (teks)
                        logger.info(f"✅ Updated Izin for {row['Nama']}: {current_izin} → {new_izin}")

                    # Untuk status 'Hadir', hanya update status terakhir saja
                    elif status == 'Hadir':
                        # Hanya update Status Terakhir (teks), angka tetap
                        self.worksheet.update_cell(idx + 2, 7, 'Hadir')    # Kolom F: Status Terakhir (teks)
                        logger.info(f"✅ Updated status for {row['Nama']}: Hadir")
                    
                    logger.info(f"✅ Updated record for {row['Nama']}: {status}")
                    return True
            
            logger.warning(f"❌ Telegram ID {telegram_id} tidak ditemukan")
            return False
            
        except Exception as e:
            logger.error(f"Error updating student record: {e}")
            return False

    def check_auto_kick_conditions(self):
        """Memeriksa kondisi untuk mengeluarkan murid secara otomatis"""
        try:
            df = self.get_student_data()
            students_to_kick = []
            students_to_warn = []
            
            for _, student in df.iterrows():
                telegram_id = student['Telegram ID']
                total_alpha = int(student['Total Alpha']) if pd.notna(student['Total Alpha']) else 0
                total_izin = int(student['Total Izin']) if pd.notna(student['Total Izin']) else 0
                nama = student['Nama']
                
                # Kick: Alpha dan Izin 3 kali
                if total_alpha >= 3 or total_izin >= 3:
                    students_to_kick.append({
                        'telegram_id': telegram_id,
                        'nama': nama,
                        'alasan': f" Sudah Alpha {total_alpha} kali"
                    })

                if total_alpha >= 2 and total_izin >= 2:
                    students_to_kick.append({
                        'telegram_id': telegram_id,
                        'nama': nama,
                        'alasan': f"Sudah Alpha {total_alpha} kali dan Izin {total_izin} kali "
                    })
                
                # Peringatan: Izin 2 kali dan Alpha 2 kali
                if total_izin >= 2 or total_alpha >= 2:
                    students_to_warn.append({
                        'telegram_id': telegram_id,
                        'nama': nama,
                        'total_izin': total_izin,
                        'total_alpha': total_alpha
                    })

            logger.info(f"🔍 Auto-kick check: {len(students_to_kick)} akan dikick, {len(students_to_warn)} peringatan")
            return students_to_kick, students_to_warn
        
        except Exception as e:
            logger.error(f"Error checking auto-kick conditions: {e}")
            return [], []

    def reset_daily_attendance(self):
        """Reset status kehadiran harian"""
        try:
            df = self.get_student_data()
            for idx, row in df.iterrows():
                self.worksheet.update_cell(idx + 2, 7, 'Belum Absen')  # Reset status terakhir (kolom 7)
            logger.info("Status kehadiran harian direset")
        except Exception as e:
            logger.error(f"Error resetting attendance: {e}")

    def get_student_emails(self):
        """Ambil daftar email siswa dari spreadsheet"""
        df = self.get_student_data()
        # Filter hanya siswa yang memiliki email
        students_with_email = df[df['Email'].notna() & (df['Email'] != '')]
        return students_with_email['Email'].tolist()

    def initialize_classroom_service(self):
        """Inisialisasi Google Classroom service"""
        try:
            if not hasattr(self, 'classroom_service') or self.classroom_service is None:
                creds = self.get_credentials()
                if creds:
                    self.classroom_service = build('classroom', 'v1', credentials=creds)
            return self.classroom_service
        except Exception as e:
            logger.error(f"Error initializing Classroom service: {e}")
            return None
    
    def get_students_without_submission(self, course_id, coursework_id):
        """Dapatkan siswa yang belum mengumpulkan tugas berdasarkan email di spreadsheet"""
        try:
            # Dapatkan email siswa yang terdaftar
            student_emails = self.get_student_emails()
        
            if not student_emails:
                return [], "Tidak ada email siswa yang terdaftar di spreadsheet"
        
            # Inisialisasi classroom service
            classroom_service = self.initialize_classroom_service()
            if not classroom_service:
                return [], "Gagal menginisialisasi Classroom service"
        
            # Dapatkan submission dari Classroom - PERBAIKAN: gunakan classroom_service yang sudah didefinisikan
            submissions_result = classroom_service.courses().courseWork().studentSubmissions().list(
                courseId=course_id,
                courseWorkId=coursework_id
            ).execute()
        
            submitted_emails = []
            if submissions_result.get('studentSubmissions'):
                for submission in submissions_result['studentSubmissions']:
                    # Dapatkan email student dari submission
                    student_profile = classroom_service.userProfiles().get(
                        userId=submission['userId']
                    ).execute()
                    student_email = student_profile.get('emailAddress', '')
                    if student_email:
                        submitted_emails.append(student_email.lower())
        
            # Cari siswa yang terdaftar tapi belum submit
            students_without_submission = []
            for email in student_emails:
                if email.lower() not in submitted_emails:
                    students_without_submission.append(email)
        
            return students_without_submission, f"Berhasil memeriksa {len(student_emails)} siswa terdaftar"
        
        except Exception as e:
            logger.error(f"Error checking submissions: {e}")
            return [], f"Error: {str(e)}"


class ClassroomAutoReminder:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.running = False
        self.reminder_thread = None
    
    def get_all_coursework(self, course_id):
        """Ambil semua tugas dari course tertentu"""
        try:
            classroom_service = self.bot.initialize_classroom_service()
            if not classroom_service:
                return []
                
            coursework = classroom_service.courses().courseWork().list(
                courseId=course_id
            ).execute()
            
            active_assignments = []
            if coursework.get('courseWork'):
                for assignment in coursework['courseWork']:
                    # Cek apakah tugas masih aktif (belum lewat due date)
                    if assignment.get('dueDate'):
                        due_date = datetime(
                            assignment['dueDate']['year'],
                            assignment['dueDate']['month'], 
                            assignment['dueDate']['day']
                        )
                        # Jika due date masih di masa depan atau hari ini
                        if due_date >= datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
                            active_assignments.append(assignment)
            
            return active_assignments
        except Exception as e:
            logger.error(f"Error getting coursework: {e}")
            return []
    
    def get_students_without_submission_for_coursework(self, course_id, coursework_id):
        """Dapatkan siswa yang belum mengumpulkan tugas tertentu"""
        try:
            student_emails = self.bot.get_student_emails()
            
            if not student_emails:
                return [], "Tidak ada email siswa terdaftar"
            
            # Dapatkan submission
            classroom_service = self.bot.initialize_classroom_service()
            if not classroom_service:
                return [], "Gagal menginisialisasi Classroom service"
                
            submissions_result = classroom_service.courses().courseWork().studentSubmissions().list(
                courseId=course_id,
                courseWorkId=coursework_id
            ).execute()
            
            submitted_emails = []
            if submissions_result.get('studentSubmissions'):
                for submission in submissions_result['studentSubmissions']:
                    if submission['state'] == 'TURNED_IN' or submission['state'] == 'RETURNED':
                        student_profile = classroom_service.userProfiles().get(
                            userId=submission['userId']
                        ).execute()
                        student_email = student_profile.get('emailAddress', '')
                        if student_email:
                            submitted_emails.append(student_email.lower())
            
            # Siswa yang belum submit
            students_without_submission = []
            for email in student_emails:
                if email.lower() not in submitted_emails:
                    students_without_submission.append(email)
            
            return students_without_submission, "Berhasil memeriksa"
            
        except Exception as e:
            logger.error(f"Error checking submissions: {e}")
            return [], f"Error: {str(e)}"
    
    def format_reminder_message(self, assignment, late_students, course_id):
        """Format pesan reminder yang akan dikirim ke grup"""
        due_date = f"{assignment['dueDate']['day']}/{assignment['dueDate']['month']}/{assignment['dueDate']['year']}"
        
        # Dapatkan data siswa yang terlambat
        df = self.bot.get_student_data()
        late_students_data = df[df['Email'].isin(late_students)]
        
        student_list = []
        for _, student in late_students_data.iterrows():
            student_info = f"• {student['Nama']}"
            if student.get('Username') and student['Username'] != '-':
                student_info += f" (@{student['Username'].replace('@', '')})"
            student_list.append(student_info)
        
        message = (
            f"📢 **REMINDER TUGAS CLASSROOM**\n\n"
            f"📚 **Tugas:** {assignment['title']}\n"
            f"⏰ **Deadline:** {due_date}\n"
            f"❌ **Belum mengumpulkan:** {len(late_students)} siswa\n\n"
        )
        
        if late_students:
            message += f"**Siswa yang belum mengumpulkan:**\n{chr(10).join(student_list)}\n\n"
        
        days_left = (datetime(
            assignment['dueDate']['year'],
            assignment['dueDate']['month'],
            assignment['dueDate']['day']
        ) - datetime.now()).days
        
        if days_left == 0:
            message += "🚨 **HARI INI BATAS AKHIR PENGUMPULAN!**\n"
        elif days_left == 1:
            message += "⚠️ **BESOK BATAS AKHIR PENGUMPULAN!**\n"
        elif days_left > 1:
            message += f"📅 **Sisa waktu: {days_left} hari**\n"
        else:
            message += "❌ **TUGAS SUDAH MELEWATI BATAS WAKTU**\n"
        
        message += f"\n🔗 **Link Tugas:** https://classroom.google.com/c/{course_id}/a/{assignment['id']}/details"
        
        return message
    
    def send_reminder_to_group(self, context, chat_id, message):
        """Kirim reminder ke grup"""
        try:
            context.bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info(f"Reminder sent to group {chat_id}")
        except Exception as e:
            logger.error(f"Error sending reminder: {e}")
    
    def check_and_send_reminders(self, context, course_id, group_chat_id):
        """Cek semua tugas aktif dan kirim reminder"""
        try:
            assignments = self.get_all_coursework(course_id)
            
            if not assignments:
                logger.info("No active assignments found")
                return
            
            for assignment in assignments:
                late_students, status_msg = self.get_students_without_submission_for_coursework(
                    course_id, assignment['id']
                )
                
                if late_students:
                    reminder_message = self.format_reminder_message(
                        assignment, late_students, course_id
                    )
                    self.send_reminder_to_group(context, group_chat_id, reminder_message)
                
                # Tunggu sebentar antara setiap tugas
                time.sleep(2)
                    
        except Exception as e:
            logger.error(f"Error in auto reminder: {e}")
    
    def should_send_reminder(self):
        """Cek apakah sekarang jam 08:00 atau 18:00"""
        now = datetime.now()
        current_hour = now.hour
        current_minute = now.minute
        
        # Kirim hanya jam 08:00 atau 18:00 (dalam rentang 1 menit)
        return (current_hour == 8 and current_minute == 0) or (current_hour == 18 and current_minute == 0)
    
    def start_daily_reminders(self, context, course_id, group_chat_id):
        """Mulai reminder harian otomatis"""
        if self.running:
            return "Reminder sudah berjalan"
        
        self.running = True
        
        def reminder_job():
            last_reminder_date = None
            
            while self.running:
                try:
                    now = datetime.now()
                    
                    # Cek apakah sudah waktunya kirim reminder (08:00 atau 18:00)
                    if self.should_send_reminder():
                        # Cek apakah sudah kirim reminder hari ini di jam ini
                        today = now.date()
                        current_hour = now.hour
                        
                        if last_reminder_date != (today, current_hour):
                            self.check_and_send_reminders(context, course_id, group_chat_id)
                            last_reminder_date = (today, current_hour)
                            logger.info(f"Auto reminder sent at {now}")
                    
                    # Tunggu 55 detik sebelum cek lagi
                    time.sleep(55)
                        
                except Exception as e:
                    logger.error(f"Error in reminder job: {e}")
                    time.sleep(300)  # Tunggu 5 menit jika error
        
        self.reminder_thread = Thread(target=reminder_job)
        self.reminder_thread.daemon = True
        self.reminder_thread.start()
        
        return "✅ Reminder harian otomatis telah diaktifkan!\nBot akan mengecek setiap hari jam 08:00 dan 18:00"
    
    def stop_reminders(self):
        """Hentikan reminder otomatis"""
        self.running = False
        try:
            if self.reminder_thread:
                self.reminder_thread.join(timeout=5)
            return "❌ Reminder otomatis dihentikan"
        except Exception as e:
            logger.error(f"Error stopping reminders: {e}")
            return "❌ Error saat menghentikan reminder"