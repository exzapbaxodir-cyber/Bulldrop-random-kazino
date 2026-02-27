import random

def generate_ladder():
    row1 = ["⬜"] * 20
    row2 = ["⬜"] * 19

    bombs1 = random.sample(range(10), 3)
    bombs2 = random.sample(range(10), 3)

    for b in bombs1:
        row1[b] = "💣"

    for b in bombs2:
        row2[b] = "💣"

    return row1, row2
