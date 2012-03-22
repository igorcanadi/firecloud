

from conf import server_list
from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from acthread import ActThread
from transcribe import build_plan
from cout import ClientThread
from time import time

from analysis import stat_trace


def create_harness():
  return Harness(server_list)


class Harness(object):
  def __init__(self, servtups):
    self.servers = []
    self.clock = Clock()
    self.xcript = Transcript(self.clock)
    self.clients = []
    
    for host, port in servtups:
      self.servers.append(Server(self.xcript, host, port))

    self.network = Network(self.servers, self.xcript)

  def client_by_mask(self, mask):
    srvs = []
    for i, srv in enumerate(self.servers):
      if mask & (2 ** i) != 0:
        srvs.append(srv)
    return self.make_client(srvs)
  
  def clients_by_masks(self, masks):
    return map(self.client_by_mask, masks)


  def make_client(self, servs):
    """ Returns a client that only talks to servs 
    Assumes servs are a sub-set of self.servers
    """
    cli = Client(self.clock, servs)
    self.clients.append(cli)
    return cli

  def fail(self, serv):
    for cli in self.clients:
      cli.fail(serv)
    serv.fail()

  def recover(self, serv):
    serv.recover()
    for cli in self.clients:
      cli.recover(serv)

  def execute(self, clkrate):
    ignore, plan, ignore = build_plan(self.network, clkrate)
    thrds = []
    for cli in self.clients:
      cltrd, ignore, ignore = build_plan(cli, clkrate)
      thrds.append(cltrd)

    act = ActThread(plan)

    # sync offset for start, in msec
    start = int(time() * 1000) + 1000
    act.abstime = start
    for t in thrds:
      t.abstime = start
    
    act.start()
    for t in thrds:
      t.start()

    act.join()
    for cli, t in zip(self.clients, thrds):
      t.join()
      cli.ctrace = t.ctrace

  def print_stats(self):
    for cli in self.clients:
      print 'CLIENT: {0}'.format(' '.join(map(str, cli.nodes)))
      req, err, ti, rate = stat_trace(cli.ctrace)
      print '  Errors: {0} / {1}'.format(err, req)
      print '  {0:7.2f} ms/req'.format(rate)
      print '  {0:7.2f} sec spent waiting on servers'.format(ti)

    


    
