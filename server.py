import socket
import select
import threading
import traceback
import time
from card_calc import *
import random


class Card():
  def __init__(self, card):
    self.card = card
    self.value = cardValue(card)


class Game():
  def __init__(self):
    self.playerMax = 10
    self.botCount = 0
    self.hasStarted = False
    self.players = []
    self.cards = []
    self.stacks = {0:[],1:[],2:[],3:[]}
    self.startedWith = 0
    self.closed = False
  
  def start(self):
    if len(self.players) <= 1:
      print("You can't play alone!")
      return
    self.startedWith = len(self.players)
    print("Starting Game with %i players." % len(self.players))
    self.hasStarted = True
    threading.Thread(target = self.play).start()
  
  def GiveCards(self):
    print("Clear Table")
    for p in self.players:
      p.sock.send("rA000000000".encode())
    print("Shuffeling deck.")
    deck = []
    for card in range(0,104):
      deck.append(Card(card+1))
    self.cards = []
    while len(deck) > 0:
      index = random.randint(1000,9999) % len(deck)
      self.cards.append(deck.pop(index))
    print("Giving cards to players.")
    for p in self.players:
      for i in range(10):
        p.hand.append(self.cards.pop())
      p.isChoosing = True
    print("Creating stacks.")
    for s in self.stacks.keys():
      self.stacks[s].append(self.cards.pop())
  
  def smallestPlayer(self):
    favoritPlayer = -10
    lessestPoints = 1000
    for p in self.players:
      if p.getGamePoints() < lessestPoints:
        lessestPoints = p.getGamePoints()
        favoritPlayer = p.num
    return favoritPlayer
  
  def play(self):
    print("Game started.")
    gameRunning = True
    while gameRunning:
      self.GiveCards()
      oneRound = True
      while oneRound:
        print("Choosing Phase ...")
        choosingPhase = True
        while choosingPhase:
          if len(self.players) < self.startedWith:
            self.closed = True
            exit()
            return
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
          if len(self.players) < self.startedWith:
            self.closed = True
            exit()
            return
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
        if len(self.players[0].hand) <= 0:
          oneRound = False
      print("Round End")
      for p in self.players:
        p.rounds.append(p.getPoints())
        p.points = []
        if p.getGamePoints() >= 66:
          gameRunning = False
      if gameRunning == False:
        for p in self.players:
          for o in self.players:
            p.sock.send(("lS%02i%03i0000" % (o.num, o.getGamePoints())).encode())
      favoritPlayer = self.smallestPlayer()
      if favoritPlayer != -10:
        for p in self.players:
          p.sock.send(("lf%02i0000000" % favoritPlayer).encode())
      for s in self.stacks:
        self.stacks[s] = []
    print("Game End")
    winner = self.smallestPlayer()
    if winner != -10:
      for p in self.players:
        p.sock.send(("lF%02i0000000" % winner).encode())
    self.closed = True
    exit()


class BotSocket:
  def __init__(self, player, game):
    self.me = player
    self.game = game
    self.playerCount = 0
    self.running = True
  
  def send(self, *args):
    # No thing to do here ;)
    pass
  
  def close(self):
    self.running = False
  
  def work(self):
    # Player leave handling
    if len(self.game.players) < self.playerCount:
      print("Bot closed: missing player!")
      return False
    # Game handling
    if self.game.hasStarted:
      if self.me.isChoosing:
        if self.me.choosen == -1:
          time.sleep(random.uniform(0,3))
          pick = None
          smalestDelta = 1000
          for i in range(len(self.me.hand)):
            for s in self.game.stacks:
              cardValue = self.me.hand[i].value
              stackValue = last(self.game.stacks[s]).value
              if stackValue < cardValue:
                delta = cardValue - stackValue
                if delta < smalestDelta:
                  smalestDelta = delta
                  pick = i
          if pick == None:
            pick = random.randint(0, len(self.me.hand)-1)
          self.me.choosen = pick
          print("%s has picked hand %i" % (self.me.addr, pick))
      elif self.me.isStacking:
        if self.me.stack == -1:
          stack = None
          smallestStack = 1000
          for s in self.game.stacks:
            sum = 0
            for c in self.game.stacks[s]:
              sum += c.value
            if sum < smallestStack:
              smallestStack = sum
              stack = s
          if stack == None:
            stack = random.randint(0,3)
          self.me.stack = stack
          print("%s has picked stack %i" % (self.me.addr, stack))
    time.sleep(1)
    # running handling
    if self.running and not self.game.closed:
      return True
    else:
      return False


class Player():
  def __init__(self, sock, addr, num):
    self.num = num
    self.host = False
    self.sock = sock
    self.addr = addr
    self.isBot = False
    self.hand = []
    self.points = []
    self.rounds = []
    self.choosen = -1
    self.stack = -1
    self.isChoosing = False
    self.isStacking = False
  
  def getPoints(self):
    sum = 0
    for card in self.points:
      sum += card.value
    return sum
  
  def getGamePoints(self):
    sum = 0
    for r in self.rounds:
      sum += r
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
    print("Waiting for %i players ..." % (self.game.playerMax - self.game.botCount))
    self.sock.listen(5)
    conCount = 0
    while self.running:
      if self.game.closed:
        return
      if conCount < (self.game.playerMax - self.game.botCount):
        client, address = self.sock.accept()
        if self.game.closed:
          return
        client.settimeout(60)
        threading.Thread(target = self.listenToClient, args = (client,address)).start()
      else:
        time.sleep(1)

  def stop(self):
    self.running = False
    socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect( (self.host, self.port))
    self.sock.close()

  def listenToClient(self, client, address):
    # Bot Handling
    if type(client) == BotSocket:
      while client.work():
        time.sleep(0.2)
      return
    # Player Handling
    try:
      # Check max players
      if self.game.playerMax <= len(self.game.players):
        client.send("full0000000".encode())
        client.close()
        return
      # Create Player
      print("New Player %s joined." % str(address))
      player = Player(client, address, len(self.game.players) + 1)
      self.game.players.append(player)
      msgWho = "lI%02i%i000000" % (player.num, int(player.host))
      client.send(msgWho.encode())
      print("sended: %s" % msgWho)
      # Creating bots
      if len(self.game.players) >= (self.game.playerMax - self.game.botCount):
        for i in range(self.game.botCount):
          bot = Player(None, "bot%i" % i, len(self.game.players) + 1)
          bot.sock = BotSocket(bot, self.game)
          bot.isBot = True
          self.game.players.append(bot)
          print("Add Bot%i to game." % i)
        for bot in self.game.players:
          if bot.isBot:
            bot.playerCount = len(self.game.players)
            threading.Thread(target = self.listenToClient, args = (bot.sock,bot.addr)).start()
      # Starting Game
      if len(self.game.players) >= self.game.playerMax:
        self.game.start()
      # Running Game
      while self.running:
        # Game stop handling
        if self.game.closed or (len(self.game.players) < self.game.startedWith):
          self.running = False
          client.close()
          break
        time.sleep(0.1)
        # Game Handling
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
            y = 600
            if (i == player.choosen) and (player.isChoosing or player.isStacking):
              y -= 60
            msg = CardPosMsg(player.hand[i].card,x,y,True).encode()
            client.send(msg)
          oponent_index = 0
          for p in self.game.players:
            client.send(("lS%02i%03i0000" % (p.num, p.getGamePoints())).encode())
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
                  if len(player.hand) <= 1:
                    player.choosen = 0
                  else:
                    for i in range(len(player.hand)):
                      if player.hand[i].card == card:
                        player.choosen = i
                        print("%s has choosen hand %i" % (str(address), i))
                elif player.isStacking:
                  for s in self.game.stacks.keys():
                    for sCard in self.game.stacks[s]:
                      if sCard.card == card:
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
    except:
      print("Client Error (%s):\n%s" % (str(address), sys.exc_info()[0]))
      print(traceback.print_exc())
    client.close()
    self.game.players.remove(player)
    self.game.closed = True
    self.stop()
    exit()

server = None
def serverWork(port, game):
  global server
  server = ThreadedServer('',port,game)
  server.listen()  


def argOf(argv, index, default=0, type=str):
  try:
    val = argv[index]
    result = type(val)
    return result
  except:
    return default


def main(argv):
  global server
  playerCount = argOf(argv, 0, 10, int)
  port_num = argOf(argv, 1, 8080, int)
  botCount = argOf(argv, 2, 0, int)
  if playerCount > 10:
    print("The player maximum is 10!")
    return
  game = Game()
  game.playerMax = playerCount
  game.botCount = botCount
  serverWork(port_num, game)
  #threading.Thread(target = serverWork, args = (port_num, game)).start()
  #command = None
  #while command != "exit":
  #  command = input("->").lower()
  #  if command == "exit":
  #    print("Bye Bye")
  #  if command == "start":
  #    game.start()
  #server.stop()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
