import os
import re
import json
from prettytable import PrettyTable
from PIL import Image, ImageDraw, ImageFont
from hoshino import aiorequests, R

# 设置源
async def set_source(source_id):
    if source_id == '1':
        source = 'infedg.xyz'
    elif source_id == '2':
        source = 'layvtwt.top'
    current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(current_dir, 'r', encoding='UTF-8') as af:
        f_data = json.load(af)
    f_data['source'] = source
    with open(current_dir, 'w', encoding='UTF-8') as f:
        json.dump(f_data, f, indent=4, ensure_ascii=False)
    return source

# 获取源
async def get_source():
    current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(current_dir, 'r', encoding='UTF-8') as af:
        f_data = json.load(af)
    source = f_data['source']
    return source

# 通用头
async def get_headers():
    source = await get_source()
    if source == 'infedg.xyz':
        source = 'kyaru.' + source
    elif source == 'layvtwt.top':
        source = 'rank.' + source
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Custom-Source': 'Kyaru',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
        'Content-Type': 'application/json',
        'Origin': f'https://{source}',
        'Referer': f'https://{source}/'
    }
    return headers

# 获取最新数据的时间档
async def get_current_time(server, source):
    if source == 'infedg.xyz':
        source = 'api.' + source
    elif source == 'layvtwt.top':
        source = 'rank.' + source + '/api'
    url = f'https://{source}/current/getalltime/tw'
    time_tmp = await aiorequests.get(url, headers = await get_headers(), timeout = 10)
    alltime = await time_tmp.json()
    alldays = alltime['data'][server].keys()
    upday = list(alldays)[-1]
    uphour = list(alltime['data'][server][upday])[-1]
    uptime = str(upday) + str(uphour)
    return uptime

# 返回查询信息
async def get_search_rank(server, uptime, source, search_type=None, search_param=''):
    if source == 'infedg.xyz':
        source = 'api.' + source
    elif source == 'layvtwt.top':
        source = 'rank.' + source + '/api'
    url = f'https://{source}/search/{search_type}'
    file_tmp = 'tw/' + str(server) + '/' + str(uptime)
    filename_tmp = 'tw-' + str(server) + '-' + str(uptime) + '-' + str(search_param) + '.png'
    params = {
        'filename': file_tmp,
        'search': search_param,
        'page': 0,
        'page_limit': 10
    }
    clan_score_tmp = await aiorequests.post(url, headers = await get_headers(), json = params, timeout = 10)
    clan_score = await clan_score_tmp.json()
    return clan_score, filename_tmp

# 生成图片
async def create_img(info_data, filename_tmp, is_all):
    if is_all:
        field_names = ('全服排名', '排名', '公会名', '人数', '会长名', '分数', '周目', 'BOSS', '剩余血量', '上期排名')
    else:
        field_names = ('排名', '公会名', '人数', '会长名', '分数', '周目', 'BOSS', '剩余血量', '上期排名')
    table = PrettyTable(field_names = field_names)
    # 输入参数
    allid = info_data['data'].keys()
    for id in allid:
        rank = info_data['data'][str(id)]['rank']
        clan_name = info_data['data'][str(id)]['clan_name']
        # 去除特殊字符，只保留中英日韩数字
        clan_name = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\uAC00-\uD7AF\u3040-\u31FF])","",clan_name)
        member_num = str(info_data['data'][str(id)]['member_num']).replace('.0', '')
        leader_name = info_data['data'][str(id)]['leader_name']
        # 去除特殊字符，只保留中英日韩数字
        leader_name = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a\uAC00-\uD7AF\u3040-\u31FF])","",leader_name)
        damage = info_data['data'][str(id)]['damage']
        lap = info_data['data'][str(id)]['lap']
        boss_id = info_data['data'][str(id)]['boss_id']
        remain = info_data['data'][str(id)]['remain']
        grade_rank = str(info_data['data'][str(id)]['grade_rank']).replace('.0', '')
        if is_all:
            all_server_rank = str(info_data['data'][str(id)]['all_server_rank'])
            table.add_row([all_server_rank, rank, clan_name, member_num, leader_name, damage, lap, boss_id, remain, grade_rank])
        else:
            table.add_row([rank, clan_name, member_num, leader_name, damage, lap, boss_id, remain, grade_rank])
    # 制作图片
    table_info = str(table)
    space = 5
    current_dir = os.path.join(os.path.dirname(__file__), 'simhei.ttf')
    font = ImageFont.truetype(current_dir, 20, encoding='utf-8')
    im = Image.new('RGB',(10, 10),(255, 255, 255, 0))
    draw = ImageDraw.Draw(im, 'RGB')
    img_size = draw.multiline_textsize(table_info, font=font)
    im_new = im.resize((img_size[0]+space*2, img_size[1]+space*2))
    del draw, im
    draw = ImageDraw.Draw(im_new, 'RGB')
    draw.multiline_text((space,space), table_info, fill=(0, 0, 0), font=font)
    save_dir = R.img('clan_rank_tw').path
    path_dir = os.path.join(save_dir, filename_tmp)
    im_new.save(path_dir, 'PNG')
    del draw