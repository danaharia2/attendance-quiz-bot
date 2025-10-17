# quiz_handler.py
import logging
import random
import time
import asyncio
import os
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import ADMIN_IDS
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

# ==================== SETUP IMPORT PATH ====================
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# ==================== IMPORT MODULES ====================
try:
    from quiz_models import Question
    from quiz_database import quiz_db
    print("✅ Successfully imported quiz_models and quiz_database")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    # Fallback implementation
    from datetime import datetime
    
    class Question:
        def __init__(self, question, correct_answers, options=None, category="umum", difficulty="medium"):
            self.question = question
            self.correct_answers = correct_answers
            self.options = options or []
            self.category = category
            self.difficulty = difficulty
            self.created_by = None
            self.created_at = datetime.now()
    
    class DummyQuizDB:
        def get_all_questions(self): return []
        def add_question(self, *args, **kwargs): return False
        def get_categories(self): return {}
        def get_question_count(self): return 0
        def get_question_count_by_category(self): return {}
    
    quiz_db = DummyQuizDB()
    print("⚠️ Using fallback Question and DummyQuizDB classes")

WIB = timezone(timedelta(hours=7))

# ==================== GLOBAL VARIABLES ====================
quiz_sessions = {}  # {chat_id: session_data}
user_scores = {}    # {user_id: score}
questions_db = []   # List of Question objects

# ==================== INITIALIZATION FUNCTIONS ====================
def initialize_questions():
    """Initialize questions dari database atau buat sample"""
    global questions_db
    try:
        questions_db.clear()
        loaded_questions = quiz_db.get_all_questions()
        
        if loaded_questions:
            questions_db.extend(loaded_questions)
            print(f"✅ Loaded {len(questions_db)} questions from database")
        else:
            print("⚠️ No questions in database, creating sample questions...")
            create_sample_questions()
            
    except Exception as e:
        print(f"❌ Error in initialize_questions: {e}")
        create_sample_questions()

def create_sample_questions():
    """Buat sample questions jika database kosong atau error"""
    global questions_db
    try:
        sample_questions = [
            Question(
                "Sebutkan apa saja huruf jebakan (Kls Rusia)?\nTulis dengan keyboard rusia",
                ["С", "Р", "В", "Х", "У", "Е", "Н"],
                category="bahasa_rusia",
                difficulty="medium"
            ),
            Question(
                "Sebutkan 2 tanda bunyi dalam Bahasa Rusia?",
                ["Ъ", "Ь"],
                category="bahasa_rusia",
                difficulty="easy"
            ),
            Question(
                "Aktivitas orang gabut?",
                ["merusuh", "baca buku", "main game", "nonton", "tidur"],
                category="umum",
                difficulty="easy"
            ),
            Question(
                "Sebutkan kota besar di Indonesia?",
                ["jakarta", "surabaya", "bandung", "medan", "makassar", "semarang", "palembang", "depok"],
                category="geografi", 
                difficulty="easy"
            ),
            Question(
                "Sebutkan warna pelangi?",
                ["merah", "jingga", "kuning", "hijau", "biru", "nila", "ungu"],
                category="sains",
                difficulty="easy"
            ),
        ]
        questions_db.extend(sample_questions)
        print(f"✅ Created {len(sample_questions)} sample questions")
        
        # Coba simpan ke database
        for question in sample_questions:
            quiz_db.add_question(
                question=question.question,
                correct_answers=question.correct_answers,
                category=question.category,
                difficulty=question.difficulty
            )
            
    except Exception as e:
        print(f"❌ Error creating sample questions: {e}")

# Initialize questions saat module load
initialize_questions()

# ==================== UTILITY FUNCTIONS ====================
def format_time():
    """Format waktu seperti di screenshot (HH:MM)"""
    now_wib = datetime.now(WIB)
    return now_wib.strftime("%H:%M")

def is_current_question_complete(chat_id):
    """Cek apakah pertanyaan saat ini sudah selesai (semua jawaban ditemukan)"""
    if chat_id not in quiz_sessions:
        return False
    
    session = quiz_sessions[chat_id]
    question_index = session['current_question_index']

    if question_index >= len(questions_db):
        return False
    
    question = questions_db[question_index]
    return len(session['current_question_answers']) == len(question.correct_answers)

# ==================== QUIZ MANAGEMENT FUNCTIONS ====================
async def quiz_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Tampilkan statistik kuis"""
    try:
        total_questions = quiz_db.get_question_count()
        category_stats = quiz_db.get_question_count_by_category()
        categories = quiz_db.get_categories()
        
        stats_text = "📊 **Statistik Kuis**\n\n"
        stats_text += f"📝 **Total Pertanyaan:** {total_questions}\n\n"
        
        stats_text += "**Pertanyaan per Kategori:**\n"
        for category_id, count in category_stats.items():
            category_name = categories.get(category_id, category_id)
            stats_text += f"• {category_name}: {count} pertanyaan\n"
        
        stats_text += f"\n**Kategori Tersedia:** {len(categories)}\n"
        
        if query:
            await query.message.reply_text(stats_text, parse_mode='Markdown')
        elif update.message:
            await update.message.reply_text(stats_text, parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Error in quiz_stats: {e}")
        error_text = "❌ Error mengambil statistik."
        if query:
            await query.message.reply_text(error_text)
        elif update.message:
            await update.message.reply_text(error_text)

async def add_question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk menambah pertanyaan via command"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ Hanya admin yang bisa menambah pertanyaan!")
        return
    
    if not context.args:
        help_text = (
            "✏️ **Tambah Pertanyaan Baru**\n\n"
            "Format: `/tambah_pertanyaan \"Pertanyaan?\" \"jawaban1, jawaban2, ...\" [kategori] [kesulitan]`\n\n"
            "**Contoh:**\n"
            "`/tambah_pertanyaan \"Sebutkan planet?\" \"merkurius, venus, bumi, mars\" sains easy`\n\n"
            "**Kategori tersedia:** umum, bahasa_rusia, geografi, sains, matematika, sejarah, teknologi\n"
            "**Tingkat kesulitan:** easy, medium, hard"
        )
        await update.message.reply_text(help_text)
        return
    
    try:
        # Parse arguments
        question_text = context.args[0].strip('"')
        answers_text = context.args[1].strip('"')
        category = context.args[2] if len(context.args) > 2 else "umum"
        difficulty = context.args[3] if len(context.args) > 3 else "medium"
        
        # Parse answers
        correct_answers = [ans.strip() for ans in answers_text.split(',')]
        
        # Add to database
        success = quiz_db.add_question(
            question=question_text,
            correct_answers=correct_answers,
            category=category,
            difficulty=difficulty
        )
        
        if success:
            # Reload questions
            initialize_questions()
            await update.message.reply_text(
                f"✅ Pertanyaan berhasil ditambahkan!\n"
                f"Kategori: {category}\n"
                f"Jawaban: {len(correct_answers)} jawaban benar"
            )
        else:
            await update.message.reply_text("❌ Gagal menambah pertanyaan.")
            
    except Exception as e:
        logger.error(f"Error in add_question_handler: {e}")
        await update.message.reply_text("❌ Format salah! Gunakan /tambah_pertanyaan untuk bantuan.")

# ==================== COMMAND HANDLERS ====================
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command /quiz - Menu utama quiz"""
    user_id = update.effective_user.id
    
    keyboard = [
        [InlineKeyboardButton("🎮 Mulai Game", callback_data="quiz_start")],
        [InlineKeyboardButton("📖 Bantuan", callback_data="quiz_help")],
        [InlineKeyboardButton("📊 Skor Saat Ini", callback_data="quiz_score")],
        [InlineKeyboardButton("⭐ Poin Saya", callback_data="quiz_points")],
        [InlineKeyboardButton("🏆 Top Skor Global", callback_data="quiz_topscore")],
        [InlineKeyboardButton("📚 Aturan Bermain", callback_data="quiz_rules")],
        [InlineKeyboardButton("📈 Statistik Kuis", callback_data="quiz_stats")],
        [InlineKeyboardButton("❤️ Donasi", callback_data="quiz_donate")],
        [InlineKeyboardButton("⚠️ Laporkan Pertanyaan", callback_data="quiz_report")],
    ]
    
    # Hanya admin yang bisa melihat tombol buat pertanyaan
    if user_id in ADMIN_IDS:
        keyboard.append([InlineKeyboardButton("✏️ Buat Pertanyaan", callback_data="quiz_create")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🤖 **Bot Tebak-Tebakan**\n\n"
        "Pilih menu di bawah untuk bermain tebak-tebakan!",
        reply_markup=reply_markup
    )

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /start - menampilkan pesan welcome dengan menu"""
    welcome_text = (
        "🤖 **Bot Tebak-Tebakan**\n\n"
        "Halo, ayo kita main tebak-tebakan. Kamu juga bisa menggunakan bot ini secara private.\n\n"
        "**Gunakan menu commands atau ketik perintah:**\n"
        "• /mulai - mulai game tebak-tebakan\n"
        "• /help - bantuan dan panduan\n"
        "• /aturan - aturan bermain\n"
        "• /quiz - menu interaktif\n"
        "• /donasi - dukung bot ini\n\n"
        "Selamat bermain! 🎮"
    )
    
    keyboard = [
        [InlineKeyboardButton("🎮 Mulai Game", callback_data="quiz_start")],
        [InlineKeyboardButton("📖 Bantuan", callback_data="quiz_help")],
        [InlineKeyboardButton("📚 Aturan", callback_data="quiz_rules")],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk /help - menampilkan pesan bantuan lengkap"""
    help_text = (
        "🤖 **Bot Tebak-Tebakan**\n\n"
        "Halo, ayo kita main tebak-tebakan. Kamu juga bisa menggunakan bot ini secara private.\n\n"
        "**Perintah yang Tersedia:**\n\n"
        "/start - Memulai Bot\n"
        "/help - Membuka pesan bantuan\n" 
        "/mulai - Memulai permainan\n"
        "/nyerah - Menyerah dari pertanyaan\n"
        "/next - Pertanyaan berikutnya\n"
        "/skor - Melihat skor saat ini\n"
        "/poin - Melihat poin kamu\n"
        "/topskor - Melihat 10 pemain teratas\n"
        "/aturan - Melihat aturan bermain\n"
        "/donasi - Dukungan untuk bot\n"
        "/lapor - Laporkan pertanyaan\n"
    )
    await update.message.reply_text(help_text)

async def quiz_help(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Handler untuk bantuan quiz"""
    help_text = (
        "🤖 **Bot Tebak-Tebakan - Bantuan**\n\n"
        "**Perintah yang tersedia:**\n"
        "/mulai - Mulai game tebak-tebakan\n"
        "/nyerah - Menyerah dari game\n"
        "/next - Pertanyaan berikutnya\n"
        "/skor - Lihat skor saat ini\n"
        "/poin - Melihat poin kamu\n"
        "/topskor - Lihat top skor global\n"
        "/aturan - Aturan bermain\n"
        "/donasi - Dukung bot ini agar tetap aktif\n"
        "/lapor - Laporkan pertanyaan\n"
    )
    if query:
        await query.message.reply_text(help_text)
    elif update.message:
        await update.message.reply_text(help_text)
    else:
        logger.error("Cannot determine message source in quiz_help")

# ==================== CALLBACK HANDLER ====================
async def quiz_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk callback queries"""
    query = update.callback_query
    if not query or not query.message:
        logger.error("Invalid callback query received")
        return
        
    await query.answer()
    
    callback_data = query.data
    user_id = query.from_user.id
    
    # Map callback data ke fungsi handler
    handler_map = {
        "quiz_help": lambda u, c: quiz_help(u, c, query),
        "quiz_start": start_quiz,
        "quiz_surrender": surrender_quiz,
        "quiz_next": next_question,
        "quiz_score": lambda u, c: show_score(u, c, query),
        "quiz_points": lambda u, c: show_points(u, c, query),
        "quiz_topscore": lambda u, c: top_score(u, c, query),
        "quiz_rules": lambda u, c: quiz_rules(u, c, query),
        "quiz_donate": lambda u, c: quiz_donate(u, c, query),
        "quiz_report": lambda u, c: quiz_report(u, c, query),
        "quiz_stats": lambda u, c: quiz_stats(u, c, query),
    }
    
    if callback_data in handler_map:
        await handler_map[callback_data](update, context)
    elif callback_data.startswith("quiz_stay_"):
        await query.message.delete()  # Hapus pesan pemberitahuan
    elif callback_data == "quiz_create":
        if user_id in ADMIN_IDS:
            await create_question_start(update, context, query)
        else:
            await query.message.reply_text("❌ Anda bukan admin!")

# ==================== QUIZ GAME FUNCTIONS ====================
async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mulai kuis baru"""
    try:
        # Determine message source
        if update.callback_query:
            query = update.callback_query
            chat_id = query.message.chat.id
            message_to_reply = query.message
        elif update.message:
            chat_id = update.message.chat.id
            message_to_reply = update.message
        else:
            logger.error("Cannot determine message source in start_quiz")
            return

        # Cek jika sudah ada session aktif
        if chat_id in quiz_sessions:
            session = quiz_sessions[chat_id]
            question_index = session['current_question_index']
            
            if 0 <= question_index < len(questions_db):
                question = questions_db[question_index]
                is_question_complete = len(session['current_question_answers']) == len(question.correct_answers)
                
                if not is_question_complete:
                    # Tampilkan pesan bahwa quiz sedang berlangsung
                    keyboard = [
                        [InlineKeyboardButton("🏃 Menyerah", callback_data="quiz_surrender")],
                        [InlineKeyboardButton("Tetap Stay", callback_data=f"quiz_stay_{message_to_reply.message_id}")],
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    notification_msg = await message_to_reply.reply_text(
                        "❓ Quiz sedang berlangsung. Apa yang ingin Anda lakukan?",
                        reply_markup=reply_markup
                    )
                    context.user_data['notification_message_id'] = notification_msg.message_id
                    return
                else:
                    # Jika pertanyaan sudah selesai, lanjutkan ke pertanyaan berikutnya
                    session['answered_questions'].add(session['current_question_index'])
                    del quiz_sessions[chat_id]
            else:
                del quiz_sessions[chat_id]
        
        # Inisialisasi session baru
        quiz_sessions[chat_id] = {
            'current_question_index': 0,
            'answered_questions': set(),
            'current_question_answers': {},
            'message_id': None,
            'start_time': time.time()
        }
        
        session = quiz_sessions[chat_id]
        
        # Cari pertanyaan yang belum dijawab
        available_questions = [i for i in range(len(questions_db)) if i not in session['answered_questions']]
        
        if not available_questions:
            session['answered_questions'] = set()
            available_questions = list(range(len(questions_db)))
            await message_to_reply.reply_text("🎉 Semua pertanyaan sudah dijawab! Mengulang dari awal...")
                
        # Pilih pertanyaan secara acak
        question_index = random.choice(available_questions)
        session['current_question_index'] = question_index
        question = questions_db[question_index]
        
        # Reset jawaban untuk pertanyaan baru
        session['current_question_answers'] = {}
        
        # Format dan kirim pertanyaan
        question_text = await format_question_text(question, session, chat_id)
        message = await message_to_reply.reply_text(question_text, parse_mode='Markdown')
        session['message_id'] = message.message_id
        
    except Exception as e:
        logger.error(f"Error in start_quiz: {e}")
        try:
            if update.effective_chat:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ Terjadi error saat memulai kuis. Silakan coba lagi."
                )
        except:
            pass

async def format_question_text(question, session, chat_id):
    """Format teks pertanyaan seperti di screenshot"""
    question_text = f"**{question.question}**\n\n"
    
    # Buat daftar jawaban sesuai urutan correct_answers
    for i, correct_answer in enumerate(question.correct_answers):
        if correct_answer in session['current_question_answers']:
            user_data = session['current_question_answers'][correct_answer]
            user_name = user_data['user_name']
            question_text += f"{i+1}. {correct_answer} (+1) [{user_name}]\n"
        else:
            question_text += f"{i+1}. ______\n"
    
    # Tambahkan waktu current
    current_time = format_time()
    question_text += f"\n{current_time}"
    
    return question_text

async def update_quiz_message(context: ContextTypes.DEFAULT_TYPE, chat_id: int, session: dict):
    """Update pesan quiz dengan jawaban terbaru"""
    try:
        question_index = session['current_question_index']
        question = questions_db[question_index]
        question_text = await format_question_text(question, session, chat_id)
        
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=session['message_id'],
            text=question_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error updating quiz message: {e}")

async def surrender_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menyerah dari kuis"""
    try:
        if update.callback_query:
            query = update.callback_query
            chat_id = query.message.chat.id
            message_to_reply = query.message
        elif update.message:
            chat_id = update.message.chat.id
            message_to_reply = update.message
        else:
            return

        if chat_id in quiz_sessions:
            session = quiz_sessions[chat_id]
            question_index = session['current_question_index']
            
            if 0 <= question_index < len(questions_db):
                question = questions_db[question_index]
                answer_text = "😔 Anda menyerah! Jawaban yang benar:\n\n"
                for i, answer in enumerate(question.correct_answers, 1):
                    answer_text += f"{i}. {answer}\n"
                
                await message_to_reply.reply_text(answer_text)
                del quiz_sessions[chat_id]
            else:
                await message_to_reply.reply_text("❌ Pertanyaan tidak valid. Session direset.")
                del quiz_sessions[chat_id]
        else:
            await message_to_reply.reply_text("ℹ️ Tidak ada game yang aktif, silahkan klik /mulai")
            
    except Exception as e:
        logger.error(f"Error in surrender_quiz: {e}")
        await update.message.reply_text("❌ Terjadi error saat menyerah dari kuis.")

async def next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Pindah ke pertanyaan berikutnya"""
    try:
        if update.callback_query:
            query = update.callback_query
            chat_id = query.message.chat.id
        elif update.message:
            chat_id = update.message.chat.id
        elif update.effective_chat:
            chat_id = update.effective_chat.id
        else:
            return

        if chat_id not in quiz_sessions:
            await update.message.reply_text("ℹ️ Tidak ada game yang aktif, silahkan klik /mulai")
            return
        
        session = quiz_sessions[chat_id]
        session['answered_questions'].add(session['current_question_index'])
        await start_quiz(update, context)
        
    except Exception as e:
        logger.error(f"Error in next_question: {e}")
        await update.message.reply_text("❌ Terjadi error saat pindah ke pertanyaan berikutnya.")

async def show_score(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Tampilkan skor saat ini"""
    try:
        if query:
            chat_id = query.message.chat.id
        elif update.message:
            chat_id = update.message.chat.id
        else:
            logger.error("Cannot determine message source in show_score")
            return

        if chat_id in quiz_sessions:
            session = quiz_sessions[chat_id]
            current_score = len(session['current_question_answers'])
            message_text = f"📊 Skor saat ini: {current_score}"
        else:
            message_text = "ℹ️ Tidak ada game yang aktif."

        if query:
            await query.message.reply_text(message_text)
        elif update.message:
            await update.message.reply_text(message_text)
            
    except Exception as e:
        logger.error(f"Error in show_score: {e}")
        error_text = "❌ Terjadi error saat mengambil skor."
        if query:
            await query.message.reply_text(error_text)
        elif update.message:
            await update.message.reply_text(error_text)

async def show_points(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Tampilkan poin user"""
    try:
        user_id = update.effective_user.id
        points = user_scores.get(user_id, 0)
        message_text = f"⭐ Poin Anda: {points}"

        if query:
            await query.message.reply_text(message_text)
        elif update.message:
            await update.message.reply_text(message_text)
            
    except Exception as e:
        logger.error(f"Error in show_points: {e}")
        error_text = "❌ Terjadi error saat mengambil poin."
        if query:
            await query.message.reply_text(error_text)
        elif update.message:
            await update.message.reply_text(error_text)

async def top_score(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Tampilkan leaderboard"""
    try:
        if not user_scores:
            message_text = "📊 Belum ada skor yang tercatat."
        else:
            top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            leaderboard = "🏆 **Top Skor Global**\n\n"
            
            for i, (user_id, score) in enumerate(top_users, 1):
                try:
                    user = await context.bot.get_chat(user_id)
                    username = user.username or user.first_name
                except:
                    username = f"User_{user_id}"
                leaderboard += f"{i}. {username}: {score} poin\n"
            
            message_text = leaderboard

        if query:
            await query.message.reply_text(message_text)
        elif update.message:
            await update.message.reply_text(message_text)
            
    except Exception as e:
        logger.error(f"Error in top_score: {e}")
        error_text = "❌ Terjadi error saat mengambil leaderboard."
        if query:
            await query.message.reply_text(error_text)
        elif update.message:
            await update.message.reply_text(error_text)

async def quiz_rules(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Tampilkan aturan bermain"""
    rules_text = (
        "📚 **Aturan Bermain**\n\n"
        "1. Gunakan /mulai untuk memulai game\n"
        "2. Jawab pertanyaan dengan mengirim pesan teks\n"
        "3. Setiap pertanyaan memiliki multiple jawaban benar\n"
        "4. Setiap jawaban benar mendapat 1 poin\n"
        "5. Gunakan /next untuk pertanyaan berikutnya\n"
        "6. Gunakan /nyerah jika ingin menyerah\n"
        "7. Skor akan disimpan secara global\n"
        "8. Bisa dimainkan di grup maupun private chat\n"
        "9. Semua anggota grup bisa menjawab pertanyaan yang sama\n"
    )
    
    if query:
        await query.message.reply_text(rules_text)
    elif update.message:
        await update.message.reply_text(rules_text)
    else:
        logger.error("Cannot determine message source in quiz_rules")

async def quiz_donate(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Tampilkan informasi donasi"""
    donate_text = (
        "❤️ **Donasi**\n\n"
        "Dukung pengembangan bot ini agar tetap aktif!\n\n"
        "**Metode Pembayaran:**\n"
        #"• QRIS (Scan gambar di bawah)\n"
        "• Dana: 083180442386\n"
        "• Seabank: 901960516142\n\n"
        "Terima kasih atas donasinya! ❤️"
    )
    
    try:
        # Coba kirim gambar QRIS
        qris_paths = ["assets/qris.jpg", "images/donation_qris.jpg", "qris.jpg", "donation_qris.jpg"]
        qris_file = None
        for path in qris_paths:
            try:
                with open(path, 'rb') as f:
                    qris_file = f.read()
                logger.info(f"✅ QRIS file found: {path}")
                break
            except FileNotFoundError:
                continue
        
        if qris_file:
            if query:
                await context.bot.send_photo(
                    chat_id=query.message.chat.id,
                    photo=qris_file,
                    caption=donate_text,
                    parse_mode='Markdown'
                )
            elif update.message:
                await context.bot.send_photo(
                    chat_id=update.message.chat.id,
                    photo=qris_file,
                    caption=donate_text,
                    parse_mode='Markdown'
                )
        else:
            if query:
                await query.message.reply_text(donate_text)
            elif update.message:
                await update.message.reply_text(donate_text)
                
    except Exception as e:
        logger.error(f"❌ Error sending QRIS image: {e}")
        if query:
            await query.message.reply_text(donate_text)
        elif update.message:
            await update.message.reply_text(donate_text)

async def quiz_report(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Handler untuk melaporkan pertanyaan"""
    report_text = (
        "⚠️ **Laporkan Pertanyaan**\n\n"
        "Jika menemukan pertanyaan yang tidak pantas atau error, "
        "silahkan laporkan ke admin.\n\n"
        "Admin akan meninjau laporan Anda."
    )
    
    if query:
        await query.message.reply_text(report_text)
    elif update.message:
        await update.message.reply_text(report_text)
    else:
        logger.error("Cannot determine message source in quiz_report")

async def create_question_start(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Mulai proses pembuatan pertanyaan (admin only)"""
    user_id = update.effective_user.id
    
    if user_id not in ADMIN_IDS:
        if query:
            await query.message.reply_text("❌ Hanya admin yang bisa membuat pertanyaan!")
        elif update.message:
            await update.message.reply_text("❌ Hanya admin yang bisa membuat pertanyaan!")
        return
    
    instruction_text = (
        "✏️ **Buat Pertanyaan Baru**\n\n"
        "Silakan kirim pertanyaan dalam format:\n"
        "`Pertanyaan|Jawaban1|Jawaban2|Jawaban3|...`\n\n"
        "**Contoh:**\n"
        "`Sebutkan kota di Indonesia?|Jakarta|Bandung|Surabaya|Medan|Makassar`\n\n"
        "**Note:** \n"
        "• Minimal 1 jawaban\n"
        "• Maksimal tidak terbatas\n"
        "• Gunakan `|` sebagai pemisah\n\n"
        "Ketik `batal` untuk membatalkan."
    )
    
    if query:
        await query.message.reply_text(instruction_text, parse_mode='Markdown')
    elif update.message:
        await update.message.reply_text(instruction_text, parse_mode='Markdown')
    
    context.user_data['waiting_for_question'] = True

    # Schedule timeout
    chat_id = query.message.chat.id if query else update.message.chat.id
    context.user_data['question_timeout'] = context.job_queue.run_once(
        question_timeout_handler, 
        300,  # 5 menit timeout
        data=chat_id
    )

async def question_timeout_handler(context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk timeout pembuatan pertanyaan"""
    chat_id = context.job.data
    if 'waiting_for_question' in context.user_data:
        del context.user_data['waiting_for_question']
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏰ Waktu pembuatan pertanyaan habis. Silakan mulai lagi dengan /buat"
        )

async def cancel_question(update: Update, context: ContextTypes.DEFAULT_TYPE, query=None):
    """Batalkan proses pembuatan pertanyaan"""
    if context.user_data.get('waiting_for_question'):
        # Cancel timeout job jika ada
        if 'question_timeout' in context.user_data:
            context.user_data['question_timeout'].schedule_removal()
            del context.user_data['question_timeout']
        
        context.user_data['waiting_for_question'] = False
        message_text = "❌ Pembuatan pertanyaan dibatalkan."
    else:
        message_text = "ℹ️ Tidak ada proses pembuatan pertanyaan yang aktif."

    if query:
        await query.message.reply_text(message_text)
    elif update.message:
        await update.message.reply_text(message_text)

# ==================== MESSAGE HANDLER ====================
async def handle_quiz_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk menerima pesan teks (jawaban quiz dan pembuatan pertanyaan)"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()
    user_name = update.effective_user.first_name

    # Di awal fungsi handle_quiz_message, tambahkan:
    if text.lower() == 'batal' and context.user_data.get('waiting_for_question'):
        await cancel_question(update, context)
        return
    
    # Cek jika user sedang membuat pertanyaan (admin only)
    if context.user_data.get('waiting_for_question') and user_id in ADMIN_IDS:
        try:
            logger.info(f"Admin {user_id} creating question: {text}")
            if '|' not in text:
                await update.message.reply_text(
                    "❌ Format salah! Gunakan pemisah `|`\n"
                    "Contoh: `Sebutkan warna?|Merah|Hijau|Biru`",
                    parse_mode='Markdown'
                )
                context.user_data['waiting_for_question'] = False
                return
            
            parts = text.split('|')
            if len(parts) < 2:
                await update.message.reply_text(
                    "❌ Format salah! Minimal 1 pertanyaan dan 1 jawaban\n"
                    "Contoh: `Sebutkan warna?|Merah|Hijau|Biru`",
                    parse_mode='Markdown'
                )
                context.user_data['waiting_for_question'] = False
                return
                
            question_text = parts[0].strip()
            answers = [ans.strip() for ans in parts[1:] if ans.strip()]

            logger.info(f"Parsed parts: {parts}")
            logger.info(f"Question: {question_text}, Answers: {answers}")
            
            if not question_text:
                await update.message.reply_text("❌ Pertanyaan tidak boleh kosong!")
                context.user_data['waiting_for_question'] = False
                return
            
            if not answers:
                await update.message.reply_text("❌ Minimal harus ada 1 jawaban!")
                context.user_data['waiting_for_question'] = False
                return
            
            # Add to database
            success = quiz_db.add_question(
                question=question_text,
                correct_answers=answers
            )

            if success:
                initialize_questions()  # Reload questions
                # Kirim notifikasi sukses dengan detail
                success_msg = (
                    "✅ **Pertanyaan Berhasil Dibuat!**\n\n"
                    f"**Pertanyaan:** {question_text}\n"
                    f"**Jumlah Jawaban:** {len(answers)}\n"
                    f"**Jawaban:** {', '.join(answers)}\n\n"
                    f"🕐 {format_time()}"
                )
                await update.message.reply_text(success_msg, parse_mode='Markdown')
                
                # Log untuk debugging
                logger.info(f"Admin {user_id} created question: {question_text}")
                
            else:
                await update.message.reply_text(
                    "❌ Gagal menambah pertanyaan ke database. "
                    "Cek logs untuk detail error."
                )
        
        except Exception as e:
            error_msg = f"❌ Error saat membuat pertanyaan: {str(e)}"
            logger.error(f"Error in question creation: {e}")
            await update.message.reply_text(error_msg)
        
        finally:
            # Reset status
            context.user_data['waiting_for_question'] = False
        return
    
    # Cek jika chat sedang dalam sesi quiz
    if chat_id in quiz_sessions:
        session = quiz_sessions[chat_id]
        question_index = session['current_question_index']
        
        if question_index < len(questions_db):
            question = questions_db[question_index]
            
            # Check if answer is correct and not already answered
            is_correct = False
            correct_answer = None
            
            for correct_ans in question.correct_answers:
                if text.lower() == correct_ans.lower() and correct_ans not in session['current_question_answers']:
                    is_correct = True
                    correct_answer = correct_ans
                    break
            
            if is_correct:
                # Tambahkan ke jawaban yang sudah diberikan
                session['current_question_answers'][correct_answer] = {
                    'user_id': user_id,
                    'user_name': user_name,
                    'timestamp': time.time()
                }
                
                # Update user score
                user_scores[user_id] = user_scores.get(user_id, 0) + 1
                
                # Update pesan pertanyaan
                await update_quiz_message(context, chat_id, session)

                # Kirim pesan konfirmasi
                await update.message.reply_text(
                    f"✅ {user_name} menjawab: {correct_answer} (+1 poin)",
                    reply_to_message_id=update.message.message_id
                )
                
                # Cek jika semua jawaban sudah ditemukan
                if len(session['current_question_answers']) == len(question.correct_answers):
                    await asyncio.sleep(2)
                    session['answered_questions'].add(session['current_question_index'])
                    await start_quiz(update, context)