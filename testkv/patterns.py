
from random import choice
from tools import make_str

from constants import MAX_VALUE_SIZE, MAX_KEY_SIZE 


STRESS_ITERS = 50
SUPER_STRESS_ITERS = 200

STRESS_ROUNDS = 10


def peek_all(kv):
  for ke in kv:
    kv[ke]

def poke_all(kv):
  for ke in kv:
    kv[ke] = kv[ke] + '_'

def poke_one(kv):
  ke = choice(kv)
  kv[ke] = make_str(30)

def peek_one(kv):
  ke = choice(kv)
  kv[ke]

def big_poke_one(kv)
  ke = choice(kv)
  kv[ke] = make_str(MAX_KEY_SIZE)

def big_poke_all(kv):
  for ke in kv:
    kv[ke] = kmake_str(MAX_KEY_SIZE)


def stress_key(kv, ke):
  for x in STRESS_ITERS:
    # set the key to be a random string of length x
    kv[ke] = make_str(x)

def stress_keys(kv, kes):
  """ pokes each key several times """
  for c in xrange(STRESS_ROUNDS)
    for ke in kes:
      poke_one(ke)



  


