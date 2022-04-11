import os
import json
import shutil
import asyncio

from .lock import move_config, lock_clan, select_all_clan, unlock_clan, judge_lock
from .search import set_source, get_source, get_current_time, create_img, get_search_rank
from hoshino import Service, R, priv

# 首次启动本插件的时候创建配置文件
con_info = {
    'source': 'layvtwt.top',
    'bind': {}
}
current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
if not os.path.exists(current_dir):
    with open(current_dir, 'w', encoding='UTF-8') as f:
        json.dump(con_info, f, indent=4, ensure_ascii=False)
    # 若是旧版更新而来，则数据移至新配置文件
    old_con_dir = os.path.join(os.path.dirname(__file__), 'config.yml')
    if os.path.exists(old_con_dir):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(move_config(current_dir, old_con_dir))

# 每次启动hoshino的时候自动清除一下历史图片
if os.path.exists(R.img('clan_rank_tw').path):
    shutil.rmtree(R.img('clan_rank_tw').path)
    os.mkdir(R.img('clan_rank_tw').path)
else:
    os.mkdir(R.img('clan_rank_tw').path)

sv_help = '''
命令如下，注意空格别漏
注：查公会、查会长、查排名可以选择(1/2/3/4/all)，其中all为全服查询

[选择会战数据源 1] 选择数据源：1."infedg.xyz" 2."layvtwt.top" ，默认为 2 (该功能限维护组)

[查看会战数据源] 查看当前使用的数据源

[查档线 1] 查看档线，数字为服务器编号(1/2/3/4)

[查公会 1 公会名] 按照公会名搜索公会排名，数字为服务器编号(1/2/3/4/all)

[查会长 1 会长名] 按照会长名搜索公会排名，数字为服务器编号(1/2/3/4/all)

[查排名 1 排名] 按照排名搜索公会排名，数字为服务器编号(1/2/3/4/all)

[绑定公会 1 公会名] 绑定QQ群和公会(一群限一个公会，只能管理员和群主绑定)，数字为服务器编号(1/2/3/4)

[解绑公会] 解绑本QQ群和已绑定的公会(只能管理员和群主解绑)

[查询绑定] 查询本QQ群的绑定状态

[公会排名] 查询本QQ群所绑定的公会的排名
'''.strip()

sv = Service('clan_rank_tw', help_=sv_help, bundle='台服会战排名查询')

#帮助界面
@sv.on_fullmatch('会战排名帮助')
async def help(bot, ev):
    await bot.send(ev, sv_help)

# 选择数据源
@sv.on_prefix('选择会战数据源')
async def select_source(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '选择数据源功能仅限维护组'
        await bot.finish(ev, msg)
    alltext = ev.message.extract_plain_text()
    if alltext not in ['1', '2']:
        msg = '数据源编号错误！\n可选值有(1/2)其中：\n1."infedg.xyz"\n2."layvtwt.top"'
        await bot.finish(ev, msg)
    else:
        try:
            source = await set_source(alltext)
            msg = f'当前数据源成功切换至：{source}'
            await bot.send(ev, msg)
        except:
            msg = f'数据源切换失败，请重新尝试！'
            await bot.send(ev, msg)

# 查看数据源
@sv.on_fullmatch('查看会战数据源')
async def view_source(bot, ev):
    source = await get_source()
    msg = f'您当前选择的数据源是：{source}'
    await bot.send(ev, msg)

# 查档线
@sv.on_prefix('查档线')
async def search_line(bot, ev):
    alltext = ev.message.extract_plain_text()
    if alltext not in ['1', '2', '3', '4']:
        msg = '服务器编号错误！(可选值有：1/2/3/4)'
        await bot.finish(ev, msg)
    source = await get_source()
    uptime = await get_current_time(alltext, source)
    await asyncio.sleep(0.5)
    score_line, filename_tmp = await get_search_rank(alltext, uptime, source, 'scoreline')
    if score_line['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.finish(ev, msg)
    await create_img(score_line, filename_tmp, False)
    line_img = R.img(f'clan_rank_tw/' + filename_tmp).cqcode
    msg = f'台服 {alltext}服 档线如下：\n时间档：{uptime}\n（数据来自{source}）\n{line_img}'
    await bot.send(ev, msg)

# 按 公会名 查询排名
@sv.on_prefix('查公会')
async def search_clan(bot, ev):
    alltext = ev.message.extract_plain_text()
    info_tmp = alltext.split(' ', 1)
    server = info_tmp[0]
    clan_name = info_tmp[1]
    if server not in ['1', '2', '3', '4', 'all']:
        msg = '服务器编号错误！(可选值有：1/2/3/4/all)'
        await bot.finish(ev, msg)
    is_all = True if server == 'all' else False
    server = 'merge' if server == 'all' else server
    source = await get_source()
    if source == 'infedg.xyz' and server == 'merge':
        await bot.finish(ev, f'{source}暂不支持全服查询，请数据源更换至 layvtwt.top')
    uptime = await get_current_time(server, source)
    await asyncio.sleep(0.5)
    clan_score, filename_tmp = await get_search_rank(server, uptime, source, 'clan_name', clan_name)
    if clan_score['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.finish(ev, msg)
    if clan_score['total'] == 0:
        msg = '未查询到信息，请确保公会名正确！'
        await bot.finish(ev, msg)
    await create_img(clan_score, filename_tmp, is_all)
    clan_img = R.img(f'clan_rank_tw/' + filename_tmp).cqcode
    server = '全' if server == 'merge' else server
    msg = f'台服 {server}服 公会名查询 “{clan_name}” 结果如下：\n时间档：{uptime}\n（数据来自{source}）\n{clan_img}'
    await bot.send(ev, msg)

# 按 会长名 查询排名
@sv.on_prefix('查会长')
async def search_leader(bot, ev):
    alltext = ev.message.extract_plain_text()
    info_tmp = alltext.split(' ', 1)
    server = info_tmp[0]
    leader_name = info_tmp[1]
    if server not in ['1', '2', '3', '4', 'all']:
        msg = '服务器编号错误！(可选值有：1/2/3/4/all)'
        await bot.finish(ev, msg)
    is_all = True if server == 'all' else False
    server = 'merge' if server == 'all' else server
    source = await get_source()
    if source == 'infedg.xyz' and server == 'merge':
        await bot.finish(ev, f'{source}暂不支持全服查询，请数据源更换至 layvtwt.top')
    uptime = await get_current_time(server, source)
    await asyncio.sleep(0.5)
    clan_score, filename_tmp = await get_search_rank(server, uptime, source, 'leader_name', leader_name)
    if clan_score['total'] == 0:
        msg = '未查询到信息，请确保会长名正确！'
        await bot.finish(ev, msg)
    await create_img(clan_score, filename_tmp, is_all)
    leader_img = R.img(f'clan_rank_tw/' + filename_tmp).cqcode
    server = '全' if server == 'merge' else server
    msg = f'台服 {server}服 会长名查询 “{leader_name}” 结果如下：\n时间档：{uptime}\n（数据来自{source}）\n{leader_img}'
    await bot.send(ev, msg)

# 按 排名 查询公会
@sv.on_prefix('查排名')
async def search_rank(bot, ev):
    alltext = ev.message.extract_plain_text()
    info_tmp = alltext.split(' ', 1)
    server = info_tmp[0]
    rank = info_tmp[1]
    if server not in ['1', '2', '3', '4', 'all']:
        msg = '服务器编号错误！(可选值有：1/2/3/4/all)'
        await bot.finish(ev, msg)
    try:
        rank_tmp = int(rank)
    except:
        msg = '排名必须为正整数！'
        await bot.finish(ev, msg)
    if rank_tmp >= 3000 or rank_tmp <= 0:
        msg = '暂且仅支持 0 < rank <= 3000 排名的公会!'
        await bot.finish(ev, msg)
    is_all = True if server == 'all' else False
    server = 'merge' if server == 'all' else server
    source = await get_source()
    if source == 'infedg.xyz' and server == 'merge':
        await bot.finish(ev, f'{source}暂不支持全服查询，请数据源更换至 layvtwt.top')
    uptime = await get_current_time(server, source)
    await asyncio.sleep(0.5)
    clan_score, filename_tmp = await get_search_rank(server, uptime, source, 'rank', rank)
    if clan_score['total'] == 0:
        msg = '未查询到信息，请确保该排名下有公会存在！'
        await bot.finish(ev, msg)
    await create_img(clan_score, filename_tmp, is_all)
    rank_img = R.img(f'clan_rank_tw/' + filename_tmp).cqcode
    server = '全' if server == 'merge' else server
    msg = f'台服 {server}服 会长名查询 “{rank}” 结果如下：\n时间档：{uptime}\n（数据来自{source}）\n{rank_img}'
    await bot.send(ev, msg)

# 绑定公会
@sv.on_prefix('绑定公会')
async def locked_clan(bot, ev):
    if (not priv.check_priv(ev, priv.ADMIN)) and (not priv.check_priv(ev, priv.SUPERUSER)) and (not priv.check_priv(ev, priv.OWNER)):
        msg = '绑定功能仅限群主和管理员'
        await bot.finish(ev, msg)
    group_id = str(ev['group_id'])
    alltext = ev.message.extract_plain_text()
    info_tmp = alltext.split(' ', 1)
    server = info_tmp[0]
    clan_name = info_tmp[1]
    if server not in ['1', '2', '3', '4']:
        msg = '服务器编号错误！(可选值有：1/2/3/4)'
        await bot.finish(ev, msg)
    source = await get_source()
    uptime = await get_current_time(server, source)
    await asyncio.sleep(0.5)
    clan_score, filename_tmp = await get_search_rank(server, uptime, source, 'clan_name', clan_name)
    if clan_score['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.finish(ev, msg)
    if clan_score['total'] == 0:
        msg = '未查询到公会，请确保公会名正确！'
        await bot.finish(ev, msg)
    elif clan_score['total'] == 1:
        msg, flag = await judge_lock(group_id)
        if flag:
            msg += f'\n因此请勿重复绑定'
        await bot.finish(ev, msg)
        msg = await lock_clan(server, clan_name, group_id)
        await bot.send(ev, msg)
    else:
        msg = await select_all_clan(clan_score)
        msg += '\n\n该功能需精确的公会名，因此请尝试重新输入命令！'
        await bot.send(ev, msg)

# 解绑公会
@sv.on_fullmatch('解绑公会')
async def unlocked_clan(bot, ev):
    if (not priv.check_priv(ev, priv.ADMIN)) and (not priv.check_priv(ev, priv.SUPERUSER)) and (not priv.check_priv(ev, priv.OWNER)):
        msg = '解绑功能仅限群主和管理员'
        await bot.finish(ev, msg)
    group_id = ev['group_id']
    msg, flag = await judge_lock(group_id)
    if not flag:
        msg += f'\n因此请先绑定公会'
        await bot.finish(ev, msg)
    msg = await unlock_clan(group_id)
    await bot.send(ev, msg)

# 查看公会绑定状态
@sv.on_fullmatch('查询绑定')
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
        await bot.finish(ev, msg)
    current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(current_dir, 'r', encoding='UTF-8') as f:
        f_data = json.load(f)
    server = f_data['bind'][group_id]['server']
    clan_name = f_data['bind'][group_id]['clan_name']
    source = await get_source()
    uptime = await get_current_time(server, source)
    await asyncio.sleep(0.5)
    info_data, filename_tmp = await get_search_rank(server, uptime, source, 'clan_name', clan_name)
    allid = info_data['data'].keys()
    for id in allid:
        rank = info_data['data'][str(id)]['rank']
        clan_name = info_data['data'][str(id)]['clan_name']
        member_num = str(info_data['data'][str(id)]['member_num']).replace('.0', '')
        leader_name = info_data['data'][str(id)]['leader_name']
        damage = info_data['data'][str(id)]['damage']
        lap = info_data['data'][str(id)]['lap']
        boss_id = info_data['data'][str(id)]['boss_id']
        remain = info_data['data'][str(id)]['remain']
        grade_rank = str(info_data['data'][str(id)]['grade_rank']).replace('.0', '')
    msg = f'公会名：{clan_name}\n时间档：{uptime}\n排名：{rank}'
    msg += f'\n会长：{leader_name}\n人数：{member_num}人\n分数：{damage}'
    msg += f'\n周目：{lap}周目\n当前BOSS：{boss_id}\n剩余血量：{remain}\n上期排名：{grade_rank}'
    await bot.send(ev, msg)