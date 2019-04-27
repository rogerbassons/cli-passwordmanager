#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings, ConditionalKeyBindings
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea, SearchToolbar
from prompt_toolkit import ANSI
from prompt_toolkit.layout.screen import Point

import pyperclip

from tabulate import tabulate

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def tabulatePasswords(selected, passwords):
    table = []
    i = 0
    for pwd in passwords:
        start = ""
        end = ""
        if (selected == i + 2):
            start = bcolors.OKGREEN
            end = bcolors.ENDC

        table.append([start + pwd["group"], pwd["name"], pwd["user"], pwd["password"] + end])
        i = i + 1

    headers = ["group", "name", "user", "password"]
    return tabulate(table, headers=headers)

def getFormattedTable(selected, passwords):
    return ANSI(tabulatePasswords(selected, passwords))


passwords = []
for x in range(0,100):
    i = str(x)
    passwords.append({"group": "G" + i, "name": "Site" + i, "user": "user" + i, "password": "pass" + i})
filteredList = passwords

selected = 0 
searching = False

def filterTable(buff):
    global searching
    global selected
    global filteredList
    selected = 0
    searching = False

    filteredList = []
    for pwd in passwords:
        if any(input_field.text in pwd[attr] for attr in pwd):
            filteredList.append(pwd)
    text = ANSI("")
    if len(filteredList) == 0:
        text = ANSI(bcolors.FAIL + "No matches..." + bcolors.ENDC)
    else:
        text = getFormattedTable(selected, filteredList)
    
    if (len(root_container.children) > 0):
        root_container.children[0].content.text = text


@Condition
def isSearching():
    return searching

class GetCursorPosition:
    def __call__(self):
        global selected
        y = selected
        return Point(0,y)

search_field = SearchToolbar()
input_field = TextArea(height=1, prompt='/', style='class:input-field', multiline=False, wrap_lines=False, search_field=search_field)
input_field.accept_handler = filterTable

root_container = HSplit([
    Window(content=FormattedTextControl(text=getFormattedTable(selected, filteredList), get_cursor_position=GetCursorPosition())),
    ConditionalContainer(content=input_field, filter=isSearching)
])
layout = Layout(container=root_container)

# Key bindings.
kb = KeyBindings()

@kb.add('c-c')
def _(event):
    " Quit when control-c is pressed. "
    event.app.exit()

@kb.add('j')
def _(event):
    global selected
    if selected <= len(filteredList):
        selected = selected + 1
        root_container.children[0].content.text = getFormattedTable(selected, filteredList)

@kb.add('k')
def _(event):
    global selected
    if selected > 0:
        selected = selected - 1
        root_container.children[0].content.text = getFormattedTable(selected, filteredList)

@kb.add('y')
def _(event):
    global selected
    password = filteredList[selected - 2]["password"]
    pyperclip.copy(password)

@kb.add('x')
def _(event):
    global selected
    username = filteredList[selected - 2]["user"]
    pyperclip.copy(username)

@kb.add('g', 'g')
def _(event):
    global selected
    selected = 0
    root_container.children[0].content.text = getFormattedTable(0, filteredList)

@kb.add('r')
def _(event):
    global selected
    global filteredList
    selected = 0
    filteredList = passwords
    root_container.children[0].content.text = getFormattedTable(0, filteredList)

@kb.add('/')
def _(event):
    global searching
    searching = True

@Condition
def notSearching():
    return not searching

registry = ConditionalKeyBindings(kb, notSearching)

# Build a main application object.
application = Application(
    layout=layout,
    key_bindings=registry,
    full_screen=True)

def main():
    application.run()


if __name__ == '__main__':
    main()
