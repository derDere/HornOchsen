from tkinter import *
from controls import *
import time
import socket
import sys
import select


class MainWin:
  def __init__(self):
    self.sock = None
    self.playFrame = None
    self.root = Tk()
    self.root.title("Horn Ochsen")
    self.root.geometry("1000x500")
    self.frame = Frame(self.root, bg='black')
    #self.tbtn = Card(self.frame, 4, 1)
    #self.tbtn.place(10,10,100,150)
    self.startFrame = StartFrame(self.frame, self.socketAction)
    self.startFrame.place()
    self.frame.pack(fill=BOTH, expand=1)
  
  def socketAction(self, sock):
    self.sock = sock
    self.playFrame = PlayFrame(self.frame, self.sock)
    self.playFrame.place()
    print("Socket opened")
  
  def timer(self):
    if self.playFrame != None:
      self.playFrame.update()
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
