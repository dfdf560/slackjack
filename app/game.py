from deck import Card, Deck
from exceptions import GameException

import uuid


class Move(object):

    def __init__(self, player, game):
        self._player = player
        self._game = game

    def do(self):
        self._do()
        self._game.game_loop()

    def _do(self):
        raise NotImplemented

    @property
    def player(self):
        return self._player


class HitMove(Move):

    def _do(self):
        hand = self._game.deal()
        self.player.notify("{} was dealt {}.".format(self._player.identifier, hand[0]))
        if not self._player.keep_turn():
            self._game.increment_active_player_index()


class StandMove(Move):

    def _do(self):
        self._game.increment_active_player_index()
        self._player.notify("You have decided to stand with a score of: {}".format(self._player.get_score()))


class Game(object):

    _MAX_GAMES = 10
    _GAMES = {}

    @classmethod
    def create(cls, players):
        if len(cls._GAMES) > cls._MAX_GAMES:
            raise GameException("too many active games.")

        if len(players) < 1:
            raise GameException("must have at least 1 player.")

        return cls(str(uuid.uuid4().hex), players)

    @classmethod
    def move(cls, game_id, player, move):
        if game_id not in cls._GAMES:
            raise GameException("no active game {}".format(game_id))

        game = cls._GAMES.get(game_id)
        move(player, game)
        move.do()

    def __init__(self, game_id, players):
        self._game_id = game_id
        self._players = players
        self._GAMES[self._game_id] = 1
        self._active_player_index = 0
        self._house = House(self._game_id, self)
        self._deck = Deck()

        self.init_house_hand()
        self.init_players_hand()
        self.game_loop()

    def init_house_hand(self):
        house_starting_hand = self.deal()
        self.notify("House dealt {}.".format(house_starting_hand[0]))
        self._house.deal_cards(house_starting_hand)

    def init_players_hand(self):
        for player in self._players:
            player_starting_hand = self.deal(2)
            player.notify("You were dealt {} and {}.".format(player_starting_hand[0], player_starting_hand[1]))
            player.deal_cards(player_starting_hand)

    def game_loop(self):
        if self._active_player_index >= len(self._players):
            while self._house.get_score() < 17:
                HitMove(self._house, self).do()
                self.tally()
        else:
            player = self._players[self._active_player_index]
            player.notify("It's your turn!")

    def deal(self, amount=1):
        return [self._deck.deal() for x in range(amount)]

    def increment_active_player_index(self):
        self._active_player_index += 1

    def tally(self):
        for player in self._players:
            score = player.get_score()
            winnings = player.get_winnings(score)
            self.notify("{} got a score of {} and won {}!".format(player.identifier, score, winnings))

    def notify(self, message):
        for player in self._players:
            player.notify(message)


class Participant(object):

    @property
    def identifier(self):
        return self._identifier

    def __init__(self, identifier):
        self._identifier = identifier
        self._hand = []

    def deal_cards(self, cards):
        self._hand.append(cards)

    def get_score(self):
        score = 0
        for card in self._hand:
            score += Card.process_card(card, score)

        return score

    def notify(self, message):
        raise NotImplemented

    def keep_turn(self):
        raise NotImplemented


class House(Participant):

    def __init__(self, identifier, game):
        super(House, self).__init__(identifier)
        self._game = game

    def notify(self, message):
        self._game.notify(message)

    def keep_turn(self):
        score = self.get_score()
        if score >= 17:
            return False
        else:
            return True


class Player(Participant):

    STATES = ["WON", "LOST", "STAND"]

    def __init__(self, identifier, bet, callback=None):
        super(Player, self).__init__(identifier)
        self._bet = bet
        self._callback = callback

    def notify(self, message):
        if self._callback:
            self._callback(message)

    def keep_turn(self):
        score = self.get_score()
        if score > 21:
            self.notify("You have gone BUST with a score of {}".format(score))
            return False
        elif score == 21:
            self.notify("BLACKJACK!")
            return False
        else:
            return True

    def get_winnings(self, score, house_score):
        if score > 21:
            muliplier = Winnings.BUST
        elif score == 21:
            muliplier = Winnings.BLACKJACK
        elif score > house_score:
            muliplier = Winnings.WIN
        elif score == house_score:
            muliplier = Winnings.PUSH
        elif house_score > 21:
            muliplier = Winnings.WIN
        else:
            muliplier = Winnings.BUST

        return muliplier * self._bet


class Winnings(object):

    BUST = 0
    PUSH = 1
    WIN = 2
    BLACKJACK = 2.5
