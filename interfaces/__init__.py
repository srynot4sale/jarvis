# Jarvis interfaces
import interfaces.firefox
import interfaces.http
import interfaces.web

def init(kernel):
    intr = []
    intr.append(interfaces.http.init(kernel))
    intr.append(interfaces.web.init(kernel))
    intr.append(interfaces.firefox.init(kernel))

    return intr
