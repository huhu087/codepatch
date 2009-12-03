# Borrowed most this code from a guy named Fabien Henon.
# Original link is here:
# http://mail.python.org/pipermail/python-list/2002-June/151652.html

"""
Pseudo debug screens

These capture stderr/std and route them to a Tkinter text widget.
This implementation uses a common window for stdout/stderr with
an asterisk at the beginning of each stderr line.

"""
import Tkinter
import sys,string

class DbgText:
    Dbgtopwin=None
    Dbgwidget=None
    DbgRoot=None
    
    def _kill_topwin(self):
        DbgText.Dbgwidget=None
        if DbgText.Dbgtopwin != None:
            DbgText.Dbgtopwin.destroy()
        DbgText.Dbgtopwin=None
       
    def __init__(self,kind=''):
        self.kind=kind
        self.window=None
        self.widget=None
        self.called=0
        self.hide=0
        self.buffer=''

##    def __del__(self):
##        "On deletion, wait for user to see the output"
##        if DbgText.Dbgtopwin != None:
##            See()
##        self._kill_topwin()
    
    def write(self,charstr):
        "write text to buffer or window"
        if self.hide:
            self.buffer.append(charstr)
        else:
            if self.window == None:
                if DbgText.Dbgtopwin == None:
                    DbgText.Dbgtopwin=Tkinter.Tk()
                    DbgText.Dbgtopwin.protocol('WM_DELETE_WINDOW',Dbg_kill_topwin)
                    DbgText.Dbgwidget=Tkinter.Text(DbgText.Dbgtopwin)
                    DbgText.Dbgwidget.pack(expand=1)
                top=DbgText.Dbgtopwin
                wid=DbgText.Dbgwidget
            else:
                if self.widget == None:
                    self.widget=Tkinter.Text(self.window)
                top=self.window
                wid=self.widget
            if self.kind != '':
                ep=wid.index('end')
                sp=string.split(ep,'.')
                # determine length of 'previous' line
                prevl=int(sp[0])
                tx='\n'
                if prevl:
                    pl='%d.0' % (prevl-1)
                    tx=wid.get(pl,ep)
                # if this is start of a new line
                if tx[0] == '\n':
                    wid.insert('end',self.kind)
            wid.insert('end',charstr)
            #scroll to the very bottom
            wid.see(wid.index('end'))
        self.called=1
        top.update()

def Dbg_kill_topwin():
    f=DbgText()
    f._kill_topwin()
    
def Take_stdout():
    "DIsplay stdout in text widget"
    if not isinstance(sys.stdout,DbgText):
        f=DbgText()
        f.prev=sys.stdout
        sys.stdout=f

def Take_stderr():
    "DIsplay stderr in text widget"
    if not isinstance(sys.stderr,DbgText):
        f=DbgText('*')
        f.prev=sys.stderr
        sys.stderr=f

    
def Restore_stdout():
    f=sys.stdout
    if isinstance(f,DbgText):
        sys.stdout=f.prev
        del f

def Restore_stderr():
    f=sys.stderr
    if isinstance(f,DbgText):
        sys.stderr=f.prev
        del f

def Define_Root():
    root=Tkinter.Tk()
    root.withdraw()
    DbgText.DbgRoot=root


def See():
    db=DbgText()
    if db.Dbgtopwin != None:
        db.Dbgtopwin.mainloop() # loop for me to see

def Take_all():
    "send stderr/stdout to Tkinter text window/widget"
    Take_stdout()
    Take_stderr()

def Restore_all():
    "restore stderr/stdout"
    Restore_stdout()
    Restore_stderr()

        
if __name__ == '__main__':
    print 'stdout is here'
    Take_stdout()
    print 'stdout should now be in window'
    print ' this is the second line'
    raw_input()
    Restore_stdout()
    print 'stdout back to original'
    
