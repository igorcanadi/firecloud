#!/usr/bin/env python

"""
Command and control for the servers
"""


server_cfg = 'servers.cfg'
proxies_cfg = 'proxy.cfg'


def _remote_exec(gate, cmd):
  retval = subprocess.call(command, shell=True)
  if retval != 0:
      return retval
  system('ssh -i keys/id_rsa -p {0[1]} user739@{0[0]} \"{1}\" &'.format(gate, srv))


def remote_exec(serv, cmd):
  remote_exec(proxies[serv], cmd)


def start_servers(servs):
  """ Starts the servers:
  @type servs: list of (host, port)
  """
  for srv in servs:
    # TODO fix cmd string
    remote_exec(serv, '')




parser = OptionParser()
(options, args) = parser.parse_args()


if len(args)


for serv, gate in zip(servers, gateways):
  run_ssh(gateway, 

