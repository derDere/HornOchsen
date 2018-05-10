import os
import socket
import select
import time
import locale
import server
import threading
import traceback
from card_calc import *
from tkinter import *

SMALL_FONT = ("Arial", 10)
MEDIUM_FONT = ("Arial", 17)
FONT = ("Arial",25)
card_bg = None
card_img = None
crown_img = None


class Language():
  def __init__(self):
    self.current = locale.getdefaultlocale()[0][:2]
    #load labels
  
  def lab(self,key):
    pass


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
      jump = self.x_go - self.x
      if jump > 2: jump = 2
      self.x += jump
      change = True
    if self.x > self.x_go:
      jump = self.x - self.x_go
      if jump > 2: jump = 2
      self.x -= jump
      change = True
    if self.y < self.y_go:
      jump = self.y_go - self.y
      if jump > (2*self.y_step): jump = (2*self.y_step)
      self.y += jump
      change = True
    if self.y > self.y_go:
      jump = self.y - self.y_go
      if jump > (2*self.y_step): jump = (2*self.y_step)
      self.y -= jump
      change = True
    if change:
      #print("moved")
      self.btn.place(x=round(self.x), y=round(self.y), width=100, height=150)
  
  def hide(self):
    self.hidden = True
    if self.y < 0:
      self.y = -150
    self.btn.place_forget()
  
  def toTop(self):
    self.btn.tkraise()
    #self.btn.place(x=self.x, y=self.y, width=100, height=150)


class PlayFrame():
  def __init__(self, parent, sock, finishAction):
    global crown_img
    crown_img = PhotoImage(file="gfx/crown.png")
    self.sock = sock
    self.finishAction = finishAction
    #height calculation: 80 + 10 + 40 + (4 * 55) + 150 + 30 + 150 = 710
    self.frame = Frame(parent, width=1000, height=710, bg="#007F00")
    self.infoLab = Label(self.frame, text="waiting ...", font=FONT, bg="#007F00", fg="white")
    self.infoLab.place(x=265, y=90, height=40, width=490)
    self.pointLab = Label(self.frame, text="Points: 0", font=SMALL_FONT, bg="#007F00", fg="white")
    self.pointLab.place(x=880, y=80, height=20, width=100)
    self.playerLab = Label(self.frame, text="...", font=MEDIUM_FONT, bg="#007F00", fg="white")
    self.playerLab.place(x=20, y=80, height=30, width=100)
    self.scoreTable = Frame(self.frame, bg="#005F00")
    self.scoreTable.place(x=0,y=115,height=220,width=140)
    Label(self.scoreTable, text="Player", font=SMALL_FONT, fg="white", bg="#005F00").place(x=0,y=0,height=20,width=70)
    Label(self.scoreTable, text="Points", font=SMALL_FONT, fg="white", bg="#005F00").place(x=70,y=0,height=20,width=70)
    self.crown = Label(self.frame, image=crown_img)
    self.crown.place(x=-20,y=-20,width=20,height=20)
    self.leaveBtn = Button(self.frame, text="leave game", font=FONT, command=self.finishAction)
    self.cards = {}
    self.lastMsg = None
    self.msgs = []
    self.running = True
    self.scores = {}
    self.myPlayNumber = -1
    self.winner = -10
    threading.Thread(target = self.read).start()    
  
  def addScoreLab(self, player):
    backColor = "#005F00"
    if player == self.myPlayNumber: backColor = "#003F00"
    lab1 = Label(self.scoreTable, text="P%2i" % player, fg="white", bg=backColor, font=SMALL_FONT)
    lab2 = Label(self.scoreTable, text="0", fg="white", bg=backColor, font=SMALL_FONT)
    self.scores[player] = lab2
    lab1.place(x=0,y=20*player,width=70,height=20)
    lab2.place(x=70,y=20*player,width=70,height=20)
  
  def read(self):
    try:
      while self.running:
        r = True
        while r:
          r,w,e = select.select([self.sock],[],[self.sock],0.1)
          if r:
            data = self.sock.recv(BUFF_SIZE)
            msg = data.decode()
            if self.lastMsg != msg:
              self.msgs.append(msg)
              self.lastMsg = msg
        time.sleep(0.001)
    except:
      print(traceback.print_exc())
      self.msgs = ["closed"]
  
  def animate(self):
    for c in self.cards:
      self.cards[c].animate()
        
  def update(self):
    #try:
    #print("waiting")
    cardMoved = False
    while (len(self.msgs) > 0) and (self.winner == -10):
      msg = self.msgs.pop(0)
      self.lastMsg = msg
      #print(msg)
      if msg[0:4] == "full":
        self.winner == -20
        self.infoLab.configure(text="Sorry the game is full!")
        self.leaveBtn.place(relx=0.5,rely=0.5,width=200,height=50,anchor=CENTER)
        return
      elif msg == "":
        self.winner == -30
        self.infoLab.configure(text="Sorry the game has closed!")
        self.leaveBtn.place(relx=0.5,rely=0.5,width=200,height=50,anchor=CENTER)
        return
      elif msg[0] == 'c':
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
          self.leaveBtn.tkraise()
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
          self.myPlayNumber = myP
        elif msg[1] == "f":
          fP = int(msg[2:4])
          self.crown.place(x=140,y=95+(20*fP),width=20,height=20)
        elif msg[1] == "F":
          fP = int(msg[2:4])
          self.infoLab.configure(text="Player %i winns the Game!" % fP)
          self.winner = fP
          self.leaveBtn.place(relx=0.5,rely=0.5,width=200,height=50,anchor=CENTER)
        elif msg[1] == "p":
          csP = int(msg[2:4])
          self.infoLab.configure(text="Player %i is stacking ..." % csP)
        elif msg[1] == "P":
          points = int(msg[2:5])
          self.pointLab.configure(text="Points: %i" % points)
        elif msg[1] == "c":
          self.infoLab.configure(text="Pick your card.")
        elif msg[1] == "s":
          self.infoLab.configure(text="Choose your stack.")
        elif msg[1] == "S":
          sP = int(msg[2:4])
          score = int(msg[4:7])
          if not sP in self.scores:
            self.addScoreLab(sP)
          self.scores[sP].configure(text="%i" % score)
        elif msg[1] == "0":
          self.infoLab.configure(text="")
  
  def place(self):
    self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=1000, height=710)
  
  def cardClicked(self, sender):
    print("Clicked on %i" % sender.card)
    self.sock.send(("c%03i0000000" % sender.card).encode())


class DiffiSpinbox(Spinbox):
  def __init__(self, *args, **keywords):
    super().__init__(*args, **keywords)
    self.lastSelection = "Normal"
    self.difficulty = StringVar()
    self.difficulty.trace("w", self.validate)
    self.difficulties = {"Easy":2, "Normal":5, "Hard":10}
    super().configure(values=["Easy","Normal","Hard"], textvariable=self.difficulty)
    self.difficulty.set("Normal")
  
  def validate(self, *args):
    val = self.difficulty.get()
    if not val in self.difficulties:
      self.difficulty.set(self.lastSelection)
      return
    self.lastSelection = val
  
  def getPlayerCount(self):
    diffi = self.difficulty.get()
    if diffi in self.difficulties:
      return self.difficulties[diffi]
    return 5


class PlayerCountSpinnbox(Spinbox):
  def __init__(self, *args, **keywords):
    super().__init__(*args, **keywords)
    self.lastInput = "5 Players"
    self.playerCount = StringVar()
    self.playerCount.trace("w", self.validate)
    self.playerCountValues = {}
    self.values = []
    for N in range(2,10+1):
      self.playerCountValues["%i Players" % N] = N
      self.values.append("%i Players" % N)
    super().configure(values=self.values, textvariable=self.playerCount)
    self.playerCount.set("5 Players")
  
  def validate(self, *args):
    val = self.playerCount.get()
    if not val in self.playerCountValues:
      self.playerCount.set(self.lastSelection)
      return
    self.lastSelection = val
  
  def getPlayerCount(self):
    pC = self.playerCount.get()
    if pC in self.playerCountValues:
      return self.playerCountValues[pC]
    return 10


class StartFrame():
  def __init__(self, parent, socketAction):
    self.socketAction = socketAction
    #Main Frame
    self.frame = Frame(parent, width=200, height=270, bg="#007F00")
    #Play Button
    self.pBtn = Button(self.frame, text="Play", font=FONT, command=self.PlayBtnClick)
    self.pBtn.place(x=20, y=20, width=160, height=50)
    #Difficulty DropDown
    self.diffiSpin = DiffiSpinbox(self.frame)
    self.diffiSpin.place(x=20, y=70, width=160, height=20)
    #Host Button
    self.hBtn = Button(self.frame, text="Host", font=FONT, command=self.HostBtnClick)
    self.hBtn.place(x=20, y=100, width=160, height=50)
    #PlayerCount Textbox
    self.pcSpin = PlayerCountSpinnbox(self.frame)
    self.pcSpin.place(x=20, y=150, width=160, height=20)
    #Join Button
    self.jBtn = Button(self.frame, text="Join", font=FONT, command=self.JoinBtnClick)
    self.jBtn.place(x=20, y=180, width=160, height=50)
    #IP Textbox
    self.ip = StringVar()
    self.ip.set("127.0.0.1")
    self.ipTxb = Entry(self.frame, textvariable=self.ip)
    self.ipTxb.place(x=20, y=230, width=160, height=20)
  
  def place(self):
    self.frame.place(relx=0.5, rely=0.5, anchor=CENTER, width=200, height=270)
  
  def PlayBtnClick(self):
    print("Starting Server ...")
    PlayerCount = self.pcSpin.getPlayerCount()
    self.StartAsync(PlayerCount, 8080, (PlayerCount - 1))
    time.sleep(0.5)
    self.JoinAndStart('127.0.0.1', 8080)
  
  def HostBtnClick(self):
    print("Starting Server ...")
    PlayerCount = self.pcSpin.getPlayerCount()
    self.StartAsync(PlayerCount, 8080, 0)
    time.sleep(0.5)
    self.JoinAndStart('127.0.0.1', 8080)
  
  def JoinBtnClick(self):
    port = 8080
    host = self.ip.get()
    self.JoinAndStart(host, port)
  
  def StartAsync(self, playerCount, port, botCount):
    threading.Thread(target = self.__AsyncCommand, args=(playerCount, port, botCount)).start()
  
  def __AsyncCommand(self, playerCount, port, botCount):
    server.main([playerCount, port, botCount])
  
  def JoinAndStart(self, Host, Port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (Host, Port)
    print('connecting to %s port %s' % server_address)
    sock.connect(server_address)
    self.frame.place_forget()
    self.socketAction(sock)















