from tkinter import *
from controls import *
import time
import socket
import sys
import select


class RuleWin:
  def __init__(self, parent):
    self.root = Toplevel(parent)
    self.root.title("Rules")
    self.root.geometry("400x300")
    self.frame = RuleFrame(self.root)
    self.frame.pack()


class MainWin:
  def __init__(self):
    self.tick = 0
    self.sock = None
    self.playFrame = None
    self.root = Tk()
    self.root.option_add('*tearOff', FALSE)
    self.root.title("Horn Ochsen")
    self.root.geometry("1000x710")
    self.frame = Frame(self.root, bg='#008F00')
    self.menu = Menu(self.root, borderwidth=0, fg="white", bg='#006F00')
    self.menu.add_command(label=LANG.lab("rules.title"), command=self.ruleBtn_Click)
    self.menu.add_command(label=LANG.lab("leave game"), command=self.leaveGameBtn_Click)
    self.root.config(menu=self.menu)
    self.startFrame = StartFrame(self.frame, self.socketAction)
    self.startFrame.place()
    self.frame.pack(fill=BOTH, expand=1)
    self.ruleWin = None
  
  def leaveGameBtn_Click(self):
    if self.playFrame != None:
      self.returnToMainScreen()
  
  def ruleBtn_Click(self):
    if self.ruleWin == None:
      self.ruleWin = RuleWin(self.root)
      self.root.wait_window(self.ruleWin.root)
      self.ruleWin = None
  
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
    self.sock.close()


def main(argv):
  mw = MainWin()
  mw.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
