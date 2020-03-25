import socket
from threading import Thread
import tkinter


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
        top.quit()


def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("{quit}")
    send()

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

top = tkinter.Tk()
top.title("Shitty Chat App")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.insert(0,"Type your messages here.")

entry_field.bind("<FocusIn>", on_entry_click)
entry_field.bind('<FocusOut>', on_focusout)
entry_field.config(fg = 'grey')
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()
disconnect_button = tkinter.Button(top, text="Disconnect", command=on_closing)
disconnect_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

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