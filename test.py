from merge import Merge

ROWS = 5
COLS = 5

game = Merge()
game.max_placement = 2
game.elixir = 4
game.add_starting_card('SPEAR_GOBLIN', 1)
game.update_hand('SPEAR_GOBLIN', 'GOLDEN_KNIGHT', 'PRINCE')
game.buy_card(0)
row, col = 3, 2
print(game.move_to_back(3, 2))
#game.move_card(3, 2, 3, 0)


game.print_map()