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

