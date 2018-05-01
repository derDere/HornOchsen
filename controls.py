import socket
from tkinter import *

FONT = ("Arial",25)


class Card():
  def __init__(self, parent, card, value):
    self.x = 0
    self.y = 0
    self.card = card
    self.value = value
    self.bgImg = PhotoImage(file="gfx/card_bg.png")
    self.img = PhotoImage(file="gfx/card_%i.png" % value)
    self.btn = Button(parent, image=self.img, text=str(card)+"\n\n", width=100, height=150, command=self.click, compound=CENTER, borderwidth=0, font=FONT)
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


class StartFrame():
  def __init__(self, parent, socketAction):
    self.socketAction = socketAction
    #Main Frame
    self.frame = Frame(parent, width=200, height=110, bg="silver")
    #Play Button
    self.pBtn = Button(self.frame, text="Play", font=FONT, command=self._PlayBtnClick)
    self.pBtn.place(x=20, y=20, width=160, height=50)
    #IP Textbox
    self.ip = StringVar()
    self.ip.set("127.0.0.1")
    self.ipTxb = Entry(self.frame, textvariable=self.ip)
    self.ipTxb.place(x=20, y=70, width=160, height=20)
  
  def place(self):
    self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=200, height=110)
  
  def _PlayBtnClick(self):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (self.ip.get(), 8080)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    self.frame.place_forget()
    self.socketAction(sock)















