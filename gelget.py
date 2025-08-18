import signal
from urllib.request import urlopen
from urllib.request import urlretrieve
from PIL import Image
from sys import argv
from os.path import exists
from os import remove
from io import BytesIO
from bs4 import BeautifulSoup as bs

images_saved = 0
i = 0

help_text = f"""
Please give at least one tag to search for
to use the script do:
python {argv[0]} tag1 tag2 tag3 ...
(just like the gelbooru search bar)

　　 _,,....,,_　 ＿人人人人人人人人人人人人人人人＿
-''":::::::::::::｀''＞　　　ゆっくりしていってね！！！　　　＜
ヽ:::::::::::::::::::::￣^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^￣
　|::::::;ノ´￣＼:::::::::::＼_,.      　　　＿_　　 _____　　 ＿_____
　|::::ﾉ　　　ヽ､ヽr-r'"´　　（.__　　　  　,´　_,, '-´￣￣｀-ゝ 、_ イ、
_,.!イ_　　_,.ﾍｰｧ'二ﾊ二ヽ､へ,_7　　　'r    ´　　　　　　　　　　ヽ、ﾝ、
::::::rｰ''7ｺ-‐'"´　 　 ;　 ',　｀ヽ/｀7 　,'＝=─-　　　 　 -─=＝',　i
r-'ｧ'"´/　 /!　ﾊ 　ハ　 !　　iヾ_ﾉ　i　ｲ　iゝ、ｲ人レ／_ルヽｲ i　|
!イ´ ,' |　/__,.!/　V　､!__ﾊ　 ,'　,ゝ  　ﾚﾘｲi (ﾋ_] 　　 　ﾋ_ﾝ ).| .|、i .||
`! 　!/ﾚi'　(ﾋ_] 　　 　ﾋ_ﾝ ﾚ'i　ﾉ　　    　!Y!""　 ,＿__, 　 "" 「 !ﾉ i　|
,'　 ﾉ 　 !'"　 　 ,＿__,　 "' i .ﾚ'　　　　L.',.　 　ヽ _ﾝ　　　　L」 ﾉ| .|
　（　　,ﾊ　　　　ヽ _ﾝ　 　人! 　　　　   | ||ヽ、　　　　　　 ,ｲ| ||ｲ| /
,.ﾍ,）､　　）＞,､ _____,　,.イ　 ハ　　   　　レ ル｀ ー--─ ´ルﾚ　ﾚ´

files are saved with the following pattern by default:
artist1_artist2__copyright1_copyright2__character1_character2
"""

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
            # flexing a recursive function where its not really needed
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
    global i
    if i == 0:
        print("no images found at all, nobody here but us chickens")
    else:
        print(f"showed {i} images and downloaded {images_saved}.")
    exit(0)

def int_handler(sig, frame):
    quit()
signal.signal(signal.SIGINT, int_handler)

if len(argv) < 2:
    print(help_text)
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
        thumbnails = search_html.find("article").find_all("a")
    except:
        quit()

    for thumbnail in thumbnails:
        pic_page_url = thumbnail["href"]
        pic_page = urlopen(pic_page_url)
        pic_page_html = bs(pic_page, "html.parser")

        pic_url = pic_page_html.find(name="a", string="Original image")["href"]

        pic_data = urlopen(pic_url).read()
        tmp_file = BytesIO(pic_data)
        img = Image.open(tmp_file)
        img.show()

        i += 1

        if input("do you want to save it? (Y/n) ") != "n":
            # resolve filename
            file_extension = pic_url[pic_url.rfind("."):]
            filename = create_ideal_name(html=pic_page_html)
            inp = input(f"should i save the image in {filename}{file_extension}? (Y/n) ")
            if inp == "n":
                print("give a different name then, without the extension")
                filename = input()
            try_save(img, filename, file_extension)

        tmp_file.close()

