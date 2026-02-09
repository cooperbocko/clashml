from dataclasses import dataclass
from typing import List
import json

@dataclass
class SystemSettings:
    is_mac_laptop_screen: bool
    is_roboflow: bool
    env_path: str

@dataclass
class ScreenBounds:
    left: int
    top: int
    right: int
    bottom: int

@dataclass
class Regions:
    card_regions: List[List[int]]
    elixr_region: List[List[int]]
    placement_region: List[List[int]]
    card_picture_region: List[List[int]]
    card_level_region: List[List[int]]
    defeated_region: List[List[int]]
    play_again_region: List[List[int]]
    ok_region: List[List[int]]
    phase_region: List[List[int]]

@dataclass
class ClickPoints:
    board: List[List[List[int]]]
    hand: List[List[int]]
    battle: List[int]
    safe_click: List[int]
    end_bar: List[int]
    play_again: List[int]
    ok: List[int]
    menu_safe_click: List[int]

@dataclass
class Colors:
    end_colors: List[int]

@dataclass
class Config:
    system_settings: SystemSettings
    screen_bounds: ScreenBounds
    regions: Regions
    click_points: ClickPoints
    colors: Colors

    @classmethod
    def load_from_json(cls, file_path: str):
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        return cls(
            system_settings=SystemSettings(**data['system_settings']),
            screen_bounds=ScreenBounds(**data['screen_bounds']),
            regions=Regions(**data['regions']),
            click_points=ClickPoints(**data['click_points']),
            colors=Colors(**data['colors'])
        )