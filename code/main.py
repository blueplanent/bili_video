# -*- coding: utf-8 -*-
# -------------------------------
# @PyCharm：PyCharm 2023.1.3 (Community Edition)
# @Python：Python 3.8.10
# @时间：2024/10/5 17:25
# -------------------------------

import os
import json
import time
from functools import wraps

import requests
from urllib import parse

import web_page_parsing
import file_write
import config

cookies = "buvid3=E02D1C1E-EE31-307A-7809-DA6D08532D8E65700infoc; b_nut=1728120365; _uuid=1457107102-D97A-6498-9F49-AB7D14E8716F66994infoc; CURRENT_FNVAL=4048; buvid4=1421D9DA-A74A-CED2-A0FA-E207C49EE8EC70651-024100509-UUXyNy9lPIW3btqqthYSVQ%3D%3D; rpdid=|(J~RYukl)Y~0J'u~k)uk|J~J; fingerprint=b6b0c74800d6fdc18a3b37cb2cad20f2; buvid_fp_plain=undefined; buvid_fp=b6b0c74800d6fdc18a3b37cb2cad20f2; header_theme_version=CLOSE; enable_web_push=DISABLE; home_feed_column=5; browser_resolution=1797-839; b_lsid=87E103BED_192C67F96D7; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzAxNjYzMDgsImlhdCI6MTcyOTkwNzA0OCwicGx0IjotMX0.kvUQoLFyRMWbWoDqlcYjzhswsJl5NHH67YtwoaZUz60; bili_ticket_expires=1730166248; sid=65rgxq0x"
headers = {
    "referer": "https://www.bilibili.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    'Accept-Encoding': '',
    'Cookie': cookies
}

def retry(n):
    def wrapper(func):
        @wraps(func)
        def abcd(*args,**kwargs):
            for i in range(n):
                result = func(*args, **kwargs)
                if result:
                    return result
                print(f"第{i + 1}次请求失败")
            print("请求终止")
        return abcd
    return wrapper

# 发送请求，n表示重试次数
@retry(3)
def req(url):
    try:
        time.sleep(3)
        res = requests.get(url, headers=headers, timeout=(3.1, 10))
        if res.status_code == 200:
            return res
        else:
            print(f"请求失败,状态码{res.status_code}")
            return
    except requests.Timeout as e:
        print(e)
        return
    except Exception as e:
        print(e)
        return

# 用于测试
def a(entry_url):
    res = req(entry_url)
    parse_result = parse.urlparse(entry_url)
    filename = parse_result.path.rstrip('/').split('/').pop()
    original_path = os.getcwd()
    os.chdir("../html")
    os.mkdir(f'{filename}')
    os.chdir(original_path)
    with open(f"bili_video/html/{filename}/{filename}.html", 'w', encoding='utf-8') as f:
        f.write(res.text)

    # 测试 web_page_parsing.get_main_inf 方法
    print("web_page_parsing.get_main_inf".center(50,'-'))
    main_inf = web_page_parsing.get_main_inf(res)
    with open(f"bili_video/html/{filename}/{filename}_inf.json", 'w', encoding='utf-8') as f:
        json.dump(main_inf,f)
    print("web_page_parsing.get_main_inf执行结束".center(50, '-'))

    # 测试 web_page_parsing.anay_inf 方法
    print("web_page_parsing.anay_inf".center(50, '-'))
    web_page_parsing.anay_inf(main_inf)
    print("web_page_parsing.anay_inf执行结束".center(50, '-'))

    # 测试 web_page_parsing.get_medium_inf 方法
    print("web_page_parsing.get_medium_inf".center(50,'-'))
    medium_inf = web_page_parsing.get_medium_inf(res)
    with open(f"bili_video/html/{filename}/{filename}_medio.json", 'w', encoding='utf-8') as f:
        json.dump(medium_inf,f)
    print("web_page_parsing.get_medium_inf执行结束".center(50,'-'))



# 抓取单个视频
def get_one(entry_url,title=0):
    res = req(entry_url)
    medium_inf = web_page_parsing.get_medium_inf(res)
    video_urls = web_page_parsing.generate_videourl(medium_inf)
    audio_urls = web_page_parsing.generate_audiourl(medium_inf)
    parse_result = parse.urlparse(entry_url)
    filename = parse_result.path.split('/').pop()
    if title:
        video_path = f"{config.video_dir}/video_{title}.mp4"
        audio_path = f"{config.audio_dir}/audio_{title}.mp3"
    else:
        video_path = f"{config.video_dir}/video_{filename}.mp4"
        audio_path = f"{config.audio_dir}/audio_{filename}.mp3"
    for video_url in video_urls:
        res = req(video_url)
        if res:
            file_write.file_write(res, video_path)
            break
    for audio_url in audio_urls:
        res = req(audio_url)
        if res:
            file_write.file_write(res, audio_path)
            break
    # options = {
    #     1: file_write.option1,
    #     2: file_write.option2,
    #     3: file_write.option3
    # }
    # options[config.file_option](video_path, audio_path)

# 抓取整个合集
def get_all(entry_url):
    res = req(entry_url)
    # 获取变量__INITIAL_STATE__（里面有视频的相关信息）
    main_inf = web_page_parsing.get_main_inf(res)
    methods = [
        web_page_parsing.anay_medium_inf1,
        web_page_parsing.anay_medium_inf2
    ]
    for method in methods:
        try:
            li = method(main_inf)
            break
        except:
            li = []
    for i in li:
        title, url = i
        get_one(url,title)



if __name__ == '__main__':
    entry_url = "https://www.bilibili.com/video/BV1QY411b7Kf/?spm_id_from=333.337.search-card.all.click"
    title = "[问号]"

    if config.scrape_option == 1:
        get_one(entry_url, title)
    elif config.scrape_option == 2:
        get_all(entry_url)
    else:
        a(entry_url)


