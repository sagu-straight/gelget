import urllib.request 
from PIL import Image
from sys import argv
from os.path import exists
from io import BytesIO
from bs4 import BeautifulSoup as bs

url = "https://gelbooru.com/index.php?page=post&s=list&tags="
tags = argv[1:]
for tag in tags:
    url += f"{tag}+"

print(url)

images_saved = 0
i = 0
while True:
    search_page = urllib.request.urlopen(f"{url}&pid={i}")
    search_html = bs(search_page, "html.parser")

    pic_page_url = search_html.find("article").find("a")["href"]
    pic_page = urllib.request.urlopen(pic_page_url)
    pic_page_html = bs(pic_page, "html.parser")

    pic_url = pic_page_html.find("picture").find("img")["src"]
    pic_data = urllib.request.urlopen(pic_url).read()
    img = Image.open(BytesIO(pic_data))
    img.show()

    # ask for user input for confirmation before saving and/or filename

    filename = ""
    inp = "" # user input

    urllib.request.urlretrieve(pic_url, filename)
    

    i += 1
