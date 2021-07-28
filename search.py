import requests
import os
from prettytable import PrettyTable, PLAIN_COLUMNS
from PIL import Image, ImageDraw, ImageFont
import datetime
from datetime import timedelta
import calendar
import time
import re
from hoshino import R

# 通用头
headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Custom-Source': 'Kyaru',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://kyaru.infedg.xyz',
    'Referer': 'https://kyaru.infedg.xyz/'
}

# 计算最新数据对应的时间戳，并设置相应的延迟
def get_current_time():
    time_now = datetime.datetime.fromtimestamp(time.time()) 
    # print(time_now)

    now = datetime.date.today()
    this_month_end = datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1])
    start_time = this_month_end - timedelta(days=4) + timedelta(minutes=10)
    end_time = this_month_end + timedelta(days=1)

    # 会战期间
    if time_now >= start_time and time_now < end_time:
        # 设定延迟10分钟，防止排名数据还未更新
        delay = 10
        time_tmp = time.strftime('%Y%m%d%H', time.localtime())
        minute_tmp = time.strftime('%M', time.localtime())
        if int(minute_tmp) >= (0 + delay) and int(minute_tmp) < (30 + delay):
            set_minute = '00'
        elif int(minute_tmp) < (0 + delay):
            time_last = time_now - timedelta(hours=1)
            time_tmp = datetime.datetime.strptime(str(time_last), '%Y-%m-%d %H:%M:%S.%f')
            time_tmp = str(time_tmp.year) + str(time_tmp.month).zfill(2) + str(time_tmp.day).zfill(2) + str(time_tmp.hour).zfill(2)
            set_minute = '30'
        else:
            set_minute = '30'
        uptime = str(time_tmp) + set_minute
        # print(uptime)
    # 会战时间外
    else:
        this_month_start = datetime.datetime(now.year, now.month, 1)
        time_tmp = this_month_start - timedelta(minutes=30)
        uptime = str(time_tmp.year) + str(time_tmp.month).zfill(2) + str(time_tmp.day).zfill(2) + str(time_tmp.hour).zfill(2) + str(time_tmp.minute).zfill(2)
        # print(uptime)
    return uptime


# 生成图片
def create_img(info_data, filename_tmp):
    
    field_names = ('排名', '公会名', '人数', '会长名', '分数', '周目', 'BOSS', '剩余血量', '上期排名')
    table = PrettyTable(field_names = field_names)

    allid = info_data['data'].keys()
    for id in allid:
        rank = info_data['data'][str(id)]['rank']
        clan_name = info_data['data'][str(id)]['clan_name']
        # 去除特殊字符，只保留中英日韩数字
        clan_name = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\uAC00-\uD7AF\u3040-\u31FF])","",clan_name)
        member_num = info_data['data'][str(id)]['member_num']
        leader_name = info_data['data'][str(id)]['leader_name']
        # 去除特殊字符，只保留中英日韩数字
        leader_name = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\uAC00-\uD7AF\u3040-\u31FF])","",leader_name)
        damage = info_data['data'][str(id)]['damage']
        lap = info_data['data'][str(id)]['lap']
        boss_id = info_data['data'][str(id)]['boss_id']
        remain = info_data['data'][str(id)]['remain']
        grade_rank = info_data['data'][str(id)]['grade_rank']
        table.add_row([rank, clan_name, member_num, leader_name, damage, lap, boss_id, remain, grade_rank])

    # table.set_style(PLAIN_COLUMNS)
    # print(table)

    table_info = str(table)
    space = 5
    current_dir = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
    font = ImageFont.truetype(current_dir, 20, encoding='utf-8')
    im = Image.new('RGB',(10, 10),(255, 255, 255, 0))
    draw = ImageDraw.Draw(im, 'RGB')
    img_size = draw.multiline_textsize(table_info, font=font)
    im_new = im.resize((img_size[0]+space*2, img_size[1]+space*2))
    del draw
    del im
    draw = ImageDraw.Draw(im_new, 'RGB')
    draw.multiline_text((space,space), table_info, fill=(0, 0, 0), font=font)
    save_dir = R.img('clan_rank_tw').path
    path_dir = os.path.join(save_dir, filename_tmp)
    im_new.save(path_dir, 'PNG')
    del draw

# 返回档线信息
def get_score_line(server, uptime):
    url = 'https://api.infedg.xyz/search/scoreline'
    file_tmp = 'tw/' + str(server) + '/' + str(uptime)
    filename_tmp = 'tw-' + str(server) + '-' + str(uptime) + '.png'
    params = {
        'filename': file_tmp,
        'search': '',
        'page': 0,
        'page_limit': 10
    }

    score_line_tmp = requests.post(url, headers = headers, json = params)
    score_line = score_line_tmp.json()
    return score_line, filename_tmp

# 返回公会名查询信息
def get_score_clan(server, uptime, clan_name):
    url = 'https://api.infedg.xyz/search/clan_name'
    file_tmp = 'tw/' + str(server) + '/' + str(uptime)
    filename_tmp = 'tw-' + str(server) + '-' + str(uptime) + '-' + str(clan_name) + '.png'
    params = {
        'filename': file_tmp,
        'search': clan_name,
        'page': 0,
        'page_limit': 10
    }

    clan_score_tmp = requests.post(url, headers = headers, json = params)
    clan_score = clan_score_tmp.json()
    return clan_score, filename_tmp

# 返回会长名查询信息
def get_score_leader(server, uptime, leader_name):
    url = 'https://api.infedg.xyz/search/leader_name'
    file_tmp = 'tw/' + str(server) + '/' + str(uptime)
    filename_tmp = 'tw-' + str(server) + '-' + str(uptime) + '-' + str(leader_name) + '.png'
    params = {
        'filename': file_tmp,
        'search': leader_name,
        'page': 0,
        'page_limit': 10
    }

    clan_score_tmp = requests.post(url, headers = headers, json = params)
    clan_score = clan_score_tmp.json()
    return clan_score, filename_tmp

# 返回排名查询信息
def get_score_rank(server, uptime, rank):
    url = 'https://api.infedg.xyz/search/rank'
    file_tmp = 'tw/' + str(server) + '/' + str(uptime)
    filename_tmp = 'tw-' + str(server) + '-' + str(uptime) + '-' + str(rank) + '.png'
    params = {
        'filename': file_tmp,
        'search': rank,
        'page': 0,
        'page_limit': 10
    }

    clan_score_tmp = requests.post(url, headers = headers, json = params)
    clan_score = clan_score_tmp.json()
    return clan_score, filename_tmp