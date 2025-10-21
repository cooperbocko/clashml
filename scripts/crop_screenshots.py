import cv2 
import os

#y coords: 600 - 670
#x coords: 43-99, 105-161, 167, 223

screenshot_path = 'images/game_screenshots/'
raw_path = 'images/raw_cards/'
count = 0
for filename in os.listdir(screenshot_path):
    image = cv2.imread(f"{screenshot_path}{filename}")
    if image is None:
        print('Erorr!')
        break
    cropped_image_1 = image[600:670, 43:99]
    cropped_image_2 = image[600:670, 105:161]
    #cropped_image_3 = image[600:670, 167:223]
    cv2.imwrite(f"{raw_path}{count}1.jpg", cropped_image_1)
    cv2.imwrite(f"{raw_path}{count}2.jpg", cropped_image_2)
    #cv2.imwrite(f"{raw_path}{count}3.jpg", cropped_image_3)
    count += 1
    
    if os.path.exists(f"{screenshot_path}{filename}"):
        os.remove(f"{screenshot_path}{filename}")