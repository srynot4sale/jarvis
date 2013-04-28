# Jarvis functions
import functions.server
import functions.calendar
import functions.list

def init():
    funcs = []
    funcs.append(functions.server.init())
    funcs.append(functions.calendar.init())
    funcs.append(functions.list.init())

    return funcs
