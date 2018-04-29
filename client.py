from tkinter import *
import time
import socket
import sys


class Card():
  def __init__(self, parent, card, value):
    self.x = 0
    self.y = 0
    self.card = card
    self.value = value
    self.bgImg = PhotoImage(file="gfx/card_bg.png")
    self.img = PhotoImage(file="gfx/card_%i.png" % value)
    self.btn = Button(parent, image=self.img, text=str(card)+"\n\n", width=100, height=150, command=self.click, compound=CENTER, borderwidth=0, font=("Arial",25))
    self.clickHandler = []
  
  def flippDown(self):
    self.btn.configure(image=self.bgImg)
  
  def flippUp(self):
    self.btn.configure(image=self.img)
  
  def click(self):
    for handler in self.clickHandler:
      handler(self)
  
  def addHandler(self, handler):
    self.clickHandler.append(handler)
  
  def place(self, x, y, w, h):
    self.x = x
    self.y = y
    self.btn.place(x=x, y=y, width=w, height=h)


class MainWin:
  def __init__(self):
    self.root = Tk()
    self.root.geometry("1000x400")
    self.frame = Frame(self.root, width=1000, height=1000, bg="white")
    self.tbtn = Card(self.frame, 4, 1)
    self.tbtn.place(10,10,100,150)
    self.frame.pack()
  
  def timer(self):
    self.tbtn.place(self.tbtn.x + 1, 10, 100, 150)
    self.root.after(100, self.timer)
  
  def run(self):
    self.timer()
    self.root.mainloop()


def main(argv):
  # Create a TCP/IP socket
  #  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # Connect the socket to the port where the server is listening
  #  server_address = ('localhost', 8080)
  #  print('connecting to %s port %s' % server_address)
  #  sock.connect(server_address)
  
  mw = MainWin()
  mw.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
