import random

gainActs = {
  0: 'sending dank memes.', 
  1: 'monke.',
  2: 'being anti-Fortnite.'
}

loseActs = {
  0: 'not being monke.',
  1: 'being a discord mod.', 
  2: 'not sending feet pics.'
}

def randGain():
  choice = random.randint(0, len(gainActs))
  return gainActs[choice]

def randLose():
  choice = random.randint(0, len(loseActs))
  return loseActs[choice]