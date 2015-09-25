from random import shuffle


class CardException(Exception):
    pass


class Card(object):

    def __init__(self, name, suit, values):
        self._name = name
        self._suit = suit
        self._values = values

    def use(self, play=None):
        raise NotImplemented

    @staticmethod
    def process_card(card, score):
        if isinstance(card, AceCard):
            if score + 11 > 21:
                return card.use(11)
            else:
                return card.use(1)
        else:
            return card.use()

    def __repr__(self):
        return "{} of {}".format(self._name, self._suit)


class StandardCard(Card):

    def use(self, play=None):
        return self._values[0]


class AceCard(Card):

    def use(self, play=None):
        if play and play in self._values:
            return play
        else:
            raise CardException("illegal card use: {} is not a valid play for an Ace.".format(play))


class CardTypes(object):

    ACE = "Ace", AceCard, [1, 11]
    TWO = "Two", StandardCard, [2]
    THREE = "Three", StandardCard, [3]
    FOUR = "Four", StandardCard, [4]
    FIVE = "Five", StandardCard, [5]
    SIX = "Six", StandardCard, [6]
    SEVEN = "Seven", StandardCard, [7]
    EIGHT = "Eight", StandardCard, [8]
    NINE = "Nine", StandardCard, [9]
    TEN = "Ten", StandardCard, [10]
    JACK = "Jack", StandardCard, [10]
    QUEEN = "Queen", StandardCard, [10]
    KING = "King", StandardCard, [10]

    ALL = [ACE, TWO, THREE, FOUR, FIVE, SIX, SEVEN, EIGHT, NINE, TEN, JACK, QUEEN, KING]

    _TYPE_MAP = {
        ACE: AceCard,
    }


class SuitTypes(object):

    DIAMONDS = "Diamonds"
    HEARTS = "Hearts"
    SPADES = "Spades"
    CLUBS = "Clubs"

    ALL = [DIAMONDS, HEARTS, SPADES, CLUBS]


class Deck(object):

    def __init__(self, decks=1):
        self._cards = []
        for x in xrange(1, decks):
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