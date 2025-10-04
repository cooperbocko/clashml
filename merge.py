from dataclasses import dataclass
from enum import Enum

@dataclass
class Card:
    base_cost: int
    faction: int
    synergy: int
    base_index: int
    is_frontline: bool
    
@dataclass 
class LeveledCard:
    card: Card
    level: int
    
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
    JUGGERNAUT: 5
    BRAWLER: 6
    RANGER: 7
    ASSASSIN: 8
    AVENGER: 9
    THROWER: 10

class Merge: 
    #all card types
    CARDS = {
    'KNIGHT' : Card(2, Synergy.NOBEL, Synergy.JUGGERNAUT, 0, True),
    'PRINCESS' : Card(4, Synergy.NOBEL, Synergy.RANGER, 6, False),
    'GOLDEN_KNIGHT' : Card(5, Synergy.NOBEL, Synergy.ASSASSIN, 9, True),
    'PRINCE' : Card(3, Synergy.NOBEL, Synergy.BRAWLER, 3, True),
    
    'ARCHER' : Card(2, Synergy.CLAN, Synergy.RANGER, 15, False),
    'VALKYRIE' : Card(3, Synergy.CLAN, Synergy.AVENGER, 18, True),
    'BARBARIAN' : Card(2, Synergy.CLAN, Synergy.BRAWLER, 12, True),
    'ARCHER_QUEEN' : (5, Synergy.CLAN, Synergy.AVENGER, 21, False),
    
    'DART_GOBLIN' : (3, Synergy.GOBLIN, Synergy.RANGER, 24, False),
    'GOBLIN' : (2, Synergy.GOBLIN, Synergy.ASSASSIN, 27, True),
    'SPEAR_GOBLIN' : (2, Synergy.GOBLIN, Synergy.THROWER, 30, False),
    'GOBLIN_MACHINE' : (4, Synergy.GOBLIN, Synergy.JUGGERNAUT, 33, True),
    
    'SKELETON_GIANT' : (3, Synergy.UNDEAD, Synergy.BRAWLER, 36, True),
    'ROYAL_GHOST' : (4, Synergy.UNDEAD, Synergy.ASSASSIN, 39, True),
    'SKELETON_BOMBER' : (2, Synergy.UNDEAD, Synergy.THROWER, 42, False),
    'SKELETON_KING' : (5, Synergy.UNDEAD, Synergy.JUGGERNAUT, 45, True),
    
    'MEGA_KNIGHT' : (4, Synergy.ACE, Synergy.BRAWLER, 48, True),
    'EXECUTIONER' : (3, Synergy.ACE, Synergy.THROWER, 51, False),
    'PEKKA' : (3, Synergy.ACE, Synergy.JUGGERNAUT, 54, True),
    'BANDIT' : (4, Synergy.ACE, Synergy.AVENGER, 57, True)
    }
    #TODO: add new cards!
    
    #map size
    ROWS = 5
    COLS = 5
    
    HAND_SIZE = 3
    
    #TODO: update
    N_SYNS = 11
    
    #TODO: update
    #number of cards (3 * each unique card -> maybe I should include 4stars?)
    N_CARDS = 60
    
    #in play map
    #reserve cards list
    #cards in hand
    
    def __init__(self, starting_elixir, starting_card_info, starting_max_placement):
        #start from top -> (0,0) == top left
        self.map = [[0 for _ in range(self.ROWS)] for _ in range(self.COLS)]
        self.elixir = starting_elixir
        self.current_cards = [0 for _ in range(self.N_CARDS)]
        self.hand = [0 for _ in range(self.HAND_SIZE)]
        #TODO: add starting card
        self.max_placement = starting_max_placement
        self.factions = [0 for _ in range(self.N_FACTIONS)]
        self.syns = [0 for _ in range(self.N_SYNS)]
        
    def buy_card(self, card_posiiton):
        card = self.hand[card_posiiton]
        print("Buying: ",  card)
        
        if card.base_cost > self.elixir:
            print("Not enough elixir!")
            return
        
        #check if it combines TODO:recursion?
        if self.current_cards[card.base_index] != 0:
            if self.current_cards[card.base_index + 1] != 0:
                self.current_cards[card.base_index + 1] = 0
                self.current_cards[card.baes_index + 2] = 1
            else:
                self.current_cards[card.base_index + 1] = 1
            self.current_cards[card.base_index] = 0
            print("Merged!")
                    
        #check for space on the board or on the bench
        card_location = (-1, -1)
        n_cards_on_board = 0
        for row in range(self.ROWS - 1):
            for col in range(self.COLS):
                if self.map[row][col] != 0:
                    n_cards_on_board += 1
                
        if n_cards_on_board < self.max_placement:
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
                for row in range(self.ROWS - 1, -1, -1):
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
                    
        #check if board if full
        if card_location == (-1, -1):
            print("Board is full!")
            return
        
        #actually add the card
        new_level_card = LeveledCard(card, 1)
        self.current_cards[new_level_card.get_index()] = 1
        self.map[card_posiiton[0]][card_posiiton[1]] = new_level_card
        print("Card bought!")
        return
    
    
    def sell_card(self, row, col):
        if (row < 0 or row >= self.ROWS or col < 0 or col >= self.COLS):
            print("Not in bounds!")
            return
        
        if (self.map[row][col] == 0):
            print("Nohting to sell!")
            return
        
        level_card = self.map[row][col]
        self.current_cards[level_card.get_index()] = 0
        self.map[row][col] = 0
        print("Card sold!")
        return
    
    def move_card(self, oldrow, oldcol, newrow, newcol):
        return
    
    #for simplicity of game actions
    def move_to_front(self):
        return
    def move_to_back(self):
        return
    def move_to_bench(self):
        return
    def get_game_state(self):
        return
    
        