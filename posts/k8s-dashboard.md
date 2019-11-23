# k8s 访问 dashboard

Tags: `<k8s>` `<dashboard>` 

### 安装 Kubernetes-dashboard
按照 [kubernetes-dashboard](https://github.com/kubernetes/dashboard) 介绍安装好 dashboard
```shell
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v1.10.1/src/deploy/recommended/kubernetes-dashboard.yaml
```

### 权限相关资源创建
kubernetes-dashboard 需要较大的权限才能够访问所有资源，所以我们可以创建一个 admin-user 的 ServiceAccount 来获取对应的 token

创建 ClusterRoleBinding
```yaml
# admin-clusterrole-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kube-system
```

创建 ServiceAccount
```yaml
# admin-serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-user
  namespace: kube-system
```

获取 ServiceAccount Token 
```shell
~/k8s/dashboard 🐶 kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}')
Name:         admin-user-token-c65l2
Namespace:    kube-system
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: admin-user
              kubernetes.io/service-account.uid: eb3181df-61b3-41c3-a6da-0f29ecab95c0

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1025 bytes
namespace:  11 bytes
token:      eyJhbGciOiJSUzI1NiIZCI6IklZJc3RnNW9EMllSSEQ2Y3EzNTJ1OHNzxdasdashZUUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLWM2NWwyIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJlYjMxODFkZi02MWIzLTQxYzMtYTZkYS0wZjI5ZWNhYjk1YzAiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06YWRtaW4tdXNlciJ9.HsYC2cZfRWm4Aatd98oHvk9aKGKKL_9QIT7zKVlWm6PcU0wKMIOo5hiqC_JLi2RgCg3xfgPUYKbJZtBIXJOVWEEJY8u5i7AK4tE1Rmks9jEbGIgi8QTeCfp3pCtMYk59e4PdJ4WHd36pQGKHdMQTcrHL_8DyrQHotd6eGFAue1pzjCI5l8n0j0j_Oa53pVLAtkL1hrb_O-z8H6SxnxhODcJ2y8SzS7tvRbL1OHCqfscIbSvnZi-virt4jygeJfTypYTkDNxP6zBG3sUP-XG17z30iIdEanawix8s0hmkddV5rgrUB8OK_l94qTv_99korGV3Z355Gt-8pd8vJEWM2whhdddd
```

### 对外暴露 dashboard 访问域名
使用 ingress-nginx 将 dashboard 服务对外暴露。先按照 [官网介绍](https://github.com/kubernetes/ingress-nginx) 安装 nginx-ingress-controller。

检查 deployments
```shell
~/blog/posts 🐶 k get deployments.apps -n ingress-nginx
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
nginx-ingress-controller   1/1     1            1           20d
```

检查 ingress-nginx-svc ，可以知道 http 被映射到了 30834 端口，https 被映射到了 30467 端口
```shell
~/blog/posts 🐶 k get svc -n ingress-nginx
NAME            TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx   NodePort   10.106.96.52   <none>        80:30834/TCP,443:30467/TCP   20d
```

查看 dashboard 对应的 svc，我们需要与 ingress-nginx 绑定的 svc 是 kubernetes-dashboard
```shell
~/blog/posts 🐶 k get svc -n kubernetes-dashboard
NAME                        TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
dashboard-metrics-scraper   ClusterIP   10.110.5.232   <none>        8000/TCP   20d
kubernetes-dashboard        ClusterIP   10.104.2.41    <none>        443/TCP    20d
```

创建 ingress 规则
```yaml
# ingress-dashboard.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/backend-protocol: HTTPS
  name: ingress-dashboard
  namespace: kubernetes-dashboard
spec:
  rules:
  - host: k8s.chenjiandongx.com
    http:
      paths:
      - backend:
          serviceName: kubernetes-dashboard
          servicePort: 443
        path: /
```

噢，别忘了将 k8s.chenjiandongx.com 这个域名写到本地 host 🐶
```shell
$ vim /etc/hosts

+ 192.168.2.12 k8s.chenjiandongx.com
```

使用 Token 访问 https://k8s.chenjiandongx.com:30467

![dashboard](https://user-images.githubusercontent.com/19553554/69475533-4a2a4480-0e09-11ea-8bfe-52478e17d551.png)

