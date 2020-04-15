class User:

    def __init__(self,username,socket_id, language='english', current_room=None):


        self.username= username
        self.socket_id = socket_id
        self.language = language
        if current_room is None:
            self.current_room = 1
        else:
            self.current_room = current_room
    def update_language_pref(self,language):
        self.language = language
