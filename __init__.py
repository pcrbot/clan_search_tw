import asyncio
import json
import os
import shutil

from hoshino import Service, R, priv

from .lock import lock_clan, select_all_clan, unlock_clan, judge_lock
from .search import set_source, get_source, get_current_time, create_img, get_search_rank

# 首次启动本插件的时候创建配置文件
current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
if not os.path.exists(current_dir):
    with open(current_dir, 'w', encoding='UTF-8') as f:
        json.dump({}, f, indent=4, ensure_ascii=False)

# 每次启动hoshino的时候自动清除一下历史图片
if os.path.exists(R.img('clan_rank_tw').path):
    shutil.rmtree(R.img('clan_rank_tw').path)
    os.mkdir(R.img('clan_rank_tw').path)
else:
    os.mkdir(R.img('clan_rank_tw').path)

sv_help = '''
命令如下，注意空格别漏

注：查询可选择服(1:台一服, 2:台二三四服, all:全服)

[查档线 1] 查看档线，数字为服务器编号(1/2)

[查公会 1 公会名] 按照公会名搜索公会排名，数字为服务器编号(1/2/all)

[查会长 1 会长名] 按照会长名搜索公会排名，数字为服务器编号(1/2/all)

[查排名 1 排名] 按照排名搜索公会排名，数字为服务器编号(1/2/all)

[绑定公会 1 公会名] 绑定QQ群和公会(一群限一个公会，只能管理员和群主绑定)，数字为服务器编号(1/2)

[解绑公会] 解绑本QQ群和已绑定的公会(只能管理员和群主解绑)

[查询公会绑定] 查询本QQ群的绑定状态

[公会排名] 查询本QQ群所绑定的公会的排名
'''.strip()

sv = Service('clan_rank_tw', help_=sv_help, bundle='台服会战排名查询')


# 帮助界面
@sv.on_fullmatch('会战排名帮助')
async def query_help(bot, ev):
    await bot.send(ev, sv_help)


# 选择数据源
@sv.on_prefix('选择会战数据源')
async def select_source(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '选择数据源功能仅限维护组'
        await bot.finish(ev, msg)
    source_name = str(ev.message).strip()

    success = await set_source(source_name)
    msg = f'当前数据源成功切换至：{source_name}' if success else f'失败！数据源{source_name}未在[data_source.json]中配置'
    await bot.send(ev, msg)


# 查看数据源
@sv.on_fullmatch('查看会战数据源')
async def view_source(bot, ev):
    f_data = await get_source()
    msg = f'您当前选择的数据源是：{f_data["current"]}'
    await bot.send(ev, msg)


# 查档线
@sv.on_prefix('查档线')
async def search_line(bot, ev):
    server = str(ev.message).strip()
    if server not in ['1', '2']:
        msg = '服务器编号错误！(可选值有：1/2)'
        await bot.send(ev, msg)
        return

    f_data = await get_source()
    up_time = await get_current_time(server, f_data)
    await asyncio.sleep(0.5)

    score_line, filename_tmp = await get_search_rank(server, up_time, f_data, 'scoreline')
    if score_line['state'] != 'success':
        msg = '查询数据失败，接口返回失败！'
        await bot.send(ev, msg)
        return

    await create_img(score_line, filename_tmp, False)
    line_img = R.img(f'clan_rank_tw/' + filename_tmp).cqcode
    msg = f'台服 {server}服 档线如下：\n时间档：{up_time}\n（数据来自{f_data["current"]}）\n{line_img}'
    await bot.send(ev, msg)


# 按 公会名 查询排名
@sv.on_prefix('查公会')
async def search_clan(bot, ev):
    await query('公会', 'clan_name', bot, ev)


# 按 会长名 查询排名
@sv.on_prefix('查会长')
async def search_leader(bot, ev):
    await query('会长', 'leader_name', bot, ev)


# 按 排名 查询公会
@sv.on_prefix('查排名')
async def search_rank(bot, ev):
    await query('排', 'rank', bot, ev)


# 实际查询逻辑
async def query(search_type, search_type_code, bot, ev):
    all_text = str(ev.message).strip()
    info_tmp = all_text.split(' ', 1)
    server = info_tmp[0]
    search_name = info_tmp[1]
    if server not in ['1', '2', 'all']:
        msg = '服务器编号错误！(可选值有：1/2/all)'
        await bot.send(ev, msg)
        return

    is_all = True if server == 'all' else False
    server = 'merge' if server == 'all' else server

    f_data = await get_source()
    up_time = await get_current_time(server, f_data)
    await asyncio.sleep(0.5)

    clan_score, filename_tmp = await get_search_rank(server, up_time, f_data, search_type_code, search_name)
    if clan_score['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.send(ev, msg)
        return
    if clan_score['total'] == 0:
        msg = f'未查询到信息，请确保输入{search_type}名[{search_name}]正确！'
        await bot.send(ev, msg)
        return

    await create_img(clan_score, filename_tmp, is_all)
    clan_img = R.img(f'clan_rank_tw/' + filename_tmp).cqcode
    server = '全' if server == 'merge' else server
    msg = f'台服 {server}服 {search_type}名查询 “{search_name}” 结果如下：\n时间档：{up_time}\n（数据来自{f_data["current"]}）\n{clan_img}'
    await bot.send(ev, msg)


# 绑定公会
@sv.on_prefix('绑定公会')
async def locked_clan(bot, ev):
    if ((not priv.check_priv(ev, priv.ADMIN)) and (not priv.check_priv(ev, priv.SUPERUSER)) and
            (not priv.check_priv(ev, priv.OWNER))):
        msg = '绑定功能仅限群主和管理员'
        await bot.send(ev, msg)
        return

    group_id = str(ev['group_id'])
    all_text = str(ev.message).strip()
    info_tmp = all_text.split(' ', 1)
    server = info_tmp[0]
    clan_name = info_tmp[1]
    if server not in ['1', '2']:
        msg = '服务器编号错误！(可选值有：1/2)'
        await bot.send(ev, msg)
        return

    f_data = await get_source()
    up_time = await get_current_time(server, f_data)
    await asyncio.sleep(0.5)

    clan_score, filename_tmp = await get_search_rank(server, up_time, f_data, 'clan_name', clan_name)
    if clan_score['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.send(ev, msg)
        return

    if clan_score['total'] == 0:
        msg = '未查询到公会，请确保公会名正确！'
    elif clan_score['total'] == 1:
        msg, flag = await judge_lock(group_id)
        if flag:
            msg += f'\n因此请勿重复绑定'
            await bot.send(ev, msg)
            return
        msg = await lock_clan(server, clan_name, group_id)
    else:
        msg = await select_all_clan(clan_score)
        msg += '\n\n该功能需精确的公会名，因此请尝试重新输入命令！'
    await bot.send(ev, msg)


# 解绑公会
@sv.on_fullmatch('解绑公会')
async def unlocked_clan(bot, ev):
    if ((not priv.check_priv(ev, priv.ADMIN)) and (not priv.check_priv(ev, priv.SUPERUSER)) and
            (not priv.check_priv(ev, priv.OWNER))):
        msg = '解绑功能仅限群主和管理员'
        await bot.send(ev, msg)
        return

    group_id = ev['group_id']
    msg, flag = await judge_lock(group_id)
    if not flag:
        msg += f'\n因此请先绑定公会'
        await bot.finish(ev, msg)
    msg = await unlock_clan(group_id)
    await bot.send(ev, msg)


# 查看公会绑定状态
@sv.on_fullmatch('查询公会绑定')
async def lock_status(bot, ev):
    group_id = str(ev['group_id'])
    msg, flag = await judge_lock(group_id)
    await bot.send(ev, msg)


# 适用于绑定公会后的查询排名信息
@sv.on_fullmatch('公会排名')
async def search_locked(bot, ev):
    group_id = str(ev['group_id'])
    msg, flag = await judge_lock(group_id)
    if not flag:
        msg += f'\n因此请先绑定公会'
        await bot.send(ev, msg)
        return

    with open(current_dir, 'r', encoding='UTF-8') as af:
        f_data = json.load(af)
    server = f_data[group_id]['server']
    clan_name = f_data[group_id]['clan_name']

    f_data = await get_source()
    up_time = await get_current_time(server, f_data)
    await asyncio.sleep(0.5)

    info_data, filename_tmp = await get_search_rank(server, up_time, f_data, 'clan_name', clan_name)
    clan_list = list(info_data['data'])
    if not clan_list:
        await bot.send(ev, f'无法查询到本群绑定的公会[{clan_name}]')
        return

    clan = clan_list[0]
    rank = clan['rank']
    clan_name = clan['clan_name']
    member_num = str(clan['member_num']).replace('.0', '')
    leader_name = clan['leader_name']
    damage = clan['damage']
    lap = clan['lap']
    boss_id = clan['boss_id']
    remain = clan['remain']
    grade_rank = str(clan['grade_rank']).replace('.0', '')

    msg = f'公会名：{clan_name}\n时间档：{up_time}\n排名：{rank}'
    msg += f'\n会长：{leader_name}\n人数：{member_num}人\n分数：{damage}'
    msg += f'\n周目：{lap}周目\n当前BOSS：{boss_id}\n剩余血量：{remain}\n上期排名：{grade_rank}'
    await bot.send(ev, msg)
