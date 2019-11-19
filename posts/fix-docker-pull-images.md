# 解决 docker 拉取镜像被墙的问题

Tags: `<docker>`

1. 设置 docker 为热更新状态
```shell
$ vim /etc/docker/daemon.json

# 新增配置
"live-restore": true
```

2. 设置 docker 环境变量
```shell
$ vim /usr/lib/systemd/system/docker.service

# 新增变量
Environment="HTTPS_PROXY=192.168.2.1:1087"
Environment="NO_PROXY=127.0.0.0/8,192.168.2.0/24"
```

3. 同步镜像到其他节点
```shell
$ docker save image-name:tag | bzip2 | pv | ssh other-node “cat | docker load”
```

