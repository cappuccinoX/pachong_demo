'''
使用脚本时，需更换exam_code 以及 headers中的Cookie
'''
import requests
from bs4 import BeautifulSoup
import json
import os
import re
from tqdm import tqdm
import random

exam_code = "99B4DB72F120E3D41003"
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

# 一鱼两吃
def yi_yu_liang_chi():
    headers = {
        "Cookie": "think_language=zh-CN; visitkey=66de1372d602b5666346cd47d8; mcduid=10006; scode=ee44bc1461a60ab63ececa8ac21ca5b512dbd365; PHPSESSID=sti8jkegdtetl8sg21p94qoq51; exam_new_11896=1; new_version_online_exam_11896=1; x-host-key-front=1794061adda-4e67e7895ea85f53d5c29cfc0e9f43b2bf4456bc; x-host-key-ngn=1794061add9-d531bfa1eb390cdcd0d6ade53baad9eb7552b1d2",
        "User-Agent": random.choice(user_agents_pool)
    }
    # 获取花名册
    r = requests.get(f"https://wehr.qq.com/Center/Roster/roster_list?code={exam_code}&search=&status=-1&page_size=999&page_num=1", headers = headers)
    high_exam_links = list()
    low_exam_links = list()
    data = json.loads(r.text)
    data = data["data"]["detail"]
    print("开始获取花名册")
    for user in tqdm(data):
        # 根据花名册生成答题url
        url = f"https://wehr.qq.com/Center/Roster/generate_link_roster?code={exam_code}&id={user['id']}"
        generate_link_res = requests.get(url, headers = headers)
        generate_link_res = json.loads(generate_link_res.text)
        # 获取每份问卷code
        if re.match(r"gg", user["email"]) != None:
            high_exam_links.append(generate_link_res["data"]["surl"])
        else:
            low_exam_links.append(generate_link_res["data"]["surl"])
    print("花名册获取完成")
    submit_exam(high_exam_links, "高管")
    submit_exam(low_exam_links, "非高管")

def submit_exam(exam_links, type):
    file_path = '%s/一鱼两吃.json' % os.path.abspath("wehr")
    print(f"开始{type}填答问卷")
    with open(file_path) as data:
        answer = data.read()
        answer = json.loads(answer)
        if type == "高管":
            for idx, val in enumerate(answer):
                if idx in range(5, 79) or idx in range(301, 306):
                    val["select"][0]["value"] = random.choice(["0", "1", "2", "3", "4", "5"])
                elif idx == 0: # 岗位题
                    val["select"][0]["value"] = random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "13"])
                elif idx == 1: # 年龄题
                    val["select"][0]["value"] = random.choice(["0", "1", "2", "3", "4"])
                elif idx == 2: # 性别题
                    val["select"][0]["value"] = random.choice(["0", "1"])
                elif idx == 3: # 工作年限题
                    val["select"][0]["value"] = random.choice(["1", "2", "3", "4", "5", "6", "7", "8"])
                elif idx == 4: # 学历题
                    val["select"][0]["value"] = random.choice(["0", "1", "2", "3", "4", "5", "6"])
        elif type == "非高管":
            # answer.json 含高管答案, 这里去掉最后5道高管题
            answer = answer[0: -5]
            for idx, val in enumerate(answer):
                if idx in range(5, 79):
                    val["select"][0]["value"] = random.choice(["0", "1", "2", "3", "4", "5"])
                elif idx == 0: # 岗位题
                    val["select"][0]["value"] = random.choice(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "13"])
                elif idx == 1: # 年龄题
                    val["select"][0]["value"] = random.choice(["0", "1", "2", "3", "4"])
                elif idx == 2: # 性别题
                    val["select"][0]["value"] = random.choice(["0", "1"])
                elif idx == 3: # 工作年限题
                    val["select"][0]["value"] = random.choice(["1", "2", "3", "4", "5", "6", "7", "8"])
                elif idx == 4: # 学历题
                    val["select"][0]["value"] = random.choice(["0", "1", "2", "3", "4", "5", "6"])
        for link in tqdm(exam_links):
            code = re.findall(r".*code=(.*)", link)[0]
            try:
                r = requests.post(
                    "https://wehr.qq.com/oca/api/answer/submit?trace_id=205c546f68fe45bbaefd0a3be035fe2e&g_trans_id=9775434ab358580d1df60271e704c346",
                    data = {
                        "code": code,
                        "ver": 11,
                        "answer": json.dumps(answer)
                    }
                )
            except Exception as e:
                print(f"填答{type}问卷失败: {e}, 填答link: {link}, response: {r.text}")
    print("问卷填答完成")

# 普通调研
def pt(type, loop_time):
    try:
        answer = None
        if type == "gg": # 高管
            file_path = "%s/普通高管.json" % os.path.abspath("wehr")
            with open(file_path) as data:
                answer = json.loads(data.read())
                for item in enumerate(answer):
                    if item["lid"] == 1: # 部门题
                        A_department = ["2", "3", "4", "5"]
                        B_department = ["7", "8", "9", "10"]
                        item["select"][0]["value"] = random.choice(A_department)
                        item["select"][1]["value"] = random.choice(B_department)
        elif type == "non_gg": # 非高管
            file_path = "%s/普通非高管.json" % os.path.abspath("wehr")
            with open(file_path) as data:
                answer = json.loads(data.read())
                for item in answer:
                    if item["lid"] == 1: # 部门题
                        A_department = ["2", "3", "4", "5"]
                        B_department = ["7", "8", "9", "10"]
                        item["select"][0]["value"] = random.choice(A_department)
                        item["select"][1]["value"] = random.choice(B_department)
                    if item["lid"] == 3: # 职能题
                        item["select"][0]["value"] = random.choice(["1", "2", "3"])
        else:
            raise Exception(f"类型错误: {type}")
        for i in tqdm(range(loop_time)):
            answer = json.dumps(answer)
            r = requests.get(
                "https://wehr.qq.com/oca/api/answer/submit?trace_id=3bb0497f586f72411b960cc1fd100d73&g_trans_id=d5540e7ca1b9779fc247d85c62b7c84e",
                params = {
                    "project": "A35424F0BF59101A74E4",
                    "ver": 11,
                    "answer": answer
                }
            )
            response = r.text
            print(response)
            # if response["ret"] != 0:
            #     raise RuntimeError(f"问卷提交报错: {response}")
    except RuntimeError as error:
        print(error)
    

if __name__ == "__main__":
    yi_yu_liang_chi()