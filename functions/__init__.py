# Jarvis functions
import functions.server
import functions.calendar
import functions.list
import functions.tv

def init():
    funcs = []
    funcs.append(functions.server.init())
    funcs.append(functions.calendar.init())
    funcs.append(functions.list.init())
    funcs.append(functions.tv.init())

    return funcs
