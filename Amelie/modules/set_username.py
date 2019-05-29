# -*- coding: utf-8 -*

from os                     import path as os_path
from libs.configParser      import Parser


# === Username installation module ===

def set_username():
    if os_path.exists("../DataBase/username.json"):
        username = ''
        with open("../DataBase/username.json", 'r') as file_user:
            username = file_user.read()

        if (username == ""):
            print(Parser("getName"))
            username = input("> ")

        if (username != ""):
            with open("../DataBase/username.json", "w") as writeUsername:
                writeUsername.write(username)
            print ("\n Welcome, "+ username + "!")

        else:
            print (Parser("emptyName"))
            set_username()

    else:
        with open("../DataBase/username.json", 'w') as file_user:
            file_user.close()
        set_username()