# Jarvis interfaces
import interfaces.http
import interfaces.web

def init(kernel):
    intr = []
    intr.append(interfaces.http.init(kernel))
    intr.append(interfaces.web.init(kernel))

    return intr
