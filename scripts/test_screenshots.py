import cv2
from pyautogui import screenshot

screenshot_path = "./"
filename = "screenshot_pyautogui.png"
raw_path = "scripts/"
count = 1

image = cv2.imread("scripts/screenshot_pyautogui.png")
    
cropped_image_1 = image[782:874, 53:128]
cropped_image_2 = image[782:874, 134:209]
cropped_image_3 = image[782:874, 215:290]
cropped_image_4 = image[822:872, 308:356]
cropped_image_5 = image[355:386, 202:254]

#1 (53, 782, 128, 874)
#2 (134, 782, 209, 874)
#3 (215, 782, 290, 874)
#elixr (308, 822, 356, 872)
#palcement (202, 355, 254, 386)
cv2.imwrite(f"{raw_path}{count}1.jpg", cropped_image_1)
cv2.imwrite(f"{raw_path}{count}2.jpg", cropped_image_2)
cv2.imwrite(f"{raw_path}{count}3.jpg", cropped_image_3)
cv2.imwrite(f"{raw_path}{count}4.jpg", cropped_image_4)
cv2.imwrite(f"{raw_path}{count}5.jpg", cropped_image_5)