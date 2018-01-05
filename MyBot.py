import hlt
import logging
from collections import OrderedDict
game = hlt.Game("MyBot-V11")
logging.info("Starting MyBot-V11")

"""def bestOtherPlayer(players, myId):
    maxShip = -1
    for player in players:
        if player != myId and len(player.all_ships()) > maxShip:
            maxShip = len(player.all_ships())
            bestOtherPlayerId = player
    return bestOtherPlayerId"""

cpt = 0
while cpt < 500:
    game_map = game.update_map()
    command_queue = []
    myId = game_map.get_me()
    #if cpt % 5 == 0:
    #bestOtherPlayerId = bestOtherPlayer(game_map.all_players(), myId)

    allPlanets = game_map.all_planets()
    num_docking_spots_planets = {}
    places = 0
    for planet in allPlanets:
        num_docking_spots_planets[planet.id] = planet.num_docking_spots - len(planet._docked_ship_ids) + 1
        places += planet.num_docking_spots - len(planet._docked_ship_ids) + 1

    if len(game_map.all_players()) > 2:
        dependOnEnemy = 1
        dependOnEnemy_rate = 1.2
    else:
        dependOnEnemy = 0
        dependOnEnemy_rate = 2.0
    team_ships = game_map.get_me().all_ships()
    team_ships_docked = [team_ships[x] for x in range(len(team_ships)) if team_ships[x].planet != None]

    for x, ship in enumerate(team_ships[1:]):
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        
        sum_empty_closest_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and ((entities_by_distance[distance][0].owner == myId and not entities_by_distance[distance][0].is_full()) or not entities_by_distance[distance][0].is_owned())]
        not_full_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0].owner == myId and not entities_by_distance[distance][0].is_full()]
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and not(entities_by_distance[distance][0] in team_ships) and entities_by_distance[distance][0].planet != None]
        #closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and not(entities_by_distance[distance][0] in team_ships)]
        moreShipThanEnemy = len(team_ships) > len(closest_enemy_ships)*1.1
        diffShipEnemy = (len(team_ships) > len(closest_enemy_ships) + 5) and (len(team_ships) > len(closest_enemy_ships)*dependOnEnemy_rate)
        # If there are any empty planets, let's try to mine!
        # FIND SHIP TO ATTACK!
        if len(closest_enemy_ships) > 0 and diffShipEnemy:
            target_ship = closest_enemy_ships[0]
            direction = ship.closest_point_to(target_ship)
            navigate_command = ship.move(
                        direction,
                        game_map)

            if navigate_command:
                command_queue.append(navigate_command)
        elif len(sum_empty_closest_planets) > 0 and len(closest_empty_planets) > dependOnEnemy:# moreShipThanEnemy and :
            target_planet = sum_empty_closest_planets[0]
            i = 1
            while num_docking_spots_planets[target_planet.id] <= 0 and len(sum_empty_closest_planets) > i:
                target_planet = sum_empty_closest_planets[i]
                i += 1
            num_docking_spots_planets[target_planet.id] -= 1
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                direction = ship.closest_point_to(target_planet)
                navigate_command = ship.move(
                            direction,
                            game_map)

                if navigate_command:
                    command_queue.append(navigate_command)
        elif places > 0 and len(not_full_planets) > 0: #len(not_full_planets) > 0:# moreShipThanEnemy and :
            target_planet = not_full_planets[0]
            i = 1
            while num_docking_spots_planets[target_planet.id] <= 0 and len(not_full_planets) > i:
                target_planet = not_full_planets[i]
                i += 1
            num_docking_spots_planets[target_planet.id] -= 1
            places -= 1
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                direction = ship.closest_point_to(target_planet)
                navigate_command = ship.move(
                            direction,
                            game_map)

                if navigate_command:
                    command_queue.append(navigate_command)
        elif len(closest_enemy_ships) > 0:
            target_ship = closest_enemy_ships[0]
            direction = ship.closest_point_to(target_ship)
            navigate_command = ship.move(direction,game_map)

            if navigate_command:
                command_queue.append(navigate_command)
        logging.info(str(ship.x) + ' ' + str(ship.y) + ' : ' + str(direction.x) + ' ' + str(direction.y))

    ship = team_ships[0]
    entities_by_distance = game_map.nearby_entities_by_distance(ship)
    entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
    closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and not(entities_by_distance[distance][0] in team_ships)]
    target_ship = closest_enemy_ships[0]
    direction = ship.closest_point_to(target_ship)
    navigate_command = ship.move(
                direction,
                game_map)

    if navigate_command:
        command_queue.append(navigate_command)

    game.send_command_queue(command_queue)
    logging.info(command_queue)
    # TURN END
# GAME END