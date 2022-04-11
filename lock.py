import yaml
import json
import os
import asyncio

# 将数据移至新配置文件
async def move_config(current_dir, old_con_dir):
    # 读取旧数据
    with open(old_con_dir, 'r', encoding='UTF-8') as f:
        file_data = f.read()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    data = {}
    for server in range(1, 5):
        server = str(server)
        for user in config[server]:
            if user['user']['clan_name'] != '样例：公会名字':
                group_id = str(user['user']['group_id'])
                data[group_id] = {}
                data[group_id]['server'] = server
                data[group_id]['clan_name'] = user['user']['clan_name']
    # 写入新数据
    with open(current_dir, 'r', encoding='UTF-8') as af:
        f_data = json.load(af)
    f_data['bind'] = data
    with open(current_dir, 'w', encoding='UTF-8') as f:
        json.dump(f_data, f, indent=4, ensure_ascii=False)
    # 删除旧数据文件
    asyncio.sleep(2)
    os.remove(os.path.join(os.path.dirname(__file__), 'config.yml'))
    os.remove(os.path.join(os.path.dirname(__file__), 'source.txt'))

# 绑定公会
async def lock_clan(server, clan_name, group_id):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(current_dir, 'r', encoding='UTF-8') as af:
        f_data = json.load(af)
    f_data['bind'][group_id] = {}
    f_data['bind'][group_id]['server'] = server
    f_data['bind'][group_id]['clan_name'] = clan_name
    with open(current_dir, 'w', encoding='UTF-8') as f:
        json.dump(f_data, f, indent=4, ensure_ascii=False)
    msg = f'QQ群：{group_id} 已成功绑定{server}服公会“{clan_name}”'
    return msg

# 多个绑定选择触发
async def select_all_clan(clan_score):
    num = clan_score['total']
    msg = '查询到该名字为前缀的公会如下:'
    for num_id in range(num):
        data_id = list(clan_score['data'].keys())[num_id]
        clan_name = clan_score['data'][data_id]['clan_name']
        msg = msg + '\n' + str(num_id + 1) + '. ' + str(clan_name)
    return msg

# 解绑公会
async def unlock_clan(group_id):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(current_dir, 'r', encoding='UTF-8') as af:
        f_data = json.load(af)
    clan_name = f_data['bind'][group_id]['clan_name']
    f_data['bind'].pop(group_id)
    with open(current_dir, 'w', encoding='UTF-8') as f:
        json.dump(f_data, f, indent=4, ensure_ascii=False)
    msg = f'QQ群：{group_id} 已成功解绑公会"{clan_name}"'
    return msg

# 查询公会绑定
async def judge_lock(group_id):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(current_dir, 'r', encoding='UTF-8') as af:
        f_data = json.load(af)
    if group_id in list(f_data['bind'].keys()):
        server = f_data['bind'][group_id]['server']
        clan_name = f_data['bind'][group_id]['clan_name']
        msg = f'本群：{group_id} 已成功绑定{server}服公会“{clan_name}”'
        return msg, True
    else:
        msg = f'本群：{group_id} 暂未绑定任何公会'
        return msg, False