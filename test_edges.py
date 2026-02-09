import time
from PIL import Image, ImageDraw
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
check_edge = DetectEdge(control, config.click_points.board, 10, 15)


def draw_dot(draw, x, y, radius, color):
    left_up_point = (x - radius, y - radius)
    right_down_point = (x + radius, y + radius)
    draw.ellipse([left_up_point, right_down_point], fill=color)

# Example usage:
img = control.screenshot()
draw = ImageDraw.Draw(img)

for row in range(5):
    for col in range(5):
        point = config.click_points.board[row][col]
        draw_dot(draw, point[0], point[1], 2, 'red')

img.show()


screenshot = control.screenshot()
board = check_edge.detect_edges(screenshot)
print(board)
print()

