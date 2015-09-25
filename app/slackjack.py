from game import Game, Player
from pcol import pcol


def info(message):
    print pcol.bold(pcol.blue(message))


def error(message):
    print pcol.bold(pcol.red(message))
    exit(1)


def query(question):
    return raw_input(pcol.bold(pcol.yellow(question)))

info("Welcome to SlackJack!")
name = query("What's your name?")
bet = query("How much would you like to bet?")
if not bet.isdigit():
    error("{} is an invalid")

player = Player(name, bet)

game = Game([player])