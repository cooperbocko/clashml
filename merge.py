from dataclasses import dataclass
from enum import Enum

import numpy as np

@dataclass(frozen=True)
class Card:
    base_cost: int
    synergy1: int
    synergy2: int
    base_index: int
    is_frontline: bool
    name: str
    
@dataclass 
class LeveledCard:
    card: Card
    level: int
    row: int
    col: int
    hand_position: int = 0
    
    def get_cost(self):
        return (2 ** (self.level - 1)) * self.card.base_cost
    
    def get_index(self):
        return self.card.base_index + self.level - 1
     
class Synergy(Enum):
    NOBEL = 0
    CLAN = 1
    GOBLIN = 2
    UNDEAD = 3
    ACE = 4
    JUGGERNAUT = 5
    BRAWLER = 6
    RANGER = 7
    ASSASSIN = 8
    AVENGER = 9
    BLASTER = 10
    MAGE = 11
    ELECTRIC = 12
    FIRE = 13
    GIANT = 14
    PEKKA = 15
    BRUTALIST = 16
    SUPERSTAR = 17

class Merge: 
    CARDS = {
    'KNIGHT' : Card(2, Synergy.NOBEL, Synergy.JUGGERNAUT, 0, True, 'Knight'),
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
    'MONK': Card(5, Synergy.ACE, Synergy.SUPERSTAR, 116, True, 'Monk')
    }
    
    #consts
    ROWS = 5
    COLS = 5
    HAND_SIZE = 3
    N_SYNS = len(Synergy)
    N_CARDS = len(CARDS) * 4
    
    def __init__(self):
        self.map = [[0 for _ in range(self.ROWS)] for _ in range(self.COLS)]
        self.elixir = 0
        self.current_cards = [0 for _ in range(self.N_CARDS)]
        self.hand = [0 for _ in range(int(self.N_CARDS / 4))] 
        self.max_placement = 2
        self.syns = [0 for _ in range(self.N_SYNS)]
        
    def buy_card(self, card_posiiton: int) -> tuple[bool, int]:
        card = None
        for hand_card in self.hand:
            if hand_card != 0 and hand_card.hand_position == card_posiiton:
                card = hand_card.card
        if card == None:
            print("Not a valid position")
            return (False, -1)
        
        if card.base_cost > self.elixir:
            print("Not enough elixir!")
            return (False, -1)
        
        return self.add_card(card)
    
    def sell_card(self, row: int, col: int) -> tuple[bool, int]:
        if (row < 0 or row >= self.ROWS or col < 0 or col >= self.COLS):
            print("Not in bounds!")
            return (False, -1)
        
        if (self.map[row][col] == 0):
            print("Nohting to sell!")
            return (False, -1)
        
        level_card = self.map[row][col]
        self.current_cards[level_card.get_index()] = 0
        self.map[row][col] = 0
        print("Card sold!")
        _, reward = self.update_syns()
        return (True, reward)
    
    def move_card(self, oldrow: int, oldcol: int, newrow: int, newcol: int) -> tuple[bool, int]:
        if (oldrow < 0 or oldrow >= self.ROWS or oldcol < 0 or oldcol >= self.COLS or newrow < 0 or newrow >= self.ROWS or newcol < 0 or newcol >= self.COLS):
            print("Not in bounds!")
            return (False, -1)
        
        if self.map[oldrow][oldcol] == 0:
            print('No card to move!')
            print(oldrow, oldcol)
            return (False, -1)
        
        if oldrow == self.ROWS - 1 and self.map[newrow][newcol] == 0:
            if self.is_board_full():
                print('Cannot move card!')
                return (False, -1)
        
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
        _, reward = self.update_syns()
        return (True, reward)
    
    def add_card(self, card: Card) -> tuple[bool, int]:
        if(self.merge(card)):
            print("merged!")
            return (True, 3)
                    
        if self.is_game_full():
            print("Game is full!")
            return (False, -1)
        
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
        
        new_level_card = LeveledCard(card, 1, card_location[0], card_location[1])
        self.current_cards[new_level_card.get_index()] = new_level_card
        self.map[new_level_card.row][new_level_card.col] = new_level_card
        print("Card Added!")
        _, reward = self.update_syns()
        return (True, reward)
    
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
        self.current_cards[highest_level_card.get_index()] = highest_level_card
        self.map[highest_level_card.row][highest_level_card.col] = highest_level_card
        return True
    
    def get_state(self) -> np.array:
        cards = np.array([1 if card != 0 else 0 for card in self.current_cards])
        cards_positions = np.array([(card.row * 5 + card.col + 1)/25 if card != 0 else 0 for card in self.current_cards])
        hand = np.array([1 if card != 0 else 0 for card in self.hand])
        hand_positions = np.array([(card.hand_position + 1)/3 if card != 0 else 0 for card in self.hand])
        #TODO: have synergies updated after every action?
        self.update_syns()
        synergies = np.array(self.syns) / 6
        elixir = np.array([self.elixir/100])
        max_placement = np.array([self.max_placement/10])
        state = np.concatenate([cards, cards_positions, hand, hand_positions, synergies, elixir, max_placement])
        return state
    
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
        if card1 not in self.CARDS or card2 not in self.CARDS or card3 not in self.CARDS:
            print('Card(s) not found!')
            return False
        
        self.hand = [0 for _ in range(int(self.N_CARDS / 4))]
        card_1 = LeveledCard(self.CARDS[card1], 1, -1, -1, 0)
        card_2 = LeveledCard(self.CARDS[card2], 1, -1, -1, 1)
        card_3 = LeveledCard(self.CARDS[card3], 1, -1, -1, 2)
        self.hand[int(card_1.get_index() / 4)] = card_1
        self.hand[int(card_2.get_index() / 4)] = card_2
        self.hand[int(card_3.get_index() / 4)] = card_3
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
        self.current_cards[level_card.get_index()] = level_card
        return True
        
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
        self.current_cards[level_card.get_index()] = level_card
        return True
    
    def update_syns(self) -> tuple[bool, int]:
        old_syns = self.syns.copy()
        
        self.syns = [0 for _ in range(self.N_SYNS)]
        card_set = set()
        for row in range(self.ROWS - 1):
            for col in range(self.COLS):
                if self.map[row][col] != 0:
                    card_set.add(self.map[row][col].card)
                    
        for card in card_set:
            self.syns[card.synergy1.value] += 1
            self.syns[card.synergy2.value] += 1
            
        net = 0
        for old_syn, new_syn in zip(old_syns, self.syns):
            if old_syn < new_syn and new_syn >= 2:
                net += 1
            elif old_syn > new_syn and old_syn >= 2:
                net -= 1
        
        reward = 0
        if net > 0:
            reward = 5
        if net < 0:
            reward = -5
            
        return (True, reward)
    
    def print_state(self):
        print('')
    
    def print_map(self):
        print('[')
        for row in range(self.ROWS):
            row_str = []
            for col in range(self.COLS):
                cell = self.map[row][col]
                if cell == 0:  
                    row_str.append(' 0')
                else:
                    row_str.append(f'{str(cell.card.name)} {str(cell.level)}')
            print(' '.join(row_str))
        print(']')
        
    #for simplicity of game actions
    def move_to_front(self, old_row: int, old_col: int) -> tuple[bool, int, int, int]:
        #find first open spot, if nothing is open just replace the first slot
        r, c = 0, 0
        for col in range(self.COLS):
            if self.map[r][col] == 0:
                c = col
                break
        
        b, reward = self.move_card(old_row, old_col, r, c)
        return (b, r, c, reward)
    
    def move_to_back(self, old_row: int, old_col: int) -> tuple[bool, int, int, int]:
        #find first open spot, if nothing is open just replace the first slot
        r, c = self.ROWS-2, 0
        for col in range(self.COLS):
            if self.map[r][col] == 0:
                c = col
                break
        
        b, reward = self.move_card(old_row, old_col, r, c)
        return (b, r, c, reward)
    
    def move_to_bench(self, old_row: int, old_col: int) -> tuple[bool, int, int, int]:
        #find first open spot, if nothing is open just replace the first slot
        r, c = self.ROWS-1, 0
        for col in range(self.COLS):
            if self.map[r][col] == 0:
                c = col
                break
        
        b, reward = self.move_card(old_row, old_col, r, c)
        return (b, r, c, reward)