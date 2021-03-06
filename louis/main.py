from louis.GameClass import Position
from louis.Service import ServiceUtils, ServiceMovement, ServiceOrder, ServiceTorpedo

# Init
global_data, board, ennemy_ship, my_ship = ServiceUtils.init()

# game loop
while True:
    # read turn data and update own ship accordingly
    turn_data = ServiceUtils.read_turn_data()
    my_ship.update_turn_data(turn_data)

    # Read and analyse opponent order
    ennemy_ship.read_opponent_order(turn_data["opponent_orders"])

    move_order = ServiceMovement.chose_movement_and_move(my_ship, board)
    attack_order = ServiceTorpedo.chose_torpedo(my_ship, ennemy_ship)
    message_order = ServiceOrder.create_number_of_possible_position_order(ennemy_ship)
    if not move_order:
        move_order = ServiceMovement.surface(board)
    orders = ServiceOrder.concatenate_order([move_order, attack_order, message_order])
    ServiceOrder.display_order(orders)
