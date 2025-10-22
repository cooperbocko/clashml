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

class Merge: 
    #TODO: add method for recifying changes made from golden bubbles
    CARDS = {
    'KNIGHT' : Card(2, Synergy.NOBEL, Synergy.JUGGERNAUT, 0, True),
    'PRINCE' : Card(3, Synergy.NOBEL, Synergy.BRAWLER, 4, True),
    'PRINCESS' : Card(4, Synergy.NOBEL, Synergy.RANGER, 8, False),
    'GOLDEN_KNIGHT' : Card(5, Synergy.NOBEL, Synergy.ASSASSIN, 12, True),
    
    'ARCHER' : Card(2, Synergy.CLAN, Synergy.RANGER, 16, False),
    'VALKYRIE' : Card(3, Synergy.CLAN, Synergy.AVENGER, 20, True),
    'BARBARIAN' : Card(2, Synergy.CLAN, Synergy.BRAWLER, 24, True),
    'ARCHER_QUEEN' : Card(5, Synergy.CLAN, Synergy.AVENGER, 28, False),
    
    'DART_GOBLIN' : Card(3, Synergy.GOBLIN, Synergy.RANGER, 32, False),
    'GOBLIN' : Card(2, Synergy.GOBLIN, Synergy.ASSASSIN, 36, True),
    'SPEAR_GOBLIN' : Card(2, Synergy.GOBLIN, Synergy.BLASTER, 40, False),
    'GOBLIN_MACHINE' : Card(4, Synergy.GOBLIN, Synergy.JUGGERNAUT, 44, True),
    
    'SKELETON_GIANT' : Card(3, Synergy.UNDEAD, Synergy.BRAWLER, 48, True),
    'ROYAL_GHOST' : Card(4, Synergy.UNDEAD, Synergy.ASSASSIN, 52, True),
    'SKELETON_BOMBER' : Card(2, Synergy.UNDEAD, Synergy.BLASTER, 56, False),
    'SKELETON_KING' : Card(5, Synergy.UNDEAD, Synergy.JUGGERNAUT, 60, True),
    
    'MEGA_KNIGHT' : Card(4, Synergy.ACE, Synergy.BRAWLER, 64, True),
    'EXECUTIONER' : Card(3, Synergy.ACE, Synergy.BLASTER, 68, False),
    'PEKKA' : Card(3, Synergy.ACE, Synergy.JUGGERNAUT, 72, True),
    'BANDIT' : Card(4, Synergy.ACE, Synergy.AVENGER, 76, True),
    
    'ELECTRO_GIANT': Card(3, Synergy.ELECTRIC, Synergy.AVENGER, 80, True),
    'ELECTRO_WIZARD': Card(4, Synergy.ELECTRIC, Synergy.MAGE, 84, False),
    'WIZARD': Card(2, Synergy.FIRE, Synergy.MAGE, 88, False),
    'BABY_DRAGON': Card(4, Synergy.FIRE, Synergy.BLASTER, 92, False),
    
    'WITCH': Card(4, Synergy.UNDEAD, Synergy.AVENGER, 96, False),
    'SKELETON_DRAGON': Card(2, Synergy.UNDEAD, Synergy.RANGER, 100, False),
    'MUSKETEER': Card(3, Synergy.NOBEL, Synergy.BLASTER, 104, False)
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
        self.hand = [0 for _ in range(int(self.N_CARDS / 4))] #TODO: is this the best way to do this
        self.max_placement = 2
        self.syns = [0 for _ in range(self.N_SYNS)]
        
    def buy_card(self, card_posiiton: int) -> bool:
        card = None
        for hand_card in self.hand:
            if hand_card != 0 and hand_card.hand_position == card_posiiton:
                card = hand_card.card
        if card == None:
            print("Not a valid position")
            return False
        
        if card.base_cost > self.elixir:
            print("Not enough elixir!")
            return False
        
        return self.add_card(card)
    
    def sell_card(self, row: int, col: int) -> bool:
        if (row < 0 or row >= self.ROWS or col < 0 or col >= self.COLS):
            print("Not in bounds!")
            return False
        
        if (self.map[row][col] == 0):
            print("Nohting to sell!")
            return False
        
        level_card = self.map[row][col]
        self.current_cards[level_card.get_index()] = 0
        self.map[row][col] = 0
        print("Card sold!")
        self.update_syns()
        return True
    
    def move_card(self, oldrow: int, oldcol: int, newrow: int, newcol: int) -> bool:
        if (oldrow < 0 or oldrow >= self.ROWS or oldcol < 0 or oldcol >= self.COLS or newrow < 0 or newrow >= self.ROWS or newcol < 0 or newcol >= self.COLS):
            print("Not in bounds!")
            return False
        
        #check if there is a card to move
        if self.map[oldrow][oldcol] == 0:
            print('No card to move!')
            return False
        
        #check if moving from bench and moving to an open spot
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
        self.update_syns()
        return True
    
    def add_card(self, card: Card) -> bool:
        #check if it combines
        if(self.merge(card)):
            print("merged!")
            return True
                    
        #check for space on the board or on the bench
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
                    elif self.map[row][5] == 0:
                        card_location = (row, 5)
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
                    elif self.map[row][5] == 0:
                        card_location = (row, 5)
                        break
        
        #if card location is still not found check bench
        if card_location == (-1, -1):
            for col in range(self.COLS):
                if self.map[self.ROWS - 1][col] == 0:
                    card_location = (self.ROWS - 1, col)
                    break
        
        #actually add the card
        new_level_card = LeveledCard(card, 1, card_location[0], card_location[1])
        self.current_cards[new_level_card.get_index()] = new_level_card
        self.map[new_level_card.row][new_level_card.col] = new_level_card
        print("Card Added!")
        self.update_syns()
        return True
    
    #TODO: # star into 4 star merge when 4 star is present exception
    def merge(self, card: Card) -> bool:
        if self.current_cards[card.base_index] == 0:
            return False #no merge
        
        highest_level_card = self.current_cards[card.base_index]
        for i in range(card.base_index, card.base_index + 4):
            if self.current_cards[i] != 0:
                #get highest level card and remove all cards that are merging
                highest_level_card = self.current_cards[i]
                self.current_cards[i] = 0
                self.map[highest_level_card.row][highest_level_card.col] = 0
            else:
                break
            
        #level card up and add it back to list and map
        highest_level_card.level = highest_level_card.level + 1
        self.current_cards[highest_level_card.get_index()] = highest_level_card
        self.map[highest_level_card.row][highest_level_card.col] = highest_level_card
        self.update_syns()
        return True
    
    def get_state(self) -> np.array:
        cards = np.array([1 if card != 0 else 0 for card in self.current_cards])
        cards_positions = np.array([card.row * 5 + card.col + 1 if card != 0 else 0 for card in self.current_cards])
        hand = np.array([1 if card != 0 else 0 for card in self.hand])
        hand_positions = np.array([card.hand_position if card != 0 else 0 for card in self.hand])
        #TODO: have synergies updated after every action?
        synergies = np.array(self.syns)
        elixir = np.array([self.elixir])
        max_placement = np.array([self.max_placement])
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
        self.update_syns()
        return True
    
    #not the most optimal approach but much cleaner code wise
    def update_syns(self) -> bool:
        self.syns = [0 for _ in range(self.N_SYNS)]
        card_set = set()
        for row in range(self.ROWS - 1):
            for col in range(self.COLS):
                if self.map[row][col] != 0:
                    card_set.add(self.map[row][col].card)
                    
        for card in card_set:
            self.syns[card.synergy1.value] += 1
            self.syns[card.synergy2.value] += 1
        return True
    
    def print_map(self):
        print('[')
        for row in range(self.ROWS):
            row_str = []
            for col in range(self.COLS):
                cell = self.map[row][col]
                if cell == 0:  
                    row_str.append(' 0')
                else:
                    row_str.append(f'{str(cell.card.synergy1)} {str(cell.card.synergy2)}')
            print(' '.join(row_str))
        print(']')
        
    #for simplicity of game actions
    def move_to_front(self):
        return
    def move_to_back(self):
        return
    def move_to_bench(self):
        return

    
        