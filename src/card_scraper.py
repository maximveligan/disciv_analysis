from PIL import Image
from PIL import ImageChops
import pytesseract

NAME_BOX = (165, 48, 724, 104)
VERIFIED_BOX = (6, 690, 99, 710)

def xiv_char_card_to_text(card):
    card_img = Image.open(card)
    character = pytesseract.image_to_string(card_img.crop(NAME_BOX).convert('L')).split()
    diff = ImageChops.difference(card_img.crop(VERIFIED_BOX).convert('L').point(lambda x: 255 if x > 200 else 0, mode='1'), Image.open(".\\verified.png"))
    verified = not diff.getbbox()
    
    first_name = character[0]
    last_name = character[1]
    server = character[2]
    world = character[3][1:-1]

    return {
        "first_name": first_name,
        "last_name": last_name,
        "server": server,
        "world": world,
        "verified": verified
    }