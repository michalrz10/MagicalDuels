import threading


class Log:
    def __init__(self):
        self.lock=threading.Lock()

    def log(self,message):
        self.lock.acquire()
        try:
            x=open('server.log','w+')
            x.write(str(message)+'\n')
            x.close()
            print(message)
        finally:
            self.lock.release()