from tkinter import *
from controls import *
import time
import socket
import sys
import select


class MainWin:
  def __init__(self):
    self.sock = None
    self.root = Tk()
    self.root.title("Horn Ochsen")
    self.root.geometry("1000x400")
    self.frame = Frame(self.root, width=1000, height=1000, bg="white")
    #self.tbtn = Card(self.frame, 4, 1)
    #self.tbtn.place(10,10,100,150)
    self.startFrame = StartFrame(self.frame, self.socketAction)
    self.startFrame.place()
    self.frame.pack(fill=BOTH, expand=1)
  
  def socketAction(self, sock):
    self.sock = sock
    print("Socket opened")
  
  def timer(self):
    size = 1024
    if self.sock != None:
      #try:
      print("waiting")
      r,w,e = select.select([self.sock],[],[],0.1)
      if r:
        data = self.sock.recv(size)
        print(data.decode())
      #except:
      #  pass
    self.root.after(100, self.timer)
  
  def run(self):
    self.timer()
    self.root.mainloop()


def main(argv):
  mw = MainWin()
  mw.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
