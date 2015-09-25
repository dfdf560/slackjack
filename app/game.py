from deck import Card, Deck
from exceptions import GameException
from state import StateFactory, StatefulObject, StateTransition

import uuid


class Move(object):

    HIT = "Hit"
    STAND = "Stand"

    def __init__(self, player, move):
        self._player = player
        self._move = move

    @property
    def player(self):
        return self._player

    @property
    def move(self):
        return self._move


class Game(StatefulObject):

    GAME_STATES = StateFactory.create(['INIT', 'READY', 'ANALYZING', 'DONE'])

    MAX_GAMES = 10
    DEALER_ID = "DEALER"

    _games = {}

    def __init__(self, players):
        if len(self._games) > self.MAX_GAMES:
            raise GameException("too many active games.")

        super(Game, self).__init__(
            model=self,
            states=self.GAME_STATES.ALL,
            transitions=[
                StateTransition(self.GAME_STATES.INIT, self.GAME_STATES.DONE, 'game_is_over', 'finish_game'),
                StateTransition(self.GAME_STATES.INIT, self.GAME_STATES.READY, '!game_is_over', 'start_round'),
                StateTransition(self.GAME_STATES.READY, self.GAME_STATES.ANALYZING, 'round_is_over', 'refresh'),
                StateTransition(self.GAME_STATES.ANALYZING, self.GAME_STATES.DONE, 'game_is_over', 'finish_game'),
                StateTransition(self.GAME_STATES.ANALYZING, self.GAME_STATES.READY, '!game_is_over', 'start_round'),
            ],
            default_state=self.GAME_STATES.INIT
        )

        self._game_id = str(uuid.uuid4().hex)
        self._players = players
        self._house = House(self._generate_dealer_id(self._game_id))
        self._deck = Deck()

        house_starting_hand = [self._deck.deal()]
        self.notify("House dealt {}.".format(house_starting_hand[0]))
        self._house.deal_cards(house_starting_hand)

        for player in self._players:
            player_starting_hand = [self._deck.deal(), self._deck.deal()]
            player.notify("You were dealt {} and {}.".format(player_starting_hand[0], player_starting_hand[1]))
            player.deal_cards(player_starting_hand)

        self._games[self._game_id] = 1
        self.game_loop()

    def game_loop(self):
        for player in self._players:
            move = player.get_move()



    def round_is_over(self):
        return all([not player.is_active_in_round() for player in self._players])

    def game_is_over(self):
        return self._house.hand_is_done() or all(not player.state_is_active() for player in self._players)

    def move(self, move):
        if not self.matches(self.GAME_STATES.READY):
            raise GameException("game not accepting moves.")

        if move.player not in self._players:
            raise GameException("invalid player: ".format(move.player.identifier))

        if not move.player.state_is_active():
            raise GameException("player not allowed to make move.")

        move.player.make_move(move.move, self._deck)
        self.refresh()

    def start_round(self):
        self.notify("Starting round...")
        for player in self._players:
            if not player.hand_is_done():
                player.start_round()

        if self._house.can_make_move():
            dealer_card = deck.deal()
            self.notify("Dealer ")

    def finish_game(self):
        self.notify("Game over!")
        for player in self._players:
            self.print_winnings(player)

    def notify(self, message):
        for player in self._players:
            player.notify(message)

    def print_winnings(self, player, dealer_score):
        result = player.get_result(dealer_score)
        print "Player: {} | Result: {} | Winnings: {}".format(player.identifier, result, player.get_winnings(dealer_score))
        del self._games[self._game_id]

    @classmethod
    def move(cls, game_id, move):
        if game_id in cls._games:
            game = cls._games.get(game_id)
            game.move(move)
        else:
            raise GameException("invalid game id.")

    @classmethod
    def _generate_dealer_id(cls, identifier):
        return "{}.{}".format(cls.DEALER_ID, identifier)


class PlayerResult(object):

    BUST = 0
    PUSH = 1
    WIN = 2
    BLACKJACK = 2.5


class Participant(StatefulObject):

    PARTICIPANT_STATES = StateFactory.create(['ACTIVE', 'INACTIVE'])

    @property
    def identifier(self):
        return self._identifier

    def __init__(self, identifier):
        super(Participant, self).__init__(
            model=self,
            states=self.PARTICIPANT_STATES.ALL,
            transitions=[
                StateTransition(self.PARTICIPANT_STATES.ACTIVE, self.PARTICIPANT_STATES.INACTIVE, 'hand_is_done')
            ],
            default_state=self.PARTICIPANT_STATES.ACTIVE
        )

        self._identifier = identifier
        self._hand = []

    def state_is_active(self):
        return self.matches(self.PARTICIPANT_STATES.ACTIVE)

    def result_is_blackjack(self, score=None):
        score = score or self._calculate_score()
        return score == 21

    def result_is_bust(self, score=None):
        score = score or self._calculate_score()
        return score > 21

    def hand_is_done(self):
        score = self._calculate_score()
        return self.result_is_blackjack(score) or self.result_is_bust(score)

    def deal_cards(self, cards):
        self._hand.append(cards)
        self.refresh()

    def _calculate_score(self):
        score = 0
        for card in self._hand:
            score += Card.process_card(card, score)

        return score


class House(Participant):

    def can_hit(self):
        return self._calculate_score() < 17


class Player(Participant):

    def __init__(self, identifier, bet, callback=None):
        super(Player, self).__init__(identifier)
        self._bet = bet
        self._active_in_round = True
        self._callback = callback

    def state_is_active(self):
        return super(Player, self).state_is_active() and self._active_in_round

    def make_move(self, deck, move=None):
        if move == Move.HIT:
            card = deck.deal()
            self.notify("You were dealt {}.".format(card))
            self.deal_cards([card])
        else:
            self.set_state(self.PARTICIPANT_STATES.INACTIVE)

        self.finish_round()

    def start_round(self):
        self._active_in_round = True

    def is_active_in_round(self):
        return self._active_in_round

    def finish_round(self):
        self._active_in_round = False

    def get_result(self, dealer_score):
        score = self._calculate_score()
        if self.result_is_bust(score):
            return PlayerResult.BUST
        elif score == dealer_score:
            return PlayerResult.PUSH
        elif self.result_is_blackjack(score):
            return PlayerResult.BLACKJACK
        elif score > dealer_score:
            return PlayerResult.WIN
        else:
            return PlayerResult.BUST

    def get_winnings(self, dealer_score):
        return self.get_result(dealer_score) * self._bet

    def notify(self, message):
        if self._callback:
            self._callback(message)
