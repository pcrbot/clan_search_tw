from .search import *
from .lock import *
import os
import shutil
import re
from hoshino import Service, R, priv
from hoshino.util import FreqLimiter

# 存在目录就删除目录重建文件夹，不存在则创建文件夹
if os.path.exists(R.img('clan_rank_tw').path):
    shutil.rmtree(R.img('clan_rank_tw').path)
    os.mkdir(R.img('clan_rank_tw').path)
else:
    os.mkdir(R.img('clan_rank_tw').path)

_limtime = 5    # 单个人查询冷却时间（单位：喵）
_flmt = FreqLimiter(_limtime)
sv_help = '''命令如下，注意空格别漏：

[查档线 1] 查看档线，数字为服务器编号(1/2/3/4)

[查公会 1 公会名] 按照公会名搜索公会排名，数字为服务器编号(1/2/3/4)

[查会长 1 会长名] 按照会长名搜索公会排名，数字为服务器编号(1/2/3/4)

[查排名 1 排名] 按照排名搜索公会排名，数字为服务器编号(1/2/3/4)

[绑定公会 1 公会名] 绑定QQ群和公会(一群限一个公会，只能管理员和群主绑定)，数字为服务器编号(1/2/3/4)

[解绑公会] 解绑本QQ群和已绑定的公会(只能管理员和群主解绑)

[查询绑定] 查询本QQ群的绑定状态

[公会排名] 查询本QQ群所绑定的公会的排名'''.strip()

sv = Service('clan_rank_tw', help_=sv_help, bundle='台服会战排名查询')
svcl = Service('clan_rank_tw_auto_clean', enable_on_default = True, help_='台服会战排名查询图片自动清理')

#帮助界面
@sv.on_fullmatch('会战排名帮助')
async def help(bot, ev):
    await bot.send(ev, sv_help)

# 图片自动清理
@svcl.scheduled_job('cron', hour='03', minute='00')
async def auto_clean():
    if os.path.exists(R.img('clan_rank_tw').path):
        shutil.rmtree(R.img('clan_rank_tw').path)
        os.mkdir(R.img('clan_rank_tw').path)
    else:
        os.mkdir(R.img('clan_rank_tw').path)

# 查档线
@sv.on_prefix('查档线')
async def search_line(bot, ev):
    uid = ev['user_id']
    if not _flmt.check(uid):
        await bot.send(ev, f'请勿频繁操作，冷却时间为{_limtime}秒！', at_sender=True)
        return
    alltext = ev.message.extract_plain_text()
    if alltext != '1' and alltext != '2' and alltext != '3' and alltext != '4':
        msg = '服务器编号错误！(可选值有：1/2/3/4)'
        await bot.send(ev, msg)
        return
    uptime = get_current_time()
    score_line, filename_tmp = get_score_line(alltext, uptime)
    if score_line['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.send(ev, msg)
        return
    create_img(score_line, filename_tmp)
    line_img = ' '.join(map(str, [
        R.img(f'clan_rank_tw/' + filename_tmp).cqcode,
    ]))
    msg = f'台服 {alltext}服 档线如下：\n时间档：{uptime}\n（数据来自infedg.xyz）\n{line_img}'
    await bot.send(ev, msg)

# 按 公会名 查询排名
@sv.on_prefix('查公会')
async def search_clan(bot, ev):
    uid = ev['user_id']
    if not _flmt.check(uid):
        await bot.send(ev, f'请勿频繁操作，冷却时间为{_limtime}秒！', at_sender=True)
        return
    alltext = ev.message.extract_plain_text()
    info_tmp = re.split(r' ', alltext)
    server = info_tmp[0]
    clan_name = info_tmp[1]
    if server != '1' and server != '2' and server != '3' and server != '4':
        msg = '服务器编号错误！(可选值有：1/2/3/4)'
        await bot.send(ev, msg)
        return
    uptime = get_current_time()
    clan_score, filename_tmp = get_score_clan(server, uptime, clan_name)
    if clan_score['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.send(ev, msg)
        return
    if clan_score['total'] == 0:
        msg = '未查询到信息，请确保公会名正确！'
        await bot.send(ev, msg)
        return
    create_img(clan_score, filename_tmp)
    clan_img = ' '.join(map(str, [
        R.img(f'clan_rank_tw/' + filename_tmp).cqcode,
    ]))
    msg = f'台服 {server}服 公会名查询 “{clan_name}” 结果如下：\n时间档：{uptime}\n（数据来自infedg.xyz）\n{clan_img}'
    await bot.send(ev, msg)

# 按 会长名 查询排名
@sv.on_prefix('查会长')
async def search_leader(bot, ev):
    uid = ev['user_id']
    if not _flmt.check(uid):
        await bot.send(ev, f'请勿频繁操作，冷却时间为{_limtime}秒！', at_sender=True)
        return
    alltext = ev.message.extract_plain_text()
    info_tmp = re.split(r' ', alltext)
    server = info_tmp[0]
    leader_name = info_tmp[1]
    if server != '1' and server != '2' and server != '3' and server != '4':
        msg = '服务器编号错误！(可选值有：1/2/3/4)'
        await bot.send(ev, msg)
        return
    uptime = get_current_time()
    clan_score, filename_tmp = get_score_leader(server, uptime, leader_name)
    if clan_score['total'] == 0:
        msg = '未查询到信息，请确保会长名正确！'
        await bot.send(ev, msg)
        return
    create_img(clan_score, filename_tmp)
    leader_img = ' '.join(map(str, [
        R.img(f'clan_rank_tw/' + filename_tmp).cqcode,
    ]))
    msg = f'台服 {server}服 会长名查询 “{leader_name}” 结果如下：\n时间档：{uptime}\n（数据来自infedg.xyz）\n{leader_img}'
    await bot.send(ev, msg)

# 按 排名 查询公会
@sv.on_prefix('查排名')
async def search_rank(bot, ev):
    uid = ev['user_id']
    if not _flmt.check(uid):
        await bot.send(ev, f'请勿频繁操作，冷却时间为{_limtime}秒！', at_sender=True)
        return
    alltext = ev.message.extract_plain_text()
    info_tmp = re.split(r' ', alltext)
    server = info_tmp[0]
    rank = info_tmp[1]
    if server != '1' and server != '2' and server != '3' and server != '4':
        msg = '服务器编号错误！(可选值有：1/2/3/4)'
        await bot.send(ev, msg)
        return
    try:
        rank_tmp = int(rank)
    except:
        msg = '排名必须为正整数！'
        await bot.send(ev, msg)
        return
    if rank_tmp >= 3000 or rank_tmp <= 0:
        msg = '暂且仅支持 0 < rank <= 3000 排名的公会!'
        await bot.send(ev, msg)
        return
    uptime = get_current_time()
    clan_score, filename_tmp = get_score_rank(server, uptime, rank)
    if clan_score['total'] == 0:
        msg = '未查询到信息，请确保该排名下有公会存在！'
        await bot.send(ev, msg)
        return
    create_img(clan_score, filename_tmp)
    rank_img = ' '.join(map(str, [
        R.img(f'clan_rank_tw/' + filename_tmp).cqcode,
    ]))
    msg = f'台服 {server}服 会长名查询 “{rank}” 结果如下：\n时间档：{uptime}\n（数据来自infedg.xyz）\n{rank_img}'
    await bot.send(ev, msg)

# 绑定公会
@sv.on_prefix('绑定公会')
async def locked_clan(bot, ev):
    if (not priv.check_priv(ev, priv.ADMIN)) and (not priv.check_priv(ev, priv.SUPERUSER)) and (not priv.check_priv(ev, priv.OWNER)):
        msg = '绑定功能仅限群主和管理员'
        await bot.send(ev, msg)
        return
    uid = ev['user_id']
    group_id = ev['group_id']
    if not _flmt.check(uid):
        await bot.send(ev, f'请勿频繁操作，冷却时间为{_limtime}秒！', at_sender=True)
        return
    alltext = ev.message.extract_plain_text()
    info_tmp = re.split(r' ', alltext)
    server = info_tmp[0]
    clan_name = info_tmp[1]
    if server != '1' and server != '2' and server != '3' and server != '4':
        msg = '服务器编号错误！(可选值有：1/2/3/4)'
        await bot.send(ev, msg)
        return
    uptime = get_current_time()
    clan_score, filename_tmp = get_score_clan(server, uptime, clan_name)
    if clan_score['state'] != 'success':
        msg = '出现异常，请尝试重新输入命令！'
        await bot.send(ev, msg)
        return
    if clan_score['total'] == 0:
        msg = '未查询到公会，请确保公会名正确！'
        await bot.send(ev, msg)
        return
    elif clan_score['total'] == 1:
        msg,flag = judge_lock(group_id)
        if flag == 1:
            msg = msg + f'\n因此请勿重复绑定'
            await bot.send(ev, msg)
            return
        msg = lock_clan(server, clan_name, group_id)
        await bot.send(ev, msg)
    else:
        msg = '查询到该名字为前缀的公会有多个，请确保公会名精确！（后续添加触发选择公会的函数）'
        await bot.send(ev, msg)
        return

# 解绑公会
@sv.on_fullmatch('解绑公会')
async def unlocked_clan(bot, ev):
    if (not priv.check_priv(ev, priv.ADMIN)) and (not priv.check_priv(ev, priv.SUPERUSER)) and (not priv.check_priv(ev, priv.OWNER)):
        msg = '解绑功能仅限群主和管理员'
        await bot.send(ev, msg)
        return
    group_id = ev['group_id']
    msg,flag = judge_lock(group_id)
    if flag == 0:
        msg = msg + f'\n因此请先绑定公会'
        await bot.send(ev, msg)
        return
    msg = unlock_clan(group_id)
    await bot.send(ev, msg)

# 查看公会绑定状态
@sv.on_fullmatch('查询绑定')
async def lock_status(bot, ev):
    group_id = ev['group_id']
    msg,flag = judge_lock(group_id)
    await bot.send(ev, msg)

# 适用于绑定公会后的查询排名信息
@sv.on_fullmatch('公会排名')
async def search_locked(bot, ev):
    group_id = ev['group_id']
    msg,flag = judge_lock(group_id)
    if flag == 0:
        msg = msg + f'\n因此请先绑定公会'
        await bot.send(ev, msg)
        return
    clan_name_list = re.findall(r'“.+”', msg)
    for clan_name in clan_name_list:
        clan_name = clan_name.replace('“', '')
        clan_name = clan_name.replace('”', '')
    server_list = re.findall(r'成功绑定.服公会', msg)
    for server in server_list:
        server = server.replace('成功绑定', '')
        server = server.replace('服公会', '')
    uptime = get_current_time()
    clan_score, filename_tmp = get_score_clan(server, uptime, clan_name)
    info_data = clan_score
    allid = info_data['data'].keys()
    for id in allid:
        rank = info_data['data'][str(id)]['rank']
        clan_name = info_data['data'][str(id)]['clan_name']
        member_num = info_data['data'][str(id)]['member_num']
        leader_name = info_data['data'][str(id)]['leader_name']
        damage = info_data['data'][str(id)]['damage']
        lap = info_data['data'][str(id)]['lap']
        boss_id = info_data['data'][str(id)]['boss_id']
        remain = info_data['data'][str(id)]['remain']
        grade_rank = info_data['data'][str(id)]['grade_rank']
    msg = f'公会名：{clan_name}\n时间档：{uptime}\n排名：{rank}'
    msg = msg + f'\n会长：{leader_name}\n人数：{member_num}人\n分数：{damage}'
    msg = msg + f'\n周目：{lap}周目\n当前BOSS：{boss_id}\n剩余血量：{remain}\n上期排名：{grade_rank}'
    await bot.send(ev, msg)