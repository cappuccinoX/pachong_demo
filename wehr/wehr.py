import requests
from bs4 import BeautifulSoup
import json
import os
import re
from tqdm import tqdm

exam_code = "6763BB8F785649C27076"

def do_exam():
    headers = {
        "Cookie": "think_language=zh-CN; visitkey=02d852c92554979924555c7cac; mcduid=170603; scode=43bece0cca377272df8f17c488fd8fd46c78c79b; PHPSESSID=hmoepck4uvfq34ir0jlktvtdn5; exam_new_2088=1; new_version_online_exam_2088=1"
    }
    # 获取花名册
    r = requests.get("https://wehr.qq.com/Center/Roster/roster_list?code=6763BB8F785649C27076&search=&status=-1&page_size=999&page_num=1", headers = headers)
    exam_links = list()
    data = json.loads(r.text)
    data = data["data"]["detail"]
    print("开始获取花名册")
    for user in tqdm(data):
        # 根据花名册生成答题url
        url = f"https://wehr.qq.com/Center/Roster/generate_link_roster?code={exam_code}&id={user['id']}"
        generate_link_res = requests.get(url, headers = headers)
        generate_link_res = json.loads(generate_link_res.text)
        # 获取每份问卷code
        exam_links.append(generate_link_res["data"]["surl"])
    print("花名册获取完成")
    submit_exam(exam_links)

def submit_exam(exam_links):
    file_path = '%s/answer.json' % os.path.abspath("wehr")
    print("开始填答问卷")
    with open(file_path) as data:
        answer = data.read()
        for link in tqdm(exam_links):
            code = re.findall(r".*code=(.*)", link)[0]
            r = requests.post(
                "https://wehr.qq.com/oca/api/answer/submit?trace_id=205c546f68fe45bbaefd0a3be035fe2e&g_trans_id=9775434ab358580d1df60271e704c346",
                data = {
                    "code": code,
                    "ver": 11,
                    "answer": answer
                }
            )
    print("问卷填答完成")



if __name__ == "__main__":
    do_exam()