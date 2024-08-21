import requests
import os
from bs4 import BeautifulSoup

base_url = "https://www.gamekee.com"
url = "https://www.gamekee.com/gakumas"

# 主页soup
def make_base_soup(url):
    r = requests.get(url) 
    return BeautifulSoup(r.text, "html.parser")

# 下载一张图
def download_img(file_name, image_uri):
    print("downloading ", image_uri)
    img_data = requests.get(image_uri).content
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, 'wb') as f:
        f.write(img_data)

# 洗一下src
def draw_src(src):
    #存在编辑出错的src
    if src.startswith("///"):
        src=src[1:]
    return "https:"+src



############################# S卡部分 ##########################
# S卡链接
def get_s_entries(soup):
    group_nodes = soup.find_all(name="div",attrs={"class":"item-wrapper icon-size-3 pc-item-group gakumas-item-group"})
    s_entries = group_nodes[-1].find_all("a", href=True,title=True)
    return list(map(lambda a:{"title":a["title"], "url":base_url+a["href"]},s_entries))

# 获取cover的uri
def get_cover_path(entry_url):
    print("requesting ",entry_url)
    r = requests.get(entry_url)
    soup = BeautifulSoup(r.text,"html.parser")
    editor_node = soup.find(name="img",attrs={"class":"preview-image"},src=True)
    src = editor_node["src"]
    return draw_src(src)

# 主函数
def download_s_covers(soup):
    target_dir = "./download/supports"
    entries = get_s_entries(soup)
    list(
        map(lambda x:download_img(os.path.join(target_dir,x["title"]+".png"),x["uri"]),
            map(lambda x:{"title":x["title"],"uri":get_cover_path(x["url"])},
                entries)))

############################# S卡部分END ##########################


############################# P卡部分 ##########################
# P卡链接
def get_p_entries(soup):
    group_nodes = soup.find_all(name="div",attrs={"class":"item-wrapper icon-size-7 pc-item-group gakumas-item-group"})
    s_entries = group_nodes[2].find_all("a", href=True,title=True)
    return list(map(lambda a:{"title":a["title"], "url":base_url+a["href"]},s_entries))

# 获取P卡封面地址与标题
def get_idol_path(entry_url):
    print("requesting ",entry_url)
    r = requests.get(entry_url)
    soup = BeautifulSoup(r.text,"html.parser")
    tab_container = soup.find_all(name="div",attrs={"class":"tab-container"})[0]
    title_nodes = tab_container.find_all(name="div",attrs={"class":"tab-item"})
    panel_nodes = tab_container.find_all(name="div",attrs={"class":"tab-panel"})
    if len(title_nodes)!=len(panel_nodes):
        return []
    try:
        titles = list(
            map(lambda x:x.find(name="div",title=True)["title"], title_nodes)
            )
        srcs = list(
            map(lambda x:x.find(name="img",src=True)["src"], panel_nodes)
            )
    except Exception as e:
        return []
    srcs = list(map(lambda x:draw_src(x),srcs))
    zips = list(filter(lambda x: not x[1].endswith(".gif"), zip(titles, srcs)))
    return zips

def download_idol_cards(idol_uris):
    target_dir = os.path.join("./download/idols", idol_uris["title"])
    list(
        map(lambda x:download_img(os.path.join(target_dir,x[0]+".png"), x[1]),idol_uris["uris"])
    )
# 主函数
def download_p_cards(soup):
    entries = get_p_entries(soup)
    list(
        map(lambda x:download_idol_cards({"title":x["title"],"uris":get_idol_path(x["url"])}),
            entries))
############################# P卡部分END ##########################

if __name__ == "__main__":
    soup = make_base_soup(url)
    download_s_covers(soup)
    download_p_cards(soup)
    print("main")
