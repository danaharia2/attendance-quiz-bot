import os
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from config import SCOPES, CREDENTIALS_FILE, CLASSROOM_COURSE_ID

logger = logging.getLogger(__name__)

try:
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    GOOGLE_CLASSROOM_AVAILABLE = True
except ImportError:
    GOOGLE_CLASSROOM_AVAILABLE = False
    print("⚠️  Google Classroom API tidak tersedia. Fitur reminder tugas akan dinonaktifkan.")

class ClassroomManager:
    def __init__(self):
        if not GOOGLE_CLASSROOM_AVAILABLE:
            raise ImportError("Google Classroom API tidak terinstall")
        self.service = None
        self.setup_classroom()
    
    def setup_classroom(self):
        """Setup koneksi ke Google Classroom"""
        try:
            logger.info("Memulai koneksi ke Google Classroom...")
            
            # Validasi file credentials
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"File {CREDENTIALS_FILE} tidak ditemukan!")
            
            # Setup credentials dan koneksi
            creds = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
            self.service = build('classroom', 'v1', credentials=creds)
            
            logger.info("✅ Berhasil terhubung ke Google Classroom!")
            
        except Exception as e:
            logger.error(f"❌ Error connecting to Google Classroom: {e}")
            raise
    
    def get_unsubmitted_assignments(self):
        """Mendapatkan daftar siswa yang belum mengumpulkan tugas"""
        try:
            # Dapatkan daftar course work (tugas)
            course_work = self.service.courses().courseWork().list(
                courseId=CLASSROOM_COURSE_ID
            ).execute()
            logger.info(f"📋 Found {len(course_work.get('courseWork', []))} assignments")
            
            unsubmitted_students = {}
            
            for work in course_work.get('courseWork', []):
                work_title = work['title']
                work_id = work['id']

                logger.info(f"📝 Checking assignment: {work_title}")
                
                # Dapatkan submission untuk setiap tugas
                submissions = self.service.courses().courseWork().studentSubmissions().list(
                    courseId=CLASSROOM_COURSE_ID,
                    courseWorkId=work_id
                ).execute()
                logger.info(f"   📊 Found {len(submissions.get('studentSubmissions', []))} submissions")
                
                # Cek siswa yang belum submit
                for submission in submissions.get('studentSubmissions', []):
                    if submission['state'] != 'TURNED_IN':
                        student_id = submission['userId']
                        
                        # Dapatkan info siswa
                        try:
                            student = self.service.courses().students().get(
                            courseId=CLASSROOM_COURSE_ID,
                            userId=student_id
                            ).execute()
                        
                            student_name = student['profile']['name']['fullName']
                        
                            if student_name not in unsubmitted_students:
                                unsubmitted_students[student_name] = []
                        
                            unsubmitted_students[student_name].append(work_title)
                        
                        except Exception as e:
                            logger.error(f"❌ Error getting student info: {e}")
                            continue
            
            logger.info(f"🎯 Unsubmitted assignments: {len(unsubmitted_students)} students")
            return unsubmitted_students
            
        except Exception as e:
            logger.error(f"Error getting unsubmitted assignments: {e}")
            return {}

    """    
    def get_upcoming_assignments(self, days=3):
        \"\"\"Mendapatkan tugas yang deadline-nya dalam beberapa hari ke depan\"\"\"
        # Implementation: return assignments with due date within next 'days' days
        pass

    def get_overdue_assignments(self):
        \"\"\"Mendapatkan tugas yang sudah melewati deadline\"\"\"
        # Implementation: return assignments that are past due date
        pass

    def get_all_active_assignments(self):
        \"\"\"Mendapatkan semua tugas yang masih aktif\"\"\"
        # Implementation: return all active assignments
        pass
    """