from GUI import *
from API import get_token

import tkinter as tk


if __name__ == "__main__":
    tk_root = tk.Tk()

    # check if email / user are set, else do that
    if not (config["USER DATA"]["auth_email"] and config["USER DATA"]["auth_password"]):
        change_auth(tk_root)

    # get a token
    get_token()

    # display main window
    Main(master=tk_root)
    tk_root.mainloop()


# loads of info
# https://gist.github.com/mattdsteele/7386ec363badfdeaad05a418b9a1f30a
