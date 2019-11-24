# Kubernetes Tips

Tags: `<k8s>` `<tips>`

### 如何暂停 deployments？

在 k8s 中 deployments 没有一个明确的暂停概念，也没有 pause 这样的命令，不过我们可以按照 k8s 的使用规则来，既然它会帮我们把系统无限接近我们所期望的状态，那我们把期望状态设置为 0 不就行了。

```shell
# 在集群内跑了一个 4 个实例的 busybox 应用
~ 🐶 k get deployments.apps | grep bbox
bbox                     4/4     4            4           6d

# 将 deployment 缩容为 0
~ 🐶 k scale --replicas=0 deployment bbox
deployment.apps/bbox scaled

# 可以看到 bbox 的 pod 正在被清除
~ 🐶 k get pods | grep bbox
bbox-579fff957d-5ndnn                     1/1     Terminating   3          46h
bbox-579fff957d-g6fsv                     1/1     Terminating   3          46h
bbox-579fff957d-tbk7c                     1/1     Terminating   3          46h
bbox-579fff957d-tgzzm                     1/1     Terminating   3          46h

# 最终会得到一个 0 实例的 deployment 应用
~ 🐶 k get deployments.apps | grep bbox
bbox                     0/0     0            0           6d
```

### 如何在 deployment.spec 没有任何改变的情况下重启 deployment？

个人觉得这个需求也是蛮常见的，比如你变更了一些非代码因素的内容，或者你为了排除问题只想把应用重新启动。

在之前实现方法可谓是多种多样，[kubernetes/issues/13488](https://github.com/kubernetes/kubernetes/issues/13488) 对此进行了一个长达 4 年的讨论，一开始 kubernetes 维护者还不屑于这个需求，如他所愿，得到了很多 👎。不过一般方案是注入一个无实际影响的环境变量，这样就会让 deployment 重新更新一遍。

直到了今年五月份才终于有人实现了这个 feature，加入了 `rollout restart` 命令，这也是社区开发者坚持后的成果吧。

```shell
# 可通过 rollout restart 命令达到重启效果
$ kubectl rollout restart {your_deployment_name}
```

### 新增节点后如何获取加入到集群内的执行语句？

```shell
$ kubeadm token create --print-join-command
```

