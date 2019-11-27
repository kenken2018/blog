# kubernetes 之 Ingress 资源

Tags: `<k8s>` `<ingress>`

Kubernetes 中有两种最重要网络，Pod 网络和 Sevice 网络。

* Pod 网络：Pod 网络的边界在集群节点（Node）组成的局域网，因为 Kubernetes 默认要求集群网络中每个 Pod-IP 都能互通。
* Service 网络：如若是 ClusterIP 类型，则网络边界是容器网络，因为 ClusterIP 并没有对应的虚拟网卡，仅仅只是 iptables 的转发规则而已，kube-proxy/core-dns 两者负责处理网络的转发和解析工作。

### 什么是 Ingress?

Kubernetes 与集群外部的通信最简单的方式就是通过暴露一个 NodePort 类型的 Service，然后集群外部即可与集群内部的服务互通。这样做确实比较方便，但需要自己对 NodePort 进行端口的规划和管理，而且 Service 本身并不能自定义转发规则，比如根据 Header 或者 Host 转发到不同的后端。

```
# NodePort 与外部交互

    internet
        |
   --|-----|--
   [ Services ]
```

Ingress 就是为了解决这个问题而出现的，可以通过定义 Ingress 定义丰富的后端转发规则。

```
# Ingress 与外部交互

    internet
        |
   [ Ingress ]
   --|-----|--
   [ Services ]
```

### 什么是 Ingress Controller?

Ingress 是一种资源对象，Ingress Controller 就是控制 Ingress 如何运作的具体实现。目前开源社区已经有多种 Ingress-Controller，不过最热门的还是 Kubernetes 团队开发的 [kubernetes/ingress-nginx](https://github.com/kubernetes/ingress-nginx)。实际上 Ingress-Controller 就是一个外部的负载均衡，负责将外部流量导入到集群内部。

### 如何部署 Ingress-nginx？

官方已经将所有相关资源都集中到一个 yaml 文件中了，所以部署还是很方便的。
```shell
$ kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/master/deploy/static/mandatory.yaml
```

nginx-ingress-controller 会以 deployment 的形式部署在 ingress-nginx 命名空间里
```shell
~ 🐶 k get -n ingress-nginx deploy
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
nginx-ingress-controller   1/1     1            1           24d
```

另外还会自动创建一个 NodePort 类型的 Service。HTTP:80 =>  30834，HTTPS:443 => 30467
```shell  
~ 🐶 k get svc -n ingress-nginx
NAME            TYPE       CLUSTER-IP     EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx   NodePort   10.106.96.52   <none>        80:30834/TCP,443:30467/TCP   24d
```

### 如何使用 Ingress-nginx？

#### 基于路由转发

Ingress 最简单的 fanout 例子就是基于不同的路由前缀转发到不同的后端服务
```
foo.bar.com -> 178.91.123.132 -> / foo    service1:4200
                                 / bar    service2:8080

```

simple-fanout-example.yaml
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: simple-fanout-example
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: foo.bar.com
    http:
      paths:
      # foo.bar.com/foo/* => service1:4200
      - path: /foo
        backend:
          serviceName: service1
          servicePort: 4200
      # foo.bar.com/bar/* => service2:8080
      - path: /bar
        backend:
          serviceName: service2
          servicePort: 8080
```

#### 基于域名转发

单个 Ingress 资源也可支持同时转发多个域名的流量

```
foo.bar.com --|                 |-> foo.bar.com service1:80
              | 178.91.123.132  |
bar.foo.com --|                 |-> bar.foo.com service2:80
```

name-virtual-host-ingress.yaml
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: name-virtual-host-ingress
spec:
  rules:
  - host: foo.bar.com
    http:
      paths:
      - backend:
          serviceName: service1
          servicePort: 80
  - host: bar.foo.com
    http:
      paths:
      - backend:
          serviceName: service2
          servicePort: 80
```

如果想同时基于域名和 IP 访问呢，也简单，同时配置一个 host 和一个没有 host 的转发规则。这样所有直接使用 IP 访问的请求就会被转发到 service3 上。

name-virtual-host-ip-ingress.yaml
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: name-virtual-host-ingress
spec:
  rules:
  - host: first.bar.com
    http:
      paths:
      - backend:
          serviceName: service1
          servicePort: 80
  - host: second.foo.com
    http:
      paths:
      - backend:
          serviceName: service2
          servicePort: 80
  - http:
      paths:
      - backend:
          serviceName: service3
          servicePort: 80
```

#### 基于 TLS 加密认证

Ingress 同样支持 TLS 加密认证，可以在 Ingress 里配置 TLS 的相关证书来做客户端的校验，首先需要自己生成一对需要加密认证域名的 tls.crt/tls.key 并创建 Secret 资源。
      
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: testsecret-tls
  namespace: default
data:
  tls.crt: base64 encoded cert
  tls.key: base64 encoded key
type: kubernetes.io/tls
```

然后在配置对应域名 TLS Ingress 规则
```yaml
apiVersion: networking.k8s.io/v1beta1
kind: Ingress
metadata:
  name: tls-example-ingress
spec:
  tls:
  - hosts:
    - sslexample.foo.com
    secretName: testsecret-tls
  rules:
    - host: sslexample.foo.com
      http:
        paths:
        - path: /
          backend:
            serviceName: service1
            servicePort: 80
```

### Ingress-Controller 实战

实际上我部署 Ingress-Controller 是为了转发我后端一些服务的前端界面，比如 Kubernetes-Dashboard/Grafana/Promethues/... 行，那我们就操练起来吧。

**Kubernetes-Dashboard**

```yaml
# ingress-dashboard.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-dashboard
  namespace: kubernetes-dashboard
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  rules:
  - host: k8s.chenjiandongx.com
    http:
      paths:
        - path: /
          backend:
            serviceName: kubernetes-dashboard
            servicePort: 443
```

**Grafana**

```yaml
# ingress-grafana.yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-grafana
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
spec:
  rules:
  - host: grafana.chenjiandongx.com
    http:
      paths:
        - path: /
          backend:
            serviceName: grafana-svc
            servicePort: 3000
```

**Prometheus**

```yaml
apiVersion: extensions/v1beta1
kind: Ingress
metadata:
  name: ingress-prometheus
  namespace: default
  annotations:
    kubernetes.io/ingress.class: "nginx"
    nginx.ingress.kubernetes.io/backend-protocol: "HTTP"
spec:
  rules:
  - host: prometheus.chenjiandongx.com
    http:
      paths:
        - path: /
          backend:
            serviceName: prometheus
            servicePort: 9090
```

当部署完上面的 Ingress 资源后，还需要修改本地的 /etc/hosts 文件，毕竟我真没有这些域名 😅

```shell
$ vim /etc/hosts

# 192.168.2.11 是我 k8s 集群 master 节点的 IP
192.168.2.11 k8s.chenjiandongx.com grafana.chenjiandongx.com prometheus.chenjiandongx.com
```

虽然是部署起来了，但是还是有点不爽，因为 kubeadm 在安装 k8s 集群的时候，NodePort 端口默认只开放 30000 以后的，这也是 ingress-controller-svc 的 HTTP/HTTPS 端口都被映射到 30000+ 的原因。

所以我们虽然配置了域名，但是访问的时候还是需要把端口带上。比如 http://prometheus.chenjiandongx.com:30834 我还是喜欢直接访问 http://prometheus.chenjiandongx.com （傲娇脸）

那怎么办呢，我依稀记得一个不知名的程序员曾经说过。

> 没有什么网络代理问题是一次转发解决不了的，如果有，那就再加一层转发。 -- by chenjiandongx

所以我们可以在 master 节点上再新增一个 nginx 来做 4 层转发，这样我们就可以达到我们想要的效果啦！

首先安装 nginx
```shell
$ ssh master
$ yum install nginx -y
```

然后配置 nginx 转发规则
```shell
$ cd /etc/nginx/
$ mkdir stream.d && cd steram.d

# 创建并编辑 k8s.conf
$ vim k8s.conf

stream {
    upstream http_backend {
        # master IP，把其他 node 写上做负载也可以 不过也没什么必要
        server 192.168.2.11:30834        max_fails=3 fail_timeout=30s;
    }

    upstream https_backend {
        server 192.168.2.11:30467        max_fails=3 fail_timeout=30s;
    }

    server {
        listen 0.0.0.0:80;
        proxy_connect_timeout 1s;
        proxy_pass http_backend;
    }

    server {
        listen 0.0.0.0:443;
        proxy_connect_timeout 1s;
        proxy_pass https_backend;
    }
}
```

导入 nginx 配置
```shell
$ vim /etc/nginx/nginx.conf

+ include /etc/nginx/stream.d/*.conf;
```

启动 nginx
```shell
$ systemctl enable nginx
$ systemctl start nginx
```

#### 效果 

http://prometheus.chenjiandongx.com
> Prometheus 查询面板

![](https://user-images.githubusercontent.com/19553554/69706178-19f8e380-1132-11ea-8c33-954312e023d4.jpg)

http://grafana.chenjiandongx.com
> Nginx-ingress-controller 的 Grafana 监控面板

![](https://user-images.githubusercontent.com/19553554/69706191-1feec480-1132-11ea-8f1e-1aa647d60844.jpg)

https://k8s.chenjiandongx.com
> Kubernetes 资源面板

![prometheus](https://user-images.githubusercontent.com/19553554/69706203-267d3c00-1132-11ea-95a5-725a7cae9acd.jpg)

