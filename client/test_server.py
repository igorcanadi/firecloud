import SocketServer
import time

packet_num = 0
replies = ['OK [384] []', 'OK [385] [a]']

class MyUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        print "{} wrote:".format(self.client_address[0])
        print data
        global packet_num
        global replies
        if packet_num % 2 == 1:
            time.sleep(.003)

        socket.sendto(replies[packet_num % 2], self.client_address)
        packet_num += 1

if __name__ == "__main__":
    HOST, PORT = "localhost", 9999
    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()
