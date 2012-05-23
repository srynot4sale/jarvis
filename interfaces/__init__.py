# Jarvis interfaces
import interfaces.http

def init(kernel):
    intr = []
    intr.append(interfaces.http.init(kernel))

    return intr
