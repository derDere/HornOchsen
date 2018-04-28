from tkinter import *
import socket
import sys


class MainWin:
  def __init__(self):
    self.win = Tk()
  
  def run(self):
    self.win.mainloop()


def main(argv):
  # Create a TCP/IP socket
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # Connect the socket to the port where the server is listening
  server_address = ('localhost', 8080)
  print('connecting to %s port %s' % server_address)
  sock.connect(server_address)

  #com = None
  #while com != 'exit':
  #  com = input("com:")
  #  if com != 'exit':
  #    sock.sendall(com.encode())
  
  mw = MainWin()
  mw.run()


if __name__=="__main__":
  import sys
  if len(sys.argv) > 1:
    main(sys.argv[1:])
  else:
    main([])
