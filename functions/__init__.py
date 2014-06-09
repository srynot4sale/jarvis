# Jarvis functions
import functions.server
import functions.calendar
import functions.list
import functions.log
import functions.habit

def init():
    funcs = []
    funcs.append(functions.server.init())
    funcs.append(functions.calendar.init())
    funcs.append(functions.list.init())
    funcs.append(functions.log.init())
    funcs.append(functions.habit.init())

    return funcs
