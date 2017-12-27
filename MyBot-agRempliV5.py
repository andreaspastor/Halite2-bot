import hlt
import logging
from collections import OrderedDict
game = hlt.Game("MyBot-agRempliV5")
logging.info("Starting MyBot-agressifV5")


i = 0
while True:
    i += 1
    game_map = game.update_map()
    command_queue = []
    
    if len(game_map.all_players()) > 2:
        dependOnEnemy = 1
    else:
        dependOnEnemy = 0
    team_ships = game_map.get_me().all_ships()
    myId = game_map.get_me()

    for x, ship in enumerate(team_ships):
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
        diffShipEnemy = (len(team_ships) > len(closest_enemy_ships) + 5) and (len(team_ships) > len(closest_enemy_ships)*1.2)
        # If there are any empty planets, let's try to mine!
        # FIND SHIP TO ATTACK!
        if len(closest_enemy_ships) > 0 and diffShipEnemy:
            target_ship = closest_enemy_ships[0]
            direction = ship.closest_point_to(target_ship)
            navigate_command = ship.navigate(
                        direction,
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=True)

            if navigate_command:
                command_queue.append(navigate_command)
        elif len(sum_empty_closest_planets) > 0 and len(closest_empty_planets) > dependOnEnemy:# moreShipThanEnemy and :
            target_planet = sum_empty_closest_planets[0]
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                direction = ship.closest_point_to(target_planet)
                navigate_command = ship.navigate(
                            direction,
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)

                if navigate_command:
                    command_queue.append(navigate_command)
        elif len(not_full_planets) > 0:# moreShipThanEnemy and :
            target_planet = not_full_planets[0]
            if ship.can_dock(target_planet):
                command_queue.append(ship.dock(target_planet))
            else:
                direction = ship.closest_point_to(target_planet)
                navigate_command = ship.navigate(
                            direction,
                            game_map,
                            speed=int(hlt.constants.MAX_SPEED),
                            ignore_ships=False)

                if navigate_command:
                    command_queue.append(navigate_command)
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