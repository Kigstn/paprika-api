from src.API import *

import tkinter as tk
import tkinter.scrolledtext as tkscrolled
import uuid
import hashlib
import gzip
import json
import datetime


# ------------------------------------------------------------
# tkinter windows

class ChangeAuth:
    # window to change your authentication
    def __init__(self, master):
        self.master = master
        self.master.title("Please update your authentication")
        self.frame = tk.Frame(self.master)

        # set all entries
        self.label_email = make_label(self.frame, text="Email")
        self.email = make_entry(self.frame, width=70, text=config["USER DATA"]["auth_email"])
        self.label_pw = make_label(self.frame, text="Password")
        self.pw = make_entry(self.frame, width=70, text=config["USER DATA"]["auth_password"])
        self.update = make_button(self.frame, text="Update User Data", command=self.set_auth, width=20)

        # pack all entries
        self.label_email.grid(row=0)
        self.email.grid(row=1)
        self.label_pw.grid(row=2)
        self.pw.grid(row=3)
        self.update.grid(row=4, column=0, padx=50, pady=10)
        self.frame.pack()

    def set_auth(self):
        # change config values
        config["USER DATA"]["auth_email"] = self.email.get()
        config["USER DATA"]["auth_password"] = self.pw.get()

        with open('../config.ini', 'w') as configfile:  # save
            config.write(configfile)

        print(f"updated user data with email - {config['USER DATA']['auth_email']}, pw - {config['USER DATA']['auth_password']}")

        # get a new token
        get_token()

        # kill window
        self.master.destroy()


class Recipes:
    # window which shows all recipes
    def __init__(self, master):
        self.master = master
        self.master.title("Your Recipes")
        self.frame = tk.Frame(self.master)

        # get all recipes
        self.recipes = {}
        for recipe in get_request(f"/api/v2/sync/recipes/"):
            # get recipe infos and save them in a dict
            info = get_request(f"/api/v2/sync/recipe/{recipe['uid']}")
            self.recipes.update({
                info["name"]: info
            })

        # create the buttons to view infos
        self.buttons = []
        for name, info in self.recipes.items():
            if not info["in_trash"]:
                self.buttons.append(make_button(self.frame, name, command=lambda x=name: self.select_recipe(x), width=30, height=2))

        # make buttons fancy and actually make them
        i = 0
        j = 0
        for button in self.buttons:
            button.grid(row=i, column=j, padx=10, pady=10)
            j += 1
            if j > 6:
                i += 1
                j = 0

        self.frame.pack()

    def select_recipe(self, name):
        new_window = tk.Toplevel(self.master)
        Recipe(new_window, self.recipes[name])


class Recipe:
    # window which displays one recipe
    def __init__(self, master, info={}):
        self.dict = {}

        self.dict["categories"] = []
        self.dict["cook_time"] = ""
        self.dict["created"] = str(datetime.datetime.utcnow())[0:19]
        self.dict["description"] = ""
        self.dict["difficulty"] = ""
        self.dict["directions"] = ""
        self.dict["hash"] = hashlib.sha256(str(uuid.uuid4()).encode("utf-8")).hexdigest().upper()
        self.dict["image_url"] = ""
        self.dict["in_trash"] = False
        self.dict["ingredients"] = ""
        self.dict["is_pinned"] = False
        self.dict["name"] = ""
        self.dict["notes"] = ""
        self.dict["nutritional_info"] = ""
        self.dict["on_favorites"] = False
        self.dict["on_grocery_list"] = ""
        self.dict["photo"] = ""
        self.dict["photo_hash"] = ""
        self.dict["photo_large"] = ""
        self.dict["photo_url"] = ""
        self.dict["prep_time"] = ""
        self.dict["rating"] = 0
        self.dict["scale"] = ""
        self.dict["servings"] = ""
        self.dict["source"] = ""
        self.dict["source_url"] = ""
        self.dict["total_time"] = ""
        self.dict["uid"] = str(uuid.uuid4()).upper()

        # update the info with all current info
        self.dict.update(info)
        self.master = master
        self.master.title("Recipe Viewer")

        # create scrollabe canvas
        canvas = tk.Canvas(master, width=1000, height=800, background="#ffffff")
        frame = tk.Frame(canvas, background="#ffffff")
        vsb = tk.Scrollbar(master, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((4, 4), window=frame, anchor="nw")

        frame.bind("<Configure>", lambda event, x=canvas: self.on_frame_configure(x))

        i = 0
        self.entries = {}
        # display the values
        for name, value in self.dict.items():
            # skip some
            if name in ["entries", "uid", "hash", "rating", "categories", "photo_large", "is_pinned", "on_favorites", "created", "in_trash"]:
                continue

            label = make_label(frame, name)

            # make text scrollabel if long entry
            if name in ["ingredients", "directions"]:
                entry = make_scrollable_entry(frame, width=100, text=value)
            else:
                entry = make_entry(frame, width=100, text=value)

            label.grid(row=i, column=0, padx=10, pady=10)
            i += 1
            entry.grid(row=i, column=0, padx=10, pady=10)
            i += 1

            self.entries.update({name: entry})

        # create button to save changes
        update = make_button(frame, text="Upload Changes", command=self.save, width=20)
        update.grid(row=i, column=0, padx=10, pady=10)

    def on_frame_configure(self, canvas):
        # Reset the scroll region to encompass the inner frame
        canvas.configure(scrollregion=canvas.bbox("all"))

    def as_paprikarecipe(self) -> bytes:
        return gzip.compress(json.dumps(self.dict).encode("utf-8"))

    def save(self):
        # get the new data
        for name, entry in self.entries.items():
            try:
                self.entries[name] = entry.get()
            except TypeError:
                self.entries[name] = entry.get(1.0, tk.END)

        # populate the dict again
        self.dict.update(self.entries)

        # save the data and upload it
        files = {'data': self.as_paprikarecipe()}
        post_request(request_url=f"/api/v2/sync/recipe/{self.dict['uid']}/", files=files)

        # kill window
        self.master.destroy()


class Main:
    # window main window which does all the things
    def __init__(self, master):
        self.master = master
        self.master.title("Paprika Editor")
        self.frame = tk.Frame(self.master)

        # set all entries
        self.edit = make_button(self.frame, text="Edit and View Recipes", command=self.view_recipes, width=30)
        self.make = make_button(self.frame, text="Create New Recipe", command=self.make_recipe, width=30)
        self.update = make_button(self.frame, text="Update Authentication Data", command=self.change_auth, width=30)

        # pack all entries
        self.edit.grid(row=1, column=0, padx=50, pady=10)
        self.make.grid(row=2, column=0, padx=50, pady=10)
        self.update.grid(row=3, column=0, padx=50, pady=10)
        self.frame.pack()

    # create new window
    def new_window(self, window_class):
        new_window = tk.Toplevel(self.master)
        window_class(new_window)

    # change user auth
    def change_auth(self):
        self.new_window(ChangeAuth)

    # change user auth
    def view_recipes(self):
        self.new_window(Recipes)

    # change user auth
    def make_recipe(self):
        self.new_window(Recipe)


# ------------------------------------------------------------
# Functions for making tkinter objects

def make_entry(frame, width, text=""):
    entry = tk.Entry(frame, fg="black", bg="white", width=width)
    if text:
        entry.insert(index=0, string=text)
    return entry


def make_scrollable_entry(frame, width, text=""):
    entry = tkscrolled.ScrolledText(frame, fg="black", bg="white", width=width)
    if text:
        entry.insert(1.0, text)
    return entry


def make_label(frame, text):
    return tk.Label(frame, text=text)


def make_button(frame, text, command, width=10, height=2):
    return tk.Button(frame, text=text, command=command, width=width, height=height)


# ------------------------------------------------------------
# general functions

def change_auth(tk_root):
    ChangeAuth(master=tk_root)
    tk_root.mainloop()
