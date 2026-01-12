import time

from edge import DetectEdge
from control import Control, control
from config import Config

config = Config.load_from_json('./configs/pc.json')
control = Control(
    config.screen_bounds.left,
    config.screen_bounds.top,
    config.screen_bounds.right,
    config.screen_bounds.bottom
)
check_edge = DetectEdge(control, config.click_points.board, 5, 10)

while True:
    time.sleep(1)
    screenshot = control.screenshot()
    board = check_edge.detect_edges(screenshot)
    print(board)

