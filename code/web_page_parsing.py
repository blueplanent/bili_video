# -*- coding: utf-8 -*-
# -------------------------------
# @PyCharm：PyCharm 2023.1.3 (Community Edition)
# @Python：Python 3.8.10
# @时间：2024/10/22 13:15
# -------------------------------

import json
import re
import time

from lxml import etree

def get_main_inf1(html_text):
    """获取 window.__INITIAL_STATE__ 的值"""
    pattern_total_inf = '__INITIAL_STATE__=(.*?);\(function\(\)'
    a = re.search(pattern_total_inf, html_text)
    dic = json.loads(a.group(1))
    return dic


def get_main_inf2(html_text):
    """获取标签 <script id=’__NEXT_DATA__‘...</script> 的文本内容"""
    etree_ele = etree.fromstring(html_text, etree.HTMLParser())
    a= etree_ele.xpath('//*[@id="__NEXT_DATA__"]')[0]
    dic = json.loads(a.text)
    return dic


def get_medium_inf1(html_text):
    '''获取 “video":[...],"audio":[...] 的值'''
    pattern = re.compile('"video":.*?"audio":.*?(?=,"dolby")', re.DOTALL)
    medium_inf = pattern.search(html_text)
    json_text = "{" + medium_inf.group() + "}"
    dic = json.loads(json_text)
    return dic


def get_medium_inf2(html_text):
    '''获取 "durl":[...] 的值'''
    pattern = r'"durl":.*?(?=,"support_formats":)'
    a = re.search(pattern, html_text)
    json_text = "{" + a.group() + "}"
    dic = json.loads(json_text)
    return dic


def anay_main_inf1(main_inf):
    """解析视频常规信息，用来获取封面，信息是附带的"""
    bvid = main_inf['videoData']['bvid']  # 形如BV1Yt4y1J7qk
    owner = main_inf['videoData']['owner']
    dic = {
        "视频url：": "https://www.bilibili.com/video/" + bvid,
        '视频标题：': main_inf['videoData']['title'],
        '总播放量：': main_inf['videoData']['stat']['view'],
        '点赞人数：': main_inf['videoData']['stat']['like'],
        '投币人数：': main_inf['videoData']['stat']['coin'],
        '收藏人数：': main_inf['videoData']['stat']['favorite'],
        '转发人数：': main_inf['videoData']['stat']['share'],
        "评论人数": main_inf['videoData']['stat']['reply'],
        "封面地址": main_inf["videoData"]["pic"],
        "简介": main_inf["videoData"]["desc"],
        "发布时间": main_inf['videoData']['ctime'],
        "UP主mid": owner['mid'],
        "UP主": owner['name'],
        "UP主头像": owner['face']
    }
    print(json.dumps(dic, indent=4, ensure_ascii=False))
    del dic
    return main_inf["videoData"]["pic"]


def anay_main_inf2(main_inf):
    """获取 合集里所有视频的url(方式一)"""
    episodes = main_inf['videoData']['ugc_season']['sections'][0]['episodes']
    print('合集里有多少视频', len(episodes))
    for i in episodes:
        title = i['title']
        url = f'https://www.bilibili.com/video/{i["bvid"]}'
        print(f"标题：{title}, url：{url}")
        yield (title, url)


def anay_main_inf3(main_inf):
    """获取 合集里所有视频的url(方式二)"""
    bvid = main_inf['videoData']['bvid']
    pages = main_inf['videoData']['pages']
    print(f'合集里总共{len(pages)}个视频', )
    for i, j in zip(pages, range(1, len(pages) + 1)):
        title = i['part']
        url = f'https://www.bilibili.com/video/{bvid}/?p={j}'
        print(f"标题：{title}, url：{url}")
        yield (title, url)


def anay_main_inf4(main_inf):
    """解析视频常规信息以及获取 session_id ，用于番剧的抓取"""
    data = main_inf["props"]["pageProps"]["dehydratedState"]["queries"][1]["state"]["data"]
    stat = data["stat"]
    play_view_business_info = \
    main_inf["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["result"]["play_view_business_info"]
    epid = play_view_business_info["episode_info"]["ep_id"]
    bvid = play_view_business_info["episode_info"]["bvid"]
    session_id = play_view_business_info["season_info"]["season_id"]
    dic = {
        "视频url1：": "https://www.bilibili.com/video/" + bvid,
        "视频url2：": "https://www.bilibili.com/bangumi/play/ep" + str(epid),
        "封面url：": data["seasons"][0]["cover"],
        '视频标题：': data["season_title"],
        "类型：": data["styles"],
        '总播放量：': stat['views'],
        '点赞人数：': stat['likes'],
        '投币人数：': stat['share'],
        '收藏人数：': stat['favorite'],
        '转发人数：': stat['share'],
        "评论人数：": stat['reply'],
        "追番人数：": stat['favorites'],
        "员工：": data["staff"],
        "简介：": data["evaluate"],
        "评分：": data["rating"]["score"],
        "评分人数：": data["rating"]["count"]
    }
    print(json.dumps(dic, indent=4, ensure_ascii=False))
    del dic
    return session_id

def anay_main_inf5(dic):
    """获取 同一番剧的所有非会员集"""
    for i in dic["result"]["episodes"]:
        badge = i['badge']
        if badge == '会员':
            break
        epid = i['id']
        ep_link = i['link']
        bvid_link = 'https://www.bilibili.com/video/' + i['bvid']
        share_link = 'https://b23.tv/ep833513'
        long_title = i['long_title']
        pub_time = time.ctime(i['pub_time'])
        cover = i['cover']
        dic = {
            'badge': badge,
            'epid': epid,
            'ep_link': ep_link,
            'bvid_link': bvid_link,
            'share_link': share_link,
            'long_title': long_title,
            'pub_time': pub_time
        }
        print(json.dumps(dic, indent=4, ensure_ascii=False))
        yield (long_title, ep_link, cover)


def anay_medium_inf1(medium_inf):
    """获取视频链接"""
    accept_description = ["高码率 1080P+", "高清 1080P", "高清 720P", "清晰 480P", "流畅 360P"]
    accept_quality = [112, 80, 64, 32, 16]
    for i in medium_inf['video']:
        print('视频质量', accept_description[accept_quality.index(i['id'])])
        yield i['baseUrl']
        yield i['base_url']
        for j in i['backupUrl']:
            yield j
        for j in i['backup_url']:
            yield j

def anay_medium_inf2(medium_inf):
    """获取音频链接"""
    accept_description = ["高码率 1080P+", "高清 1080P", "高清 720P", "清晰 480P", "流畅 360P"]
    accept_quality = [30112, 30280, 30264, 30232, 30216]
    for i in medium_inf['audio']:
        print('音频质量', accept_description[accept_quality.index(i['id'])])
        yield i['baseUrl']
        yield i['base_url']
        for j in i['backupUrl']:
            yield j
        for j in i['backup_url']:
            yield j

def anay_medium_inf3(medium_inf):
    """获取视频链接"""
    i = medium_inf['durl'][0]
    yield i['url']
    for j in i['backup_url']:
        yield j

if __name__ == '__main__':
    filename = 'ss48511'
    with open(f"../data/html/{filename}/{filename}.json", 'r', encoding='utf-8') as f:
        dic = json.load(f)
    # main_inf = get_main_inf2(text)
    for i in anay_main_inf5(dic):
        print(i)

    # with open(r'C:\Users\PC\Desktop\bilibili\a.json','r',encoding='utf-8') as f:
    #     dic = json.load(f)
    # for i in anay_main_inf5(dic):
    #     print(i)