from .search import *
import os
import shutil
import re
from hoshino import Service, R
from hoshino.util import FreqLimiter

# 存在目录就删除目录重建文件夹，不存在则创建文件夹
if os.path.exists(R.img('clan_rank_tw').path):
    shutil.rmtree(R.img('clan_rank_tw').path)
    os.mkdir(R.img('clan_rank_tw').path)
else:
    os.mkdir(R.img('clan_rank_tw').path)

_flmt = FreqLimiter(5)
sv_help = '''命令如下，注意空格别漏：

[查档线 1] 查看档线，数字为服务器编号(1/2/3/4)

[查公会 1 公会名] 按照公会名搜索公会排名，数字为服务器编号(1/2/3/4)

[查会长 1 会长名] 按照会长名搜索公会排名，数字为服务器编号(1/2/3/4)

[查排名 1 排名] 按照排名搜索公会排名，数字为服务器编号(1/2/3/4)'''.strip()

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
        await bot.send(ev, '请勿频繁操作，冷却时间为5秒！', at_sender=True)
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
async def search_line(bot, ev):
    uid = ev['user_id']
    if not _flmt.check(uid):
        await bot.send(ev, '请勿频繁操作，冷却时间为5秒！', at_sender=True)
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
async def search_line(bot, ev):
    uid = ev['user_id']
    if not _flmt.check(uid):
        await bot.send(ev, '请勿频繁操作，冷却时间为5秒！', at_sender=True)
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
async def search_line(bot, ev):
    uid = ev['user_id']
    if not _flmt.check(uid):
        await bot.send(ev, '请勿频繁操作，冷却时间为5秒！', at_sender=True)
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
    if int(rank) >= 3000 or int(rank) <= 0:
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