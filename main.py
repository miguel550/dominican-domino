import collections
import random


class DominicanDomino():

    def __init__(self):
        self.table = collections.deque()
        self.matching_number_left = None
        self.matching_number_right = None
        pieces = list({
            (i, j)
            for i in range(7)
            for j in range(i + 1)
        })
        assert len(pieces) == 28, len(pieces)

        random_pieces = random.sample(pieces, k=len(pieces))
        chunk_size = 7
        self.hands = [random_pieces[i:i+chunk_size] for i in range(0, len(random_pieces), chunk_size)]

        self.current_player = None

    def start(self):
        if len(self.table) != 0:
            return
        # find who has 6/6 and do the play
        for pos, player in enumerate(self.hands):
            if (6,6) not in player:
                continue
            self.current_player = pos
            self._play((6,6), 6)
            break

    def _play(self, piece, matching_number):
        if matching_number not in piece:
            raise Exception('Wrong matching number')
        if piece in self.table:
            raise Exception('Already played')
        if len(self.table) == 0:
            self.table.append(piece)
            self.matching_number_left, self.matching_number_right = piece
        # find end where it should be
        elif matching_number == self.matching_number_left:
            self.table.appendleft(piece)
            # double
            if piece[0] != piece[1]:
                self.matching_number_left = next(number for number in piece if number != matching_number)
        elif matching_number == self.matching_number_right:
            self.table.append(piece)
            if piece[0] != piece[1]:
                self.matching_number_right = next(number for number in piece if number != matching_number)
        else:
            raise Exception(f'Bad move {piece} does not match in any end')
        before = len(self.current_hand)
        self.hands[self.current_player].remove(piece)
        assert before > len(self.current_hand), f'{before=} {len(self.current_hand)=}'
        self._set_next_player()

    def _set_next_player(self):
        self.current_player += 1
        self.current_player %= 4

    def get_table(self):
        return tuple(self.table)
    
    @property
    def allowed_tiles_of_current_player(self):
        return [
            tile
            for tile in self.hands[self.current_player]
            if self.matching_number_left in tile or self.matching_number_right in tile
        ]

    @property
    def current_hand(self):
        return tuple(self.hands[self.current_player])

    def play_tile(self, tile, matching_number=None):
        if matching_number is not None:
            self._play(tile, matching_number=matching_number)
            return 'OK'
        elif self.matching_number_left in tile and self.matching_number_right in tile and self.matching_number_right != self.matching_number_left:
            return 'BOTH_SIDES'
        elif self.matching_number_left in tile:
            self._play(tile, matching_number=self.matching_number_left)
            return 'OK'
        elif self.matching_number_right in tile:
            self._play(tile, matching_number=self.matching_number_right)
            return 'OK'
        else:
            return 'INVALID'


domino = DominicanDomino()
domino.start()
while True:
    print('Table: ')
    print(domino.get_table())
    print()
    print(f'Player {domino.current_player} hand')
    if not domino.allowed_tiles_of_current_player:
        print('User doesnt have tiles! passing to next player')
        domino._set_next_player()
        continue
    current_hand = domino.current_hand
    print(current_hand)
    option = int(input('Choose: '))
    tile = current_hand[option]
    response = domino.play_tile(tile)
    if response == 'BOTH_SIDES':
        matching_number = int(input(f'Choose side {tile}: '))
        domino.play_tile(tile, matching_number=matching_number)
    elif response == 'INVALID':
        print(f'Tile {tile} is not valid please choose a valid tile')
        continue
