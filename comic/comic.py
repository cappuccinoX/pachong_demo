'''
网站：动漫之家
漫画：妖神记
'''

import requests
from bs4 import BeautifulSoup
import os
from tqdm import tqdm
import time
from urllib.request import urlretrieve
import re

def download_comic():
    # 保存漫画内容的根目录
    start_time = time.time()
    comic_path = os.path.abspath("comic")
    url = "https://www.dmzj.com/info/yaoshenji.html"
    r1 = requests.get(url)
    bs1 = BeautifulSoup(r1.text, 'lxml')
    # 找到所有章节目录
    ele_zj_list = bs1.find(attrs = {"class": "zj_list"})
    ele_tab_content_selected = ele_zj_list.find(attrs = {"class": "tab-content-selected"})
    charpters = ele_tab_content_selected.find(attrs = {"class": "list_con_li"})
    charpters = charpters.find_all("a")
    # 获取每个章节的内容
    for item in tqdm(charpters):
        try:
            charpter_name = item.text
            # if charpter_name in os.listdir('./comic/妖神记'):
            #     continue
            charpter_url = item.get("href")
            r2 = requests.get(charpter_url)
            bs2 = BeautifulSoup(r2.text, "lxml")
            # 正则匹配找到拼凑漫画图片链接所需的关键字段
            script = str(bs2.script)
            pics = re.findall("\d{13,14}", script)
            chapterpic_qian = re.findall("\|(\d{4})\|", script)[0]
            chapterpic_hou = re.findall("\|(\d{5})\|", script)[0]
            # 漫画链接有13和14位，这里采取末尾补0，方便排序
            for idx, pic in enumerate(pics):
                if len(pic) == 13:
                    pics[idx] = pics[idx] + "0"
            # 排序，避免后面获取到的漫画处于乱序状态
            pics = sorted(pics, key = lambda x: int(x))
            pic_base_url = "https://images.dmzj1.com/img/chapterpic"
            for pic in pics:
                if pic[-1] == '0':
                    url = f"{pic_base_url}/{chapterpic_qian}/{chapterpic_hou}/{pic[:-1]}.jpg"
                else:
                    url = f"{pic_base_url}/{chapterpic_qian}/{chapterpic_hou}/{pic}.jpg"
                if charpter_name not in os.listdir('./comic/妖神记'):
                    os.mkdir(f"./comic/妖神记/{charpter_name}")
                urlretrieve(url, "%s/妖神记/%s/%s.jpg" % (comic_path, charpter_name, pic))
        except Exception as e:
            print(f"下载章节: {charpter_name} 报错, 错误信息: {e}")
        continue
    end_time = time.time()
    duration = (end_time - start_time)/60
    duration = str(round(duration, 1))
    print("下载完成, 耗时: " + duration + " min")

if __name__ == "__main__":
    download_comic()
