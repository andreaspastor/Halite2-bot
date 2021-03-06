import hlt
import logging
from collections import OrderedDict
import random as r
game = hlt.Game("MyBot-V1")
logging.info("Starting MyBot-V1")


i = 0
while True:
    i += 1
    game_map = game.update_map()
    command_queue = []
    
    team_ships = game_map.get_me().all_ships()
    myId = game_map.get_me()

    if i == 1:
        entities_by_distance = game_map.nearby_entities_by_distance(team_ships[0])
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
         
    if len(team_ships) < 4:
        for current, ship in enumerate(team_ships):
            target_planet = closest_empty_planets[current%len(closest_empty_planets)]
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                # Skip this ship
                continue
            elif ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                command = ship.navigate(ship.closest_point_to(target_planet), game_map, speed=hlt.constants.MAX_SPEED)
                if command:
                    command_queue.append(command)

    else:
        for x, ship in enumerate(team_ships):
            if ship.docking_status != ship.DockingStatus.UNDOCKED:
                # Skip this ship
                continue

            entities_by_distance = game_map.nearby_entities_by_distance(ship)
            entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
            
            not_full_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and entities_by_distance[distance][0].owner == myId and not entities_by_distance[distance][0].is_full()]
            closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]
            closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]
            moreShipThanEnemy = len(team_ships) > len(closest_enemy_ships) + 10
            # If there are any empty planets, let's try to mine!
            if len(closest_empty_planets) > 0:
                target_planet = closest_empty_planets[0]
                if ship.can_dock(target_planet):
                    command_queue.append(ship.dock(target_planet))
                else:
                    direction = ship.closest_point_to(target_planet)
                    navigate_command = ship.navigate(
                                direction,
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=True)

                    if navigate_command:
                        command_queue.append(navigate_command)

            elif moreShipThanEnemy and len(not_full_planets) > 0 and r.random() > 0.75:
                target_planet = not_full_planets[0]
                if ship.can_dock(target_planet):
                    command_queue.append(ship.dock(target_planet))
                else:
                    direction = ship.closest_point_to(target_planet)
                    navigate_command = ship.navigate(
                                direction,
                                game_map,
                                speed=int(hlt.constants.MAX_SPEED),
                                ignore_ships=True)

                    if navigate_command:
                        command_queue.append(navigate_command)
            # FIND SHIP TO ATTACK!
            elif len(closest_enemy_ships) > 0:
                target_ship = closest_enemy_ships[0]
                direction = ship.closest_point_to(target_ship)
                navigate_command = ship.navigate(
                            direction,
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=True)

                if navigate_command:
                    command_queue.append(navigate_command)

    game.send_command_queue(command_queue)
    # TURN END
# GAME END