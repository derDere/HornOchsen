import socket
import select
import threading
import time
from card_calc import *
import random


class Card():
  def __init__(self, card):
    self.card = card
    self.value = cardValue(card)


class Game():
  def __init__(self):
    self.hasStarted = False
    self.players = []
    self.cards = []
    self.stacks = {0:[],1:[],2:[],3:[]}
  
  def start(self):
    if len(self.players) <= 1:
      print("You can't play alone!")
      return
    print("Starting Game with %i players." % len(self.players))
    print("Shuffeling deck.")
    deck = []
    for card in range(0,104):
      deck.append(Card(card+1))
    while len(deck) > 0:
      index = random.randint(1000,9999) % len(deck)
      self.cards.append(deck[index])
      del deck[index]
    print("Giving cards to players.")
    for p in self.players:
      for i in range(10):
        p.hand.append(self.cards.pop())
      p.isChoosing = True
    print("Creating stacks.")
    for s in self.stacks.keys():
      self.stacks[s].append(self.cards.pop())
    self.hasStarted = True
    threading.Thread(target = self.play).start()
  
  def play(self):
    print("Game started.")
    while True:
      print("Choosing Phase ...")
      choosingPhase = True
      while choosingPhase:
        choosingPhase = False
        for p in self.players:
          if p.choosen == -1:
            choosingPhase = True
        time.sleep(0.5)
      time.sleep(3) # Last time to choose
      for p in self.players:
        p.isChoosing = False
      print("Stacking Phase ...")
      pL = []
      pL += self.players
      pL = sorted(pL, key=lambda player: player.hand[player.choosen].card)
      stackingPhase = True
      while stackingPhase:
        cP = pL.pop(0) # currentPlayer
        playerCard = cP.hand[cP.choosen]
        delta = {}
        for s in self.stacks.keys():
          lastC = last(self.stacks[s])
          if lastC.card < playerCard.card:
            d = playerCard.card - lastC.card
            delta[s] = d
        stack = -1
        TakeStack = False
        if len(delta) <= 0:
          cP.isStacking = True
          while cP.stack == -1:
            time.sleep(0.5)
          stack = cP.stack
          cP.isStacking = False
          TakeStack = True
        else:
          smallestDelta = 200
          smallestStack = -1
          for s in delta.keys():
            if delta[s] < smallestDelta:
              smallestDelta = delta[s]
              smallestStack = s
          stack = smallestStack
        del cP.hand[cP.choosen]
        self.stacks[stack].append(playerCard)
        if (len(self.stacks[stack]) >= 6) or TakeStack:
          while len(self.stacks[stack]) > 1:
            cP.points.append(self.stacks[stack].pop(0))
        if len(pL) <= 0:
          stackingPhase = False
        time.sleep(0.5)
      for p in self.players:
        p.stack = -1
        p.choosen = -1
        p.isChoosing = True


class Player():
  def __init__(self, sock, addr, num):
    self.num = num
    self.sock = sock
    self.hand = []
    self.points = []
    self.choosen = -1
    self.stack = -1
    self.isChoosing = False
    self.isStacking = False
  
  def getPoints(self):
    sum = 0
    for card in self.points:
      sum += card.value
    return sum


def CardPosMsg(card, x, y, f):
  cf = "1"
  if not f: cf = "0"
  s = "c%03i%03i%03i%c" % (card, x, y, cf)
  return s


def last(l):
  i = len(l) - 1
  return l[i]


class ThreadedServer(object):
  def __init__(self, host, port, game):
    self.running = True
    self.host = host
    self.port = port
    self.game = game
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((self.host, self.port))

  def listen(self):
    print("Listening to port:%i" % self.port)
    self.sock.listen(5)
    while self.running:
      client, address = self.sock.accept()
      client.settimeout(60)
      threading.Thread(target = self.listenToClient, args = (client,address)).start()

  def stop(self):
    self.running = False
    socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect( (self.host, self.port))
    self.sock.close()

  def listenToClient(self, client, address):
    print("New Player %s joined." % str(address))
    player = Player(client, address, len(self.game.players) + 1)
    self.game.players.append(player)
    while self.running:
      time.sleep(0.2)
      if self.game.hasStarted:
        #Updating Player cards
        for s in self.game.stacks.keys():
          for i in range(len(self.game.stacks[s])):
            x = (s * 130) + 265
            y = 130 + (i * 55)
            msg = CardPosMsg(self.game.stacks[s][i].card,x,y,True).encode()
            client.send(msg)
        for i in range(len(player.hand)):
          x = (i * 100)
          y = 390 + 210
          if i == player.choosen:
            y -= 60
          msg = CardPosMsg(player.hand[i].card,x,y,True).encode()
          client.send(msg)
        oponent_index = 0
        for p in self.game.players:
          if p != player:
            if p.choosen != -1:
              x = (oponent_index * 110) + ((1000 - (((len(self.game.players) - 1) * 110) - 10)) / 2)
              y = -80
              msg = CardPosMsg(-oponent_index,x,y,False).encode()
              client.send(msg)
            else:
              client.send(("r%03i0000000" % -oponent_index).encode())
            for card in p.points:
              client.send(("r%03i0000000" % card.card).encode())
            oponent_index += 1
        for i in range(len(player.points)):
          x = 880
          y = 80 + (13 * i)
          msg = CardPosMsg(player.points[i].card,x,y,True).encode()
          client.send(msg)
        someOneStacks = False
        for p in self.game.players:
          if p != player:
            if p.isStacking:
              client.send(("lp%02i0000000" % p.num).encode())
              someOneStacks = True
        if someOneStacks == False:
          if player.isChoosing:
            client.send("lc000000000".encode()) #Send msg: Choose your card.
          elif player.isStacking:
            client.send("ls000000000".encode()) #Send msg: Choose your stack.
          else:
            client.send("l0000000000".encode()) #Send msg: (empty string)
        client.send(("lP%03i000000" % player.getPoints()).encode())
        #Reading Player Input
        r = True
        while r:
          r,w,e = select.select([client],[],[],0.1)
          if r:
            data = client.recv(BUFF_SIZE)
            msg = data.decode()
            print(msg)
            if msg[0] == "c":
              card = int(msg[1:4])
              if player.isChoosing:
                for i in range(len(player.hand)):
                  if player.hand[i].card == card:
                    player.choosen = i
                    print("%s has choosen hand %i" % (str(address), i))
              elif player.isStacking:
                for s in self.game.stacks.keys():
                  for card in self.game.stacks[s]:
                    if card.card == card:
                      player.stack = s
                      print("%s has choosen stack %i" % (str(address), s))
              else:
                print("%s no action." % str(address))
      else:
        client.send("lw000000000".encode()) #Send msg: waiting ...
      #data = client.recv(size)
      #if data:
      #  # Set the response to echo back the recieved data
      #  print("received from client %s: %s" % (str(address), data))
      #  response = data
      #  client.send(response)
      #else:
      #  raise error('Client disconnected')
      #except:
      #  print("failed")
      #  client.close()
      #  return False
    client.close()
    self.game.players.remove(player)

server = None
def serverWork(port, game):
  global server
  server = ThreadedServer('',port,game)
  server.listen()  


def main(argv):
  global server
  game = Game()
  port_num = 8080
  threading.Thread(target = serverWork, args = (port_num, game)).start()
  command = None
  while command != "exit":
    command = input("->").lower()
    if command == "exit":
      print("Bye Bye")
    if command == "start":
      game.start()
  server.stop()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
