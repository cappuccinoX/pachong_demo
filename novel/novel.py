'''
网站：新笔趣阁
小说：诡秘之主
'''
import requests
import json
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import time

from requests.api import request

def download_novel():
    start_time = time.time()
    dir_name = os.path.abspath("novel")
    file = f"{dir_name}\诡秘之主.txt"
    
    base_url = "http://www.ltoooo.com"
    url = "http://www.ltoooo.com/0_71/"
    r1 = requests.get(url)
    bs1 = BeautifulSoup(r1.text, 'lxml')
    charpters = bs1.find(attrs = {"class": "listmain"})
    # 获取诡秘之主目录
    charpters = charpters.find_all("a")

    for item in tqdm(charpters):
        name = item.string
        url = base_url + item.get("href")
        r2 = requests.get(url)
        html = r2.text
        bs2 = BeautifulSoup(html, 'lxml')
        texts = bs2.find("div", id = "content")
        texts = texts.text.strip().split("\xa0"*4)

        charpter_contents = ""
        for item in texts:
            if item != "":
                charpter_contents = charpter_contents + item.strip() + "\n"

        # 将每章内容写入文件
        with open(file, "a", encoding="utf-8") as data:
            data.write(name)
            data.write(charpter_contents)

    end_time = time.time()
    duration = (start_time - end_time)/60
    duration = str(round(duration, 1))
    print("下载完成, 耗时: " + duration + " min")
        
if __name__ == "__main__":
    download_novel()
