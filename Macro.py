

class Macro:

    def __init__(self, modifier=None, key=None, command=None, text=None, x=None, y=None, color=None):
        self.modifier = modifier
        self.key = key
        self.command = command
        self.text = text
        self.x = x
        self.y = y
        self.color = color

    def move(self, x, y):
        self.x = x
        self.y = y

    def todict(self):
        m = {
            "command": self.command,
            "text": self.text,
            "x": str(self.x + 1),
            "y": str(self.y + 1),
        }
        if self.color:
            m["color"] = "FF" + self.color[1:]
        return m
