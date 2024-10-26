# b站视频抓取

## 目录结构

```
├───bili_video 主文件夹
│   ├───code 代码文件夹
│   │   ├───web_page_parsing.py 网页解析
│   │   ├───file_write.py 文件写入
│   │   ├───config.py 配置文件
│   │   └───main.py 执行文件
│   ├───data 媒体存放
│   │   ├───audios 默认的音频输出路径
│   │   └───videos 默认的视频输出路径
│   └───html 后期更改代码会用到的，可以不用管
│       └───BV1jE4PehEQq 
```

## 环境说明

操作系统类别：Windows 11 专业版
开发环境：PyCharm：PyCharm 2023.1.3 (Community Edition)
Python解释器版本：Python 3.8.10

## 使用流程

1、修改配置文件config.py，选择抓取类别，抓取范围，更改输出路径
2、修改main.py文件，将main文件末尾的entry_url和title变量设置为要抓取的视频的链接和标题
3、执行main.py文件

## 附加说明

1、确保安装好python解释器和相关第三方库
2、出现错误可以试试网上的解决办法，也可以私信我



联系方式：QQ 485558145
