#!/usr/bin/env python
from __future__ import unicode_literals

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings, ConditionalKeyBindings
from prompt_toolkit.filters import Condition
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.widgets import TextArea, SearchToolbar, Dialog, Label, Button
from prompt_toolkit import ANSI
from prompt_toolkit.layout.screen import Point


import pyperclip

from tabulate import tabulate

from unidecode import unidecode

import math

def toPlain(a):
    return unidecode(a.lower())

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

        table.append([start + pwd["group"], pwd["name"], pwd["user"], pwd["password"], pwd["project"] + end])
        i = i + 1

    headers = ["group", "name", "user", "password", "project"]
    return tabulate(table, headers=headers)

page = -1
pageSize = 30

def nextPassword():
    global selected
    global page
    
    if page != -1:
        selected = (selected + 1) % (pageSize + 2)
        if selected == 0:
            page += 1
            selected = 2
    else:
        selected += 1

def previousPassword():
    global selected
    global page
    
    if page != -1 and page != 0:
        selected = (selected - 1) % (pageSize + 2)
        if selected == 1:
            page -= 1
            selected = pageSize + 1
    else:
        selected -= 1

def nextPage():
    global selected
    global page
    global filteredList
    
    lastPage = math.floor(len(filteredList) / pageSize)
    if page != -1 and page != lastPage: 
        page += 1
        selected = 2
        table.content.text = getFormattedTable(selected, filteredList)


def previousPage():
    global selected
    global page
    
    if page != -1 and page > 0:
        page -= 1
        selected = 2
        table.content.text = getFormattedTable(selected, filteredList)

    
def getFormattedTable(selected, passwords):
    global page

    if len(passwords) > pageSize:
        if page == -1:
            passwords = passwords[:pageSize]
            page = 0
        else:
            passwords = passwords[page * pageSize: page * pageSize + pageSize]

    return ANSI(tabulatePasswords(selected, passwords))

passwords = lambda: []
filteredList = []

selected = 0 
searching = False
info = False
selectedInfo = selected

def filterTable(buff):
    global searching
    global selected
    global filteredList
    global table
    selected = 0
    searching = False

    filteredList = []
    for pwd in passwords:
        found = False
        for attr in pwd:
            if (pwd[attr] and not found):
                found = toPlain(input_field.text) in toPlain(pwd[attr])
        if (found):
            filteredList.append(pwd)

    text = ANSI("")  
    if len(filteredList) == 0:
        text = ANSI(bcolors.FAIL + "No matches..." + bcolors.ENDC)
    else:
        page = -1
        text = getFormattedTable(selected, filteredList)
    
    table.content.text = text

def reloadPasswords():
    global selected
    global filteredList
    global passwords
    global page

    page = -1 
    passwords = getPasswords()
    filteredList = passwords
    if len(filteredList) > 0:
        selected = 2
    table.content.text = getFormattedTable(selected, filteredList)


@Condition
def isSearching():
    return searching

@Condition
def showInfo():
    return info


class GetCursorPosition:
    def __call__(self):
        global selected
        y = selected
        return Point(0,y)

def button_handler():
    global info
    info = False
    layout.focus(input_field)


dialog = Dialog(
        title="Info",
        body=Label(text="...", dont_extend_height=True),
        buttons=[
            Button(text="OK", handler=button_handler),
        ])

search_field = SearchToolbar()
input_field = TextArea(height=1, prompt='/', style='class:input-field', multiline=False, wrap_lines=False, search_field=search_field)
input_field.accept_handler = filterTable

table = Window(content=FormattedTextControl(text=getFormattedTable(selected, filteredList), 
            get_cursor_position=GetCursorPosition()))

root_container = HSplit([
    table,
    ConditionalContainer(content=input_field, filter=isSearching),
    ConditionalContainer(content=dialog, filter=showInfo)
])
layout = Layout(container=root_container)

def goNextPassword():
    nextPassword()
    table.content.text = getFormattedTable(selected, filteredList)


def getSelectedPassword(selected):
    if selected < 2:
        return None
    else:
        if (page > 0):
            return filteredList[selected - 2 + pageSize * page]
        else:
            return filteredList[selected - 2]

# Key bindings.
kb = KeyBindings()

@kb.add('c-c')
def _(event):
    " Quit when control-c is pressed. "
    event.app.exit()

@kb.add('n')
def _(event):
    nextPage()

@kb.add('p')
def _(event):
    previousPage()

@kb.add('j')
def _(event):
    global selected

    lastPage = math.floor((len(filteredList) / pageSize))
    if page == -1:
        if selected <= len(filteredList):
            goNextPassword()
    elif page != lastPage:
        goNextPassword()
    elif page == lastPage:
        lastPageElements = len(filteredList) - pageSize * page 
        if selected <= lastPageElements:
            goNextPassword()

@kb.add('k')
def _(event):
    global selected
    if selected > 0:
        previousPassword()
        table.content.text = getFormattedTable(selected, filteredList)

@kb.add('y')
def _(event):
    global selected
    password = getSelectedPassword(selected)["password"]
    pyperclip.copy(password)

@kb.add('x')
def _(event):
    global selected
    username = getSelectedPassword(selected)["user"]
    pyperclip.copy(username)

@kb.add('w')
def _(event):
    global selected
    info = getSelectedPassword(selected)["info"]
    pyperclip.copy(info)


@kb.add('g', 'g')
def _(event):
    global selected
    global page

    selected = 0
    page = 0
    table.content.text = getFormattedTable(0, filteredList)

@kb.add('r')
def _(event):
    reloadPasswords()

@kb.add('i')
def _(event):
    global info
    global selectedInfo

    if (not info or selected != selectedInfo):
        selectedInfo = selected
        info = True
        textInfo = getSelectedPassword(selected)["info"]
        dialog.body = Label(text=textInfo, dont_extend_height=True)
        layout.focus(dialog)
    else:
        info = False
        layout.focus(input_field)


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


def pwdmgr(_getPasswords, *args, **kwargs):
    global getPasswords
    global pageSize

    pageSize = kwargs.get("pageSize", 30)

    getPasswords = _getPasswords
    reloadPasswords()
    application.run()

if __name__ == '__main__':
    pwdmgr(lambda: [])
