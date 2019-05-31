# read and write files generated with the windower config library
from collections import OrderedDict


def load(filename):
    with open(filename, "r") as file:
        root = {}
        keystack = []
        current = root
        data = ""  # string data between tags
        while True:
            end = False
            c = file.read(1)
            if not c:
                break
            # ignore all leading whitespace
            if c.isspace() and data == "":
                continue
            # first, parse tags
            if c == "<":
                tag = ""
                while c != ">":
                    c = file.read(1)
                    if not c:
                        raise Exception("Unexpected EOF")
                    if c == "/":
                        end = True
                    elif c != ">":
                        tag += c
                if end and tag == keystack[-1]:
                    if data != "":
                        if parent:
                            parent[keystack[-1]] = data.strip()
                        else:
                            raise Exception("Multiple values in key: " + " ".join(keystack))
                    data = ""
                    keystack.pop()
                    current = root
                    parent = None
                    for key in keystack:  # go up a level in the tree
                        current = current[key]
                elif end:
                    raise Exception("Closed tag that wasn't open:  " + tag)
                elif tag[0] == "!":
                    if tag[0:8] == "![CDATA[" and tag[-2:] == "]]":
                        data = tag[8:-2]
                        data = data.replace("\t", "")  # remove tabs
                        if parent:
                            parent[keystack[-1]] = data
                            data = ""
                        else:
                            raise Exception("Multiple values in key: " + " ".join(keystack))
                    elif tag[1:3] == "--":  # start of a comment
                        comment = True
                        while comment:
                            while c != "-":
                                c = file.read(1)
                                if not c:
                                    raise Exception("Unexpected EOF")
                            if file.read(2) == "->":
                                comment = False
                        # last character of the comment is read, state is unchanged
                    else:
                        raise Exception("Unable to read tag: " + tag)
                elif tag[0] == "?":
                    continue
                else:
                    if "&" in tag:  # resolve escape sequences in tags
                        escape = ""
                        i = tag.index("&")
                        j = i
                        while j < len(tag):
                            while tag[j] != "&" and j < len(tag):
                                j += 1
                            i = j
                            if tag[j] == "&":
                                while tag[j] != ";":
                                    j += 1
                                escape = tag[i+1:j+1]
                                tag = tag[:i] + lookup[escape] + (j+1 < len(tag) and tag[j+1:] or "")
                                j = i + 1
                    keystack.append(tag)  # push tag to stack
                    current[tag] = {}  # create a new dict for the tag
                    parent = current  # reference to the parent.  this reference is only valid after opening a tag
                    current = current[tag]  # set current one layer deeper
            # next, parse data
            else:
                if c == "&":
                    escape = ""
                    while c != ";":
                        c = file.read(1)
                        if not c:
                            raise Exception("Unexpected EOF")
                        escape += c
                    if not escape in lookup:
                        raise Exception("Unrecognized Escape Sequence: &" + escape)
                    c = lookup[escape]
                data += c
    return root


def save(dict, filename):
    with open(filename, "w") as file:
        file.write("<?xml version=\"1.1\" ?>\n")  # config wants this, even though config files aren't valid xml
        file.write(tagtostring(dict, 0))


def tagtostring(layer, tabdepth):
    string=""
    for k, v in layer.items():
        tabs = "".join(["\t" for c in range(tabdepth)])
        if type(v) == dict:
            string += tabs + "<" + k + ">\n" + tagtostring(v, tabdepth + 1) + tabs + "</" + k + ">\n"
        else:
            value = v.strip()
            if "\n" in value:
                value = value.replace("\n", "\n" + tabs + "\t")
                value = cdata(value)
            else:
                value = escape(value)
            value = "\t" + value
            string += tabs + "<" + k + ">\n" + tabs + value + "\n" + tabs + "</" + k + ">\n"
    return string

def cdata(string):
    return "<![CDATA[" + string + "]]>"


lookup = {
    "amp;": "&",
    "lt;": "<",
    "gt;": ">",
    "quot;": "\"",
    "apos;": "'"
}

lookup2 = OrderedDict({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
    "'": "&apos;"
})

# TODO to improve escaping accuracy, need to use a single pass method for escaping
def escape(string):
    for k, v in lookup2.items():
        string = string.replace(k, v)
    return string

