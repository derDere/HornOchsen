import socket
import select
import time
import threading
from card_calc import *
from tkinter import *

SMALL_FONT = ("Arial", 10)
MEDIUM_FONT = ("Arial", 17)
FONT = ("Arial",25)
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
    self.x = -1000
    self.y = -1000
    self.x_go = -1000
    self.y_go = -1000
    self.y_step = 1
    self.f = False
    self.hidden = False
    self.parent = parent
    self.card = card
    self.value = cardValue(card)
    self.img = card_img[self.value]
    self.btn = Button(parent, image=card_bg, text="%s\n\n"%str(self.card), width=100, height=150, command=self.click, compound=CENTER, borderwidth=0, font=FONT, highlightbackground="#007F00", highlightcolor="#007F00", bg="white")          
    self.clickHandler = []
  
  def flippDown(self):
    global card_bg
    #print("Flipp Down")
    self.f = False
    text = ""
    if self.card > 109:
      text = "Player %i" % (self.card - 109)
    self.btn.configure(image=card_bg, text=text, font=SMALL_FONT, compound=TOP)
  
  def flippUp(self):
    #print("Flipp Up")
    self.f = True
    self.btn.configure(image=self.img, text=str(self.card)+"\n\n", font=FONT, compound=CENTER)
  
  def click(self):
    for handler in self.clickHandler:
      handler(self)
  
  def addHandler(self, handler):
    self.clickHandler.append(handler)
  
  def place(self, x, y, f = True):
    if f != self.f:
      if f == True:
        self.flippUp()
      else:
        self.flippDown()
    if (self.x_go != x) or (self.y_go != y) or (self.hidden):
      xD = x - self.x_go
      if xD < 0: xD = -xD
      if xD == 0:
        self.y_step = 1
      else:
        yD = y - self.y_go
        if yD < 0: yD = -yD
        yS = yD / xD
        self.y_step = yS
      self.x_go = x
      self.y_go = y
      self.toTop()
      if self.hidden:
        self.btn.place(x=self.x, y=self.y, width=100, height=150)
      self.hidden = False
      return True
    return False
  
  def animate(self):
    if self.hidden:
      return
    change = False
    if (self.x == -1000) and (self.x_go != -1000):
      if self.y_go == 600:
        self.x = -100
      else:
        self.x = self.x_go
      change = True
    if (self.y == -1000) and (self.y_go != -1000):
      if self.y_go == 600:
        self.y = self.y_go
      else:
        self.y = -150
      change = True
    if self.x < self.x_go:
      self.x += 2
      change = True
    if self.x > self.x_go:
      self.x -= 2
      change = True
    if self.y < self.y_go:
      self.y += 2*self.y_step
      change = True
    if self.y > self.y_go:
      self.y -= 2*self.y_step
      change = True
    if change:
      self.btn.place(x=self.x, y=self.y, width=100, height=150)
  
  def hide(self):
    self.hidden = True
    self.btn.place_forget()
  
  def toTop(self):
    self.btn.tkraise()
    #self.btn.place(x=self.x, y=self.y, width=100, height=150)


class PlayFrame():
  def __init__(self, parent, sock):
    self.sock = sock
    #height calculation: 80 + 10 + 40 + (4 * 55) + 150 + 30 + 150 = 710
    self.frame = Frame(parent, width=1000, height=710, bg="#007F00")
    self.infoLab = Label(self.frame, text="waiting ...", font=FONT, bg="#007F00", fg="white")
    self.infoLab.place(x=265, y=90, height=40, width=490)
    self.pointLab = Label(self.frame, text="Points: 0", font=SMALL_FONT, bg="#007F00", fg="white")
    self.pointLab.place(x=880, y=60, height=20, width=100)
    self.playerLab = Label(self.frame, text="...", font=MEDIUM_FONT, bg="#007F00", fg="white")
    self.playerLab.place(x=20, y=60, height=30, width=100)
    self.cards = {}
    self.lastMsg = None
    self.msgs = []
    self.running = True
    self.checks = {}
    threading.Thread(target = self.read).start()    
  
  def read(self):
    while self.running:
      r = True
      while r:
        r,w,e = select.select([self.sock],[],[],0.1)
        if r:
          data = self.sock.recv(BUFF_SIZE)
          msg = data.decode()
          if self.lastMsg != msg:
            self.msgs.append(msg)
            self.lastMsg = msg
      time.sleep(0.02)
  
  def animate(self):
    for c in self.cards:
      self.cards[c].animate()
        
  def update(self):
    #try:
    #print("waiting")
    cardMoved = False
    while len(self.msgs) > 0:
      msg = self.msgs.pop(0)
      self.lastMsg = msg
      #print(msg)
      if msg[0] == 'c':
        c = int(msg[1:4])
        x = int(msg[4:7])
        y = int(msg[7:10])
        f = (msg[10] == '1')
        if not c in self.cards:
          card = Card(self.frame, c)
          card.addHandler(self.cardClicked)
          self.cards[c] = card
        if self.cards[c].place(x, y, f):
          cardMoved = True
      elif msg[0] == "r":
        if msg[1] == "A":
          for c in self.cards:
            self.cards[c].hide()
        else:
          c = int(msg[1:4])
          if c in self.cards:
            self.cards[c].hide()
      elif msg[0] == "l":
        if msg[1] == "w":
          self.infoLab.configure(text="waiting ...")
        elif msg[1] == "I":
          myP = int(msg[2:4])
          host = bool(msg[4] == "1")
          hostStr = ""
          if host: hostStr = " (host)"
          self.playerLab.configure(text="Player %i%s" % (myP, hostStr))
        elif msg[1] == "p":
          csP = int(msg[2:4])
          self.infoLab.configure(text="Player %i is stacking ..." % csP)
        elif msg[1] == "P":
          points = int(msg[2:5])
          self.pointLab.configure(text="Points: %i" % points)
        elif msg[1] == "c":
          self.infoLab.configure(text="Choose your card.")
        elif msg[1] == "s":
          self.infoLab.configure(text="Choose your stack.")
        elif msg[1] == "0":
          self.infoLab.configure(text="")
    #if cardMoved:
    #  #print("Sorting Cards")
    #  cLs = {}
    #  for c in self.cards:
    #    x = self.cards[c].x_go
    #    if not x in cLs:
    #      cLs[x] = []
    #    cLs[x].append(c)
    #  for x in cLs:
    #    if not x in self.checks:
    #      self.checks[x] = str(cLs[x])
    #    cLs[x] = sorted(cLs[x], key=lambda k: self.cards[k].y_go)
    #  for x in cLs:
    #    if str(cLs[x]) != self.checks[x]:
    #      print("%s != %s" % (str(cLs[x]), self.checks[x]))
    #      self.checks[x] = str(cLs[x])
    #      for k in cLs[x]:
    #        self.cards[k].toTop()
    #except:
    #  pass
  
  def place(self):
    self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=1000, height=710)
  
  def cardClicked(self, sender):
    print("Clicked on %i" % sender.card)
    self.sock.send(("c%03i0000000" % sender.card).encode())

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















