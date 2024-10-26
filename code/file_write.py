# -*- coding: utf-8 -*-
# -------------------------------
# @PyCharm：PyCharm 2023.1.3 (Community Edition)
# @Python：Python 3.8.10
# @时间：2024/10/22 13:55
# -------------------------------

import os
from moviepy.editor import ffmpeg_tools

# 选项一，将视频和音频合并，然后删除掉原材料，只保留合并的
def option1(video_path,audio_path):
    path = video_path.replace('video_', '')
    ffmpeg_tools.ffmpeg_merge_video_audio(video_path, audio_path, path)
    os.remove(video_path)
    os.remove(audio_path)
    print("选项一，将视频和音频合并，然后删除掉原材料，只保留合并的")

# 选项二，只获取并重命名音频
def option2(video_path,audio_path):
    os.remove(video_path)
    path = audio_path.replace('audio_', '')
    os.rename(audio_path, path)
    print("选项二，只获取并重命名音频")

# 选项三，只获取并重命名视频
def option3(video_path,audio_path):
    os.remove(audio_path)
    path = video_path.replace('video_', '')
    os.rename(video_path, path)
    print("选项三，只获取并重命名视频")

# # 检查文件路劲是否合法
# def check_path(path):
#     path = path.strip()
#     if os.path.isabs(path):
#         filename = os.path.basename(path)
#     else:
#         filename = path
#     if re.match("\w+\.\w+", filename):
#         print(f"{path}是有效的文件路径")
#         return True
#     else:
#         print(f"{path}不是有效的文件路径")
#         return False


# 音视频请求并写入
def file_write(res,path):
    # 判断文件路径是否合法
    # if check_path(path) and res:
    #     with open(path, 'wb') as f:
    #         f.write(res.content)
    with open(path, 'wb') as f:
        f.write(res.content)


