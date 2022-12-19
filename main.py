import collections
import random
import enum


class PlayStatus(enum.Enum):
    OK = enum.auto()
    INVALID = enum.auto()
    WON_GAME = enum.auto()
    WON_HAND = enum.auto()
    AMBIGUOUS_PLAY = enum.auto()

class DominicanDomino():

    def __init__(self, team_a_name: str, team_b_name: str, max_points_per_team: int=200):
        self._max_points = max_points_per_team
        self._teams_points = {
            team_a_name: [],
            team_b_name: []
        }
        self._player_team_names = {
            k: team_a_name if k % 2 == 0 else team_b_name
            for k in range(4)
        }
        self.matching_number_left = None
        self.matching_number_right = None
        self.pieces = list({
            (i, j)
            for i in range(7)
            for j in range(i + 1)
        })
        assert len(self.pieces) == 28, len(self.pieces)

        self._reset()

        self.current_player = None

    def _get_player_team_name(self, player_id):
        return self._player_team_names[player_id]
    
    @property
    def current_team_name(self):
        return self._get_player_team_name(self.current_player)

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

    def _reset(self):
        self.table = collections.deque()
        random_pieces = random.sample(self.pieces, k=len(self.pieces))
        chunk_size = 7
        self.hands = [random_pieces[i:i+chunk_size] for i in range(0, len(random_pieces), chunk_size)]
    
    def _tranque(self):
        return not bool([
            hand
            for hand in self.hands
            if self._can_hand_go(hand)
        ])
    
    def _capicua(self, tile):
        return self.matching_number_left in tile and self.matching_number_right in tile

    def _won(self):
        return not len(self.current_hand) or self._tranque()
    
    def _add_points(self, amount, limit_max=False):
        current_team_name = self._get_player_team_name(self.current_player)
        if limit_max and self._max_points > self._points_of_team(current_team_name) + amount:
            return
        for team_name in self._teams_points.keys():
            if self._get_player_team_name(self.current_player) == team_name:
                self._teams_points[team_name].append(amount)
            else:
                self._teams_points[team_name].append(0)

    def _points_of_team(self, team_name):
        return sum(self._teams_points[team_name])

    def _set_winning_rewards(self, last_tile):
        if not len(self.current_hand) and self._capicua(last_tile):
            self._add_points(30, limit_max=True)
        for hand in self.hands:
            self._add_points(sum(sum(tile) for tile in hand))

    def get_game_scores(self):
        return 
    
    def _no_other_player_can_go(self):
        return len([
            hand
            for player, hand in enumerate(self.hands)
            if player != self.current_player and self._can_hand_go(hand)
        ]) == 0

    def _second_play_passing(self):
        if len(self.current_hand) != 6:
            return
        for hand in self.hands:
            if len(hand) != 7:
                return
        next_player = self._get_next_player(self.current_player)
        team_member = self._get_next_player(self.current_player + 1)
        next_hand = self.hands[next_player]
        team_member_hand = self.hands[team_member]
        add_reward = not self._can_hand_go(next_hand) and self._can_hand_go(team_member_hand)
        return add_reward

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
        self._remove_tile(piece)

        if self._won():
            print('someone won')
            self._set_winning_rewards(piece)
            self._reset()
            return

        if self._no_other_player_can_go():
            print('tranque')
            self._add_points(30, limit_max=True)
            return

        if self._second_play_passing():
            print('sencond player passing')
            self._add_points(30 * len(set(piece)), limit_max=True)
            return
        self._set_next_player()

    def _remove_tile(self, tile):
        self.hands[self.current_player].remove(tile)

    def _get_next_player(self, current_player):
        return (current_player + 1) % 4

    def _set_next_player(self):
        self.current_player = self._get_next_player(self.current_player)

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

    def _can_hand_go(self, hand):
        return bool([
            tile
            for tile in hand
            if self.matching_number_left in tile or self.matching_number_right in tile
        ])

    def play_tile(self, tile, matching_number=None):
        response = None
        if matching_number is not None:
            self._play(tile, matching_number=matching_number)
            response = PlayStatus.OK
        elif self.matching_number_left in tile and self.matching_number_right in tile and self.matching_number_right != self.matching_number_left:
            response = PlayStatus.AMBIGUOUS_PLAY
        elif self.matching_number_left in tile:
            self._play(tile, matching_number=self.matching_number_left)
            response = PlayStatus.OK
        elif self.matching_number_right in tile:
            self._play(tile, matching_number=self.matching_number_right)
            response = PlayStatus.OK
        else:
            return PlayStatus.INVALID

        if self._max_points <= self._points_of_team(self._get_player_team_name(self.current_player)):
            # current team won
            response = PlayStatus.WON_GAME
        elif len([hand for hand in self.hands if len(hand) == 7]) == len(self.hands):
            response = PlayStatus.WON_HAND

        return response


domino = DominicanDomino('Los locos', 'los bois')
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
    if response == PlayStatus.AMBIGUOUS_PLAY:
        matching_number = int(input(f'Choose side {tile}: '))
        domino.play_tile(tile, matching_number=matching_number)
    elif response == PlayStatus.INVALID:
        print(f'Tile {tile} is not valid please choose a valid tile')
        continue
    elif response == PlayStatus.WON_HAND:
        print(f'{domino.current_team_name} won this round!')
    elif response == PlayStatus.WON_GAME:
        print(f'{domino.current_team_name} won this game!')
        print('restarting...')
