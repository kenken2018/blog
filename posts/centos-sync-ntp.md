# CentOS 时间同步

Tags: `<CentOS>`

1. 安装 ntpdate
```shell
$ yum install ntpdate
```

2. 设置 ntpdate 开机启动命令
```shell
$ vim /etc/rc.local

+ ntpdate ntp1.aliyun.com
```

3. 对 rc.local 授权
```shell
$ chmod +x /etc/rc.local
```

4. 手动执行一次时间同步
```shell
$ ntpdate ntp1.aliyun.com
```

不过这种方式还是出现了一个问题 😅，当我的 mac 休眠以后，虚拟机也跟着休眠，下次启动恢复快照的时候时间还是休眠那个时刻的。为了解决这个问题，可以将同步命令加入到 crontab 里面。

```shell
$ crontab -e

# 每五分钟同步一次
*/5 * * * * ntpdate ntp1.aliyun.com
```

