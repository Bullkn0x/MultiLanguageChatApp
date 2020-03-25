import socket
from threading import Thread
import tkinter
LANGUAGES = {
    'af': 'afrikaans',
    'sq': 'albanian',
    'am': 'amharic',
    'ar': 'arabic',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'eu': 'basque',
    'be': 'belarusian',
    'bn': 'bengali',
    'bs': 'bosnian',
    'bg': 'bulgarian',
    'ca': 'catalan',
    'ceb': 'cebuano',
    'ny': 'chichewa',
    'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)',
    'co': 'corsican',
    'hr': 'croatian',
    'cs': 'czech',
    'da': 'danish',
    'nl': 'dutch',
    'en': 'english',
    'eo': 'esperanto',
    'et': 'estonian',
    'tl': 'filipino',
    'fi': 'finnish',
    'fr': 'french',
    'fy': 'frisian',
    'gl': 'galician',
    'ka': 'georgian',
    'de': 'german',
    'el': 'greek',
    'gu': 'gujarati',
    'ht': 'haitian creole',
    'ha': 'hausa',
    'haw': 'hawaiian',
    'iw': 'hebrew',
    'hi': 'hindi',
    'hmn': 'hmong',
    'hu': 'hungarian',
    'is': 'icelandic',
    'ig': 'igbo',
    'id': 'indonesian',
    'ga': 'irish',
    'it': 'italian',
    'ja': 'japanese',
    'jw': 'javanese',
    'kn': 'kannada',
    'kk': 'kazakh',
    'km': 'khmer',
    'ko': 'korean',
    'ku': 'kurdish (kurmanji)',
    'ky': 'kyrgyz',
    'lo': 'lao',
    'la': 'latin',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'lb': 'luxembourgish',
    'mk': 'macedonian',
    'mg': 'malagasy',
    'ms': 'malay',
    'ml': 'malayalam',
    'mt': 'maltese',
    'mi': 'maori',
    'mr': 'marathi',
    'mn': 'mongolian',
    'my': 'myanmar (burmese)',
    'ne': 'nepali',
    'no': 'norwegian',
    'ps': 'pashto',
    'fa': 'persian',
    'pl': 'polish',
    'pt': 'portuguese',
    'pa': 'punjabi',
    'ro': 'romanian',
    'ru': 'russian',
    'sm': 'samoan',
    'gd': 'scots gaelic',
    'sr': 'serbian',
    'st': 'sesotho',
    'sn': 'shona',
    'sd': 'sindhi',
    'si': 'sinhala',
    'sk': 'slovak',
    'sl': 'slovenian',
    'so': 'somali',
    'es': 'spanish',
    'su': 'sundanese',
    'sw': 'swahili',
    'sv': 'swedish',
    'tg': 'tajik',
    'ta': 'tamil',
    'te': 'telugu',
    'th': 'thai',
    'tr': 'turkish',
    'uk': 'ukrainian',
    'ur': 'urdu',
    'uz': 'uzbek',
    'vi': 'vietnamese',
    'cy': 'welsh',
    'xh': 'xhosa',
    'yi': 'yiddish',
    'yo': 'yoruba',
    'zu': 'zulu',
    'fil': 'Filipino',
    'he': 'Hebrew'
}

LANGCODES = dict(map(reversed, LANGUAGES.items()))

def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    client_socket.send(bytes(msg, "utf8"))
    if msg == "{quit}":
        client_socket.close()
        window.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()


# Tkinter utils 
def on_entry_click(event):
    """function that gets called whenever entry_field is clicked"""
    if entry_field.get() == "Type your messages here.":
       entry_field.delete(0, "end") # delete all the text in the entry_field
       entry_field.insert(0, '') #Insert blank for user input
       entry_field.config(fg = 'black')
def on_focusout(event):
    if entry_field.get() == '':
        entry_field.insert(0, "Type your messages here.")
        entry_field.config(fg = 'grey')

def select_text_or_select_and_copy_text(e):
    e.widget.select_range(0, 'end')     

def delete_text(e):
    e.widget.delete('0', 'end')

def language_chosen(language):
    print('closed by', language)
    lang_code= LANGCODES[language]
    client_socket.send(bytes(f'!changelanguage {lang_code}', "utf8"))

window = tkinter.Tk()
window.title("Shitty Chat App")
window.geometry('500x500')

messages_frame = tkinter.Frame(window)
my_msg = tkinter.StringVar()  # For the messages to be sent.
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
messages_frame.pack(fill='both',expand=True)

entry_field = tkinter.Entry(window, width=50, textvariable=my_msg)
entry_field.insert(0,"Type your messages here.")
entry_field.bind("<FocusIn>", on_entry_click)
entry_field.bind('<FocusOut>', on_focusout)
entry_field.config(fg = 'grey')
entry_field.bind('<Control-a>', select_text_or_select_and_copy_text)
entry_field.bind('<Control-c>', select_text_or_select_and_copy_text)
entry_field.bind('<Delete>', delete_text)
entry_field.bind("<Return>", send)

entry_field.pack()

tkvar = tkinter.StringVar()
language_select = tkinter.OptionMenu(window, tkvar, *LANGCODES, command=language_chosen)
language_select.pack()
send_button = tkinter.Button(window, text="Send", command=send)
send_button.pack()
disconnect_button = tkinter.Button(window, text="Disconnect", command=on_closing)
disconnect_button.pack()

window.protocol("WM_DELETE_WINDOW", on_closing)

#----Now comes the sockets part----
HOST = None
PORT = None
if not PORT:
    PORT = 33008
else:
    PORT = int(PORT)

if not HOST:
    HOST = '127.0.0.1'
else:
    HOST = HOST


BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.