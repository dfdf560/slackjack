from app import Game, Move, Player
from pcol import pcol
from time import sleep


def info(message):
    print pcol.bold(pcol.blue(message))


def error(message):
    print pcol.bold(pcol.red(message))
    exit(1)


def query(question):
    return raw_input(pcol.bold(pcol.yellow(question)))

info("Welcome to SlackJack!")
name = query("What's your name?")
play = True
while play:
    bet = query("How much would you like to bet?")
    if not bet.isdigit():
        error("{} is an invalid bet amount.".format(bet))

    player = Player(name, bet, info)

    game = Game.create([player])

    while not game.can_make_move(player):
        sleep(0.1)

    while game.can_make_move(player):
        move_raw = query("What would you like to do? [H = Hit, S = Stand]")
        move = Move.from_raw(move_raw, player, game)
        Game.move(move)

    play = str(query("Play again? [Y/N]")).lower() == 'y'

