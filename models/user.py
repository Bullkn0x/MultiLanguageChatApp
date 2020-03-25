class User:

    def __init__(self,username,language='english'):

        self.username= username
        self.language = language

    def update_language_pref(self,language):
        self.language = language
