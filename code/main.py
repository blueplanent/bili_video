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
from moviepy.editor import ffmpeg_tools

import requests
from urllib import parse

import web_page_parsing
import config

cookies = "buvid3=E02D1C1E-EE31-307A-7809-DA6D08532D8E65700infoc; b_nut=1728120365; _uuid=1457107102-D97A-6498-9F49-AB7D14E8716F66994infoc; buvid4=1421D9DA-A74A-CED2-A0FA-E207C49EE8EC70651-024100509-UUXyNy9lPIW3btqqthYSVQ%3D%3D; rpdid=|(J~RYukl)Y~0J'u~k)uk|J~J; buvid_fp_plain=undefined; header_theme_version=CLOSE; enable_web_push=DISABLE; home_feed_column=5; browser_resolution=1797-839; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzAyNTA2NTYsImlhdCI6MTcyOTk5MTM5NiwicGx0IjotMX0.wL19Y7kfm6wt152LmS1NMBU5ZOuPsV6dYyobsypyFn8; bili_ticket_expires=1730250596; fingerprint=355933030be7e270f3aa12997fc9ee2f; buvid_fp=355933030be7e270f3aa12997fc9ee2f; CURRENT_BLACKGAP=0; CURRENT_FNVAL=4048; b_lsid=666E955D_192D75E9505; bmg_af_switch=1; bmg_src_def_domain=i2.hdslb.com; sid=6p402t8i"
headers = {
    "referer": "https://www.bilibili.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    'Accept-Encoding': '',
    'Cookie': cookies
}

def retry(n):
    def wrapper(func):
        @wraps(func)
        def abcd(*args, **kwargs):
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
        # time.sleep(10)
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

# 音视频请求并写入
def file_write(urls,path):
    for url in urls:
        res = req(url)
        if res:
            with open(path, 'wb') as f:
                f.write(res.content)
            break


# 抓取单个视频
def get_one(entry_url, title=0):
    if title:
        video_path = f"{config.video_dir}/{title}.mp4"
        audio_path = f"{config.audio_dir}/{title}.mp3"
        medium_path = f"{config.medium_dir}/{title}.mp4"
    else:
        parse_result = parse.urlparse(entry_url)
        filename = parse_result.path.split('/').pop()
        video_path = f"{config.video_dir}/{filename}.mp4"
        audio_path = f"{config.audio_dir}/{filename}.mp3"
        medium_path = f"{config.medium_dir}/{filename}.mp4"
    methods = {
        1: (web_page_parsing.get_medium_inf1, web_page_parsing.anay_medium_inf1, web_page_parsing.anay_medium_inf2,lambda x: []),
        2: (web_page_parsing.get_medium_inf1, lambda x: [], web_page_parsing.anay_medium_inf2,lambda x: []),
        3: (web_page_parsing.get_medium_inf1, web_page_parsing.anay_medium_inf1, lambda x: [],lambda x: []),
        4: (web_page_parsing.get_medium_inf2, lambda x: [], lambda x: [], web_page_parsing.anay_medium_inf3)
    }
    res = req(entry_url)
    if config.scrape_option != 3:
        main_inf = web_page_parsing.get_main_inf1(res.text)
        cover_url = web_page_parsing.anay_main_inf1(main_inf)
        file_write((cover_url,), f'{config.cover_dir}/{title}.png')
    for i in range(2):
        try:
            medium_inf = methods[config.file_option][0](res.text)
            video_urls = methods[config.file_option][1](medium_inf)
            audio_urls = methods[config.file_option][2](medium_inf)
            medium_urls = methods[config.file_option][3](medium_inf)
            break
        except:
            config.file_option = 1
    file_write(video_urls,video_path)
    file_write(audio_urls,audio_path)
    file_write(medium_urls,medium_path)
    if config.file_option == 1:
        ffmpeg_tools.ffmpeg_merge_video_audio(video_path, audio_path, medium_path)
        os.remove(video_path)
        os.remove(audio_path)
    print(f"已获取{title if title else filename}")

# 抓取整个合集
def get_all(entry_url):
    res = req(entry_url)
    main_inf = web_page_parsing.get_main_inf1(res.text)
    methods = [
        web_page_parsing.anay_main_inf2,
        web_page_parsing.anay_main_inf3
    ]
    for method in methods:
        try:
            li = method(main_inf)
            break
        except:
            li = []
    for i in li:
        title, url = i
        get_one(url, title)

def get_all1(entry_url):
    res = req(entry_url)
    main_inf = web_page_parsing.get_main_inf2(res.text)
    session_id = web_page_parsing.anay_main_inf4(main_inf)
    res = req(f'https://api.bilibili.com/pgc/view/web/ep/list?season_id={session_id}')
    dic = json.loads(res.text)
    for i in web_page_parsing.anay_main_inf5(dic):
        title, url, cover_url = i
        file_write((cover_url,),f'{config.cover_dir}/{title}.png',)
        get_one(url, title)

if __name__ == '__main__':
    entry_url = "https://www.bilibili.com/video/BV1gA18YpEeS?spm_id_from=333.1007.tianma.1-1-1.click"
    title = '【博德之门3】以防万一你没见过守墓人耶格中狂笑术'
    if config.scrape_option == 1:
        get_one(entry_url, title)
    elif config.scrape_option == 2:
        get_all(entry_url)
    elif config.scrape_option == 3:
        get_all1(entry_url)

