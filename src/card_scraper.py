from PIL import Image
from PIL import ImageChops
import pytesseract
import sys

NAME_BOX = (165, 48, 724, 104)
VERIFIED_BOX = (6, 690, 99, 710)

def xiv_char_card_to_text(card):
    card_img = Image.open(card)
    character = pytesseract.image_to_string(card_img.crop(NAME_BOX).convert('L')).split()
    diff = ImageChops.difference(card_img.crop(VERIFIED_BOX).convert('L').point(
        lambda x: 0 if x > 200 else 255, mode='1'), Image.open("./verified.jpg"))

    return {
        "first_name": character[0],
        "last_name": character[1],
        "server": character[2],
        "world": character[3][1:-1],
        "verified": not diff.getbbox()
    }

print(xiv_char_card_to_text(sys.argv[1]))