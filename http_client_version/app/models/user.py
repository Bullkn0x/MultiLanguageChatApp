class User:

    def __init__(self,username,socketID,language='english'):

        self.username= username
        self.socketID = socketID
        self.language = language
    def update_language_pref(self,language):
        self.language = language
