import time

from edge import DetectEdge
from control import Control
from config import Config

config = Config.load_from_json('./configs/pc.json')
control = Control(
    config.screen_bounds.left,
    config.screen_bounds.top,
    config.screen_bounds.right,
    config.screen_bounds.bottom,
    0.1
)
check_edge = DetectEdge(control, config.click_points.board, 20, 10)

while True:
    time.sleep(3)
    screenshot = control.screenshot()
    board = check_edge.detect_edges(screenshot)
    print(board)
    print()

