# coding=utf-8
from numpy.random import rand
from selenium import webdriver
from time import sleep
import requests
import random
import json
import os
from tqdm import tqdm
import re
import matplotlib.pyplot as plt
import matplotlib
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
import time

file = "%s/jobs.json" % os.path.abspath("boss")
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

headers = {
    "user-agent": random.choice(user_agents_pool),
}

def jobs():
    driver = webdriver.Chrome()
    # BOSS直聘----长沙软件测试岗位招聘
    driver.get("https://www.zhipin.com/job_detail/?query=%E8%BD%AF%E4%BB%B6%E6%B5%8B%E8%AF%95&city=101250100&industry=&position=")
    driver.maximize_window()
    def next_page_enabled():
        try:
            driver.find_element_by_class_name("page").find_element_by_class_name("disabled")
        except NoSuchElementException as e:
            return True
        return False

    def get_all_jobs(jobs, page_index):
        try:
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "job-list")))
            job_list = driver.find_element_by_class_name("job-list").find_elements_by_tag_name("li")
            print(f"开始获取第{page_index}页工作信息")
            for item in tqdm(job_list):
                company_info = item.find_element_by_class_name("company-text")
                company_name = company_info.find_element_by_tag_name("h3").text
                company_details = company_info.find_element_by_tag_name("p")
                company_type = company_details.find_element_by_tag_name("a").text
                company_scale = company_details.text

                job_name = item.find_element_by_class_name("job-name").text
                job_url = item.find_element_by_class_name("job-name").find_element_by_tag_name("a").get_attribute("href")
                job_area = item.find_element_by_class_name("job-area-wrapper").text
                salary = item.find_element_by_class_name("red").text

                job = {
                    "company_name": company_name,
                    "company_type": company_type,
                    "company_scale": company_scale,
                    "job_name": job_name,
                    "job_area": job_area,
                    "salary": salary,
                    "job_url": job_url
                }
                jobs.append(job)
            if next_page_enabled():
                next_btn = driver.find_element_by_class_name("next")
                next_btn.click()
                page_index = page_index + 1
                return get_all_jobs(jobs, page_index)
            else:
                return jobs
        except TimeoutException as e:
            now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
            screenshots_path = "%s/screenshots/failure/%s.png" % (os.path.abspath("boss"), now)
            driver.save_screenshot(screenshots_path)
            print(f"job-list不可见, 截图: {now}.png")
    
    jobs = get_all_jobs(jobs = [], page_index = 1)

    with open(file, "w") as data:
        data.write(json.dumps(jobs, ensure_ascii = False))

def cal_area_salay(area, data):
    salary_re = r"(.*)(k|K)(.*)"
    useless_salary_re = r"(.*/)([\u4E00-\u9FA5]+)(.*)" # 日薪匹配
    count_less_than_5k = 0
    count_5to10 = 0
    count_11to15 = 0
    count_16to20 = 0
    count_more_than_20 = 0
    try:
        for job in data:
            
            if re.match(useless_salary_re, job["salary"]) != None:
                # 跳过日薪岗位, 不计入统计范围内
                continue
            # "13-26K·13薪", 正则匹配得到 [('13-26', 'K', '·13薪')]
            salary_range = re.findall(salary_re, job["salary"])[0][0]
            min_salary = None
            max_salary = None

            salary_range = salary_range.split("-")
            if len(salary_range) == 1:
                min_salary = max_salary = int(salary_range)
            elif len(salary_range) == 2:
                min_salary = int(salary_range[0])
                max_salary = int(salary_range[1])       

            unpack_area = job["job_area"].split("·")
            area_name = None
            if len(unpack_area) == 1 :
                area_name = "其他"
            else:
                area_name = unpack_area[1]        
            if area in area_name and max_salary < 5:
                count_less_than_5k = count_less_than_5k + 1
            elif area in area_name and max_salary <= 10:
                if min_salary >= 5:
                    count_5to10 = count_5to10 + 1
                else:
                    count_5to10 = count_5to10 + 1
                    count_less_than_5k = count_less_than_5k + 1
            elif area in area_name and max_salary <= 15:
                if min_salary >= 11:
                    count_11to15 = count_11to15 + 1
                else:
                    count_5to10 = count_5to10 + 1
                    count_11to15 = count_11to15 + 1
            elif area in area_name and max_salary <= 20:
                if min_salary >= 16:
                    count_16to20 = count_16to20 + 1
                else:
                    count_16to20 = count_16to20 + 1
                    count_11to15 = count_11to15 + 1
            elif area in area_name and max_salary >= 21:
                count_more_than_20 = count_more_than_20 + 1
    except Exception as e:
        print(f"{job}")
    return [count_less_than_5k, count_5to10, count_11to15, count_16to20, count_more_than_20]

# 长沙各区薪资对比柱状图
def draw_bar():
    plt.rcParams['font.sans-serif']=['SimHei']
    plt.rcParams['axes.unicode_minus']=False
    plt.title('Tester salary in changsha')
    try:
        data = None
        with open(file, "r") as file_data:
            data = json.loads(file_data.read())
        
        x_name = ["less than 5k", "5-10k", "11-15k", "16-20k", "more than 20k"]
        x = list(range(len(x_name)))
        area_salary = []
        for area in tqdm(["岳麓", "开福", "雨花", "芙蓉", "天心", "长沙县", "望城", "其他"]):
            area_salary.append(cal_area_salay(area, data))
        # area_salary 分别为岳麓，开福，雨花，芙蓉，天心，长沙县，望城，其他地区的薪资统计
        print(area_salary)
        total_width, n = 0.8, 8
        width = total_width / n    

        yuelu_rects = plt.bar(x, area_salary[0], width = width, label = "yuelu", tick_label = x_name, fc = 'y')
        for i in range(len(x)):
            x[i] = x[i] + width

        kaifu_rects = plt.bar(x, area_salary[1], width = width, label = "kaifu", fc = 'r')
        for i in range(len(x)):
            x[i] = x[i] + width

        yuhua_rects = plt.bar(x, area_salary[2], width = width, label = "yuhua", fc = 'b')
        for i in range(len(x)):
            x[i] = x[i] + width

        furong_rects = plt.bar(x, area_salary[3], width = width, label = "furong", fc = 'g')
        for i in range(len(x)):
            x[i] = x[i] + width

        tianxin_rects = plt.bar(x, area_salary[4], width = width, label = "tianxin", fc = 'peru')
        for i in range(len(x)):
            x[i] = x[i] + width

        changshaxian_rects = plt.bar(x, area_salary[5], width = width, label = "changshaxian", fc = 'c')
        for i in range(len(x)):
            x[i] = x[i] + width

        wangcheng_rects = plt.bar(x, area_salary[6], width = width, label = "wangcheng", fc = 'm')
        for i in range(len(x)):
            x[i] = x[i] + width

        others_rects = plt.bar(x, area_salary[7], width = width, label = "others", fc = 'skyblue')

        def set_label(rects):
            for rect in rects:
                height = rect.get_height() # 获取⾼度
                plt.text(x = rect.get_x() + rect.get_width()/2, # ⽔平坐标
                        y = height + 0.5, # 竖直坐标
                        s = height, # ⽂本
                        ha = 'center') # ⽔平居中
        for area in [yuelu_rects, kaifu_rects, yuhua_rects, furong_rects, tianxin_rects, changshaxian_rects, wangcheng_rects, others_rects]:
            set_label(area)
        plt.tight_layout() # 紧凑布局
        plt.legend()
        root_dir = os.path.abspath("boss")
        now = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
        results_img = "%s/screenshots/results/薪资统计_%s.png" % (root_dir, now)
        plt.savefig(results_img)
        # plt.show()
    except Exception as e:
        print(e)



if __name__ == "__main__":
    draw_bar()