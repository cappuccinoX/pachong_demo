import requests
import random
from bs4 import BeautifulSoup
import os
from datetime import datetime
from urllib.request import urlretrieve
import xlsxwriter
from io import BytesIO
from urllib.request import urlopen
import PIL.Image as im
from tqdm import tqdm


# 伪装请求
user_agents_pool = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7',
    'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0',
]

def top_movie():
    headers = {
        "User-Agent": random.choice(user_agents_pool)
    }
    r = requests.get("https://movie.douban.com/coming?sequence=asc", headers = headers)
    bs = BeautifulSoup(r.text, "lxml")
    html = bs.find("div", attrs = {"class": "article"}).find("tbody")
    rows = html.find_all("tr")
    movies = list()
    print("获取电影信息")
    for row in tqdm(rows):
        cells = row.find_all("td")
        movie_info = list()
        # 上映时间
        movie_info.append(cells[0].text.strip())
        # 电影名称
        movie_info.append(cells[1].text.strip())
        # 类型
        movie_info.append(cells[2].text.strip())
        # 国家/地区
        movie_info.append(cells[3].text.strip())
        # 热度
        movie_info.append(cells[4].text.strip())
        # 电影详情链接
        details_link = cells[1].find("a").get("href")
        movie_info.append(details_link)
        details = movie_details(details_link)
        # 主演
        movie_info.append(details["starring"])
        # 海报信息
        movie_info.append({"image_url": details["image_url"]})
        movies.append(movie_info)
    print("电影信息获取完成")
    save_excel(movies)

def movie_details(details_link):
    try:
        details = {}
        r = requests.get(details_link, headers = {
            "User-Agent": random.choice(user_agents_pool)
        })
        bs = BeautifulSoup(r.text, "lxml")
        # 海报
        img = bs.find("a", attrs = {"class": "nbgnbg"}).find("img")
        img_link = img.get("src")
        # 主演
        starring = bs.find("span", attrs = {"class": "actor"})
        if starring is not None:
            starring = bs.find("span", attrs = {"class": "attrs"}).text
        else:
            starring = "暂无主演信息"
        details["image_url"] = img_link
        details["starring"] = starring
        return details
    except Exception as e:
        print(f"获取详情报错: {e}, 详情链接: {details_link}")

def save_excel(data):
    try:
        print("开始写入excel")
        dir_name = os.path.abspath("douban")
        workbook = xlsxwriter.Workbook(
            filename = f"{dir_name}/即将上映的电影.xlsx",
            options = {
                'default_format_properties': {
                    "font_size": 20,
                    "text_wrap": True, # 单元格自动换行
                    "align": "center",
                    "valign": "vcenter"
                }
            }
        )
        sheet1 = workbook.add_worksheet("即将上映的电影")
        col = ("上映时间", "电影名称", "类型", "国家/地区", "想看", "详情链接", "主演", "海报")
        sheet1.set_column(0, len(col) - 1, 25)

        title = str(datetime.today()).split(' ')[0]
        title = f"统计日期: {title}"
        sheet1.merge_range(0, 0, 0, 7, title)

        for idx, name in enumerate(col):
            sheet1.set_row(idx, 100)
            sheet1.write(1, idx, name)

        for row_no, row in tqdm(enumerate(data)):
            for idx, content in enumerate(row):
                sheet1.set_row(row_no + 2, 100)
                if idx == len(row) - 1:
                    sheet1.insert_image(
                        row_no + 2,
                        idx,
                        content["image_url"],
                        {
                            "image_data": BytesIO(urlopen(content["image_url"]).read()),
                            "x_offset": 0,
                            "y_offset": 0,
                            "x_scale": 0.3, # 水平缩放
                            "y_scale": 0.3, # 垂直缩放
                        }
                    )
                else:
                    sheet1.write(row_no + 2, idx, content)

        workbook.close()
        print("excel写入完成")
    except Exception as e:
        print(f"生成excel报错: {e}")
        


if __name__ == "__main__":
    top_movie()