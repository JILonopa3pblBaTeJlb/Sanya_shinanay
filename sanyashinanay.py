import random
import re
import time
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

TOKEN = "YOUR_BOT_TOKEN"

DIALOGUE_LIST = [
    "ну а дальше что",
    "и что дальше",
    "нет, ты объясни",
    "но почему",
    "а это почему",
    "а почему это",
    "ага и чо дальше",
    "это ты так думаешь",
    "поясни",
    "я не понял, чо еще раз?",
    "и что",
    "повтори",
    "в смысле",
    "а чо в смысле",
    "чо еще ляпнешь",
    "сам додумался?",
    "чо ты хочешь-то?",
    "чо сказал щас",
    "а по фактам?",
    "мне показалось или ты быканул?",
    "это зачем щас сказал",
    "ты кто такой",
    "ты где есть то",
    "конкретнее",
    "подробнее",
    "обоснуй",
    "и чо к чему",
    "а ну повтори"
]

STRELKA_REPLYS_LIST = [
    "то чо борзый дохуя самый",
    "слышь охуел ты ли чо?",
    "ебать ты дерзота",
    "втащу тебе чо скажешь тогда",
    "ты ща в рог словиш э",
    "ты предъявить решил или чо я не вкурю",
    "слышь рамс попутал кучерявый я эбал завязывай моросить",
    "чорт я тя найду",
    "попутавший ты ли чо",
    "э бля нахуй фильтруй базар",
    "слышь ты реально выхватишь сейчас"
]

STRELKA_TRIGGERS_LIST = [
    "завали",
    "заткнись",
    "задорнов"
]

SPECIAL_EVENTS_LIST = {
    "тупой бот": "тупой бот мамку твою ебет",
    "300": "отсоси у тракториста",
    "триста": "отсоси у тракториста",
    "бот пидор": "пидор у тебя в штанах",
    "вульва": "лол вульва",
    "вагина": "лол вагина она же почти вульва",
    "пизда": "ДА",
    "ПИДОР": "100% НАТУРАЛЬНАЯ ПИДРИЛА",
    "админ": "админ питух",
    "саня чо как": ["запор газы геморрой в жопе размером с грецкий орех а так норм", "пиздык хуяк", "SELFTEST SEQUENCE INIT"],    
    "ГА": ["в жопе панина нога", "буа га ГА", "крокодил залупа сыр"],
    "гараж": ["бля ща бы в гараж", "обожаю гараж и спидгараж", "как же хочется в гараж"],
    "Химмаш": ["химмаш это вам не уралмаш", "химаш не купиш не продаш", "химмаш ванлав"],    
}

def special_events(message_text: str):
    for word, reply_set in SPECIAL_EVENTS_LIST.items():
        if re.search(r'\b' + re.escape(word.lower()) + r'\b', message_text.lower()):
            if isinstance(reply_set, list):  # Check if the reply_set is a list of phrases
                return random.choice(reply_set)  # Choose a random phrase from the set
            else:
                return reply_set
    return None

def contains_cyrillic(text):
    return bool(re.search('[а-яА-Я]', text))

def lexical_reduplication(word):
    if len(word) > 20 or not contains_cyrillic(word):
        return None

    vowels = "аеёиоуыэюя"
    vowel_mapping = {"а": "я", "е": "е", "ё": "ё", "и": "и", "о": "ё", "у": "ю", "ы": "ы", "э": "е", "ю": "ю", "я": "я"}

    first_vowel_index = None
    for i, char in enumerate(word):
        if char.lower() in vowels:
            first_vowel_index = i
            break

    if first_vowel_index is None:
        return word

    first_vowel = word[first_vowel_index].lower()
    mapped_vowel = vowel_mapping.get(first_vowel, first_vowel)

    new_word = "ху" + ("" if first_vowel_index == 1 else "й") + mapped_vowel + word[first_vowel_index:]

    # Remove doubled letters
    new_word = "".join(new_word[i] for i in range(len(new_word)) if i == 0 or new_word[i] != new_word[i - 1])

    # Handle specific combinations
    new_word = new_word.replace("ёо", "ё").replace("йю", "ю").replace("яа", "я").replace("юу", "ю").replace("йе", "е")

    if word[0].isupper():
        new_word = new_word.capitalize()

    return new_word

def reduplicate(update: Update, context: CallbackContext):
    last_word = re.findall(r'\b\w+\b', update.message.text)[-1]
    reduplicated_word = lexical_reduplication(last_word)
    if reduplicated_word:
        update.message.reply_text(reduplicated_word)

def restart(update: Update, context: CallbackContext):
    context.chat_data['mode'] = 'NORMAL'
    context.chat_data['dialogue_count'] = 0
    update.message.reply_text("ухх бля ебать")

def handle_message(update: Update, context: CallbackContext):
    if not update.message:
        return

    chat_data = context.chat_data
    user_id = update.message.from_user.id
    reply_to_message = update.message.reply_to_message

    special_event_reply = special_events(update.message.text)
    if special_event_reply:
        update.message.reply_text(special_event_reply)
        return

    if reply_to_message and reply_to_message.from_user.id == context.bot.id:
        if chat_data.get('mode') != 'STRELKA':
            chat_data['mode'] = 'DIALOGUE'
            chat_data['dialogue_count'] = 0
    else:
        if chat_data.get('mode') != 'NORMAL':
            chat_data['mode'] = 'NORMAL'

    if chat_data.get('mode') == 'NORMAL':
        if random.random() <= 0.05:
            reduplicate(update, context)
        return

    if any(trigger.lower() in update.message.text.lower() for trigger in STRELKA_TRIGGERS_LIST):
        chat_data['mode'] = 'STRELKA'
        chat_data['strelka_user'] = user_id
        chat_data['strelka_count'] = 0
        update.message.reply_text(random.choice(STRELKA_REPLYS_LIST))
        return

    if chat_data.get('mode') == 'STRELKA':
        if not update.message.reply_to_message or update.message.reply_to_message.from_user.id != context.bot.id:
            return
        if user_id == chat_data['strelka_user']:
            update.message.reply_text(random.choice(STRELKA_REPLYS_LIST))
            chat_data['strelka_count'] += 1
            if chat_data['strelka_count'] >= 5:
                chat_data['mode'] = 'NORMAL'
                chat_data['strelka_count'] = 0
            return

    if chat_data.get('mode') == 'DIALOGUE':
        chat_data['dialogue_count'] += 1
        dialogue_limit = 15  # Change this value to set a different limit
        if chat_data['dialogue_count'] >= dialogue_limit:
            chat_data['mode'] = 'NORMAL'
            chat_data['dialogue_count'] = 0
        else:
            update.message.reply_text(random.choice(DIALOGUE_LIST))
            return



def main():
    updater = Updater(token=TOKEN, use_context=True)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", restart))
    dispatcher.add_handler(CommandHandler("restart", restart))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
