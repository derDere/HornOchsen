import socket
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
    print("Creating stacks.")
    for s in self.stacks.keys():
      self.stacks[s].append(self.cards.pop())
      self.stacks[s].append(self.cards.pop())
    self.hasStarted = False


class Player():
  def __init__(self, sock, addr):
    self.sock = sock
    self.hand = []
    self.choosen = -1


def CardPosMsg(card, x, y, f):
  cf = "1"
  if not f: cf = "0"
  s = "c%03i%03i%03i%c" % (card, x, y, cf)
  return s


class ThreadedServer(object):
  def __init__(self, host, port):
    self.running = True
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((self.host, self.port))

  def listen(self):
    print("Listening to port:%i" % self.port)
    self.sock.listen(5)
    while self.running:
      client, address = self.sock.accept()
      client.settimeout(60)
      threading.Thread(target = self.listenToClient,args = (client,address)).start()

  def stop(self):
    self.running = False
    socket.socket(socket.AF_INET, 
                  socket.SOCK_STREAM).connect( (self.host, self.port))
    self.sock.close()

  def listenToClient(self, client, address):
    global game
    if game == None:
      print("No game!")
      client.close()
      return
    print("New Player %s joined." % str(address))
    player = Player(client, address)
    game.players.append(player)
    while self.running:
      time.sleep(0.2)
      if game.hasStarted:
        print("I'm in: %s" & str(address))
        for s in self.game.stacks.keys():
          for i in range(len(g.stacks[s])):
            x = (s * 130) + 265
            y = 130 + (i * 10)
            msg = CardPosMsg(g.stacks[s][i].card,x,y,True).encode()
            client.send(msg)
      else:
        client.send("w0000000000".encode())
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

game = None
server = None
def serverWork(port):
  global server
  server = ThreadedServer('',port)
  server.listen()  


def main(argv):
  global server, game
  game = Game()
  port_num = 8080
  threading.Thread(target = serverWork, args = (port_num,)).start()
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
