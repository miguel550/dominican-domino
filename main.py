import collections
import random


table = collections.deque()
matching_number_left = None
matching_number_right = None
pieces = [
    (i, j)
    for i in range(7)
    for j in range(i + 1)
]
assert len(pieces) == 28, len(pieces)

random_pieces = random.sample(pieces, k=len(pieces))
chunk_size = 7
players = [random_pieces[i:i+chunk_size] for i in range(0, len(random_pieces), chunk_size)]
print(players)

current_player = None

def play(piece, matching_number):
    if matching_number not in piece:
        raise Exception('Wrong matching number')
    if piece in table:
        raise Exception('Already played')
    if len(table) == 0:
        table.append(piece)
        matching_number_left, matching_number_right = piece
        return
    # find end where it should be
    if matching_number == matching_number_left:
        table.appendleft(piece)
        matching_number_left = next(number for number in piece if number != matching_number)
    elif matching_number == matching_number_right:
        table.append(piece)
        matching_number_right = next(number for number in piece if number != matching_number)
    else:
        raise Exception(f'Bad move ${piece} does not match in any end')

def play_left(piece):
    if len(table) == 0:
        play(piece, piece[0])
        print(f'Player who played was {current_player} a {piece}')
        set_next_player()
        return
    if matching_number_left not in piece:
        raise Exception('Cannot do play')
    play(piece, matching_number_left)
    print(f'Player who played was {current_player} a {piece}')
    set_next_player()
    
def play_right(piece):
    if len(table) == 0:
        play(piece, 0)
        print(f'Player who played was {current_player} a {piece}')
        set_next_player()
        return
    if matching_number_right not in piece:
        raise Exception('Cannot do play')
    play(piece, matching_number_right)
    print(f'Player who played was {current_player} a {piece}')
    set_next_player()

def set_next_player():
    global current_player
    current_player += 1
    current_player %= 4

if len(table) == 0:
    # find who has 6/6 and do the play
    for pos, player in enumerate(players):
        if (6,6) not in player:
            continue
        current_player = pos
        play_left((6,6))
        break
