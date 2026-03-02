from digits import DetectDigits
from PIL import Image

digits = DetectDigits(True, './models/best_digits.pt', './env.json')
img = Image.open('./debug/49/elixir_49.png')
print(digits.predict(img))
    


