import time
import socket

class Cloud:
    (HEARTBEAT_TIMEOUT) = (0.1)

    def __init__(self, cloud, me):
        self.nodes = {}
        for node in cloud:
            self.nodes[node] = {
                'dead': False,
                'master': False,
                'last_heartbeat': time.time()
            }
        self.nodes[min(self.nodes.keys())]['master'] = True
        self.me = me

    def servers(self):
        return filter(lambda x: self.nodes[x]['dead'] == False, self.nodes)

    def whoami(self):
        return self.me

    # true if i have to kill myself
    def shoot_or_bang(self):
        # TODO add a special case for (2, 2) partitions
        # with master or no logic
        return len(self.servers()) <= (len(self.nodes) / 2)

    def this_guy_died(self, server):
        self.nodes[server]['dead'] = True
        # TODO master reelection

    def ping_them_all(self):
        now = time.time()
        have_to_ping = filter(lambda x: self.nodes[x]['dead'] == False and now - self.nodes[x]['last_heartbeat'] > Cloud.HEARTBEAT_TIMEOUT, self.nodes)
        for node in have_to_ping:
            if self.ping(node):
                self.nodes[node]['last_heartbeat'] = time.time()
            else:
                self.this_guy_died(node)

    def ping(self, server):
        print "Pinging ", server
        result = False
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((server.split(':')[0], int(server.split(':')[1])))
            sock.send('HBT')
            result = True
        except Exception as e:
            result = False
        finally:
            if sock:
                sock.close()
        print "......", result
        return result

if __name__ == "__main__":
    # run cloudtester.py with arguments 10003, 10004, 10005, 10006
    cloud = Cloud(['localhost:10003', 'localhost:10004', 'localhost:10005', 'localhost:10006'], 'localhost:10003')
    cloud.ping_them_all()
    print cloud.servers()
    # now kill one cloudtester to see what happens
    a = raw_input()
    cloud.ping_them_all()
    print cloud.servers()
