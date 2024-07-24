import requests
import os
from bs4 import BeautifulSoup

base_url = "https://www.gamekee.com"
target_dir = "./download"
url = "https://www.gamekee.com/gakumas"


def get_s_entries(url):
    r = requests.get(url) 
    soup = BeautifulSoup(r.text, "html.parser")
    group_nodes = soup.find_all(name="div",attrs={"class":"item-wrapper icon-size-3 pc-item-group gakumas-item-group"})
    s_entries = group_nodes[-1].find_all("a", href=True,title=True)
    return list(map(lambda a:{"title":a["title"], "url":base_url+a["href"]},s_entries))


def get_cover_path(entry_url):
    print("requesting ",entry_url)
    r = requests.get(entry_url)
    soup = BeautifulSoup(r.text,"html.parser")
    editor_node = soup.find(name="img",attrs={"class","preview-image"},src=True)
    src = editor_node["src"]
    # maybe /// path in document
    if src.startswith("///"):
        src=src[1:]
    return "https:"+src

def download_img(file_name, image_uri):
    print("downloading ",file_name)
    img_data = requests.get(image_uri).content
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'wb') as f:
        f.write(img_data)

if __name__ == "__main__":
    entries = get_s_entries(url)
    list(
        map(lambda x:download_img(os.path.join(target_dir,x["title"]+".png"),x["uri"]),
            map(lambda x:{"title":x["title"],"uri":get_cover_path(x["url"])},
                entries)))