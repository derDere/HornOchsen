import socket
import threading
import time
from card_calc import *


class ThreadedServer(object):
  def __init__(self, host, port):
    self.host = host
    self.port = port
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.sock.bind((self.host, self.port))

  def listen(self):
    print("Listening to port:%i" % self.port)
    self.sock.listen(5)
    while True:
      client, address = self.sock.accept()
      client.settimeout(60)
      threading.Thread(target = self.listenToClient,args = (client,address)).start()

  def listenToClient(self, client, address):
    print("New client %s" % str(address))
    size = 1024
    while True:
      #try:
      print("sending")
      client.send("c0050100101".encode())
      time.sleep(2)
      client.send("c0051100100".encode())
      time.sleep(2)
      client.send("c0051101101".encode())
      time.sleep(2)
      client.send("c0050101100".encode())
      print("sended")
      time.sleep(2)
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


def main(argv):
  port_num = 8080
  server = ThreadedServer('',port_num)
  server.listen()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
