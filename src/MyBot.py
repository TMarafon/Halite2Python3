"""
Welcome to your first Halite-II bot!

This bot's name is Settler. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""
# Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
import hlt
# Then let's import the logging module so we can print out information
import logging

import numpy as np

from enum import Enum

import math

import time

from random import choices

# GAME START
# Here we define the bot's name as Settler and initialize the game, including communication with the Halite engine.
game = hlt.Game("Hyve2.5")
# Then we print our start message to the logs
#logging.info("Starting my Hyve2 bot!")

bot_turn = 0

def is_dockable_or_enemy_ship(ship, entity,gm):
    return (isinstance(entity, hlt.entity.Planet) and planet_has_free_slot(entity,gm)) or (isinstance(entity, hlt.entity.Ship) and entity.owner != ship.owner)

def get_closest_entity(ship, gm):
    entities_by_distance = gm.nearby_entities_by_distance(ship)
    for distance in sorted(entities_by_distance):
      nearest = next((nearest_entity for nearest_entity in entities_by_distance[distance] if is_dockable_or_enemy_ship(ship, nearest_entity,gm)), None)
      if nearest:
        return nearest

def dock(ship, friend_planet, command_queue):
    command = ship.dock(friend_planet)
    if command:
        command_queue.append(command)

def get_closest_enemy_ship(ship, game_map):
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    nearest_ship = None
    for distance in sorted(entities_by_distance):
      nearest_ship = next((nearest_entity for nearest_entity in entities_by_distance[distance] if isinstance(nearest_entity, hlt.entity.Ship)), None)
      if nearest_ship and nearest_ship.owner != ship.owner:
        return nearest_ship

def attack_enemy_ship(curr_ship, enemy_ship, command_queue):
    #logging.info("Attacking enemy ship ")
    navigate_command = curr_ship.navigate(
            curr_ship.closest_point_to(enemy_ship, min_distance=get_distance(curr_ship)),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False)
    if navigate_command:
        command_queue.append(navigate_command)

def attack_closest_enemy_ship(curr_ship, game_map, command_queue):
    #logging.info("Attacking enemy ship ")
    enemy_ship = get_closest_enemy_ship(curr_ship, game_map)
    navigate_command = curr_ship.navigate(
            curr_ship.closest_point_to(enemy_ship, min_distance=get_distance(curr_ship)),
            game_map,
            speed=int(hlt.constants.MAX_SPEED),
            ignore_ships=False)
    if navigate_command:
        command_queue.append(navigate_command)

def can_dock(ship, planet, gm):
    return ship.can_dock(planet) and planet_has_free_slot(planet, gm)

def get_planet_capacity(planet):
    return max(1.0, math.ceil(planet.radius / 3.0))

def planet_has_free_slot(planet, gm):
    return get_planet_capacity(planet) > len(planet.all_docked_ships()) and (planet.owner == gm.get_me() or planet.owner is None);

speed = hlt.constants.MAX_SPEED

def get_distance(ship):
    if ship.health < 129:
        return 0
    else:
        return 3

while True:

    t0 = time.time()
    # TURN START
    #logging.info(bot_turn)

    # Update the map for the new turn and get the latest version
    game_map = game.update_map()

    # Here we define the set of commands to be sent to the Halite engine at the end of the turn
    command_queue = []

    ships = [ship for ship in game_map.get_me().all_ships() if ship.docking_status == ship.DockingStatus.UNDOCKED ]
    for current in range(0, len(ships)):

        curr_ship = ships[current]

        if bot_turn < 1 and current < 2:
            continue
        if bot_turn < 2 and current < 1:
            continue


        entity = get_closest_entity(curr_ship, game_map)

        if isinstance(entity, hlt.entity.Planet):

            if entity is not None\
                and can_dock(curr_ship, entity, game_map):
                logging.info("Can dock!")
                dock(curr_ship, entity, command_queue)

            elif entity is not None\
                and len(entity.all_docked_ships()) != 0 \
                and entity.all_docked_ships()[0].owner != curr_ship.owner:
                attack_enemy_ship(curr_ship, entity.all_docked_ships()[0], command_queue)

            else :
                #logging.info("Navigating ")
                navigate_command = curr_ship.navigate(
                                    curr_ship.closest_point_to(entity),
                                    game_map,
                                    speed=int(speed),
                                    ignore_ships=False)
                if navigate_command:
                    command_queue.append(navigate_command)

        else:
            attack_enemy_ship(curr_ship, entity, command_queue)

        t1 = time.time()
        #logging.info(t1-t0)
        if t1 - t0 > 1.7:
            break

    # Send our set of commands to the Halite engine for this turn
    #logging.info("Sending commands ")
    #logging.info(command_queue)
    game.send_command_queue(command_queue)
    bot_turn = bot_turn + 1
    # TURN END
# GAME END

