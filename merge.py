from dataclasses import dataclass
from enum import Enum

@dataclass
class Card:
    base_cost: int
    faction: str
    synergy: str
    
@dataclass 
class LeveledCard:
    card: Card
    level: int
    
    def get_cost(self):
        return (2 ** (self.level - 1)) * self.card.base_cost

class Faction(Enum):
    NOBEL = 'nobel'
    CLAN = 'clan'
    GOBLIN = 'goblin'
    UNDEAD = 'undead'
    ACE = 'ace'
    
class Synergy(Enum):
    JUGGERNAUT: 'juggernaut'
    BRAWLER: 'brawler'
    RANGER: 'ranger'
    ASSASSIN: 'assassin'
    AVENGER: 'avenger'
    THROWER: 'thrower'

class Merge: 
    #all cards
    KNIGHT = Card(2, Faction.NOBEL, Synergy.JUGGERNAUT)
    PRINCE = Card(3, Faction.NOBEL, Synergy.BRAWLER)
    PRINCESS = Card(4, Faction.NOBEL, Synergy.RANGER)
    GOLDEN_KNIGHT = Card(5, Faction.NOBEL, Synergy.ASSASSIN)
    
    BARBARIAN = Card(2, Faction.CLAN, Synergy.BRAWLER)
    ARCHER = Card(2, Faction.CLAN, Synergy.RANGER)
    VALKYRIE = Card(3, Faction.CLAN, Synergy.AVENGER)
    ARCHER_QUEEN = (5, Faction.CLAN, Synergy.AVENGER)
    
    DART_GOBLIN = (3, Faction.GOBLIN, Synergy.RANGER)
    GOBLIN = (2, Faction.GOBLIN, Synergy.ASSASSIN)
    SPEAR_GOBLIN = (2, Faction.GOBLIN, Synergy.THROWER)
    GOBLIN_MACHINE = (4, Faction.GOBLIN, Synergy.JUGGERNAUT)
    
    SKELETON_GIANT = (3, Faction.UNDEAD, Synergy.BRAWLER)
    ROYAL_GHOST = (4, Faction.UNDEAD, Synergy.ASSASSIN)
    SKELETON_BOMBER = (2, Faction.UNDEAD, Synergy.THROWER)
    SKELETON_KING = (5, Faction.UNDEAD, Synergy.JUGGERNAUT)
    
    MEGA_KNIGHT = (4, Faction.ACE, Synergy.BRAWLER)
    EXECUTIONER = (3, Faction.ACE, Synergy.THROWER)
    PEKKA = (3, Faction.ACE, Synergy.JUGGERNAUT)
    BANDIT = (4, Faction.ACE, Synergy.AVENGER)
    
    #in play map
    #reserve cards list
    #cards in hand
    
    def __init__(self):
        