from dataclasses import dataclass
from enum import Enum

import numpy as np

@dataclass(frozen=True)
class Card:
    base_cost: int
    synergy1: int
    synergy2: int
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
    TANK = 2
    CLAN = 3
    MARKSMAN = 4
    GOBLIN = 5
    ASSASSIN = 6
    WARRIOR = 7
    UNDEAD = 8
    DRAGON = 9
    FIRE = 10
    HINDER = 11
    TITAN = 12
    SUPERSTAR = 13
    ACE = 14
    
'''
ALL_CARDS = {
    'KNIGHT' : Card(2, Synergy.NOBEL, Synergy.TANK, 0, True, 'Knight'),
    'PRINCE' : Card(3, Synergy.NOBEL, Synergy.BRAWLER, 4, True, 'Prince'),
    'PRINCESS' : Card(4, Synergy.NOBEL, Synergy.BLASTER, 8, False, 'Princess'),
    'GOLDEN_KNIGHT' : Card(5, Synergy.NOBEL, Synergy.ASSASSIN, 12, True, 'Golden Knight'),
    
    'ARCHER' : Card(2, Synergy.CLAN, Synergy.RANGER, 16, False, 'Archer'),
    'VALKYRIE' : Card(3, Synergy.CLAN, Synergy.BRUTALIST, 20, True, 'Valkyrie'),
    'BARBARIAN' : Card(2, Synergy.CLAN, Synergy.BRAWLER, 24, True, 'Barbarian'),
    'ARCHER_QUEEN' : Card(5, Synergy.CLAN, Synergy.RANGER, 28, False, 'Archer Queen'),
    
    'DART_GOBLIN' : Card(3, Synergy.GOBLIN, Synergy.RANGER, 32, False, 'Dart Goblin'),
    'GOBLIN' : Card(2, Synergy.GOBLIN, Synergy.ASSASSIN, 36, True, 'Goblin'),
    'SPEAR_GOBLIN' : Card(2, Synergy.GOBLIN, Synergy.BLASTER, 40, False, 'Spear Goblin'),
    'GOBLIN_MACHINE' : Card(4, Synergy.GOBLIN, Synergy.BRUTALIST, 44, True, 'Gobin Machine'),
    
    'SKELETON_GIANT' : Card(3, Synergy.UNDEAD, Synergy.BRAWLER, 48, True, 'Skeleton Giant'),
    'ROYAL_GHOST' : Card(4, Synergy.UNDEAD, Synergy.ASSASSIN, 52, True, 'Royal Ghost'),
    'SKELETON_BOMBER' : Card(2, Synergy.UNDEAD, Synergy.BLASTER, 56, False, 'Skeleton Bomber'),
    'SKELETON_KING' : Card(5, Synergy.UNDEAD, Synergy.BRUTALIST, 60, True, 'Skeleton King'),
    
    'MEGA_KNIGHT' : Card(4, Synergy.ACE, Synergy.BRAWLER, 64, True, 'Mega Knight'),
    'EXECUTIONER' : Card(3, Synergy.ACE, Synergy.BLASTER, 68, False, 'Executioner'),
    'PEKKA' : Card(3, Synergy.PEKKA, Synergy.BRAWLER, 72, True, 'Pekka'),
    'BANDIT' : Card(4, Synergy.ACE, Synergy.AVENGER, 76, True, 'Bandit'),
    
    'ELECTRO_GIANT': Card(3, Synergy.GIANT, Synergy.SUPERSTAR, 80, True, 'Eletro Giant'),
    'ELECTRO_WIZARD': Card(4, Synergy.ELECTRIC, Synergy.MAGE, 84, False, 'Electro Wizard'),
    'WIZARD': Card(2, Synergy.CLAN, Synergy.BLASTER, 88, False, 'Wizard'),
    'BABY_DRAGON': Card(4, Synergy.FIRE, Synergy.BLASTER, 92, False, 'Baby Dragon'),
    
    'WITCH': Card(4, Synergy.UNDEAD, Synergy.SUPERSTAR, 96, False, 'Witch'),
    'SKELETON_DRAGON': Card(2, Synergy.UNDEAD, Synergy.RANGER, 100, False, 'Skeleton Dragon'),
    'MUSKETEER': Card(3, Synergy.NOBEL, Synergy.SUPERSTAR, 104, False, 'Musketeer'),
    
    'MINI_PEKKA': Card(2, Synergy.PEKKA, Synergy.BRUTALIST, 108, True, 'Mini Pekka'),
    'ROYAL_GIANT': Card(2, Synergy.GIANT, Synergy.RANGER, 112, False, 'Royal Giant'),
    'MONK': Card(5, Synergy.ACE, Synergy.SUPERSTAR, 116, True, 'Monk'),
    
    'GIANT': Card(3, Synergy.TITAN, Synergy.SUPERSTAR, 120, True, 'Giant'),
    'GOBLIN_DEMOLISHER': Card(3, Synergy.GOBLIN, Synergy.WARRIOR, 124, True, 'Goblin Demolisher')
    }'''

class Merge: 
    CARDS = {
        'EMPTY' : Card(0, 0, 0, False, 'Empty', 0),
        'KNIGHT': Card(2, Synergy.NOBEL, Synergy.TANK, True, 'Knight', 1),
        'ARCHER': Card(2, Synergy.CLAN, Synergy.MARKSMAN, False, 'Archer', 2),
        'GOBLIN': Card(2, Synergy.GOBLIN, Synergy.ASSASSIN, True, 'Goblin', 3),
        'BARBARIAN': Card(2, Synergy.CLAN, Synergy.WARRIOR, True, 'Barbarian'),
        'SKELETON_DRAGON': Card(2, Synergy.UNDEAD, Synergy.DRAGON, False, 'Skeleton Dragon', 4),
        'WIZARD': Card(2, Synergy.FIRE, Synergy.HINDER, False, 'Wizard', 5),
        'DART_GOBLIN': Card(2, Synergy.GOBLIN, Synergy.MARKSMAN, False, 'Dart Goblin', 6),
        'GIANT': Card(3, Synergy.TITAN, Synergy.SUPERSTAR, True, 'Giant', 7),
        'MUSKETEER': Card(3, Synergy.NOBEL, Synergy.MARKSMAN, False, 'Musketeer', 8),
        'VALKYRIE': Card(3, Synergy.CLAN, Synergy.TANK, True, 'Valkyrie', 9),
        'ROYAL_GIANT': Card(3, Synergy.TITAN, Synergy.MARKSMAN, False, 'Royal Giant', 10),
        'SKELETON_GIANT': Card(3, Synergy.UNDEAD, Synergy.TANK, True, 'Skeleton Giant', 11),
        'GOBLIN_DEMOLISHER': Card(3, Synergy.GOBLIN, Synergy.WARRIOR, False, 'Goblin Demolisher', 12),
        'PEKKA': Card(4, Synergy.ACE, Synergy.SUPERSTAR, True, 'Pekka', 13),
        'WITCH': Card(4, Synergy.UNDEAD, Synergy.HINDER, False, 'Witch', 14),
        'BABY_DRAGON': Card(4, Synergy.FIRE, Synergy.DRAGON, False, 'Baby Dragon', 15),
        'PRINCE': Card(4, Synergy.NOBEL, Synergy.WARRIOR, True, 'Prince', 16),
        'GOBLIN_MACHINE': Card(4, Synergy.GOBLIN, Synergy.SUPERSTAR, True, 'Gobin Machine', 17),
        'SKELETON_KING': Card(5, Synergy.UNDEAD, Synergy.WARRIOR, True, 'Skeleton King', 18),
        'GOLDEN_KNIGHT' : Card(5, Synergy.NOBEL, Synergy.ASSASSIN, True, 'Golden Knight', 19),
        'ARCHER_QUEEN' : Card(5, Synergy.CLAN, Synergy.SUPERSTAR, False, 'Archer Queen', 20),
        'MONK': Card(5, Synergy.ACE, Synergy.TANK, True, 'Monk', 21),
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
        self.hand: list[LeveledCard] = [3]
        self.max_placement = 2
        self.syns = [0 for _ in range(self.N_SYNS)]
        self.action_mask = np.zeros(654, dtype=np.float32)
        
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
        card_leaving = self.map[newrow][newcol]
        card_incoming.row = newrow
        card_incoming.col = newcol
        if (card_leaving != 0):
            card_leaving.row = oldrow
            card_leaving.col = oldcol
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
        self.map[new_level_card.row][new_level_card.col] = new_level_card
        print("Card Added!")
        return True
    
    def merge(self, card: Card) -> bool:
        if self.current_cards[card.base_index] == 0:
            return False 
        
        highest_level_card = self.current_cards[card.base_index]
        for i in range(card.base_index, card.base_index + 4):
            if self.current_cards[i] != 0:
                highest_level_card = self.current_cards[i]
                self.current_cards[i] = 0
                self.map[highest_level_card.row][highest_level_card.col] = 0
            else:
                break
            
        highest_level_card.level = highest_level_card.level + 1
        self.map[highest_level_card.row][highest_level_card.col] = highest_level_card
        self.elixir += highest_level_card.level - 1
        return True

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
                    board_cards[i * self.ROWS + j] = [card.card.id, card.card.synergy1, card.card.synergy2, card.level, card.card.base_cost]
                else:
                    board_cards[i * self.ROWS + j] = [0, 0, 0, 0, 0]
                    
        shop_cards = np.zeros((3, 5, 2), dtype=np.int64)
        for i in range(len(self.hand)):
            card = self.hand[i]
            shop_cards[i] = [card.card.id, card.card.synergy1, card.card.synergy2, card.level, card.card.base_cost]
            
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
        
        card_1 = LeveledCard(self.CARDS[card1], 1, -1, -1, 0)
        card_2 = LeveledCard(self.CARDS[card2], 1, -1, -1, 1)
        card_3 = LeveledCard(self.CARDS[card3], 1, -1, -1, 2)
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
        
        level_card = LeveledCard(self.CARDS[card], level, -1, -1)
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
            self.syns[card.synergy2.value] += 1
    
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
            for index, level_card in enumerate(self.hand):
                if self.elixir >= level_card.card.base_cost:
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