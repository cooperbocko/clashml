from merge import Merge

game = Merge()
game.max_placement = 2
game.elixir = 4
game.add_starting_card('GOBLIN', 1)
game.update_hand('ELECTRO_WIZARD', 'GOLDEN_KNIGHT', 'BABY_DRAGON')
game.buy_card(2)

game.update_hand('ELECTRO_GIANT', 'WITCH', 'EXECUTIONER')
game.elixir = 8
game.max_placement = 3
game.sell_card(0, 2)
game.elixir = 9
game.buy_card(0)
game.elixir = 6
game.update_hand('SKELETON_GIANT', 'SPEAR_GOBLIN', 'BABY_DRAGON')
game.buy_card(2)

game.elixir = 3
game.update_hand('MEGA_KNIGHT', 'ELECTRO_GIANT', 'PRINCESS')
game.buy_card(1)

game.update_hand('BARBARIAN','ELECTRO_GIANT','MEGA_KNIGHT')
game.elixir = 5
game.max_placement = 4
game.buy_card(0)
game.elixir = 3
game.update_hand('BARBARIAN', 'MEGA_KNIGHT', 'BABY_DRAGON')
game.buy_card(0)

game.update_hand('ARCHER_QUEEN', 'GOBLIN_MACHINE', 'PRINCESS')
game.elixir = 6
game.max_placement = 5
game.buy_card(0)

game.max_placement = 6
game.update_hand('WITCH', 'ARCHER_QUEEN', 'PRINCESS')
game.elixir = 9
game.buy_card(1)
game.move_card(3, 1, 3, 0)
game.move_card(3, 2, 3, 4)
game.move_card(0, 1, 0, 0)
game.elixir = 3
game.update_hand('PRINCE', 'PRINCESS', 'MUSKETEER')
game.buy_card(2)

game.elixir = 6
game.update_hand('SPEAR_GOBLIN', 'PRINCESS', 'MUSKETEER')
game.buy_card(2)
game.elixir = 4
game.update_hand('MUSKETEER', 'SKELETON_DRAGON', 'SKELETON_GIANT')
game.buy_card(1)
game.elixir = 2
game.update_hand('ARCHER', 'GOBLIN', 'ELECTRO_WIZARD')
game.buy_card(0)
game.move_card(3, 1, 4, 1)
game.move_card(4, 0, 3, 3)

game.elixir = 4
game.update_hand('BABY_DRAGON', 'PRINCESS', 'EXECUTIONER')
game.buy_card(2)
game.elixir = 1
game.update_hand('GOBLIN_MACHINE', 'BANDIT', 'ELECTRO_WIZARD')
game.sell_card(4, 0)
game.elixir = 3
game.sell_card(4, 1)
game.elixir = 4
game.buy_card(2)
game.move_card(4, 0, 3, 1)

#print(game.hand)
game.print_map()
print(game.syns)