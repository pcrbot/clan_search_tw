## clan_search_tw

一个适用hoshinobot的 公主连结 台服公会战 排名查询 插件

本插件仅供学习研究使用，插件免费，请勿用于违法商业用途，一切后果自己承担

## 项目地址：

https://github.com/pcrbot/clan_search_tw

## 注意

## 数据来自 https://kyaru.infedg.xyz/tw 和 https://rank.layvtwt.top/ （已获两位作者授权）

插件后续将继续在 github 更新，欢迎提交 isuue 和 Pull request

问题说明：插件支持两个数据源，默认第二个：https://kyaru.infedg.xyz/tw 和 https://rank.layvtwt.top/

## 最近四条更新日志

23-07-03    v3.1    适配合服后的三服、四服查询

22-04-11    v3.0    新增全服查询[issue #11](https://github.com/pcrbot/clan_search_tw/issues/11)，仅限layvtwt.top数据源，同时重构部分代码，优化数据结构，更换数据存储形式，规范化存储库，添加GPL3.0协议

21-08-01    v2.4    新增绑定公会时前缀同名的提醒(选择功能好像不会写，欸嘿嘿，后续再说吧)

21-07-31    v2.3    新增数据源 layvtwt.top 并默认使用，妈妈再也不用担心我的数据不更新了（

<details>
<summary>更以前的更新日志</summary>

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

#### 更新小提示

由于v3.0后更换存储格式，因此原先的 `config.yml` 和 `source.txt` 已经不需要了，因此插件会再更新后再次重启hoshino的时候自动移动数据和删除旧版文件，下次再更新的时候会自动忽略这俩文件。

如果更新后启动报错：
```
ModuleNotFoundError: No module named 'hoshino.modules.clan_search_tw.source'
```
则关闭hoshinobot再次启动即可

## 功能

```
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
