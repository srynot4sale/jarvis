# Jarvis functions
import functions.server
import functions.calendar
import functions.list
import functions.log

def init():
    funcs = []
    funcs.append(functions.server.init())
    funcs.append(functions.calendar.init())
    funcs.append(functions.list.init())
    funcs.append(functions.log.init())

    return funcs
