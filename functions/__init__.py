# Jarvis functions
import functions.calendar
import functions.list
import functions.server

def init():
    funcs = []
    funcs.append(functions.calendar.init())
    funcs.append(functions.list.init())
    funcs.append(functions.server.init())

    return funcs
