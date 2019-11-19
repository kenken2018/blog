# kubernetes kube-proxy 修改 ipvs 规则

Tags: `<k8s>` `<ipvs>`

1. 查看 kube-proxy 信息
```shell
$ kubectl get pods -n kube-system -o wide | grep proxy
```

2. 使用 kubectl logs 可以看到目前 kube-proxy pod 的 proxy 模式
```shell
$ kubectl logs kube-proxy-4hw9j -n kube-system
```

3. 启动 ipvs 模块
```shell
cat <<EOF > /etc/sysconfig/modules/ipvs.modules 
  #!/bin/bash
  ipvs_modules_dir="/usr/lib/modules/\`uname -r\`/kernel/net/netfilter/ipvs"
  for i in \`ls \$ipvs_modules_dir | sed  -r 's#(.*).ko.xz#\1#'\`; do
      /sbin/modinfo -F filename \$i  &> /dev/null
      if [ \$? -eq 0 ]; then
          /sbin/modprobe \$i
      fi
  done
EOF

chmod +x /etc/sysconfig/modules/ipvs.modules 
bash /etc/sysconfig/modules/ipvs.modules
```

4. 确保所有节点的 ipvs 的模块已经运行
```shell
$ lsmod | grep ip_vs
```

5. 修改 kube-proxy configMap 文件，修改为 ipvs 模式
```shell
$ kubectl edit configmap kube-proxy -n kube-system

+ mode: "ipvs"  # 原来为 mode: ""
```

6. 删除所有 kube-proxy 的 pod，K8S 有自动愈合功能，当 pod 被删除之后，会重启被删除的 pod
```shell
$ kubectl delete pods `kubectl get pods -n kube-system | grep kube-proxy  | awk '{print $1}'` -n kube-system 
```

7. 查看重启后的 kube-proxy pod 的 proxy 模式是否是 ipvs
```shell
$ kubectl get pods -n kube-system -o wide | grep proxy
```

8. 安装 ipvsadm 查看具体的 ipvs 规则
```shell
# 安装 ipvsadm
$ yum install -y ipvsadm

# 查看 ipvsadm 已经启用的规则
# 从 forward 的 masq 标识来看，为 lvs/nat 模式
$ ipvsadm -ln
```

