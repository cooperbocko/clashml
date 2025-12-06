from PIL import Image

from image_match import ImageMatch

cardmatch = ImageMatch('./card_match_db.npz', './images/cards')

card = Image.open('./debug/1/2/battle/cards_10_2025-11-30 12:47:08.354576.png')

print(cardmatch.match(card))