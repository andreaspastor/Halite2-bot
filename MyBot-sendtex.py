import hlt
import logging
from collections import OrderedDict
game = hlt.Game("SentdexBot")
logging.info("Starting SentdexBot")

while True:
    game_map = game.update_map()
    command_queue = []
    
    for ship in game_map.get_me().all_ships():
        shipid = ship.id
        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # Skip this ship
            continue

        entities_by_distance = game_map.nearby_entities_by_distance(ship)
        entities_by_distance = OrderedDict(sorted(entities_by_distance.items(), key=lambda t: t[0]))
        
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Planet) and not entities_by_distance[distance][0].is_owned()]

        team_ships = game_map.get_me().all_ships()
        closest_enemy_ships = [entities_by_distance[distance][0] for distance in entities_by_distance if isinstance(entities_by_distance[distance][0], hlt.entity.Ship) and entities_by_distance[distance][0] not in team_ships]

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
        logging.info(str(ship.id) + ' : ' + str(ship.x) + ' ' + str(ship.y) + ' : ' + str(direction.x) + ' ' + str(direction.y))
    game.send_command_queue(command_queue)
    logging.info(command_queue)
    # TURN END
# GAME END