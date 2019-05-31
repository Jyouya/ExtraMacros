import tkSimpleDialog
import tkinter as tk
from Macro import *
from tkinter.colorchooser import *


class EditDialog(tkSimpleDialog.Dialog):

    def __init__(self, master, settings, defaults):
        self.master = master
        self.settings = settings
        self.defaults = defaults
        super().__init__(master, title="Edit Macro")

    def body(self, master):
        contentpanel = tk.Frame(master=self)
        leftpanel = tk.Frame(contentpanel)
        rightpanel = tk.Frame(contentpanel)

        contentpanel.pack(side=tk.TOP, expand=True, fill=tk.BOTH)

        self.character = tk.StringVar(master=leftpanel, value=self.defaults["char"].title())
        self.mainjob = tk.StringVar(master=leftpanel, value=self.defaults["main"])
        self.subjob = tk.StringVar(master=leftpanel, value=self.defaults["sub"])
        self.modifier = tk.StringVar(master=leftpanel, value=self.defaults["mod"].title())

        self.x = tk.StringVar(master=rightpanel, value=str(int(self.defaults["macro"].x) + 1))
        self.y = tk.StringVar(master=rightpanel, value=str(int(self.defaults["macro"].y) + 1))
        self.key = tk.StringVar(master=rightpanel, value=self.defaults["macro"].key)
        self.color = self.defaults["macro"].color

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
        for char_k, char in self.settings.items():
            charoptions.add(char_k)

        char = self.settings[self.defaults["char"].lower()]
        if "jobspecific" in char:
            for main_k, main in char["jobspecific"].items():  # calculate all main options for current char
                if main_k not in modoptions and main_k not in mainoptions:
                    mainoptions.add(main_k)
            if self.defaults["main"] != "None":
                for sub_k, sub in char["jobspecific"][self.defaults["main"]].items():
                    if sub_k not in modoptions and sub_k not in suboptions:
                        suboptions.add(sub_k)

        self.charselect = tk.OptionMenu(leftpanel, self.character, *[x.title() for x in charoptions])
        self.mainselect = tk.OptionMenu(leftpanel, self.mainjob, *mainoptions)
        self.subselect = tk.OptionMenu(leftpanel, self.subjob, *suboptions)
        self.modselect = tk.OptionMenu(leftpanel, self.modifier, *[x.title() for x in modoptions])

        self.character.trace("w", self.recalculatemain)
        self.mainjob.trace("w", self.recalculatesub)

        leftpanel.pack(side=tk.LEFT, expand=False, fill=tk.Y)
        self.charselect.pack(side=tk.TOP, fill=tk.X)
        self.mainselect.pack(side=tk.TOP, fill=tk.X)
        self.subselect.pack(side=tk.TOP, fill=tk.X)
        self.modselect.pack(side=tk.TOP, fill=tk.X)

        xentry = tk.Entry(master=rightpanel,
                          textvariable=self.x,
                          validate="key",
                          validatecommand=(self.register(lambda new: new == "" or new.isdigit()), "%P"))
        xentry.bind("<Tab>", EditDialog.focus_next_window)
        xentry.bind("<Shift-Tab>", EditDialog.focus_prev_window)
        yentry = tk.Entry(master=rightpanel,
                          textvariable=self.y,
                          validate="key",
                          validatecommand=(self.register(lambda new: new == "" or new.isdigit()), "%P"))
        yentry.bind("<Tab>", EditDialog.focus_next_window)
        yentry.bind("<Shift-Tab>", EditDialog.focus_prev_window)
        keyentry = tk.Entry(master=rightpanel, textvariable=self.key)
        keyentry.bind("<Tab>", EditDialog.focus_next_window)
        keyentry.bind("<Shift-Tab>", EditDialog.focus_prev_window)
        self.text = tk.Text(master=rightpanel, width=10, height=3, font=("Helvetica", 10), wrap=tk.NONE)
        self.text.insert(tk.INSERT, self.defaults["macro"].text)
        self.text.bind("<Tab>", EditDialog.focus_next_window)
        self.text.bind("<Shift-Tab>", EditDialog.focus_prev_window)
        self.command = tk.Text(master=rightpanel, width=30, height=3, font=("Helvetica", 10))
        self.command.insert(tk.INSERT, self.defaults["macro"].command)
        self.command.bind("<Tab>", EditDialog.focus_next_window)
        self.command.bind("<Shift-Tab>", EditDialog.focus_prev_window)

        def getcolor():
            _, self.color = askcolor() or self.color
            self.color = self.color != "#FFFFFF" and self.color or None
            self.colorbutton.config(bg=self.color or "#FFFFFF")

        self.colorbutton = tk.Button(rightpanel, bg=self.color or "#FFFFFF", command=getcolor)

        rightpanel.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        tk.Label(rightpanel, text="Column: ").grid(row=0, sticky=tk.W)
        xentry.grid(row=0, column=1, sticky=tk.W)
        tk.Label(rightpanel, text="Row: ").grid(row=1, sticky=tk.W)
        yentry.grid(row=1, column=1, sticky=tk.W)
        tk.Label(rightpanel, text="Key: ").grid(row=2, sticky=tk.W)
        keyentry.grid(row=2, column=1, sticky=tk.W)
        tk.Label(rightpanel, text="Text: ").grid(row=3, sticky=tk.W)
        self.text.grid(row=3, column=1, sticky=tk.W)
        tk.Label(rightpanel, text="Command: ").grid(row=4, sticky=tk.W)
        self.command.grid(row=4, column=1, sticky=tk.W)
        tk.Label(rightpanel, text="Color: ").grid(row=5, sticky=tk.W)
        self.colorbutton.grid(row=5, column=1, sticky=tk.W + tk.E)

    def apply(self):
        macro = Macro(
            modifier=self.modifier.get().lower(),
            key=self.key.get(),
            command=self.command.get(1.0, tk.END),
            text=self.text.get(1.0, tk.END),
            x=int(self.x.get()) - 1,
            y=int(self.y.get()) - 1,
            color=self.color  # and ("#FF" + self.color[1:]) or None
        )
        self.result = {
            "macro": macro,
            "char": self.character.get().lower(),
            "main": self.mainjob.get(),
            "sub": self.subjob.get(),
            "mod": self.modifier.get().lower()
        }

    def recalculatemain(self, *args):
        char = self.character.get().lower()
        mainoptions = {"None"}
        suboptions = {"None"}
        modoptions = {
            "win",
            "ctrl",
            "alt",
            "apps"
        }

        # build the option values for the dropdowns
        if "jobspecific" in self.settings[char]:
            for main_k, main in self.settings[char]["jobspecific"].items():
                if main_k not in modoptions and main_k not in mainoptions:
                    mainoptions.add(main_k)
                for sub_k, sub in main.items():
                    if sub_k not in modoptions and sub_k not in suboptions:
                        suboptions.add(sub_k)

        self.mainselect["menu"].delete(0, 'end')
        for option in mainoptions:
            self.mainselect["menu"].add_command(label=option, command=tk._setit(self.mainjob, option))

        self.subselect["menu"].delete(0, 'end')
        for option in suboptions:
            self.subselect["menu"].add_command(label=option, command=tk._setit(self.subjob, option))

        if self.mainjob.get() not in mainoptions:
            self.mainjob.set("None")

        if self.subjob.get() not in suboptions:
            self.subjob.set("None")

        self.recalculatesub()

    def recalculatesub(self, *args):
        char = self.character.get().lower()
        main = self.mainjob.get()
        suboptions = {"None"}
        modoptions = {
            "win",
            "ctrl",
            "alt",
            "apps"
        }

        if "jobspecific" in self.settings[char]:
            if main != "None":
                for sub_k, sub in self.settings[char]["jobspecific"][main].items():
                    if sub_k not in modoptions and sub_k not in suboptions:
                        suboptions.add(sub_k)

        self.subselect["menu"].delete(0, 'end')
        for option in suboptions:
            self.subselect["menu"].add_command(label=option, command=tk._setit(self.subjob, option))

        if self.subjob.get() not in suboptions:
            self.subjob.set("None")

    @staticmethod
    def focus_next_window(event):
        event.widget.tk_focusNext().focus()
        return("break")

    @staticmethod
    def focus_prev_window(event):
        event.widget.tk_focusPrev().focus()
        return("break")