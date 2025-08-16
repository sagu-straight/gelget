import signal
from urllib.request import urlopen
from urllib.request import urlretrieve
from PIL import Image
from sys import argv
from os.path import exists
from io import BytesIO
from bs4 import BeautifulSoup as bs

images_saved = 0
i = 0

def try_save(img, filename, file_extention):
    global images_saved

    if not exists(f"{filename}{file_extension}"):
        img.save(f"{filename}{file_extension}")
        images_saved += 1
    else:
        print(f"File {filename}{file_extension} already exists. Overwrite it? (y/N)")
        overwrite = input()
        if overwrite == "y":
            img.save(f"{filename}{file_extension}")
            images_saved += 1
        else:
            print("Give a different name for the file, then. Without the extension")
            new_name = input()
            # we're recursive in this bitch
            try_save(img, new_name, file_extension)
            
    

def create_ideal_name(html):
    filename = ""

    artists = html.find_all(class_="tag-type-artist")
    for artist in artists:
        filename += artist.find("a", recursive=False).get_text().replace(" ","_")
        if artists.index(artist) < len(artists) - 1:
            filename += "_"

    filename += "__"

    copyrights = html.find_all(class_="tag-type-copyright")
    for copyright in copyrights:
        filename += copyright.find("a", recursive=False).get_text().replace(" ","_")
        if copyrights.index(copyright) < len(copyrights) - 1:
            filename += "_"

    filename += "__"

    characters = html.find_all(class_="tag-type-character")
    for character in characters:
        filename += character.find("a", recursive=False).get_text().replace(" ","_")
        if characters.index(character) < len(characters) - 1:
            filename += "_"

    return filename

def quit():
    print(f"showed {i} images and downloaded {images_saved}.")
    print(f"that means you owe sagu {images_saved} kisses")
    exit(0)

def int_handler(sig, frame):
    quit()
signal.signal(signal.SIGINT, int_handler)

if len(argv) < 2:
    print("Please give at least one tag to search for... baka")
    exit(1)

url = "https://gelbooru.com/index.php?page=post&s=list&tags="
tags = argv[1:]
for tag in tags:
    url += f"{tag}+"


print("options in uppercase letters are the default, just pressing enter is the same as choosing them")
print("close the image viewer before choosing to save or not")
print("ctrl + c to quit")

while True:
    search_page = urlopen(f"{url}&pid={i}")
    search_html = bs(search_page, "html.parser")

    try:
        pic_page_url = search_html.find("article").find("a")["href"]
        pic_page = urlopen(pic_page_url)
        pic_page_html = bs(pic_page, "html.parser")
    except:
        quit()

    pic_url = pic_page_html.find(name="a", string="Original image")["href"]

    pic_data = urlopen(pic_url).read()
    img = Image.open(BytesIO(pic_data))
    img.show()

    i += 1

    if input("do you want to save it? (Y/n) ") != "n":
        # resolve filename
        file_extension = pic_url[pic_url.rfind("."):]
        filename = create_ideal_name(html=pic_page_html)
        inp = input(f"should i save the image in {filename}{file_extension}? (Y/n) ")
        if inp == "n":
            print("FINE YOU BAKA give me a different name then, just without the extension")
            filename = input()
        try_save(img, filename, file_extension)

