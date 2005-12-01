
import gtk
import time
import threading

import RHPL_execWithCaptureErrorStatus


BASH_PATH='/bin/bash'

def execWithCapture(bin, args):
    return execWithCaptureErrorStatus(bin, args)[0]

def execWithCaptureStatus(bin, args):
    res = execWithCaptureErrorStatus(bin, args)
    return res[0], res[2]

def execWithCaptureErrorStatus(bin, args):
    command = 'LANG=C ' + bin
    if len(args) > 0:
        for arg in args[1:]:
            command = command + ' ' + arg
    ex = ExecutionThread(BASH_PATH, [BASH_PATH, '-c', command])
    ex.start()
    return ex.get_result()


class ExecutionThread(threading.Thread):
    
    def __init__(self, bin, args):
        threading.Thread.__init__(self)
        
        self.__bin = bin
        self.__args = args
        self.__ret = ['', '', -1]
    
    def run(self):
        # call RHPL.execWithCaptureErrorStatus when moved into RHPL
        self.__ret = RHPL_execWithCaptureErrorStatus.execWithCaptureErrorStatus(self.__bin, self.__args)
    
    def get_result(self):
        while self.isAlive():
            time.sleep(0.1)
            while gtk.events_pending():
                gtk.main_iteration()
        self.join()
        return self.__ret
    
