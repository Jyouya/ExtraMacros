from tkinter import *
from tkinter import font
from Macro import *
import copy
from EditDialog import *
import Config as config

class MacroBar(Canvas):
    #left click selects cell,
    #right click brings up a menu
    #double click brings up the edit macro dialog
    keynames = {
        "backtick": "`",
        "minus": "-",
        "equals": "=",
        "backslash": "\\",
        "period": ".",
        "comma": ",",
        "lbracket": "[",
        "rbracket": "]",
        "semicolon": ";",
        "slash": "/",
        }

    def __init__(self, master, **options):
        self.master = master
        self.root = self.master.master

        #innitialize properties
        self.curX, self.curY = 0, 0
        self.colCount, self.rowCount = 12, 12
        self.cellArray = [[None for x in range(self.rowCount)] for x in range(self.colCount)] #12 x 12 grid
        self.highlightindex = 0

        self.settings = options["Settings"]

        self.char = options["Char"]
        self.main = options["Main"]
        self.sub = options["Sub"]
        self.mod = options["Mod"]

        # remove the keys from the dict before passing it on to the constructor
        del options["Settings"]
        del options["Char"]
        del options["Main"]
        del options["Sub"]
        del options["Mod"]

        Canvas.__init__(self, master, **options)

        # build the right click menu
        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="Edit",command=self.openeditdialog)  # placeholder
        self.menu.add_command(label="Delete", command=self.deletecurrent)
        self.menu.add_command(label="Cut", command=self.copycurrent)
        self.menu.add_command(label="Paste", command=self.pastecurrent)

        self.bind("<Button-3>", self.rightclick)  # call the rightclick method of
        self.bind("<Button-1>", self.leftclick)
        # self.bind("<Double-Button-1>", self.doubleclick)

        self.macrobutton = PhotoImage(file="data/macro_tile.png")
        self.highlight = PhotoImage(file="data/highlight_tile.png")
        self.font = font.Font(family="Helvetica", size=10, weight="bold")

        self.redraw()

        self.copied = {
            "active": False,  # true if something is copied
            "macro": Macro(),  # goes in cellArray
        }

    def rightclick(self, event):
        curX = int(event.x / 68)
        curY = int(event.y / 56)
        self.selectcell(curX, curY)
        self.menu.post(event.x_root, event.y_root)

    def leftclick(self, event):
        curX = int(event.x / 68)
        curY = int(event.y / 56)
        self.selectcell(curX, curY)

    def selectcell(self, x, y):
        self.curX, self.curY = x, y
        self.coords(self.highlightindex, x * 68, y * 56)

    # delete currently selected cell
    def deletecurrent(self, *args):
        if self.curX < len(self.cellArray) and self.curY < len(self.cellArray[self.curX]):
            self.deletecell(self.curX, self.curY)

    # delete specific cell
    def deletecell(self, x, y):
        if x < len(self.cellArray) and y < len(self.cellArray[x]):
            if self.cellArray[x][y]:
                char = self.char.get().lower()
                main = self.main.get()
                sub = self.sub.get()
                mod = self.mod.get().lower()
                layer = self.settings[char]
                if main != "None":
                    layer = layer["jobspecific"][main]
                    if sub != "None":
                        layer = layer[sub]
                layer = layer[mod]
                for key, macro in layer.items():
                    if macro["x"] == str(x + 1) and macro["y"] == str(y + 1):
                        del layer[key]  # remove the backend representation of the macro
                        break
                self.cellArray[x][y] = None  # remove the frontend representation of the macro
                self.redraw()

    def copycurrent(self, *args):
        self.copycell(self.curX, self.curY)

    def copycell(self, x, y):
        if self.cellArray[x][y]:
            self.copied["active"] = True
            self.copied["macro"] = copy.deepcopy(self.cellArray[x][y])

    def pastecurrent(self, *args):
        if self.copied["active"]:
            self.pastecell(self.curX, self.curY)

    def pastecell(self, x, y):
        self.cellArray[x][y] = copy.deepcopy(self.copied["macro"])
        macro = self.cellArray[x][y]
        macro.x = x + 1
        macro.y = y + 1
        char = self.char.get().lower()
        main = self.main.get()
        sub = self.sub.get()
        mod = self.mod.get().lower()
        layer = self.settings[char]
        if main != "None":
            layer = layer["jobspecific"][main]
            if sub != "None":
                layer = layer[sub]
        layer = layer[mod]
        layer[macro.key] = {
            "command": macro.command,
            "text": macro.text,
            "x": str(x + 1),
            "y": str(y + 1),
            "key": macro.key,
            "modifier": mod
        }
        if macro.color:
            print(macro.color)
            layer[macro.key]["color"] = "FF" + macro.color[1:]
        self.redraw()

    def openeditdialog(self, *args):
        d = EditDialog(self,
                       settings=self.settings,
                       defaults={
                           "char": self.char.get().lower(),
                           "main": self.main.get(),
                           "sub": self.sub.get(),
                           "mod": self.mod.get().lower(),
                           "macro": self.cellArray[self.curX][self.curY] or Macro(
                               key="",
                               command="",
                               text="",
                               x=self.curX,
                               y=self.curY
                           )
                       })
        r = d.result
        if not r:
            return
        m = r["macro"]
        # delete the old settings entry so we don't duplicate the cell if the key is changed
        old = self.settings[self.char.get().lower()]
        if self.main.get() != "None":
            old = old["jobspecific"][self.main.get()]
            if self.sub.get() != "None":
                old = old[self.sub.get()]
        old = old[self.mod.get().lower()]
        if self.cellArray[self.curX][self.curY]:
            del old[self.cellArray[self.curX][self.curY].key]

        self.curX, self.curY = m.x, m.y
        print(m.x, m.y)
        # self.cellArray[self.curX][self.curY] = m
        layer = self.settings[r["char"]]
        if r["main"] != "None":
            layer = layer["jobspecific"][r["main"]]
            if r["sub"] != "None":
                layer = layer[r["sub"]]
        layer = layer[r["mod"]]
        layer[m.key] = m.todict()
        print(layer[m.key])
        self.redraw()

    def loadfile(self, filename):
        self.settings = config.load(filename)["settings"]

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
            """if "jobspecific" in char:
                for main_k, main in char["jobspecific"].items():
                    if main_k not in modoptions and main_k not in mainoptions:
                        mainoptions.add(main_k)
                    for sub_k, sub in main.items():
                        if sub_k not in modoptions and sub_k not in suboptions:
                            suboptions.add(sub_k)"""

        self.char.set("Global")
        self.main.set("None")
        self.sub.set("None")
        self.mod.set("Win")

        self.master.charselect["menu"].delete(0, 'end')
        for option in [x.title() for x in charoptions]:
            self.master.charselect["menu"].add_command(label=option, command=tk._setit(self.char, option))

        self.master.mainselect["menu"].delete(0, 'end')
        for option in mainoptions:
            self.master.mainselect["menu"].add_command(label=option, command=tk._setit(self.main, option))

        self.master.subselect["menu"].delete(0, 'end')
        for option in suboptions:
            self.master.subselect["menu"].add_command(label=option, command=tk._setit(self.sub, option))

        self.redraw()

    def newchar(self, char):
        if char.lower() in self.settings:
            return
        self.master.charselect["menu"].add_command(label=char, command=tk._setit(self.char, char))
        self.settings[char.lower()] = {
            "win": {},
            "ctrl": {},
            "alt": {},
            "apps": {}
        }

    def deletechar(self):
        if self.char.get() != "Global":
            del self.settings[self.char.get().lower()]
            self.char.set("Global")

            charoptions = set()

            for char_k, char in self.settings.items():
                charoptions.add(char_k)

            self.master.charselect["menu"].delete(0, 'end')
            for option in [x.title() for x in charoptions]:
                self.master.charselect["menu"].add_command(label=option, command=tk._setit(self.char, option))

            self.recalculatemain()

    def newmain(self, main):
        d = self.settings[self.char.get().lower()]
        if "jobspecific" in d and main in d["jobspecific"]:
            return
        self.master.mainselect["menu"].add_command(label=main, command=tk._setit(self.main, main))
        if "jobspecific" not in d:
            d["jobspecific"] = {}
        d["jobspecific"][main] = {
            "win": {},
            "ctrl": {},
            "alt": {},
            "apps": {}
        }

    def deletejob(self):
        if self.char.get() != "Global" and self.main.get() != "None":
            if self.sub.get() != "None":
                del self.settings[self.char.get().lower()]["jobspecific"][self.main.get()][self.sub.get()]
                self.sub.set("None")
                self.recalculatesub()
            else:
                del self.settings[self.char.get().lower()]["jobspecific"][self.main.get()]
                self.main.set("None")
                self.recalculatemain()
            if not self.settings[self.char.get().lower()]["jobspecific"]:
                del self.settings[self.char.get().lower()]["jobspecific"]
            self.redraw()

    def newsub(self, sub):
        d = self.settings[self.char.get().lower()]
        if "jobspecific" in d and \
                self.main.get() in d["jobspecific"] and\
                sub in d["jobspecific"][self.main.get()]:
            return
        self.master.subselect["menu"].add_command(label=sub, command=tk._setit(self.sub, sub))
        if self.main.get() not in d["jobspecific"]:
            d["jobspecific"][self.main.get()] = {
                "win": {},
                "ctrl": {},
                "alt": {},
                "apps": {}
            }
        d["jobspecific"][self.main.get()][sub] = {
            "win": {},
            "ctrl": {},
            "alt": {},
            "apps": {}
        }

    def recalculatemain(self, *args):
        char = self.char.get().lower()
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

        self.master.mainselect["menu"].delete(0, 'end')
        for option in mainoptions:
            self.master.mainselect["menu"].add_command(label=option, command=tk._setit(self.main, option))

        self.master.subselect["menu"].delete(0, 'end')
        for option in suboptions:
            self.master.subselect["menu"].add_command(label=option, command=tk._setit(self.sub, option))

        if self.main.get() not in mainoptions:
            self.main.set("None")

        if self.sub.get() not in suboptions:
            self.sub.set("None")

        self.recalculatesub()

    def recalculatesub(self, *args):
        char = self.char.get().lower()
        main = self.main.get()
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

        self.master.subselect["menu"].delete(0, 'end')
        for option in suboptions:
            self.master.subselect["menu"].add_command(label=option, command=tk._setit(self.sub, option))

        if self.sub.get() not in suboptions:
            self.sub.set("None")

        self.redraw()

    def savefile(self, filename):
        config.save({"settings": self.settings}, filename)

    def newrow(self):
        for col in self.cellArray:
            col.append(None)
        self.rowCount = self.rowCount + 1

    def newcol(self):
        self.cellArray.append([None for x in range(self.colCount)])
        self.colCount = self.colCount + 1

    def redraw(self, *args):
        self.delete(ALL)

        char = self.char.get().lower()
        main = self.main.get()
        sub = self.sub.get()
        mod = self.mod.get().lower()

        self.cellArray = [[None for x in range(self.rowCount)] for x in range(self.colCount)]  # 12 x 12 grid

        # fill in global keybinds
        if not mod in self.settings["global"]:
            self.settings["global"][mod] = {}

        for key, bind in self.settings["global"][mod].items():
            self.cellArray[int(bind["x"]) - 1][int(bind["y"]) - 1] = Macro(
                modifier=mod,
                key=key,
                command=bind["command"],
                text=bind["text"],
                x=bind["x"],
                y=bind["y"],
                color="color" in bind and ("#" + bind["color"][2:]) or None)

        # fill in character specific keybinds
        if char != "global":
            for key, bind in self.settings[char][mod].items():
                self.cellArray[int(bind["x"]) - 1][int(bind["y"]) - 1] = Macro(
                    modifier=mod,
                    key=key,
                    command=bind["command"],
                    text=bind["text"],
                    x=bind["x"],
                    y=bind["y"],
                    color="color" in bind and ("#" + bind["color"][2:]) or None)

        # job specific keybinds
        if main != "None":
            for key, bind in self.settings[char]["jobspecific"][main][mod].items():
                self.cellArray[int(bind["x"]) - 1][int(bind["y"]) - 1] = Macro(
                    modifier=mod,
                    key=key,
                    command=bind["command"],
                    text=bind["text"],
                    x=bind["x"],
                    y=bind["y"],
                    color="color" in bind and ("#" + bind["color"][2:]) or None)

            if sub != "None":
                for key, bind in self.settings[char]["jobspecific"][main][sub][mod].items():
                    self.cellArray[int(bind["x"]) - 1][int(bind["y"]) - 1] = Macro(
                        modifier=mod,
                        key=key,
                        command=bind["command"],
                        text=bind["text"],
                        x=bind["x"],
                        y=bind["y"],
                        color="color" in bind and ("#" + bind["color"][2:]) or None)

        for col in range(self.colCount):
            for row in range(self.rowCount):
                self.create_image(col * 68, row * 56, image=self.macrobutton, anchor=NW)
                macro = self.cellArray[col][row]
                if macro:
                    macro.x = int(macro.x) - 1
                    macro.y = int(macro.y) - 1
                    self.create_text(5 + col * 68,
                                     1 + row * 56,
                                     font=self.font,
                                     anchor=NW,
                                     fill=macro.color or "white",
                                     text=macro.text)
                    self.create_text(62 + col * 68,
                                     36 + row * 56,
                                     font=self.font,
                                     anchor=NE,
                                     fill=macro.color or "white",
                                     justify=RIGHT,
                                     text=mod.title() + " " + (
                                          macro.key in MacroBar.keynames and
                                          MacroBar.keynames[macro.key] or
                                          macro.key).upper())
        # draw the highlight box
        self.highlightindex = self.create_image(self.curX * 68, self.curY * 56, image=self.highlight, anchor=NW)



