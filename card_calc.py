BUF_SIZE = 1024

def cardValue(card):
  sum = 1
  if (card % 5) == 0:
    sum += 1
  if (card % 10) == 0:
    sum += 1
  if len(list(str(card))) == 2:
    A = list(str(card))[0]
    B = list(str(card))[1]
    if A == B:
      sum = 5
  if card == 55:
    sum = 7
  return sum
