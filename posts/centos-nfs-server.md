# CentOS 中搭建 nfs 服务

Tags: `<nfs>`

1. 在所有节点都安装 nfs-utils
```shell
$ yum install nfs-utils -y
```

2. 服务端设置 nfs-server/rpcbind 为开机启动
```shell
# nfs-server
$ systemctl start nfs-server
$ systemctl enable nfs-server

# rpcbind
$ systemctl start rpcbind 
$ systemctl enable rpcbind 
```

3. 服务端设置挂载目录
```shell
$ vim /etc/exports

# 开发测试使用，权限设置得比较高 🤣
+ /mnt    *(rw,async,no_root_squash)

# 导出挂载点
$ exportfs -av
```

4. 查看服务端挂载结果
```shell
$ showmount -e
Export list for master:
/mnt *
```

5. 客户端设置挂载点
```shell
$ showmount -e master
$ mount.nfs master:/mnt /mnt
```

6. 测试是否成功搭建 nfs 服务
```shell
# node1
$ echo "test nfs server" >> /mnt/a.txt

# master
$ cat /mnt/a.txt
```

