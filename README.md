## clan_search_tw

一个适用hoshinobot的 公主连结 台服公会战 排名查询 插件

本插件仅供学习研究使用，插件免费，请勿用于违法商业用途，一切后果自己承担

## 项目地址：

https://github.com/pcrbot/clan_search_tw

## 注意

## 数据来自 https://kyaru.infedg.xyz

支持其他数据源，需要在`data_source.json`中填入后，使用命令切换一下数据源即可，如果有新的数据源可向本项目提交PR

```
        "layvtwt.top": { // 数据源名字，随便写即可
            "api": "https://rank.layvtwt.top/api", // 数据请求接口
            "domain": "rank.layvtwt.top", // 完整域名
            "remarks": "目前唯一可用数据源" // 备注
        }
```

## 最近四条更新日志

24-07-06    v3.2    重构垃圾代码，需要删除旧项目重新安装

23-07-03    v3.1    适配合服后的三服、四服查询

22-04-11    v3.0    新增全服查询[issue #11](https://github.com/pcrbot/clan_search_tw/issues/11)，仅限layvtwt.top数据源，同时重构部分代码，优化数据结构，更换数据存储形式，规范化存储库，添加GPL3.0协议

21-08-01    v2.4    新增绑定公会时前缀同名的提醒(选择功能好像不会写，欸嘿嘿，后续再说吧)

<details>
<summary>更以前的更新日志</summary>

21-07-31    v2.3    新增数据源 layvtwt.top 并默认使用，妈妈再也不用担心我的数据不更新了（

21-07-30    v2.2    修复时间档异常导致查询出错的问题

21-07-28    v2.1    修复图片缩进问题，并将绑定公会后的查询改为文字描述，（注意：不绑定公会的三个查询支持模糊搜索）

21-07-26    v2      新增公会绑定查询相关功能，v2开始多了文件`lock.py`和`config.yml`建议重新git clone一下，yml里面的样例别删不然报错，公会同名选择功能在咕了

21-07-26    v1.1    修了几个小问题，然后`__init__.py`最上方可以自己修改查询冷却

21-07-13    v1.0    大概能用了？

</details>

## 如何更新

```
git pull
```

## 功能

```
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
```

## 食用教程

1. git clone本插件：

在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目
```
git clone https://github.com/pcrbot/clan_search_tw
```

2. 安装依赖：

到HoshinoBot\hoshino\modules\destiny2_hoshino_plugin目录下，打开powershell运行
```
pip install -r requirements.txt -i https://repo.huaweicloud.com/repository/pypi/simple
```

3. 在 HoshinoBot\hoshino\config\ `__bot__.py` 文件的 MODULES_ON 加入 'clan_search_tw'

然后重启 HoshinoBot即可使用
