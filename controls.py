import socket
import select
from card_calc import *
from tkinter import *

FONT = ("Arial",25)
BUF_SIZE = 1024
card_bg = None
card_img = None


class Card():
  def __init__(self, parent, card):
    global card_img, card_bg
    if card_img == None:
      card_bg = PhotoImage(file="gfx/card_bg.png")
      card_img = {
        1: PhotoImage(file="gfx/card_1.png"),
        2: PhotoImage(file="gfx/card_2.png"),
        3: PhotoImage(file="gfx/card_3.png"),
        5: PhotoImage(file="gfx/card_5.png"),
        7: PhotoImage(file="gfx/card_7.png")
      }
    self.x = 0
    self.y = 0
    self.card = card
    self.value = cardValue(card)
    self.img = card_img[self.value]
    self.btn = Button(parent, image=card_bg, text=str(self.card)+"\n\n", width=100, height=150, command=self.click, compound=CENTER, borderwidth=0, font=FONT, highlightbackground="white", highlightcolor="white")          
    self.clickHandler = []
  
  def flippDown(self):
    global card_bg
    print("Flipp Down")
    self.btn.configure(image=card_bg, text="")
  
  def flippUp(self):
    print("Flipp Up")
    self.btn.configure(image=self.img, text=str(self.card)+"\n\n")
  
  def click(self):
    for handler in self.clickHandler:
      handler(self)
  
  def addHandler(self, handler):
    self.clickHandler.append(handler)
  
  def place(self, x, y, f = True):
    if f == True:
      self.flippUp()
    else:
      self.flippDown()
    self.x = x
    self.y = y
    self.btn.place(x=x, y=y, width=100, height=150)


class PlayFrame():
  def __init__(self, parent, sock):
    self.sock = sock
    #height calculation: 80 + 20 + 30 + 40 + 150 + 30 + 150 = 500
    self.frame = Frame(parent, width=1000, height=500, bg="white")
    self.cards = {}
        
  def update(self):
    #try:
    print("waiting")
    r,w,e = select.select([self.sock],[],[],0.1)
    if r:
      data = self.sock.recv(BUF_SIZE)
      print(data.decode())
      msg = data.decode()
      if msg[0] == 'c':
        c = int(msg[1:4])
        x = int(msg[4:7])
        y = int(msg[7:10])
        f = (msg[10] == '1')
        if not c in self.cards:
          self.cards[c] = Card(self.frame, c)
        self.cards[c].place(x, y, f)
    #except:
    #  pass
  
  def place(self):
    self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=1000, height=500)


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















