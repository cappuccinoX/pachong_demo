import requests
import random
from bs4 import BeautifulSoup
import xlwt
import os
from datetime import datetime
from urllib.request import urlretrieve
import xlsxwriter

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
    for row in rows:
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
        movie_info.append(cells[1].find("a").get("href"))
        movies.append(movie_info)
    save_excel(movies)

def save_excel(data):
    dir_name = os.path.abspath("douban")
    workbook = xlsxwriter.Workbook(f"{dir_name}/即将上映的电影.xls")
    sheet1 = workbook.add_worksheet("即将上映的电影")

    t_prpos = title_prpos()
    sheet1.write_merge(0, 0, 0, 8, t_prpos["msg"], style = t_prpos["style"])

    col = ("上映时间", "电影名称", "类型", "国家/地区", "想看", "详情链接")

    for idx, name in enumerate(col):
        sheet1.write(1, idx, name)

    for row_no, row in enumerate(data):
        for idx, content in enumerate(row):
            sheet1.write(row_no + 2, idx, content)

    workbook.save(f"{dir_name}/即将上映的电影.xls")

def title_prpos():
    style = xlwt.XFStyle()
    al = xlwt.Alignment()
    al.horz = 0x02 # 水平居中
    al.vert = 0x02 # 垂直居中
    style.alignment = al

    font = xlwt.Font()
    font.bold = True # 字体加粗
    font.height = 20*14 # 字体大小，18为字号，20为衡量单位
    style.font = font

    title = str(datetime.today()).split(' ')[0]
    title = f"统计日期: {title}"
    return {"msg": title, "style": style}
    

def get_movie_details(url):
    headers = {
        "User-Agent": random.choice(user_agents_pool)
    }
    r = requests.get(url, headers = headers)
    bs = BeautifulSoup(r.text, "lxml")
    

from io import BytesIO
from urllib.request import urlopen
import PIL.Image as im

if __name__ == "__main__":
    # top_movie()
    # save_excel([])
    headers = {
        "User-Agent": random.choice(user_agents_pool)
    }
    r = requests.get("https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2640236255.webp", headers = headers)
    urlretrieve("https://img9.doubanio.com/view/photo/s_ratio_poster/public/p2640236255.webp", "aa.png")

    workbook = xlsxwriter.Workbook('images.xlsx')
    worksheet = workbook.add_worksheet()
    
    a=im.open("aa.png")
    a.save("jj.png")
    # https://blog.csdn.net/AuserBB/article/details/79259328 xlsxwriter 插入图片
    # https://www.jianshu.com/p/c87edf948658 xlsxwriter 常用方法
    worksheet.insert_image(0, 0, 'jj.png', {'x_offset': 0, 'y_offset': 0, 'x_scale': 0.3, 'y_scale': 0.3})
    workbook.close()

    