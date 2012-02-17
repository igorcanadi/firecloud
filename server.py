import os
import SocketServer

def process(data):
  assert(len(data) >= 6);
  cmd = data[:4]
  print "'%s'" % cmd
  if cmd == "GET ":
    return res(get(data[5:]))
  elif cmd == "PUT ":
    return res(put(data[5:]))
  else:
    raise ValueError

d = {}

def get(data):
  try:
    return ("OK", d[data]);
  except:
    return ("EMPTY", "[]");
    
def put(data):
  idx = data.find('[', 1)
  assert (data[idx-1] == ' ')
  key = data[:idx-1]
  val = data[idx:]

  try:
    ret = ("OK", d[key]);
  except KeyError:
    ret = ("EMPTY", "[]")

  d[key] = val;

  return ret

def res(tup):
  return ' '.join(tup)


class RTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(8000).strip()
        res = process(data);
        print res
        self.request.sendall(res)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), RTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

