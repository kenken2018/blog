# k8s 中使用 nfs-storageclass 持久化数据

Tags: `<nfs>` `<k8s>` `<storageclass>`

在 Kubernetes 中有三种资源对象用来描述持久化存储，PresistentVloume(PV)/PresistentVolumeClaim(PVC)/StroageClass 

## 概念篇

### PV

PV 是后端存储实体，持久化卷。PV 包含存储类型，存储大小和访问模式，生命周期独立于 Pod（不然怎么叫持久化存储呢...），目前 Kubernetes 支持以下的 PV 类型

* awsElasticBlockStore
* azureDisk
* azureFile
* cephfs
* cinder
* configMap
* csi
* downwardAPI
* emptyDir
* fc (fibre channel)
* flexVolume
* flocker
* gcePersistentDisk
* gitRepo (deprecated)
* glusterfs
* hostPath
* iscsi
* local
* nfs
* persistentVolumeClaim
* projected
* portworxVolume
* quobyte
* rbd
* scaleIO
* secret
* storageos
* vsphereVolume

每种类型的具体介绍请参考 [https://kubernetes.io/docs/concepts/storage/volumes/](https://kubernetes.io/docs/concepts/storage/volumes/)。在这里就不一一赘述了。

### PVC

PVC 是持久化卷声明，描述所期待的 PV 资源对象，也就是说，要使用持久化存储必须使用 PVC 来声明。

### StroageClass

StroageClass 是用于动态分配持久化卷的资源对象，毕竟如果每次需要使用挂载一个持久化卷都要先创建一个 PV，然后再创建一个 PVC 来绑定对应的 PV，还是比较麻烦的。StroageClass 就是为了解决这个问题而出现的，一个 StroageClass 需要绑定一个后端的 provisioner，provisioner 是描述如何使用 PV，那就有 nfs-provisioner, glusterfs-provisioner 等等，可以理解为一种 PV 类型的控制器。

## 实战篇

### 集群节点安装 nfs-server 以及 nfs-provisioner

#### nfs-server
这部分内容参考我的另一篇博客，[centos-nfs-server.md](./centos-nfs-server.md)

#### nfs-provisioner
Kubernetes 提供了各种 StroageClass 对应的 provisioner，详情可见 [kubernetes-incubator/external-storage](https://github.com/kubernetes-incubator/external-storage)。在这里我们使用的是 [nfs-client](https://github.com/kubernetes-incubator/external-storage/tree/master/nft-client)

创建权限相关资源
```yaml
# nfs-provisioner-rbac.yaml
# kubectl apply -f nfs-provisioner-rbac.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: nfs-client-provisioner
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: nfs-client-provisioner-runner
rules:
  - apiGroups: [""]
    resources: ["persistentvolumes"]
    verbs: ["get", "list", "watch", "create", "delete"]
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    verbs: ["get", "list", "watch", "update"]
  - apiGroups: ["storage.k8s.io"]
    resources: ["storageclasses"]
    verbs: ["get", "list", "watch"]
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "update", "patch"]
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: run-nfs-client-provisioner
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
roleRef:
  kind: ClusterRole
  name: nfs-client-provisioner-runner
  apiGroup: rbac.authorization.k8s.io
---
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
rules:
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["get", "list", "watch", "create", "update", "patch"]
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: leader-locking-nfs-client-provisioner
subjects:
  - kind: ServiceAccount
    name: nfs-client-provisioner
roleRef:
  kind: Role
  name: leader-locking-nfs-client-provisioner
  apiGroup: rbac.authorization.k8s.io
```

部署 provisioner-deployment
```yaml
# nft-provisioner-deployment.yaml
# kubectl apply -f nft-provisioner-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nfs-client-provisioner
  labels:
    app: nfs-client-provisioner
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nfs-client-provisioner
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: nfs-client-provisioner
  template:
    metadata:
      labels:
        app: nfs-client-provisioner
    spec:
      serviceAccountName: nfs-client-provisioner
      containers:
        - name: nfs-client-provisioner
          imagePullPolicy: IfNotPresent
          image: quay.io/external_storage/nfs-client-provisioner:latest
          volumeMounts:
            - name: nfs-client-root
              mountPath: /persistentvolumes
          env:
            - name: PROVISIONER_NAME
              # 自定义 provisioner 名称
              value: nfs-provisioner
            - name: NFS_SERVER
              # 替换为本地 nfs 服务器地址
              value: 192.168.2.11 
            - name: NFS_PATH
              # 替换为本地挂载路径
              value: /mnt 
      volumes:
        - name: nfs-client-root
          nfs:
            # 替换为本地 nfs 服务器地址
            server: 192.168.2.11
            # 替换为本地挂载路径
            path: /mnt
```

检查 provisioner 是否成功创建
```shell
~ 🐶 k get deployments.apps | grep nfs
nfs-client-provisioner   1/1     1            1           23h
``` 

#### nfs-storageclass
接下来创建 nfs-storageclass
```yaml
# nfs-storage.yaml
# kubectl apply -f nfs-storage.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-storage
# 使用上面的自定义名称
provisioner: nfs-provisioner
parameters:
  # archiveOnDelete 指定为 false 表示删除 PVC 后 PV 也会被删除。
  # 如果想在 PVC 被删除后仍旧保留数据的，可指定为 true
  archiveOnDelete: "false"
```

检查 storageclass 是否成功创建
```shell
~ 🐶 k get sc
NAME          PROVISIONER       AGE
nfs-storage   nfs-provisioner   23h
```

### 部署测试服务
万事俱备，就差把需要持久化数据的服务跑起来

```yaml
# nfs-statefulset-app.yaml
# kubectl apply -f nfs-statefulset-app.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: nfs-web
spec:
  serviceName: "nginx"
  replicas: 1
  selector:
    matchLabels:
      app: nfs-web
  template:
    metadata:
      labels:
        app: nfs-web
    spec:
      terminationGracePeriodSeconds: 10
      containers:
      - name: nginx
        image: nginx
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
      annotations:
        # 在这里声明使用我们刚才创建的 storageclass
        volume.beta.kubernetes.io/storage-class: nfs-storage
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

查看 StatefulSet.app 运行情况
```shell
~/k8s/external-storage/nfs-client/deploy 🐶 k get statefulsets.apps -o wide | grep nfs
nfs-web                 1/1     23s    nginx                                                            nginx
```

查看 PV/PVC，可以看到两者都已成功创建并绑定
```shell
~ 🐶 k get pv,pvc
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                   STORAGECLASS   REASON   AGE
persistentvolume/pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1   1Gi        RWO            Delete           Bound    default/www-nfs-web-0   nfs-storage             112s

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/www-nfs-web-0   Bound    pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1   1Gi        RWO            nfs-storage    112s
```

### 验证数据是否持久化
我们可以进入到 nfs-web-pod 容器内去创建一些数据，然后看本地 nfs 挂载点是否会同步更新

查看 pod
```shell
~ 🐶 k get pods | grep nfs-web
nfs-web-0                                 1/1     Running   0          4m15s
```

进入到 pod 内部，并往挂载路径写点东西
```shell
~ 🐶 k exec -it nfs-web-0 /bin/bash
root@nfs-web-0:/# cd /usr/share/nginx/html
root@nfs-web-0:/usr/share/nginx/html# ls
root@nfs-web-0:/usr/share/nginx/html# echo "hello nginx" >> a.txt
root@nfs-web-0:/usr/share/nginx/html# cat a.txt
hello nginx
root@nfs-web-0:/usr/share/nginx/html#
root@nfs-web-0:/usr/share/nginx/html# exit
```

到本机 /mnt 目录看看数据情况
```shell
[root@master ~]# cd /mnt
[root@master mnt]# ls
default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1
[root@master mnt]# cd default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1/
[root@master default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1]# ls
a.txt
[root@master default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1]# cat a.txt
hello nginx
```

完美 😉，不过事情到这里并没有结束，我们需要再一步确认删除 statefulsets.app 后的结果
```shell
~ 🐶 k delete statefulsets.apps nfs-web
statefulset.apps "nfs-web" deleted
~ 🐶 k get pods | grep nfs-web
nfs-web-0                                 0/1     Terminating   0          11m
```

待 pod 被移除后，我们查看下 pv/pvc
```shell
~ 🐶 k get pv,pvc
NAME                                                        CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                   STORAGECLASS   REASON   AGE
persistentvolume/pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1   1Gi        RWO            Delete           Bound    default/www-nfs-web-0   nfs-storage             12m

NAME                                  STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS   AGE
persistentvolumeclaim/www-nfs-web-0   Bound    pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1   1Gi        RWO            nfs-storage    12m
```

没毛病，两个都在。最后一步，检验我们本地 /mnt 的数据是否也是存在
```shell
[root@master mnt]# cd ~
[root@master ~]# cd /mnt
[root@master mnt]# ls
default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1
[root@master mnt]# cd default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1/
[root@master default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1]# ls
a.txt
[root@master default-www-nfs-web-0-pvc-2dc1cd0a-6aaf-4c9d-b9ac-43be2c6afec1]# cat a.txt
hello nginx
```

数据完好无损！✌️
