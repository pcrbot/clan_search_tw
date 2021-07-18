
## 注意

## 数据来自 https://kyaru.infedg.xyz/tw （已获作者授权）

插件后续将继续在github更新，不过我喜欢咕咕咕，其他功能在想了(

插件未经充分测试，尤其是台服现在还没到会战呢，大佬们发现代码有问题可以帮我修改修改

BTW.~~这个插件好写啊，写个一晚就写完了~~（我好菜啊）

## 更新日志

21-07-13    v1.0    大概能用了？

## clan_search_tw

一个适用hoshinobot的 公主连结 台服公会战 排名查询 插件

本插件仅供学习研究使用，插件免费，请勿用于违法商业用途，一切后果自己承担

## 项目地址：
https://github.com/azmiao/clan_search_tw

已放至pcrbot仓库

https://github.com/pcrbot/clan_search_tw

## 功能

```
命令如下，注意空格别漏：

[查档线 1] 查看档线，数字为服务器编号(1/2/3/4)

[查公会 1 公会名] 按照公会名搜索公会排名，数字为服务器编号(1/2/3/4)

[查会长 1 会长名] 按照会长名搜索公会排名，数字为服务器编号(1/2/3/4)

[查排名 1 排名] 按照排名搜索公会排名，数字为服务器编号(1/2/3/4)

其他：

每天凌晨3点自动清理之前的图片
```


## 简单食用教程：

可看下方链接：

https://www.594594.xyz/2021/07/13/clan_search_tw_for_hoshino/

或本页面：

1. 下载或git clone本插件：

在 HoshinoBot\hoshino\modules 目录下使用以下命令拉取本项目
```
git clone https://github.com/azmiao/clan_search_tw
```
2. 安装依赖：

到HoshinoBot\hoshino\modules\destiny2_hoshino_plugin目录下，打开powershell运行
```
pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple
```

3. 在 HoshinoBot\hoshino\config\ `__bot__.py` 文件的 MODULES_ON 加入 'clan_search_tw'

然后重启 HoshinoBot即可使用
