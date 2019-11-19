# CentOS 时间同步

Tags: `<CentOS>`

1. 安装 ntp, ntpdate
```shell
$ yum install ntp ntpdate
```

2. 设置 ntpd 为开机启动
```shell
$ systemctl start ntpd
$ systemctl enable ntpd
```

3. 修改 /etc/ntp.conf 文件
```shell
$ vim /etc/ntpd.conf

server ntp1.aliyun.com iburst
server ntp2.aliyun.com iburst
server ntp3.aliyun.com iburst
server ntp4.aliyun.com iburst
server ntp5.aliyun.com iburst
server ntp6.aliyun.com iburst
server ntp7.aliyun.com iburst
```

4. 重启 ntpd 服务
```shell
$ systemctl restart ntpd
```

