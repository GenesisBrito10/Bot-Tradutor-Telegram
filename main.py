import sqlite3
from time import sleep
import telebot
from telebot import types
from googletrans import Translator



LANGUAGE, = range(1)

TOKEN = '6332535404:AAEhRqLwYDIPSR4wai9n437QMqlLSkirQvw'

admin_user_id = 1747910349


bot = telebot.TeleBot(TOKEN,parse_mode='HTML',disable_web_page_preview=True)

language_codes = {
    '🇦🇿 Azərbaycan': 'az',
    '🇧🇩 বাংলাদেশ': 'bn',
    '🇨🇳 中国（简体）': 'zh-cn',
    '🇨🇳 中國（繁體）': 'zh-tw',
    '🇭🇷 Hrvatska': 'hr',
    '🇨🇿 Česká republika': 'cs',
    '🇩🇰 Danmark': 'da',
    '🇳🇱 Nederland': 'nl',
    '🇺🇸 United States': 'en',
    '🇫🇮 Suomi': 'fi',
    '🇫🇷 France': 'fr',
    '🇩🇪 Deutschland': 'de',
    '🇬🇷 Ελλάδα': 'el',
    '🇮🇳 भारत': 'hi',
    '🇭🇺 Magyarország': 'hu',
    '🇮🇩 Indonesia': 'id',
    '🇮🇹 Italia': 'it',
    '🇯🇵 日本': 'ja',
    '🇰🇷 대한민국': 'ko',
    '🇱🇹 Lietuva': 'lt',
    '🇲🇾 Malaysia': 'ms',
    '🇳🇴 Norge': 'no',
    '🇵🇱 Polska': 'pl',
    '🇵🇹 Portugal': 'pt',
    '🇷🇴 România': 'ro',
    '🇷🇺 Россия': 'ru',
    '🇸🇰 Slovensko': 'sk',
    '🇸🇮 Slovenija': 'sl',
    '🇪🇸 España': 'es',
    '🇸🇪 Sverige': 'sv',
    '🇹🇷 Türkiye': 'tr',
    '🇺🇦 Україна': 'uk',
    '🇺🇿 Oʻzbekiston': 'uz'
}



# SQLite database setup
def setup_database():
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            language TEXT
        )
    ''')
    conn.commit()
    conn.close()

def is_language_saved(user_id):
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    existing_user = cursor.fetchone()
    
    conn.close()
    
    return existing_user is not None

def save_user_to_db(user_id, language):
    if not is_language_saved(user_id):
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users (user_id, language) VALUES (?, ?)', (user_id, language))
        conn.commit()

        conn.close()


def get_all_user_ids():
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    user_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return user_ids





@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    print(user_id)
    markup = create_language_markup()
    bot.send_message(user_id, "Hello! Please select your preferred language.", reply_markup=markup)
    bot.register_next_step_handler(message, select_language)


def create_language_markup():
   
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = [types.InlineKeyboardButton(language, callback_data=language) for language in language_codes.keys()]
    markup.add(*buttons)
    return markup


def select_language(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Please use the buttons below to select your preferred language.")

@bot.callback_query_handler(func=lambda call: call.data in language_codes)
def handle_language_selection(callback_query):
    user_id = callback_query.from_user.id
    selected_language = callback_query.data
    language_code = language_codes[selected_language]
    if not is_language_saved(user_id):
        
        
        save_user_to_db(user_id, language_code)
        welcome_message = translate("Bem vindo ao nosso bot !",language_code)
        bot.send_message(user_id, welcome_message)
    else:
        language_code = get_user_language(user_id)
        erro = translate("Ja esta cadastrado ao nosso bot !",language_code)
        bot.send_message(user_id,erro )

def translate(text,language_code):
    translator = Translator()
    try:
        sleep(1.5)
        translated = translator.translate(text,src='pt', dest=language_code)
    except:
        sleep(1.5)
        translated = translator.translate(text,src='pt', dest=language_code)
        return translated.text
    
    return translated.text

def get_user_language(user_id):
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
    language = cursor.fetchone()
    conn.close()
    return language[0] if language else None

@bot.message_handler(func=lambda message: message.from_user.id == admin_user_id, content_types=['text','photo', 'video','audio','voice'])
def handle_admin_message(message):
    user_ids = get_all_user_ids()
    
    if message.text:
        admin_message = message.text
        for user_id in user_ids:
            user_language = get_user_language(user_id)
            if user_language:
        
                translated_message = translate(admin_message, user_language)
                sent_message = bot.send_message(user_id, translated_message)
                
                
               

    if message.audio:
        admin_audio = message.audio.file_id
        caption = message.caption if message.caption else None
        for user_id in user_ids:
            bot.send_audio(user_id, admin_audio,caption=caption)
    
    if message.photo:
        photo_id = message.photo[-1].file_id  # Obtenha o ID do arquivo da maior foto (última da lista)
        caption = message.caption if message.caption else None
        for user_id in user_ids:
            bot.send_photo(user_id, photo_id, caption=caption)
    
    if message.video:
        admin_video = message.video.file_id
        caption = message.caption if message.caption else None
        for user_id in user_ids:
            bot.send_video(user_id, admin_video,caption=caption)
    
    if message.voice:
        admin_voice = message.voice.file_id
        caption = message.caption if message.caption else None
        for user_id in user_ids:
            bot.send_voice(user_id, admin_voice,caption=caption)
    
    if message.document:
        admin_document = message.document.file_id
        caption = message.caption if message.caption else None
        for user_id in user_ids:
            bot.send_document(user_id, admin_document,caption=caption)
    
    
    
    bot.send_message(admin_user_id, "Mensagens enviada.")



def main():
    setup_database()
    bot.polling()

if __name__ == "__main__":
    main()

