import yaml
import os

# 绑定公会
def lock_clan(server, clan_name, group_id):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    file = open(current_dir, 'r', encoding="UTF-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)

    data = {'user': {
        'group_id': group_id, 
        'clan_name': clan_name}}
    config[server].append(data)
    with open(current_dir, "w", encoding="UTF-8") as f:
        yaml.dump(config, f,allow_unicode=True)
    msg = f'QQ群：{group_id} 已成功绑定{server}服公会“{clan_name}”'
    return msg

# 多个绑定选择触发
def select_all_clan(clan_score):
    num = clan_score['total']
    msg = '查询到该名字为前缀的公会如下:'
    for num_id in range(num):
        data_id = list(clan_score['data'].keys())[num_id]
        clan_name = clan_score['data'][data_id]['clan_name']
        msg = msg + '\n' + str(num_id + 1) + '. ' + str(clan_name)
    return msg

# 解绑公会
def unlock_clan(group_id):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    file = open(current_dir, 'r', encoding="UTF-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)

    for server in range(1, 5):
        server = str(server)
        for user in config[server]:
            if str(user['user']['group_id']) == str(group_id):
                    data = {'user': {
                        'group_id': user['user']['group_id'], 
                        'clan_name': user['user']['clan_name']}}
                    config[server].remove(data)
                    with open(current_dir, "w", encoding="UTF-8") as f:
                        yaml.dump(config, f,allow_unicode=True)
    msg = f'QQ群：{group_id} 已成功解绑公会'
    return msg

# 查询公会绑定
def judge_lock(group_id):
    current_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    file = open(current_dir, 'r', encoding="UTF-8")
    file_data = file.read()
    file.close()
    config = yaml.load(file_data, Loader=yaml.FullLoader)
    flag = 0
    for server in range(1, 5):
        server = str(server)
        for user in config[server]:
            if str(user['user']['group_id']) == str(group_id):
                clan_name = user['user']['clan_name']
                msg = f'本群：{group_id} 已成功绑定{server}服公会“{clan_name}”'
                flag = 1
    if flag == 0:
        msg = f'本群：{group_id} 暂未绑定任何公会'
    return msg, flag