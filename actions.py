import random

gainActs = {
  0: 'lorem', 
  1: 'ipsum',
  2: 'dolor'
}

loseActs = {
  0: 'sit',
  1: 'amet', 
  2: 'consectetur'
}

def randGain():
  choice = random.randint(0, len(gainActs))
  return gainActs[choice]

def randLose():
  choice = random.randint(0, len(loseActs))
  return loseActs[choice]