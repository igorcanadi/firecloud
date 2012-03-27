
from random import choice
from tools import make_str


STRESS_ITERS = 50
SUPER_STRESS_ITERS = 200

STRESS_ROUNDS = 10


def network_horse(harn):
  s = harn.servers
  harn.network[(s[0], s[2])] = False
  harn.network[(s[0], s[3])] = False
  harn.network[(s[1], s[3])] = False


def network_quad(harn):
  s = harn.servers
  harn.network[s[0]] = False
  harn.network[s[1]] = False
  harn.network[s[2]] = False

  
def network_allup(harn):
  s = harn.servers
  harn.network[s[0]] = True
  harn.network[s[1]] = True
  harn.network[s[2]] = True



