# -*- coding: utf-8 -*-
# -------------------------------
# @PyCharm：PyCharm 2023.1.3 (Community Edition)
# @Python：Python 3.8.10
# @时间：2024/10/22 13:15
# -------------------------------

import json
import re

# 接收reponse对象，获取总的媒体链接信息
def get_medium_inf(res):
    pattern = r'"video":.*?,"audio":.*?(?=,"dolby":)'
    a = re.search(pattern, res.text)
    json_text = "{" + a.group() + "}"
    dic = json.loads(json_text)
    return dic

# 接收总的媒体链接，构造为视频迭代器
def generate_videourl(dic):
    accept_description = ["高码率 1080P+", "高清 1080P", "高清 720P", "清晰 480P", "流畅 360P"]
    accept_quality = [112, 80, 64, 32, 16]
    for i in dic['video']:
        print('视频质量', accept_description[accept_quality.index(i['id'])])
        yield i['baseUrl']
        yield i['base_url']
        for j in i['backupUrl']:
            yield j
        for j in i['backup_url']:
            yield j

# 接收总的媒体链接，构造为定义音频迭代器
def generate_audiourl(dic):
    accept_description = ["高码率 1080P+", "高清 1080P", "高清 720P" "清晰 480P", "流畅 360P"]
    accept_quality = [30112, 30280, 30264, 30232, 30216]
    for i in dic['audio']:
        print('音频质量', accept_description[accept_quality.index(i['id'])])
        yield i['baseUrl']
        yield i['base_url']
        for j in i['backupUrl']:
            yield j
        for j in i['backup_url']:
            yield j

# 接收reponse对象，获取变量__INITIAL_STATE__，里面有视频的相关信息
def get_main_inf(res):
    pattern_total_inf = '__INITIAL_STATE__=(.*?);\(function\(\)'
    a = re.search(pattern_total_inf, res.text)
    dic = json.loads(a.group(1))
    return dic

# 接收变量__INITIAL_STATE__的值，解析出里面包含的视频相关信息
# 目前可解析：标题，总播放量，点赞人数，投币人数，收藏人数，转发人数，评论人数
def anay_inf(dic):
    bvid = dic['videoData']['bvid']  # 形如BV1Yt4y1J7qk
    title = dic['videoData']['title']  # 标题
    count_reply = dic['videoData']['stat']['reply']  # 评论数量
    like = dic['videoData']['stat']['like']  # 点赞人数
    coin = dic['videoData']['stat']['coin']  # 投币人数
    share = dic['videoData']['stat']['share']  # 分享人数
    view = dic['videoData']['stat']['view']  # 观看人数
    favorite = dic['videoData']['stat']['favorite']  # 收藏人数
    dic = {
        "视频url：": "https://www.bilibili.com/video/"+bvid,
        '视频标题：': title,
        '总播放量：': view,
        '点赞人数：': like,
        '投币人数：': coin,
        '收藏人数：': favorite,
        '转发人数：': share,
        "评论人数": count_reply
    }
    print(json.dumps(dic,indent=4,ensure_ascii=False))
    return dic

# 接收变量__INITIAL_STATE__的值，解析出合集其他视频信息
# 第二种获取合集的方法
def anay_medium_inf1(dic):
    episodes = dic['videoData']['ugc_season']['sections'][0]['episodes']
    li = []
    for i in episodes:
        title = i['title']
        url = f'https://www.bilibili.com/video/{i["bvid"]}'
        li.append((title, url))
        print(f"标题：{title}, url：{url}")
    print('合集里有多少视频', len(li))
    return li

# 接收变量__INITIAL_STATE__的值，解析出合集其他视频信息
# 第一种获取合集的方法
def anay_medium_inf2(dic):
    bvid = dic['videoData']['bvid']
    pages = dic['videoData']['pages']
    li = []
    for i, j in zip(pages, range(1, len(pages) + 1)):
        title = i['part']
        url = f'https://www.bilibili.com/video/{bvid}/?p={j}'
        li.append((title, bvid))
        print(f"标题：{title}, url：{url}")
    print(f'合集里总共{len(pages)}个视频', )
    return li

if __name__ == '__main__':
    filename = 'BV1jE4PehEQq'
    # 测试 web_page_parsing.anay_medium_inf1 方法
    print("web_page_parsing.anay_medium_inf1".center(50, '-'))
    with open(f"{filename}_inf.json", 'r', encoding='utf-8') as f:
        main_inf = json.load(f)
    anay_medium_inf1(main_inf)
    print("web_page_parsing.anay_medium_inf1执行结束".center(50, '-'))

    # 测试 web_page_parsing.anay_medium_inf2 方法
    print("web_page_parsing.anay_medium_inf2".center(50, '-'))
    with open(f"{filename}_inf.json", 'r', encoding='utf-8') as f:
        main_inf = json.load(f)
    anay_medium_inf2(main_inf)
    print("web_page_parsing.anay_medium_inf2执行结束".center(50, '-'))

    # 测试 web_page_parsing.generate_videourl 方法
    print("web_page_parsing.generate_videourl".center(50, '-'))
    with open(f"{filename}_medio.json", 'r', encoding='utf-8') as f:
        mediums = json.load(f)
    for i in generate_videourl(mediums):
        print(i)
    print("web_page_parsing.generate_videourl执行结束".center(50, '-'))

    # 测试 web_page_parsing.generate_audiourl 方法
    print("web_page_parsing.generate_audiourl".center(50, '-'))
    with open(f"{filename}_medio.json", 'r', encoding='utf-8') as f:
        mediums = json.load(f)
    for i in generate_audiourl(mediums):
        print(i)
    print("web_page_parsing.generate_audiourl执行结束".center(50, '-'))