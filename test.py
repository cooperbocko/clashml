from control import Control
from template import TemplateMatch
import cv2


level1_check = TemplateMatch(0.99, ['./images/level_template/level1.png'], False)
level2_check = TemplateMatch(0.99, ['./images/level_template/level2.png'], False)
level3_check = TemplateMatch(0.99, ['./images/level_template/level3.png'], False)

image = cv2.imread('debug/0/0/start/level_0_2025-12-10 12:37:41.119183.png')

print(level1_check.detect(image))
print(level2_check.detect(image))
print(level3_check.detect(image))
