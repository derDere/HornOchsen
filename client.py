from tkinter import *
from controls import *
import time
import socket
import sys
import select


class MainWin:
  def __init__(self):
    self.tick = 0
    self.sock = None
    self.playFrame = None
    self.root = Tk()
    self.root.title("Horn Ochsen")
    self.root.geometry("1000x710")
    self.frame = Frame(self.root, bg='black')
    #self.tbtn = Card(self.frame, 4, 1)
    #self.tbtn.place(10,10,100,150)
    self.startFrame = StartFrame(self.frame, self.socketAction)
    self.startFrame.place()
    self.frame.pack(fill=BOTH, expand=1)
  
  def socketAction(self, sock):
    self.sock = sock
    self.playFrame = PlayFrame(self.frame, self.sock, self.returnToMainScreen)
    self.playFrame.place()
    print("Socket opened")
  
  def returnToMainScreen(self):
    self.playFrame.frame.place_forget()
    self.sock.close()
    self.sock = None
    self.playFrame = None
    self.startFrame.place()
  
  def timer(self):
    if self.playFrame != None:
      if (self.tick % 10) == 0:
        self.playFrame.update()
      self.playFrame.animate()
    self.tick += 1
    self.root.after(1, self.timer)
  
  def run(self):
    self.timer()
    self.root.mainloop()
    if self.playFrame != None:
      self.playFrame.running = False


def main(argv):
  mw = MainWin()
  mw.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
