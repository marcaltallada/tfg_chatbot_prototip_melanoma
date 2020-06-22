
from googletrans import Translator

def tr2english(text,user_data):
    translator = Translator()
    msg_tr = translator.translate(text).text
    if 'language' not in user_data:
        user_data['language'] = translator.detect(text).lang

    return msg_tr

def tr2other(text,language):
    translator = Translator()
    msg_tr = translator.translate(text, dest=str(language)).text
    return msg_tr
