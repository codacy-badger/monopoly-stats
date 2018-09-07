from dataclasses import dataclass, field
from typing import List, Sequence
from random import randint
from pprint import pprint, pformat
import logging


@dataclass
class GameConfig(object):
    # How many games should be played?
    num_of_games: int = 1

    # How many people are playing?
    num_of_players: int = 4

    # How many tiles are on the board?
    num_of_tiles: int = 40

    # How many round will one game last?
    num_of_rounds: int = 45

    # How many dice are rolled each turn
    num_of_dice: int = 2

    # How many doubles in a row to get sent to jail
    num_of_doubles_for_jail: int = 3

    # How many sides are on each dice?
    dice_size: int = 6

    # Which tile is the jail on (minus one)?
    jail_tile: int = 10


@dataclass
class Player(object):
    player_number: int
    logging_parent: str
    board_position: int = 0
    in_jail: bool = False
    logger: logging.Logger = field(init=False, hash=False, compare=False)

    def __post_init__(self):
        self.logger = logging.getLogger(
            f"{self.logging_parent}.player_{self.player_number}"
        )


def roll_dice(amount: int, size: int):
    return [randint(1, size) for _ in range(amount)]


def all_same(sequence: Sequence) -> bool:
    """Check if every item in sequence is the same"""
    return all([i == sequence[0] for i in sequence])


def simulate_turn(game_config: GameConfig, player: Player, tiles: List[int]):
    player.logger.info(f"Starting Player {player.player_number}'s turn...'")
    # Loop for successive doubles
    double_in_row = 0
    should_continue = True
    while should_continue:
        # roll dice
        dice_results = roll_dice(
            amount=game_config.num_of_dice,
            size=game_config.dice_size
        )

        player.logger.info(f"Rolled {dice_results}")

        # only check for doubles if more than one dice rolled
        if all_same(sequence=dice_results) and game_config.num_of_dice > 1:
            double_in_row += 1
            # Give player another turn
            should_continue = True

            player.logger.info(f"Rolled doubles {double_in_row} in a row")

            if player.in_jail:
                # Escape jail on doubles
                player.in_jail = False
                player.logger.info("Escaped jail")

            else:
                # Send player to jail after x amount of doubles
                if double_in_row == game_config.num_of_doubles_for_jail:
                    player.board_position = game_config.jail_tile
                    player.in_jail = True
                    player.logger.info("Thrown in jail")
                    break

        else:
            # End players turn streak
            should_continue = False

        # Don't update board_position if player in jail
        if player.in_jail:
            continue

        # Update board_position
        player.board_position += sum(dice_results)

        # Wrap around board
        if player.board_position >= game_config.num_of_tiles:
            player.board_position -= game_config.num_of_tiles

        player.logger.info(f"Landed on tile {player.board_position}")


def simulate_game(game_config: GameConfig, game_number: int) -> List[int]:
    logger = logging.getLogger(f"monopoly.game_{game_number}")
    logger.info("Initializing game with config:")
    logger.info(pformat(game_config))

    players = [Player(player_number=i, logging_parent=f"monopoly.game_{game_number}")
               for i in range(game_config.num_of_players)]

    # Each item is the number of times the tile(index) has been landed on
    tiles = [0 for _ in range(game_config.num_of_tiles)]

    # Run game
    logger.info("Starting game...")
    for round_number in range(game_config.num_of_rounds):
        logger.info(f"Starting round {round_number}...")
        for player in players:
            # Simulate turn
            simulate_turn(game_config, player, tiles)

            # Record tile player landed on
            tiles[player.board_position] += 1

    return tiles


if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    log = logging.getLogger("monopoly")

    config = GameConfig()

    for i in range(config.num_of_games):
        tiles_landed_on = simulate_game(config, i)
        log.info(f"Result of game {i}: {tiles_landed_on}")
