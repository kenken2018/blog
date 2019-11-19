#  Python 中的并行与并发

Tags: `<python>`

* 并发（concurrency）：在同一个处理器上快速的切换程序，只使用一个核心，**指多线程**
* 并行（parallelism）：在多个处理器上同时运行多个程序，使用多个核心，**指多进程**
* 守护进程（daemon）：如果进程设置了 daemon=True 属性，主进程结束，子进程就随着结束了。

## 用 subprocess 模块来管理子进程
```python
# 子进程会独立于父进程而运行
proc = subprocess.Popen(['echo','Hello world'], stdout=subproces.PIPE)
out, err = proc.communicate() # 使用 communiacate 读取子进程输出的信息

# 同时启动多个子进程
proces = []
for i in range(10):
    proc = proc = subprocess.Popen(['echo','Hello world'], stdout=subproces.PIPE)
    procs.appen(proc)
```

## 使用 concurrency.futuresm 模块启动多线程/进程
```python
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ProcessPoolExecutor # Windows 系统下不能用

pool = ThreadPoolExecutor(max_worker=2)
#pool = ProcessPoolExecutor(max_worker=2)
result = list(pool.map(func, arg)) # 使用map方法简化代码
```

## 使用 multprocessing.Pool 模块启动多线程/进程
```python
from multiprocessing import Pool,cup_count # 多进程
from multiprocessing.dummy import Pool as ThreadPool # 多线程

pool = ThreadPool(2)
# pocess = cpu_count()
# pool = Pool(processes=pocess)
result = list(pool.map(func, arg))
pool.close()
pool.join()
```

## 使用 queue 模块启动线程队列
Queue 是多进程安全的队列，可以使用 Queue 实现多进程之间的数据传递。

* put 方法用以插入数据到队列中，put方法还有两个可选参数：blocked 和 timeout。如果 blocked 为 True（默认值），并且 timeout 为正值，该方法会阻塞 timeout 指定的时间，直到该队列有剩余的空间。如果超时，会抛出 Queue.Full 异常。如果 blocked 为 False，但该 Queue 已满，会立即抛出 Queue.Full 异常。
* get 方法可以从队列读取并且删除一个元素。同样，get 方法有两个可选参数：blocked 和 timeout。如果 blocked 为 True（默认值），并且 timeout 为正值，那么在等待时间内没有取到任何元素，会抛出 Queue.Empty 异常。如果 blocked 为 False，有两种情况存在，如果 Queue 有一个值可用，则立即返回该值，否则，如果队列为空，则立即抛出 Queue.Empty 异常。
```python
import threading
import queue
class QueueThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.input_queue = queue.Queue()

    def send(self,item): # 放入线程
        self.input_queue.put(item)

    def close(self):
        self.input_queue.put(None) # 设置哨兵
        self.input_queue.join()

    def run(self):
        while True:
            item = self.input_queue.get()
            if item is None:
                break
            work(item) # 实际工作内容
            self.input_queue.task_done()
        # 完成，指示收到和返回了哨兵
        self.input_queue.task_done()
        return

    def work(self,item):
        print(item)

work = QueueThread()
work.start()
for i in range(len(urls)):
    work.send(urls[i])
work.close()
```

## 使用 multiprocessing 创建多进程
```python
import multiprocessing
import time

def worker(interval):
    print("do something")

if __name__ == "__main__":
    process = []
    num_cups = multiprocessing.cpu_count()
    for i in range(num_cpus):
        p = multiprocessing.Process(target=worker, arg =(arg1,)) # 创建进程
        p.start() # 启动进程
        process.append(p) # 进程入队

    for p in process:
        p.join() # 等待进程结束
```

### 使用 Thread 创建多线程
1. 创建线程要执行的函数，把这个函数传递进 Thread 对象里，让它来执行
```python
import threading

def test(nloop, nsec):
    print(nloop)
    sleep(nsec)
    print(nloop)

def main():
    threadpool=[]
    for i in xrange(10):
        th = threading.Thread(target= test,args= (i,2))
        threadpool.append(th)

    for th in threadpool:
        th.start()

    for th in threadpool :
        threading.Thread.join(th)


if __name__ == '__main__':
    main()
```

2. 继承 Thread 类，创建一个新的 class，将要执行的代码 写到 run 函数里面
```python
import threading ,time

class myThread (threading.Thread) :
      """docstring for myThread"""
      def __init__(self, nloop, nsec) :
          super(myThread, self).__init__()
          self.nloop = nloop
          self.nsec = nsec

      def run(self):
          print(nloop)
          sleep(self.nsec)
          print(nloop)

def main():
     thpool=[]
     for i in xrange(10):
         thpool.append(myThread(i,2))

     for th in thpool:
         th.start()

     for th in thpool:
         th.join()

if __name__ == '__main__':
    main()
```

