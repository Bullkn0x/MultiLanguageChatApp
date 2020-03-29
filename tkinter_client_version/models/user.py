class User:

    def __init__(self,username,client_info,language='english'):

        self.username= username
        self.language = language
        self.client_info = client_info
    def update_language_pref(self,language):
        self.language = language
