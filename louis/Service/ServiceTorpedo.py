from louis.Service import ServiceUtils, ServiceOrder
from louis.GameClass import Position


class ServiceTorpedo:
    @staticmethod
    def chose_torpedo(ship, enemy_ship):
        if ship.torpedo_cooldown > 0:
            return False
        within_range_positions = ServiceTorpedo.find_within_range_torpedo_positions(
            ship,
            enemy_ship
        )
        possible_attack_position = ServiceTorpedo. find_position_in_range_with_potential_enemy(
            within_range_positions,
            enemy_ship
        )
        if len(possible_attack_position) == 0:
            return False
        safe_attack_position = ServiceTorpedo.find_safest_attack_position(
            ship,
            possible_attack_position
        )
        return ServiceOrder.create_attack_order(safe_attack_position)

    @staticmethod
    def find_safest_attack_position(ship, positions):
        best_position = positions[0]
        best_distance = 0
        for position in positions:
            distance = position.get_distance(ship.position)
            if distance > best_distance:
                best_distance = distance
                best_position = position
        return best_position

    @staticmethod
    def find_within_range_torpedo_positions(ship, enemy_ship):
        possible_positions = []
        for x in range(enemy_ship.enemy_board.width):
            for y in range(enemy_ship.enemy_board.height):
                if ship.position.get_distance(Position(x, y)) <= 4:
                    possible_positions.append(Position(x, y))
        return possible_positions

    @staticmethod
    def find_position_in_range_with_potential_enemy(list_positions, enemy_ship):
        potential_positions = []
        for position in list_positions:
            if enemy_ship.enemy_board.get_cell(position).can_be_enemy_position:
                potential_positions.append(position)
        return potential_positions
