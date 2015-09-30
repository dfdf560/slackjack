from random import shuffle


class Card(object):

    @property
    def variations(self):
        return len(self._values)

    def __init__(self, name, suit, values):
        self._name = name
        self._suit = suit
        self._values = values

    def use(self, index):
        return self._values[index]

    @staticmethod
    def process_card(card, index):
        return card.use(index)

    def __repr__(self):
        return "{} of {}".format(self._name, self._suit)


class CardTypes(object):

    ACE = "Ace", Card, [1, 11]
    TWO = "2", Card, [2]
    THREE = "3", Card, [3]
    FOUR = "4", Card, [4]
    FIVE = "5", Card, [5]
    SIX = "6", Card, [6]
    SEVEN = "7", Card, [7]
    EIGHT = "8", Card, [8]
    NINE = "9", Card, [9]
    TEN = "10", Card, [10]
    JACK = "Jack", Card, [10]
    QUEEN = "Queen", Card, [10]
    KING = "King", Card, [10]

    ALL = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING]


class SuitTypes(object):

    DIAMONDS = "Diamonds"
    HEARTS = "Hearts"
    SPADES = "Spades"
    CLUBS = "Clubs"

    ALL = [DIAMONDS, HEARTS, SPADES, CLUBS]


class Deck(object):

    def __init__(self, decks=1):
        self._cards = []
        for x in xrange(0, decks):
            self.generate()

        self.shuffle()

    def generate(self):
        for suit in SuitTypes.ALL:
            for card_type in CardTypes.ALL:
                self._cards.append(card_type[1](card_type[0], suit, card_type[2]))

    def shuffle(self):
        shuffle(self._cards)

    def deal(self):
        return self._cards.pop()