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
images_shown = 0
i = 0

output_string = "%s__%u"

help_text = f"""
to use the script, do:
python {argv[0]} [ OPTIONS ] [ TAGS ]
(tags just like the gelbooru search bar)

The following options are available:
--skip=X   skips X images. Useful for resuming a search
--o=X      specifies de Output filename formatting
--help     prints this message 

Output filename formatting:
Specified with a string using certain special symbols.
The symbols are:
    %a --> gets replaced by all the Artist tags
    %p --> gets replaced by all the coPyright tags
    %c --> gets replaced by all the Character tags
    %s --> gets replaced by all the Search tags
    %u --> gets replaced by the identifying part of the picture's url
You may also append a number to the %s symbol:
    %sN --> gets replaced by the Nth Search tag, if it exists

The default string is %s__%u

little tip: using the %u symbol ensures you never have repeated filenames

The file extension is not affected by the string, and always
reflects the actual filetype.

　　 _,,....,,_　 ＿人人人人人人人人人人人人人人人＿
-''":::::::::::::｀''＞　　　ゆっくりしていってね！！！　　　＜
ヽ:::::::::::::::::::::￣^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^Ｙ^￣
　|::::::;ノ´￣＼:::::::::::＼_,.    　　　＿_　　 _____　　 ＿_____
　|::::ﾉ　　　ヽ､ヽr-r'"´　　（.__　　  　,´　_,, '-´￣￣｀-ゝ 、_ イ、
_,.!イ_　　_,.ﾍｰｧ'二ﾊ二ヽ､へ,_7　　　'r  ´　　　　　　　　　　ヽ、ﾝ、
::::::rｰ''7ｺ-‐'"´　 　 ;　 ',　｀ヽ/｀7 ,'＝=─-　　　 　 -─=＝',　i
r-'ｧ'"´/　 /!　ﾊ 　ハ　 !　　iヾ_ﾉ　i　ｲiゝ、ｲ人レ／_ルヽｲ i　|
!イ´ ,' |　/__,.!/　V　､!__ﾊ　 ,'　,ゝ 　ﾚﾘｲi (ﾋ_] 　　 　ﾋ_ﾝ ).| .|、i .||
`! 　!/ﾚi'　(ﾋ_] 　　 　ﾋ_ﾝ ﾚ'i　ﾉ　　    　!Y!""　 ,＿__, 　 "" 「 !ﾉ i　|
,'　 ﾉ 　 !'"　 　 ,＿__,　 "' i .ﾚ'　　　　L.',.　 　ヽ _ﾝ　　　　L」 ﾉ| .|
　（　　,ﾊ　　　　ヽ _ﾝ　 　人! 　　　　   | ||ヽ、　　　　　　 ,ｲ| ||ｲ| /
,.ﾍ,）､　　）＞,､ _____,　,.イ　 ハ　　   　　レ ル｀ ー--─ ´ルﾚ　ﾚ´

"""

start_help_text = """
options in uppercase letters are the default, just pressing enter is the same as choosing them
close the image viewer before choosing to save or not
ctrl + c to quit

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
            print("Give a different name for the file. Without the extension")
            new_name = input()
            # flexing a recursive function where its not really needed
            try_save(img, new_name, file_extension)
            
    

# this is very poorly written and does a lot of redundant string operations
# if the script is feeling slow consider improving this :)
def create_ideal_name(html, search_tags, url, string):
    artists_objects = html.find_all(class_="tag-type-artist")
    artists = ""
    for artist in artists_objects:
        artists += artist.find("a", recursive=False).get_text().replace(" ","_")
        if artists_objects.index(artist) != len(artists_objects) - 1:
            artists += "_"

    copyright_objects = html.find_all(class_="tag-type-copyright")
    copyrights = ""
    for copyright in copyright_objects:
        copyrights += copyright.find("a", recursive=False).get_text().replace(" ","_")
        if copyright_objects.index(copyright) != len(copyright_objects) - 1:
            copyrights += "_"

    character_objects = html.find_all(class_="tag-type-character")
    characters = ""
    for character in character_objects:
        characters += character.find("a", recursive=False).get_text().replace(" ","_")
        if character_objects.index(character) != len(character_objects) - 1:
            characters += "_"

    identifying_string = url[url.rfind("/") + 1 : url.rfind(".")]

    joined_search_tags = ""
    for tag in search_tags:
        joined_search_tags += tag
        if search_tags.index(tag) != len(search_tags) - 1:
            joined_search_tags += "_"


    for i in range(1, len(search_tags)):
        string = string.replace(f"%s{i}", search_tags[i - 1])
        
    string = string.replace("%s", joined_search_tags)
    string = string.replace("%c", characters)
    string = string.replace("%p", copyrights)
    string = string.replace("%a", artists)
    string = string.replace("%u", identifying_string)

    return string

def quit():
    global images_shown
    global images_saved
    global i
    
    if images_shown == 0:
        print("no images found at all, nobody here but us chickens")
    else:
        print(f" showed {images_shown} images, downloaded {images_saved}.")
        print(f"If you want to continue where you stopped, run with --skip={i-1}")
    exit(0)

def int_handler(sig, frame):
    quit()
signal.signal(signal.SIGINT, int_handler)

if len(argv) < 2:
    print(help_text)
    exit(1)

url = "https://gelbooru.com/index.php?page=post&s=list&tags="

args = argv[1:]
search_tags = []
for arg in args:
    if arg.startswith("--"):
        if arg.startswith("--skip="):
            i = int(arg[arg.find("=")+1:])
        elif arg.startswith("--o="):
            output_string = arg[arg.find("=")+1:]
        elif arg == "--help":
            print(help_text)
            exit(0)
        else:
            print(f"Unrecognized option {arg}. Ignoring...")
    else:
        url += f"{arg}+"
        search_tags.append(arg)

print(start_help_text)

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
        images_shown += 1

        if input("do you want to save it? (Y/n) ") != "n":
            # resolve filename
            file_extension = pic_url[pic_url.rfind("."):]
            filename = create_ideal_name(html=pic_page_html, string=output_string, url=pic_url, search_tags=search_tags)
            inp = input(f"should i save the image in {filename}{file_extension}? (Y/n) ")
            if inp == "n":
                print("give a different name, without the extension")
                filename = input()
            try_save(img, filename, file_extension)

        tmp_file.close()

