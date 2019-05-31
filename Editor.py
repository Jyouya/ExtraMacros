import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import Config as config
from MacroBar import *
from tkinter import simpledialog
from tkinter import messagebox


def openfile():
    return

def save():
    return

def saveas():
    return

def placeholder():
    return


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        self.characters = {"Global"}
        self.characterindex = 0

        
        self.create_widgets()

    def create_widgets(self):
        # First, the menubar
        menubar = tk.Menu(self.master)

        nav = tk.Frame(master=self)
        character = tk.StringVar(master=nav, value="Global")
        mainjob = tk.StringVar(master=nav, value="None")
        subjob = tk.StringVar(master=nav, value="None")
        modifier = tk.StringVar(master=nav, value="Win")

        self.macros = MacroBar(master=self,
                               Settings=config.load("data/settings.xml")["settings"],
                               Char=character,
                               Main=mainjob,
                               Sub=subjob,
                               Mod=modifier)

        # file menu
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='Open', command=self.openfile)
        # filemenu.add_command(label='Save', command=self.savefile)
        filemenu.add_command(label='Save As', command=self.savefile)
        filemenu.add_command(label='Exit', command=self.master.quit)
        menubar.add_cascade(label='File', menu=filemenu)

        # macrobar menu
        mbmenu = tk.Menu(menubar, tearoff=0)
        mbmenu.add_command(label='New Character', command=self.newchar)
        mbmenu.add_command(label='New Main Job', command=self.newmain)
        mbmenu.add_command(label='New Sub Job', command=self.newsub)
        mbmenu.add_command(label='Delete Character', command=self.macros.deletechar)
        mbmenu.add_command(label='Delete Job', command=self.macros.deletejob)
        menubar.add_cascade(label='Macrobar', menu=mbmenu)

        # cell menu
        cellmenu = tk.Menu(menubar, tearoff=0)
        cellmenu.add_command(label='Edit', command=self.macros.openeditdialog)
        cellmenu.add_command(label='Delete', command=self.macros.deletecurrent)
        cellmenu.add_command(label='Cut', command=self.macros.copycurrent)
        cellmenu.add_command(label='Paste', command=self.macros.pastecurrent)
        menubar.add_cascade(label='Cell', menu=cellmenu)

        # attach the menu bar to the window
        self.master.config(menu=menubar)

        settings = self.macros.settings
        charoptions = set()
        mainoptions = {"None"}
        suboptions = {"None"}
        modoptions = {
            "win",
            "ctrl",
            "alt",
            "apps"
        }

        # build the option values for the dropdowns
        for char_k, char in settings.items():
            charoptions.add(char_k)
            """if "jobspecific" in char:
                for main_k, main in char["jobspecific"].items():
                    if main_k not in modoptions and main_k not in mainoptions:
                        mainoptions.add(main_k)
                    for sub_k, sub in main.items():
                        if sub_k not in modoptions and sub_k not in suboptions:
                            suboptions.add(sub_k)"""

        self.charselect = tk.OptionMenu(nav, character, *[x.title() for x in charoptions])
        self.mainselect = tk.OptionMenu(nav, mainjob, *mainoptions)
        self.subselect = tk.OptionMenu(nav, subjob, *suboptions)
        self.modselect = tk.OptionMenu(nav, modifier, "Win", "Ctrl", "Alt", "Apps")

        nav.pack(side=tk.TOP, expand=False, fill=tk.X)
        self.charselect.pack(side=tk.LEFT)
        self.mainselect.pack(side=tk.LEFT)
        self.subselect.pack(side=tk.LEFT)
        self.modselect.pack(side=tk.LEFT)

        self.macros.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        character.trace("w", self.macros.recalculatemain)
        #character.trace("w", self.macros.redraw)
        mainjob.trace("w", self.macros.recalculatesub)
        #mainjob.trace("w", self.macros.redraw)
        subjob.trace("w", self.macros.redraw)
        modifier.trace("w", self.macros.redraw)

    def openfile(self):
        filename = tk.filedialog.askopenfilename(title="Select File",
                                                 filetypes=(("xml files", "*.xml"),("all files", "*.*")))
        if filename == "":
            return
        self.macros.loadfile(filename)

    def savefile(self):
        filename = tk.filedialog.asksaveasfilename(title="Select File",
                                                   defaultextension=".xml",
                                                   filetypes=[("xml files", "*.xml")])
        if filename == "":
            return
        self.macros.savefile(filename)

    def newchar(self):
        d = simpledialog.askstring("New Char", "Name: ",parent=self)
        if d:
            self.macros.newchar(d.title())

    def newmain(self):
        if self.macros.char.get().lower() == "global":
            messagebox.showerror("Error", "Cannot add mainjob without a character selected")
            return
        d = simpledialog.askstring("New Main Job", "Job: ", parent=self)
        if d:
            self.macros.newmain(d.upper())

    def newsub(self):
        if self.macros.main.get() == "None":
            messagebox.showerror("Error", "Cannot add subjob without a main job selected")
            return
        elif self.macros.char.get().lower() == "global":
            messagebox.showerror("Error", "Cannot add subjob without a character selected")
            return
        d = simpledialog.askstring("New Sub Job", "Job: ", parent=self)
        if d:
            self.macros.newsub(d.upper())

root = tk.Tk()
app = Application(master=root)
app.pack(expand=True, fill=tk.BOTH)
app.mainloop()
