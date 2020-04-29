from googletrans import Translator
from json import JSONEncoder, dumps, dump
from functools import lru_cache



@lru_cache(maxsize = 1000)
def try_translate(msg,sender,receiver):
    translator = Translator()
    try:
        result = translator.translate(msg, src=sender, dest=receiver)
        print(f'NOT IN CACHE\nNeed to get translation for: {msg}:', result.text)
        return result.text
    except ValueError:
        print('translate failed')
        return None

def print_user_details(user_id,username,socket_id,join_room):
    print('\nUSER CREDENTIALS')
    print('-'*40)
    print('user id:', user_id)
    print('session username:', username)
    print('socket_id:', socket_id)
    print('joining last chat room_id: ', join_room)
    print('-'*40)
    return 

def print_rooms(room_cache):
    class MyEncoder(JSONEncoder):
        def default(self, o):
            return o.__dict__ 
    print('\nROOMS:')
    print('-'*40)
    print(dumps(room_cache, cls=MyEncoder, indent=4))
    print('-'*40)
    return 


LANG_SUPPORT = {
    "en" : "English",
    "pl" : "Polski",
    "zh-cn": "中文",
    "es" : "Español",
    "iw" : "עברית",
    "fr" : "Français",
    "de" : "Deutsche",
    "ru" : "русский",
    "it" : "Italiano",
    "ja" :  "日本語",
    "pt" : "Português"
}

LANGCODES={
    "afrikaans": "af",
    "albanian": "sq",
    "amharic": "am",
    "arabic": "ar",
    "armenian": "hy",
    "azerbaijani": "az",
    "basque": "eu",
    "belarusian": "be",
    "bengali": "bn",
    "bosnian": "bs",
    "bulgarian": "bg",
    "catalan": "ca",
    "cebuano": "ceb",
    "chichewa": "ny",
    "chinese": "zh-cn",
    "corsican": "co",
    "croatian": "hr",
    "czech": "cs",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "esperanto": "eo",
    "estonian": "et",
    "filipino": "tl",
    "finnish": "fi",
    "french": "fr",
    "frisian": "fy",
    "galician": "gl",
    "georgian": "ka",
    "german": "de",
    "greek": "el",
    "gujarati": "gu",
    "haitian creole": "ht",
    "hausa": "ha",
    "hawaiian": "haw",
    "hebrew": "iw",
    "hindi": "hi",
    "hmong": "hmn",
    "hungarian": "hu",
    "icelandic": "is",
    "igbo": "ig",
    "indonesian": "id",
    "irish": "ga",
    "italian": "it",
    "japanese": "ja",
    "javanese": "jw",
    "kannada": "kn",
    "kazakh": "kk",
    "khmer": "km",
    "korean": "ko",
    "kurdish (kurmanji)": "ku",
    "kyrgyz": "ky",
    "lao": "lo",
    "latin": "la",
    "latvian": "lv",
    "lithuanian": "lt",
    "luxembourgish": "lb",
    "macedonian": "mk",
    "malagasy": "mg",
    "malay": "ms",
    "malayalam": "ml",
    "maltese": "mt",
    "maori": "mi",
    "marathi": "mr",
    "mongolian": "mn",
    "myanmar (burmese)": "my",
    "nepali": "ne",
    "norwegian": "no",
    "pashto": "ps",
    "persian": "fa",
    "polish": "pl",
    "portuguese": "pt",
    "punjabi": "pa",
    "romanian": "ro",
    "russian": "ru",
    "samoan": "sm",
    "scots gaelic": "gd",
    "serbian": "sr",
    "sesotho": "st",
    "shona": "sn",
    "sindhi": "sd",
    "sinhala": "si",
    "slovak": "sk",
    "slovenian": "sl",
    "somali": "so",
    "spanish": "es",
    "sundanese": "su",
    "swahili": "sw",
    "swedish": "sv",
    "tajik": "tg",
    "tamil": "ta",
    "telugu": "te",
    "thai": "th",
    "turkish": "tr",
    "ukrainian": "uk",
    "urdu": "ur",
    "uzbek": "uz",
    "vietnamese": "vi",
    "welsh": "cy",
    "xhosa": "xh",
    "yiddish": "yi",
    "yoruba": "yo",
    "zulu": "zu",
    "Filipino": "fil",
    "Hebrew": "he"
}