import pyautogui
import cv2
import numpy as np
import json

with open('./configs/mac_monitor_config.json', "r") as f:
    config = json.load(f)
    
click_points = config["click_points"]
main_board = click_points["board"]

image = cv2.imread('debug/2/3/battle/screenshot_23_2025-12-11 15:12:54.053526.png')
image2 = cv2.imread('debug/2/1/battle/screenshot_0_2025-12-11 15:11:11.576067.png')
image3 = cv2.imread('debug/1/1/battle/screenshot_0_2025-12-11 15:09:08.617466.png')
def overlay_points_on_screenshot(points, image):
    # 1. Take the screenshot
    # PyAutoGUI returns an RGB PIL image
    screenshot = image
    # 2. Convert PIL image to OpenCV format (BGR)
    frame = np.array(screenshot)
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    # 3. Overlay the points
    # Color is in BGR (0, 0, 255) is Bright Red
    color = (0, 0, 255) 
    thickness = -1  # -1 fills the circle
    radius = 10
    
    for row in range(5):
        for col in range(5):
            point = main_board[row][col]
            x = point[0]
            y = point[1]
            cv2.circle(frame, (x, y), radius, color, thickness)
            # Optional: Add a label or border to make it pop
            cv2.circle(frame, (x, y), radius + 2, (255, 255, 255), 2)

    # 4. Display the image
    cv2.imshow('Screenshot Overlay', frame)
    
    # Wait for any key press to close the window
    print("Image displayed. Press any key to close the window.")
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def onboard(image) -> list[list[int]]:
        img = image
        board = [[0 for _ in range(5)] for _ in range(5)]
        for row in range(5):
            for col in range(5):
                point = main_board[row][col]
                rgb = img[point[1], point[0]]
                print(rgb)
                board[row][col] = rgb[0]
                
def check_edges(image):
        image = np.array(image)
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edge_count = np.sum(edges > 0)
        
        return edge_count, edges
    
    
images = []
radius = 5

for row in range(5):
    z = ''
    for col in range(5):
        point = main_board[row][col]
        x, y = point[0], point[1]
        crop = image3[y-radius:y+radius, x-radius:x+radius]
        #cv2.imshow('crop', crop)
        #cv2.waitKey(0)
        count, edge_map = check_edges(crop)
        #cv2.imshow('edge map', edge_map)
        #print(f'# edges: {count}')
        #cv2.waitKey(0)
        z += ' ' + str(count)
    print(z)
    


