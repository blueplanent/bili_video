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

cookies = "buvid3=338B4E39-B9A3-551F-3309-16418A3E4A7A65281infoc; b_nut=1715768865; _uuid=6414C5DA-2AD5-8281-7724-D10241591671D66787infoc; buvid4=A84E2CFE-785A-3BC2-FF9D-D27DC066F5D938158-024033004-VpVPcDfyDBYapODwJgQqhw%3D%3D; rpdid=|(JYl)kmkuR)0J'u~ul~Y)))u; iflogin_when_web_push=0; header_theme_version=CLOSE; DedeUserID=484890515; DedeUserID__ckMd5=90b98033b995359d; enable_web_push=DISABLE; buvid_fp_plain=undefined; LIVE_BUVID=AUTO8117158623388548; PVID=1; hit-dyn-v2=1; home_feed_column=5; fingerprint=d2e4dcc62522dc26c76cb2730282d73a; CURRENT_QUALITY=80; CURRENT_BLACKGAP=0; buvid_fp=d2e4dcc62522dc26c76cb2730282d73a; CURRENT_FNVAL=4048; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzAyNjQ4NjQsImlhdCI6MTczMDAwNTYwNCwicGx0IjotMX0.W-m3fsrB8ShSpDzvLFtOoT96shj3ztTZc4BmxL_te6E; bili_ticket_expires=1730264804; b_lsid=D6F39C62_192CC8C438A; SESSDATA=77c9a4c3%2C1745560601%2C92c7b%2Aa1CjBcKQUlAlm_iiAGNSHdAuYMUnBvQqCBFKl9aaNG7OuXii13XSnLp7G07ToJWj2WQMcSVnQzQ3RtcUdnc2UxQ1h3cjFwSk9ZWTlSMV9oRmlyVzJpai1wSEJBemptcXlKdW1xOFdiYlgwSUFOM2hWNVluZ3E0VW13QzdfYzF3UXA4aE15Mlo2SWl3IIEC; bili_jct=3e2bcbe408e9a9b1f73271f9660bf2fc; sid=6fju1fdu; bp_t_offset_484890515=992872752367009792; browser_resolution=1489-710"
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
        time.sleep(10)
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

