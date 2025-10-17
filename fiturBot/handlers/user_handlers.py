from telegram import Update
from telegram.ext import ContextTypes
import logging
from ..attendance_bot import AttendanceBot
from config import ADMIN_IDS
from datetime import datetime, timedelta, timezone
import random

logger = logging.getLogger(__name__)

WIB = timezone(timedelta(hours=7))
def get_wib_time():
    """Mendapatkan waktu sekarang dalam WIB"""
    return datetime.now(WIB)

def get_monday_wib():
    """Mendapatkan hari Senin minggu ini dalam WIB"""
    today = get_wib_time()
    # weekday() -> Senin=0, Minggu=6
    monday = today - timedelta(days=today.weekday())
    return monday

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk command /start"""
    user_id = update.effective_user.id

    #Base message untuk semua user
    message = (
        "Halo! Saya adalah bot yang dibuat Kak Dana untuk mengelola kehadiran murid Kelas Rusia Lvl1 Batch 11.\n\n"
        "Perintah yang tersedia:\n"
        "/materi - Rangkuman materi kelas\n"
        "/quiz - Ayuk mulai quiz\n"
        "/absen - Absen dengan pilihan status\n"
        "/status - Lihat status kehadiran\n"
        "/register - Buat pendaftaran ke sistem\n"
        "/myinfo - Lihat info Anda\n"
    )

    #Tambahkan perintah admin jika user adalah admin
    if user_id in ADMIN_IDS: 
        message += (
            "\nPERINTAH KHUSUS ADMIN:\n"
            "/admin_stats - Lihat statistik lengkap\n"
            "/reset_attendance - Reset data kehadiran\n"
            "/force_check - Paksa pengecekan kehadiran\n"
            "/export_data - Export data ke CSV\n"
            "/manual_kick - Keluarkan murid manual\n"
            "/list_kehadiran - Kirim laporan kehadiran ke grup\n"
            "/list_warnings - Lihat daftar peringatan\n"
            "`/start_reminder NzgxOTM4ODI5NTEz -1002408972369` - Memulai reminder classroom otomatis\n"
            "/stop_reminder - Memberhentikan reminder classroom otomatis\n"
            "/classroom_reminder - Kirim reminder tugas\n"
            "/class_reminder - Kirim reminder kelas\n"
            "/test - Test koneksi Google Sheets"
            "/check_topics - Cek informasi topik grup\n\n"
            "\n📝 Cara Penggunaan Admin:\n"
            "• `/reset_attendance confirm` - Reset semua data\n"
            "• `/manual_kick 123456789 Alpha 3x` - Kick murid\n"
            "• Gunakan `/force_check` untuk tes auto-kick\n"
            )
        
        message += (
            "\n💡 Tips:\n"
        "• Gunakan /register NamaLengkap untuk mendaftar\n"
        "• User ID Anda akan digunakan untuk sistem\n"
        "• Cek /status secara berkala untuk monitoring"
        )

    await update.message.reply_text(message)

async def materi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk menu utama materi"""
    
    message = (
        "📚 **RANGKUMAN MATERI PEMBELAJARAN BAHASA RUSIA**\n\n"
        "Pilih materi yang ingin dipelajari:\n\n"
        "📖 /materi1 - Pengenalan Huruf & Frasa Dasar\n"
        "🎯 /materi2 - Bunyi Huruf, Penekanan, & Menanyakan Kabar\n"
        "🥋 /materi3 - Profesi, Huruf Sirilik Baru, dan Kata Ganti\n\n"
        "💡 Tips Belajar:\n"
        "• Pelajari secara bertahap\n"
        "• Praktekkan pengucapan\n"
        "• Gunakan latihan yang tersedia"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def materi1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk materi 1: Pengenalan Huruf & Frasa Dasar"""
    message = (
        "📖 <b>MATERI 1: Pengenalan Huruf & Frasa Dasar</b>\n\n"
        
        "<b>1. Aksara Sirilik:</b>\n"
        "• Aksara resmi Rusia yang terdiri dari 33 huruf\n"
        "• Ditemukan oleh Santo Kiril dan Methodius\n\n"
        
        "<b>2. Kelompok Huruf:</b>\n"
        "• <b>Huruf Mirip Latin:</b> Memiliki kemiripan bentuk dan bunyi dengan alfabet Latin\n"
        "  Contoh: A (\"A\"), K (\"K\"), M (\"M\"), O (\"O\"), T (\"T\")\n"
        "• <b>Huruf \"Jebakan\":</b> Terlihat mirip dengan huruf Latin tetapi bunyinya berbeda\n"
        "  Contoh: <b>H</b> dibaca \"N\" (Hoc = hidung), <b>P</b> dibaca \"R\" (Pыба = ikan), <b>B</b> dibaca \"V\" (Bода = air)\n\n"
        
        "<b>3. Bunyi Unik:</b>\n"
        "• <b>Ы (bi):</b> Bunyi \"i\" yang dalam\n"
        "• <b>Ш (Sh):</b> Bunyi \"sh\" seperti \"sy\" dalam \"syarat\"\n"
        "• <b>Щ (Sh-ch):</b> Bunyi \"shch\" yang lembut\n\n"
        
        "<b>4. Frasa Dasar Perkenalan:</b>\n"
        "• <b>Здравствуйте!</b> (Zdravstvuyte!) = Halo! (formal)\n"
        "• <b>Привет!</b> (Privet!) = Halo! (informal)\n"
        "• <b>Как вас зовут?</b> (Kak vas zovut?) = Siapa nama Anda?\n"
        "• <b>Меня зовут...</b> (Menya zovut...) = Nama saya...\n"
        "• <b>Очень приятно!</b> (Ochen' priyatno!) = Senang bertemu dengan Anda!\n\n"
        
        "🔜 Gunakan /materi2 untuk melanjutkan ke materi berikutnya\n"
        "🏠 Gunakan /materi untuk kembali ke menu utama"
    )
    await update.message.reply_text(message, parse_mode='HTML')
    
async def materi2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk materi 2: Bunyi Huruf, Penekanan, & Menanyakan Kabar"""
    message = (
        "🎯 <b>MATERI 2: Bunyi Huruf, Penekanan, & Menanyakan Kabar</b>\n\n"
        
        "<b>1. Huruf dan Bunyi Baru:</b>\n"
        "• <b>Huruf Konsonan:</b> Б, Д, З, Ж, Л, П\n"
        "• <b>Huruf Vokal:</b> Э, Ы\n"
        "• <b>Bunyi Mirip Latin:</b> Б (B), Д (D), З (Z), П (P), Л (L)\n"
        "• <b>Bunyi Khas Rusia:</b> Ж (Zh) - bunyi \"zh\" seperti \"j\" dalam \"pajak\"\n\n"
        
        "<b>2. Aturan Penekanan (Stress):</b>\n"
        "• Hampir setiap kata dalam bahasa Rusia memiliki satu suku kata yang ditekankan\n"
        "• Penekanan hanya berlaku untuk huruf Vokal\n"
        "• Penekanan <b>tidak dapat diprediksi</b> dan harus dihafal\n"
        "  Contoh: <b>Мáма</b> vs <b>Москвá</b>\n"
        "• Kesalahan penekanan dapat mengubah arti kata\n"
        "  Contoh: <b>зáмок</b> = kastil vs <b>замóк</b> = gembok\n\n"
        
        "<b>3. Reduksi Vokal:</b>\n"
        "• Vokal berubah bunyi ketika tidak mendapat penekanan\n"
        "• <b>Aturan 1:</b> Huruf [O] yang tidak mendapatkan penekanan dibaca \"A\"\n"
        "  Contoh: <b>Молокó</b> → dibaca \"malakO\"\n"
        "• <b>Aturan 2:</b> E yang tidak mendapatkan penekanan dibaca \"I\"\n"
        "  Contoh: <b>Звезда</b> → dibaca \"zvizdA\"\n\n"
        
        "<b>4. Ekspresi Perasaan & Menanyakan Kabar:</b>\n"
        "• <b>Pertanyaan:</b> <b>Как дела?</b> (Kak dela?) = Apa kabar?\n"
        "• <b>Jawaban:</b>\n"
        "  ✅ <b>Очень хорошо</b> (Ochen' khorosho) = Sangat baik\n"
        "  👍 <b>Хорошо</b> (Khorosho) = Baik\n"
        "  ➖ <b>Нормально</b> (Normal'no) = Biasa saja\n"
        "  🤷 <b>Так себе</b> (Tak sebe) = Lumayan / Begitu-begitu saja\n"
        "  ❌ <b>Плохо</b> (Plokho) = Buruk\n"
        "• <b>Pola Kalimat:</b> <code>..., спасибо. А у тебя?</code> (..., terima kasih. Dan kamu?)\n\n"

        "🔙 Gunakan /materi1 untuk mengulang materi sebelumnya\n"
        "🔜 Gunakan /materi3 untuk melanjutkan ke materi berikutnya\n"
        "🏠 Gunakan /materi untuk kembali ke menu utama materi"
    )
    await update.message.reply_text(message, parse_mode='HTML')

async def materi3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk materi 3: Profesi, Huruf Sirilik Baru, dan Kata Ganti"""
    message = (
        "📚 <b>MATERI 3: Profesi, Huruf Sirilik Baru, dan Kata Ganti</b>\n\n"
        
        "<b>🎯 Tujuan Pembelajaran:</b>\n"
        "• Mengenali beberapa profesi dalam bahasa Rusia\n"
        "• Huruf Sirilik: X, Φ, И, У\n"
        "• Huruf Vokal Gabungan: я (й+a), ё (й+o), ю (й+y), е (й+э)\n"
        "• Kalimat tanya: Кто это? Он/Она...\n\n"
        
        "<b>🔤 Huruf Sirilik Baru:</b>\n"
        "• <b>X x</b> - Bunyi \"kh\" seperti dalam \"хлеб\" (roti)\n"
        "• <b>Φ φ</b> - Bunyi \"f\" seperti dalam \"фото\" (foto)\n"
        "• <b>И и</b> - Bunyi \"i\" seperti dalam \"икра\" (telur ikan)\n"
        "• <b>У у</b> - Bunyi \"u\" seperti dalam \"улица\" (jalan)\n\n"
        
        "<b>🌟 Huruf Vokal Gabungan:</b>\n"
        "<b>Й (и краткое) dibaca i kratkaye </b>\n"
        "• <b>Я</b> = й + a (contoh: <b>мясо</b> - daging)\n"
        "• <b>Ё</b> = й + o (contoh: <b>мёд</b> - madu)\n"
        "• <b>Е</b> = й + э (contoh: <b>хлеб</b> - roti)\n"
        "• <b>Ю</b> = й + у (contoh: <b>юбка</b> - rok)\n\n"
        
        "<b>💼 Kosakata Profesi:</b>\n"
        "• <b>Врач</b> - Dokter\n"
        "• <b>Студент/Студентка</b> - Murid (laki-laki/perempuan)\n"
        "• <b>Водитель</b> - Supir\n"
        "• <b>Повар</b> - Juru masak\n"
        "• <b>Рыбак</b> - Nelayan\n"
        "• <b>Фотограф</b> - Fotografer\n"
        "• <b>Бизнесмен</b> - Pengusaha\n"
        "• <b>Директор</b> - Direktur\n"
        "• <b>Секретарь</b> - Sekretaris\n\n"
        
        "<b>👥 Kata Ganti Orang (Местоимения):</b>\n"
        "• <b>Я</b> - Saya\n"
        "• <b>Ты</b> - Kamu (informal)\n"
        "• <b>Он</b> - Dia (laki-laki)\n"
        "• <b>Она</b> - Dia (perempuan)\n"
        "• <b>Они</b> - Mereka\n"
        "• <b>Вы</b> - Anda (formal) / Kalian\n"
        "• <b>Мы</b> - Kami/Kita\n\n"
        
        "<b>💬 Pola Kalimat:</b>\n"
        "• <b>Ini adalah...</b>\n"
        "  <b>Это Антон. Он врач.</b> (Ini Anton. Dia dokter.)\n"
        "  <b>Это Анна. Она студентка.</b> (Ini Anna. Dia murid.)\n"
        "• <b>Kalimat tanya:</b>\n"
        "  <b>Кто это?</b> - Siapa ini?\n"
        "  <b>Он/Она ...?</b> - Apakah dia (laki/perempuan)...?\n\n"
        
        "<b>🎭 Contoh Dialog:</b>\n"
        "• <b>Кто это?</b> - <b>Это Алексей. Он бизнесмен.</b>\n"
        "• <b>Извините, вы директор?</b> - <b>Нет, я секретарь.</b>\n"
        "• <b>Вы студенты?</b> - <b>Да, мы студенты.</b>\n\n"
        
        "<b>📝 Tugas Rumah:</b>\n"
        "• Tulis 5 kata baru (contoh: хлеб, фото, яблоко)\n"
        "• Foto 3 benda di rumah, tulis kalimat \"Это...\" dalam Sirilik\n"
        "• Pelajari huruf: Г, Ц, Ч, Ь, Ъ\n\n"
        
        "<b>📚 Kosakata Tambahan:</b>\n"
        "• <b>Стетоскоп</b> - Stetoskop\n"
        "• <b>Книга</b> - Buku\n"
        "• <b>Машина</b> - Mobil\n"
        "• <b>Мясо</b> - Daging\n"
        "• <b>Икра</b> - Telur ikan\n"
        "• <b>Фото</b> - Foto\n\n"
        
        "🔙 Gunakan /materi2 untuk mengulang materi sebelumnya\n"
        "🏠 Gunakan /materi untuk kembali ke menu utama"
    )
    await update.message.reply_text(message, parse_mode='HTML')

async def absen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk absen dengan pilihan status dan notifikasi Total Hadir"""
    user_id = update.effective_user.id
    bot = AttendanceBot()
    
    # Cek apakah user sudah terdaftar
    df = bot.get_student_data()
    if df.empty:
            await update.message.reply_text(
                "❌ **Sistem sedang sibuk, silakan coba lagi dalam beberapa detik.**"
            )
            return
        
    student_data = df[df['Telegram ID'] == user_id]
    
    if student_data.empty:
        await update.message.reply_text(
            "❌ **Anda belum terdaftar dalam sistem!**\n\n"
            "Silakan daftar terlebih dahulu dengan:\n"
            "`/register NamaLengkap EmailAnda` \n\n"
            "Contoh `/register Andi Wijaya andi@gmail.com`\n"
            "Gunakan huruf kapital disetiap kata sesuai pada contoh",
            parse_mode='Markdown'
        )
        return
    
    student = student_data.iloc[0]
    student_name = student['Nama']

    # Konversi ke integer untuk memastikan tipe data benar
    try:
        total_hadir = int(student['Total Hadir']) if 'Total Hadir' in student and str(student['Total Hadir']).strip().isdigit() else 0
        total_alpha = int(student['Total Alpha']) if 'Total Alpha' in student and str(student['Total Alpha']).strip().isdigit() else 0
        total_izin = int(student['Total Izin']) if 'Total Izin' in student and str(student['Total Izin']).strip().isdigit() else 0
    except (ValueError, TypeError):
        total_hadir = 0
        total_alpha = 0
        total_izin = 0
    
    # Jika tidak ada argumen, tampilkan pilihan absen
    if not context.args:
        await update.message.reply_text(
            f"📝 **FORM ABSENSI - {student_name}**\n\n"
            "Pilih status kehadiran:\n\n"
            "✅ `/absen hadir` - Untuk kehadiran\n"
            "⚠️ `/absen izin` - Untuk izin tidak hadir\n"
            "❌ `/absen alpha` - Untuk tidak hadir\n\n"
            "💡 **Keterangan:**\n"
            "• **Hadir**: Total Hadir +1, Status menjadi 'Hadir'\n"
            "• **Izin**: Total Izin +1, Status menjadi 'Izin'\n"
            "• **Alpha**: Total Alpha +1, Status menjadi 'Alpha'\n\n"
            f"📊 **Status saat ini:**\n"
            f"• Hadir: {total_hadir}x\n"
            f"• Alpha: {total_alpha}x\n"
            f"• Izin: {total_izin}x\n"
            f"• Status: {student['Status Terakhir']}",
            parse_mode='Markdown'
        )
        return
    
    # Proses absen
    status_absen = context.args[0].lower()
    
    if status_absen not in ['hadir', 'izin', 'alpha']:
        await update.message.reply_text(
            "❌ **Status tidak valid!**\n\n"
            "Gunakan salah satu:\n"
            "• `/absen hadir`\n"
            "• `/absen izin`\n"
            "• `/absen alpha`",
            parse_mode='Markdown'
        )
        return
    
    # Update data di spreadsheet
    success = bot.update_student_record(user_id, status_absen.capitalize())
    
    if success:
        # Dapatkan data terbaru untuk konfirmasi
        df_updated = bot.get_student_data()
        student_updated = df_updated[df_updated['Telegram ID'] == user_id].iloc[0]

        # Konversi ke integer untuk data terbaru
        try:
            total_hadir_updated = int(student_updated['Total Hadir']) if 'Total Hadir' in student_updated else 0
            total_alpha_updated = int(student_updated['Total Alpha'])
            total_izin_updated = int(student_updated['Total Izin'])
            
        except (ValueError, TypeError):
            total_hadir_updated = total_hadir
            total_alpha_updated = total_alpha
            total_izin_updated = total_izin
        
        emoji = {
            'hadir': '✅',
            'izin': '⚠️', 
            'alpha': '❌'
        }
        waktu_wib = get_wib_time().strftime('%d/%m/%Y %H:%M WIB')
        
        message = (
            f"{emoji[status_absen]} **ABSENSI BERHASIL DICATAT**\n\n"
            f"👤 **Nama:** {student_name}\n"
            f"📝 **Status:** {status_absen.capitalize()}\n"
            f"🕐 **Waktu:** {waktu_wib}\n\n"
            f"📊 **Update Status:**\n"
            f"• Total Hadir: {total_hadir_updated}x\n"
            f"• Total Alpha: {total_alpha_updated}x\n"
            f"• Total Izin: {total_izin_updated}x\n"
            f"• Status Terakhir: {student_updated['Status Terakhir']}"
        )

        # Kirim notifikasi ke grup jika status hadir
        if status_absen == 'hadir':
            await send_attendance_notification(context, user_id, student_name, total_hadir_updated)
        
        # Tambahkan peringatan jika perlu (dengan tipe data ya sudah di konversi)
        if status_absen == 'alpha':
            message += "\n\n⚠️ **PERINGATAN:** Alpha akan mempengaruhi status kehadiran Anda!"
        elif status_absen == 'izin' and total_izin_updated >= 2:
            message += "\n\n⚠️ **PERINGATAN:** Total izin Anda sudah 2x, hati-hati!"
        
        await update.message.reply_text(message)
    else:
        await update.message.reply_text(
            "❌ **Gagal mencatat absensi!**\n"
            "Jika masalah berlanjut, hubungi admin."
        )

async def send_attendance_notification(context: ContextTypes.DEFAULT_TYPE, user_id: int, student_name: str, total_hadir: int):
    """Mengirim notifikasi kehadiran ke grup dengan pantun lucu"""
    # Dapatkan hari Senin minggu ini
    today = datetime.now()
    senin_minggu_ini = get_monday_wib()
 
    # Format tanggal 
    bulan_indonesia = {
        1: "Januari", 2: "Februari", 3: "Maret", 4: "April", 5: "Mei", 6: "Juni",
        7: "Juli", 8: "Agustus", 9: "September", 10: "Oktober", 11: "November", 12: "Desember"
    }
    hari = "Senin"  # Karena kita selalu mau Senin
    tanggal = senin_minggu_ini.day
    bulan = bulan_indonesia[senin_minggu_ini.month]
    tahun = senin_minggu_ini.year
    
    tanggal_str = f"{hari} tanggal {tanggal} {bulan} {tahun}"
    motivasi_list = [
        "Semangat terus belajarnya! 💪",
        "Langkah kecil setiap hari membawa hasil yang besar! 🌟",
        "Belajar bahasa Rusia itu menyenangkan, bukan? 😄",
        "Terus tingkatkan kemampuan bahasa Rusiamu! 🚀",
        "Kehadiranmu sangat berarti untuk proses belajar! 📚"
    ]
    pantun_list = [
        "Jalan-jalan ke pasar baru,\nBeli sepatu dan tas kanvas.\nJangan lupa absen hadir,\nBiar makin pinter bahasa Rusia! 🎒",
        "Makan bakso di warung,\nBaksonya enak sekali.\nKalau rajin masuk kelas,\nBisa jadi translator yang hebat! 🍲",
        "Lihat kucing manis sekali,\nKucingnya lagi tidur.\nJangan males datang ke kelas,\nBiar bisa baca buku Rusia! 😺",
        "Pergi ke mall naik bus,\nBusnya penuh sesak.\nYang rajin hadir dapat bonus,\nBisa ngobrol sama Ivan dan Sasha! 🚌",
        "Naik sepeda ke taman bunga,\nBunga mekar warna-warni.\nRajin hadir dapat pahala,\nNanti bisa jalan-jalan ke Moskwa! 🚴‍♀️",
        "Siang-siang panas sekali,\nMinum es kelapa muda.\nJangan sampai alpha terus,\nNanti nilai jadi muda! 🥥"
    ]
    # Pilih random motivasi dan pantun
    motivasi = random.choice(motivasi_list)
    pantun = random.choice(pantun_list)

    notification_message = (
        f"🎉 **NOTIFIKASI KEHADIRAN** 🎉\n\n"
        f"User ID {user_id} atas nama {student_name}\n"
        f"Terima kasih telah hadir pada {tanggal_str}\n\n"
        f"**{motivasi}**\n\n"
        f"📈 **Total Kehadiran:** {total_hadir}x\n\n"
        f"🎭 **Pantun Lucu:**\n{pantun}\n\n"
        f"🕐 _Waktu sistem: {get_wib_time().strftime('%d/%m/%Y %H:%M WIB')}_"
    )
    
    GROUP_CHAT_ID = -1002408972369
    try:
        await context.bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=notification_message
    )
        logger.info(f"Notifikasi kehadiran terkirim untuk {student_name} pada {tanggal_str}")
    except Exception as e:
        logger.error(f"Gagal mengirim notifikasi ke grup: {e}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk melihat status"""
    user_id = update.effective_user.id
    bot = AttendanceBot()
    df = bot.get_student_data()

    # Jika admin, tampilkan semua data
    if user_id in ADMIN_IDS:
        if df.empty:
            await update.message.reply_text("❌ Tidak ada data murid.")
            return
        
        # Konversi ke integer untuk perhitungan
        try:
            total_hadir = df['Total Hadir'].astype(int).sum() if 'Total Hadir' in df.columns else 0
            total_alpha = df['Total Alpha'].astype(int).sum()
            total_izin = df['Total Izin'].astype(int).sum()
        except (ValueError, TypeError):
            total_hadir = 0
            total_alpha = 0
            total_izin = 0
            
        total_students = len(df)
        
        stats_message = (
            "👑 **STATUS ADMIN**\n\n"
            f"• 👥 Total Murid: {total_students}\n"
            f"• ✅ Total Hadir: {total_hadir}\n"
            f"• ❌ Total Alpha: {total_alpha}\n"
            f"• ⚠️ Total Izin: {total_izin}\n\n"
            "Gunakan /admin_stats untuk info lebih detail\n"
            "Gunakan /list_warnings untuk lihat peringatan"
        )
        await update.message.reply_text(stats_message)
        return
    
    # Untuk user biasa
    student_data = df[df['Telegram ID'] == user_id]
    
    if student_data.empty:
        await update.message.reply_text(
            "❌ **Anda belum terdaftar dalam sistem kehadiran.**\n\n"
            "Gunakan `/register NamaLengkap EmailAnda` untuk mendaftar.\n"
            "Contoh: `/register Andi Wijaya andi@gmail.com`",
            parse_mode='Markdown'
        )
        return
    
    student = student_data.iloc[0]

    # Konversi ke integer
    try:
        total_hadir = int(student['Total Hadir']) if 'Total Hadir' in student else 0
        total_alpha = int(student['Total Alpha'])
        total_izin = int(student['Total Izin'])
    except (ValueError, TypeError):
        total_hadir = 0
        total_alpha = 0
        total_izin = 0
    
    message = (
        f"📊 **STATUS KEHADIRAN**\n\n"
        f"👤 **Nama:** {student['Nama']}\n"
        f"✅ **Total Hadir**: {total_hadir}x\n"
        f"❌ **Total Alpha:** {total_alpha}x\n"
        f"⚠️ **Total Izin:** {total_izin}x\n"
        f"📝 **Status Terakhir:** {student['Status Terakhir']}"
    )
    
    # Tambahkan peringatan jika memenuhi kriteria (dengan tipe data intenger)
    if total_alpha >= 2:
        message += f"\n\n🚨 **PERINGATAN:** Anda memiliki {total_alpha}x alpha!"
    if total_izin >= 2:
        message += f"\n\n⚠️ **PERINGATAN:** Total izin Anda {total_izin}x!"
    if student['Total Izin'] >= 2 or student['Total Alpha'] >= 2:
        message += "\n\n⚠️ **STATUS PERINGATAN:** Anda terancam akan dikeluarkan jika tidak hadir pada pertemuan selanjutnya!"
    
    await update.message.reply_text(message)

async def test_connection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test koneksi Google Sheets"""
    try:
        bot = AttendanceBot()
        df = bot.get_student_data()
        
        if df.empty:
            await update.message.reply_text("❌ Tidak ada data di spreadsheet")
        else:
            student_count = len(df)
            await update.message.reply_text(
                f"✅ Koneksi Google Sheets BERHASIL!\n"
                f"📊 Total murid terdaftar: {student_count}"
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def get_my_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dapatkan informasi user lengkap"""
    user = update.effective_user
    chat = update.effective_chat
    
    info_message = (
        f"📋 **INFORMASI AKUN TELEGRAM ANDA**\n\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"📛 **Nama:** {user.first_name} {user.last_name or ''}\n"
        f"👤 **Username:** @{user.username or 'Tidak ada'}\n"
        f"💬 **Chat ID:** `{chat.id}`\n"
        f"🏷️ **Tipe Chat:** {chat.type}\n\n"
        f"**📝 Catatan:**\n"
        f"• **User ID** digunakan untuk pendaftaran sistem\n"
        f"• **Username** bisa berubah, User ID tetap\n"
    )
    
    await update.message.reply_text(info_message, parse_mode='Markdown')

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pendaftaran murid otomatis"""
    user = update.effective_user

    #Admin tidak perlu mendaftar
    if user.id in ADMIN_IDS:
        await update.message.reply_text(
            "👑 **Anda adalah Admin!**\n\n"
            "Sebagai admin, Anda tidak perlu mendaftar sebagai murid.\n"
            "Gunakan perintah admin untuk mengelola sistem kehadiran."
        )
        return 
    
    bot = AttendanceBot()
    
    # Cek apakah sudah terdaftar
    df = bot.get_student_data()
    existing_user = df[df['Telegram ID'] == user.id]
    
    if not existing_user.empty:
        await update.message.reply_text(
            "✅ Anda sudah terdaftar dalam sistem!\n"
            f"User ID Anda: `{user.id}`",
            parse_mode='Markdown'
        )
        return
    
    # Jika belum terdaftar
    if context.args:
        nama = ' '.join(context.args)
        email = context.args[-1] if '@' in context.args[-1] else ''  # Ambil email jika ada

        # Validasi nama
        if len(nama) < 2:
            await update.message.reply_text("❌ Nama terlalu pendek. Minimal 2 karakter.")
            return
        
        # Jika ada email, hapus dari nama
        if email:
            nama = ' '.join(context.args[:-1])
        
        # Tambahkan ke spreadsheet
        try:
            new_row = [nama, user.id, email, f"@{user.username}" if user.username else "-", 0, 0, 0, "Belum Absen", "Auto-registered"]
            bot.worksheet.append_row(new_row)
            
            confirmation_msg = (
                f"✅ **Pendaftaran Berhasil!**\n\n"
                f"• Nama: {nama}\n"
                f"• User ID: `{user.id}`\n"
                f"• Username: @{user.username or 'Tidak ada'}\n"
            )

            if email:
                confirmation_msg += f"• Email: {email}\n\n"
                confirmation_msg += "📧 Email telah tercatat untuk reminder tugas Classroom"
            else:
                confirmation_msg += "\n💡 **Tips:** Tambahkan email dengan `/register Nama email@example.com` untuk reminder tugas"
            
            confirmation_msg += f"\n\nSekarang Anda bisa menggunakan /absen"
            
            await update.message.reply_text(confirmation_msg, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")
    else:
        await update.message.reply_text(
            "📝 **Form Pendaftaran**\n\n"
            "Untuk mendaftar, ketik:\n"
            "`/register NamaLengkap email@gmail.com`\n\n"
            "Contoh: `/register Andi Wijaya andi@gmail.com`",
            parse_mode='Markdown'
        )

