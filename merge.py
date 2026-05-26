from dataclasses import dataclass
from enum import Enum

import numpy as np

@dataclass(frozen=True)
class Card:
    base_cost: int
    synergy1: int
    is_frontline: bool
    name: str
    id: int
    
@dataclass 
class LeveledCard:
    card: Card
    level: int
    
    def get_cost(self):
        n = self.level - 1
        return self.card.base_cost * (2 ** n) - 1
     
class Synergy(Enum):
    EMPTY = 0
    NOBEL = 1
    CLAN = 2
    GOBLIN = 3
    UNDEAD = 4
    FOREST = 5
    BOSS = 6

class Merge: 
    CARDS = {
        'EMPTY' : Card(0, 0, False, 'Empty', 0),
        
        'KNIGHT': Card(2, Synergy.NOBEL, True, 'Knight', 1),
        'ARCHER': Card(2, Synergy.CLAN, False, 'Archer', 2),
        'GOBLIN': Card(2, Synergy.GOBLIN, True, 'Goblin', 3),
        'SPEAR_GOBLIN': Card(2, Synergy.GOBLIN, False, 'Spear Goblin', 4),
        'SKELETON_BOMBER': Card(2, Synergy.UNDEAD, False, 'Skeleton Bomber', 5),
        'BARBARIAN': Card(2, Synergy.CLAN, True, 'Barbarian', 6),
        'FIRECRACKER': Card(2, Synergy.FOREST, False, 'Firecracker', 7),
        
        'MUSKETEER': Card(3, Synergy.NOBEL, False, 'Musketeer', 8),
        'MINI_PEKKA': Card(3, Synergy.BOSS, True, 'Mini Pekka', 9),
        'VALKYRIE': Card(3, Synergy.CLAN, True, 'Valkyrie', 10),
        'ROYAL_GIANT': Card(3, Synergy.NOBEL, False, 'Royal Giant', 11),
        'PRINCE': Card(3, Synergy.NOBEL, True, 'Prince', 12),
        'SKELETON_GIANT': Card(3, Synergy.UNDEAD, True, 'Skeleton Giant', 13),
        'DART_GOBLIN': Card(3, Synergy.GOBLIN, False, 'Dart Goblin', 14),
        'GOBLIN_DEMOLISHER': Card(3, Synergy.GOBLIN, False, 'Goblin Demolisher', 15),
        'ROYAL_GHOST': Card(3, Synergy.UNDEAD, True, 'Royal Ghost', 16),
        'MAGIC_ARCHER': Card(3, Synergy.FOREST, False, 'Magic Archer', 17),
        'EXECUTIONER': Card(3, Synergy.FOREST, False, 'Executioner', 18),
        
        'GIANT': Card(4, Synergy.CLAN, True, 'Giant', 19),
        'GOBLIN_CAGER': Card(4, Synergy.GOBLIN, False, 'Goblin Cager', 20),
        'SKELETON_DRAGONS': Card(4, Synergy.UNDEAD, False, 'Skeleton Dragons', 21),
        'WIZARD': Card(4, Synergy.CLAN, False, 'Wizard', 22),
        'PEKKA': Card(4, Synergy.BOSS, True, 'Pekka', 23),
        'WITCH': Card(4, Synergy.UNDEAD, False, 'Witch', 24),
        'BABY_DRAGON': Card(4, Synergy.FOREST, False, 'Baby Dragon', 25),
        'PRINCESS': Card(4, Synergy.NOBEL, False, 'Princess', 26),
        'MEGA_KNIGHT': Card(4, Synergy.BOSS, True, 'Mega Knight', 27),
        'BANDIT': Card(4, Synergy.FOREST, True, 'Bandit', 28),
        'GOBLIN_MACHINE': Card(4, Synergy.GOBLIN, False, 'Goblin Machine', 29),
        
        'SKELETON_KNIGHT': Card(5, Synergy.UNDEAD, True, 'Skeleton Knight', 30),
        'GOLDEN_KNIGHT': Card(5, Synergy.NOBEL, True, 'Golden Knight', 31),
        'ARCHER_QUEEN': Card(5, Synergy.CLAN, False, 'Archer Queen', 32),
        'BOSS_BANDIT': Card(5, Synergy.FOREST, True, 'Boss Bandit', 33),
        'MONK': Card(5, Synergy.BOSS, True, 'Monk', 34)
    }
    
    #consts
    ROWS = 5
    COLS = 5
    HAND_SIZE = 3
    N_SYNS = len(Synergy)
    N_CARDS = len(CARDS)
    
    def __init__(self):
        self.map = [[0 for _ in range(self.ROWS)] for _ in range(self.COLS)]
        self.elixir = 0
        self.elixir_spent = 0
        self.round = 1
        self.hand: list[Card] = [None for _ in range(self.HAND_SIZE)]
        self.max_placement = 2
        self.syns = [0 for _ in range(self.N_SYNS)]
        self.action_mask = np.zeros(654, dtype=np.float32)
        self.current_cards = {} # (name, level) = (r, c)
        
    def buy_card(self, card_position: int) -> bool:
        if card_position < 0 or card_position >= len(self.hand):
            print("Not a valid position")
            return False
        
        card = self.hand[card_position]
        if card == None:
            print("Invalid card!")
            return False
        
        if card.base_cost > self.elixir:
            print("Not enough elixir!")
            return False
        
        self.elixir -= card.base_cost
        self.elixir_spent += card.base_cost
        return self.add_card(card)
    
    def sell_card(self, row: int, col: int) -> bool:
        if (row < 0 or row >= self.ROWS or col < 0 or col >= self.COLS):
            print("Not in bounds!")
            return False
        
        if (self.map[row][col] == 0):
            print("Nohting to sell!")
            return False
        
        level_card = self.map[row][col]
        self.map[row][col] = 0
        self.current_cards.pop((level_card.card.name, level_card.level))
        self.elixir += level_card.get_cost()
        print("Card sold!")
        return True
    
    def move_card(self, oldrow: int, oldcol: int, newrow: int, newcol: int) -> bool:
        if (oldrow < 0 or oldrow >= self.ROWS or oldcol < 0 or oldcol >= self.COLS or newrow < 0 or newrow >= self.ROWS or newcol < 0 or newcol >= self.COLS):
            print("Not in bounds!")
            return False
        
        if self.map[oldrow][oldcol] == 0:
            print('No card to move!')
            print(oldrow, oldcol)
            return False
        
        if oldrow == self.ROWS - 1 and self.map[newrow][newcol] == 0:
            if self.is_board_full():
                print('Cannot move card!')
                return False
        
        card_incoming = self.map[oldrow][oldcol]
        self.current_cards[(card_incoming.card.name, card_incoming.level)] = (newrow, newcol)
        card_leaving = self.map[newrow][newcol]
        if (card_leaving != 0):
            self.current_cards[(card_leaving.card.name, card_leaving.level)] = (oldrow, oldcol)
        self.map[oldrow][oldcol] = card_leaving
        self.map[newrow][newcol] = card_incoming
        print('Card moved!')
        return True
    
    def add_card(self, card: Card) -> bool:
        if(self.merge(card)):
            print("merged!")
            return True
                    
        if self.is_game_full():
            print("Game is full!")
            return False
        
        card_location = (-1, -1)
        if not self.is_board_full():
            if card.is_frontline:
                for row in range(self.ROWS - 1):
                    if self.map[row][2] == 0:
                        card_location = (row, 2)
                        break
                    elif self.map[row][1] == 0:
                        card_location = (row, 1)
                        break
                    elif self.map[row][3] == 0:
                        card_location = (row, 3)
                        break
                    elif self.map[row][0] == 0:
                        card_location = (row, 0)
                        break
                    elif self.map[row][4] == 0:
                        card_location = (row, 4)
                        break
            else:
                for row in range(self.ROWS - 2 , -1, -1):
                    if self.map[row][2] == 0:
                        card_location = (row, 2)
                        break
                    elif self.map[row][1] == 0:
                        card_location = (row, 1)
                        break
                    elif self.map[row][3] == 0:
                        card_location = (row, 3)
                        break
                    elif self.map[row][0] == 0:
                        card_location = (row, 0)
                        break
                    elif self.map[row][4] == 0:
                        card_location = (row, 4)
                        break
        
        if card_location == (-1, -1):
            for col in range(self.COLS):
                if self.map[self.ROWS - 1][col] == 0:
                    card_location = (self.ROWS - 1, col)
                    break
        
        new_level_card = LeveledCard(card, 1)
        self.map[card_location[0]][card_location[1]] = new_level_card
        self.current_cards[(card.name, 1)] = card_location
        print("Card Added!")
        return True
    
    def merge(self, card: Card) -> bool:
        highest_level_card = None
        r, c = (None, None)
        for i in range(1, 4):
            if (card.name, i) not in self.current_cards:
                break
            else:
                r, c = self.current_cards[(card.name, i)]
                highest_level_card = self.map[r][c]
                self.current_cards.pop((card.name, i))
                self.map[r][c] = 0
                
        if highest_level_card:
            highest_level_card.level += 1
            self.map[r][c] = highest_level_card
            self.current_cards[(card.name, highest_level_card.level)] = (r, c)
            return True
        return False

    def get_value(self) -> int:
        self.update_syns()
        # synergies - max = 3
        synergy_reward = 0
        for syn in self.syns:
            if syn >= 2:
                synergy_reward += 1
            if syn >= 4:
                synergy_reward += 1
            if syn >= 6:
                synergy_reward += 1

        # level - max = 11 * 4
        level_reward = 0
        #placement - max = 6 * 4
        placement_reward = 0
        for i in range(self.ROWS):
            for j in range(self.COLS):
                card = self.map[i][j]
                if card != 0:
                    level_reward += card.level # reward for card levels regardless of placement
                    if i < self.ROWS - 1:
                        placement_reward += card.level # reward for card levels of only placed cards
                        
        # elixir - max ~ 100
        elixir_reward = self.elixir / 100
        elixir_spent_reward = self.elixir_spent / 100    
        
        # max output is 4: synergy_max = 1, level_max = 1, placement_max = 1, elixir_max = 0.5, elixir_spent_max = 0.5
        return synergy_reward/3 + level_reward/44 + placement_reward/24 + elixir_reward/10 + elixir_spent_reward/10
    
    def get_state(self) -> tuple[np.array, np.array]:
        self.update_syns()
        
        board_pos = np.arange(25, dtype=np.int64)
        board_cards = np.zeros((25, 5), dtype=np.int64)
        for i in range(self.ROWS):
            for j in range(self.COLS):
                card = self.map[i][j]
                if card != 0:
                    board_cards[i * self.ROWS + j] = [card.card.id, card.card.synergy1.value, card.card.synergy2.value, card.level, card.card.base_cost]
                else:
                    board_cards[i * self.ROWS + j] = [0, 0, 0, 0, 0]
                    
        shop_cards = np.zeros((3, 5), dtype=np.int64)
        for i in range(len(self.hand)):
            card = self.hand[i]
            shop_cards[i] = [card.id, card.synergy1.value, card.synergy2.value, 1, card.base_cost]
            
        game_data = np.array([
            self.elixir / 100.0,
            self.elixir_spent / 100.0,
            self.max_placement / 6.0,
            self.round / 20.0
        ], dtype=np.float32)
        
        state = {
            "board_cards": board_cards,
            "board_pos": board_pos,
            "shop_cards": shop_cards,
            "game_data": game_data 
        }
        
        return state, self.get_action_mask()
  
    def is_board_full(self) -> bool:
        n_cards_on_board = 0
        for row in range(self.ROWS - 1):
            for col in range(self.COLS):
                if self.map[row][col] != 0:
                    n_cards_on_board += 1
                    
        return n_cards_on_board >= self.max_placement
    
    def is_bench_full(self) -> bool:
        for col in range(self.COLS):
            if self.map[self.ROWS - 1][col] == 0:
                return False
            
        return True
    
    def is_game_full(self) -> bool:
        return self.is_board_full() and self.is_bench_full()
    
    def update_hand(self, card1: str, card2: str, card3: str) -> bool:
        card1 = str.upper(card1)
        card2 = str.upper(card2)
        card3 = str.upper(card3)
        if card1 not in self.CARDS or card2 not in self.CARDS or card3 not in self.CARDS:
            print('Card(s) not found!')
            return False
        
        card_1 = self.CARDS[card1]
        card_2 = self.CARDS[card2]
        card_3 = self.CARDS[card3]
        self.hand[0] = card_1
        self.hand[1] = card_2
        self.hand[2] = card_3
        return True
    
    def add_card_in(self, card: str, level: int, row: int, col: int) -> bool:
        if card not in self.CARDS:
            print('Card not found!')
            return False
        
        if row not in range(0, self.ROWS) or col not in range(0, self.COLS):
            print('Location not in board range!')
            return False
        
        level_card = LeveledCard(self.CARDS[card], level, row, col)
        self.map[row][col] = level_card
        return True
    
    def remove_card(self, row: int, col: int):
        level_card = self.map[row][col]
        self.map[row][col] = 0
        
    def add_starting_card(self, card: str, level: int) -> bool:
        if card not in self.CARDS:
            print('Card not found!')
            return False
        
        level_card = LeveledCard(self.CARDS[card], level)
        if level_card.card.is_frontline:
            level_card.row = 0
            level_card.col = 2
            self.map[0][2] = level_card
        else:
            level_card.row = self.ROWS - 2
            level_card.col = 2
            self.map[self.ROWS - 2][2] = level_card
        return True
    
    def update_syns(self):
        card_set = set()
        for row in range(self.ROWS - 1):
            for col in range(self.COLS):
                if self.map[row][col] != 0:
                    card_set.add(self.map[row][col].card)
                    
        for card in card_set:
            self.syns[card.synergy1.value] += 1
    
    def print_map(self):
        res = ""
        res = res + '[\n'
        for row in range(self.ROWS):
            row_str = ''
            for col in range(self.COLS):
                cell = self.map[row][col]
                if cell == 0:  
                    row_str = row_str + ' 0'
                else:
                    row_str = row_str + (f' {str(cell.card.name)} {str(cell.level)}')
            res = res + (row_str + '\n')
        res = res + ']'
        return res
        
    #for simplicity of game actions
    def move_to_front(self, old_row: int, old_col: int) -> tuple[bool, int, int]:
        #find first open spot
        r, c = 0, 0
        for col in range(self.COLS):
            if self.map[r][col] == 0:
                c = col
                break
        
        b = self.move_card(old_row, old_col, r, c)
        return (b, r, c)
    
    def move_to_back(self, old_row: int, old_col: int) -> tuple[bool, int, int]:
        #find first open spot
        r, c = self.ROWS-2, 0
        for col in range(self.COLS):
            if self.map[r][col] == 0:
                c = col
                break
        
        b = self.move_card(old_row, old_col, r, c)
        return (b, r, c)
    
    def move_to_bench(self, old_row: int, old_col: int) -> tuple[bool, int, int]:
        #find first open spot, if nothing is open just replace the first slot
        r, c = self.ROWS-1, 0
        for col in range(self.COLS):
            if self.map[r][col] == 0:
                c = col
                break
        
        b = self.move_card(old_row, old_col, r, c)
        return (b, r, c)
    
    def points_to_check(self) -> list[tuple[int, int]]:
        points = []
                    
        if not self.is_board_full():
            #first front open
            front = (0,0)
            for row in range(self.ROWS - 1):
                if self.map[row][2] == 0:
                    front = (row, 2)
                    break
                elif self.map[row][1] == 0:
                    front = (row, 1)
                    break
                elif self.map[row][3] == 0:
                    front = (row, 3)
                    break
                elif self.map[row][0] == 0:
                    front = (row, 0)
                    break
                elif self.map[row][4] == 0:
                    front = (row, 4)
                    break
            points.append(front)
                
            back = (0,0)
            for row in range(self.ROWS - 2 , -1, -1):
                if self.map[row][2] == 0:
                    back = (row, 2)
                    break
                elif self.map[row][1] == 0:
                    back = (row, 1)
                    break
                elif self.map[row][3] == 0:
                    back = (row, 3)
                    break
                elif self.map[row][0] == 0:
                    back = (row, 0)
                    break
                elif self.map[row][4] == 0:
                    back = (row, 4)
                    break
            points.append(back)
        
        if not self.is_bench_full():
            bench = (0,0)
            for i in range(self.COLS):
                if self.map[self.ROWS - 1][i] == 0:
                    bench = (self.ROWS - 1, i)
                    break
            points.append(bench)
            
        #all previous points
        for row in range(self.ROWS):
            for col in range(self.COLS):
                if self.map[row][col] != 0:
                    points.append((row, col))
        
        return points
    
    def get_action_mask(self) -> np.ndarray:
        self.action_mask.fill(1.0)
        #Buy 0-2
        if not self.is_game_full():
            for index, card in enumerate(self.hand):
                if self.elixir >= card.base_cost:
                    self.action_mask[0 + index] = 0.0
        #Sell 3-27
        for r in range(self.ROWS):
            for c in range(self.COLS):
                if self.map[r][c] != 0:
                    self.action_mask[3 + (r * self.COLS) + c] = 0.0
        #Move 28-652
        for r in range(self.ROWS):
            for c in range(self.COLS):
                from_index = r * self.COLS + c
                if self.map[r][c] == 0:
                    continue
                
                for to_r in range(self.ROWS):
                    for to_c in range(self.COLS):
                        to_index = to_r * self.COLS + to_c
                        if from_index == to_index:
                            continue
                        
                        action_index = 28 + from_index * 25 + to_index
                        #From Board
                        if r < self.ROWS - 1:
                            self.action_mask[action_index] = 0.0
                        #From Bench
                        if r == self.ROWS - 1:
                            #Bench to Bench
                            if to_r == self.ROWS - 1:
                                self.action_mask[action_index] = 0.0
                            #Bench to Board
                            if to_r < self.ROWS - 1:
                                if not self.is_board_full() or self.map[r][c] != 0 and self.map[to_r][to_c] != 0:
                                    self.action_mask[action_index] = 0.0
        #Do nothing 653
        self.action_mask[653] = 0.0
        return self.action_mask