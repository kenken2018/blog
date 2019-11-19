#  教你用 Python 从零开始写出简易版跳一跳外挂

Tags: `<python>` `<wechat>`

关注 Python 的人想必都知道 [跳一跳辅助外挂](https://github.com/wangshub/wechat_jump_game) 这个项目近来在 Github 上火得不行，相信不少人也可能尝试过一番，并暗暗叹息，为什么我一开始就没有这个好想法呢！

现在，参照外挂项目的源码，我们就从零开始来自己动手写一个手动版本的跳一跳外挂。

思路：

1. 利用 adb 命令先把跳一跳截图保留至本地
2. 通过点击图上两个坐标点，算出两点之间的距离（勾股定理），最后得出按压屏幕的时间。
3. 通过 adb 命令执行按压屏幕操作
4. 重复 1 - 3 

思路已经有了，就可以动手开码了。不过要先安装好 adb 环境，至于怎么配置安装，Google it！无非就是下载安装 adb 驱动，并设置好环境变量而已！

先把后面需要的库引进来
```python
import os
import math

# 这两个库用于图片的操作
import matplotlib.pyplot as plt
from PIL import Image
```

新建 WechatJump 类，并进行初始化操作
```python
class WechatJump:

    def __init__(self):
        # 按压系数，不同分辨率的手机需要做调整
        self._coefficient = 1.35
        # 记录按压次数
        self._click_count = 0
        # 记录点击点坐标的数组
        self._coords = []
```

首先需要保存图片至本地
```python
def generate_screenshot(self):
    # 截图，并将图片保存为 /sdcard/screenshot.png
    os.system('adb shell screencap -p /sdcard/screenshot.png')
    # pull 命令是将图片从手机发送到电脑本地
    os.system('adb pull /sdcard/screenshot.png .')
```

点击图片坐标点
```python
# event 是点击事件
def on_click(self, event):
    # event.xdata, event.ydata 分别是点击的横纵坐标，将坐标依次保存到 _coords 数组中
    self._coords.append((event.xdata, event.ydata))
    # 这里是每两次点击（起始点和目标点）就会执行按压按压屏幕操作，所以当
    # self._click_count == 2 时才执行
    self._click_count += 1
    if self._click_count == 2:
        self._click_count = 0
        # 弹出第二次点击时的坐标
        _next = self._coords.pop()
        # 弹出第一次点击时的坐标
        _prev = self._coords.pop()
        # 根据勾股定理计算出两点之间的距离
        self.jump_to_next(
            math.sqrt((_next[0] - _prev[0]) ** 2 + (_next[1] - _prev[1]) ** 2))
```

先点击 1 号点，再点击 2 好点即可

![screenshot](https://user-images.githubusercontent.com/19553554/34648209-64e74c54-f3d1-11e7-85ea-8da23e2c96fd.png)


按压屏幕，执行跳跃操作
```python
def jump_to_next(self, distance):
    press_time = int(distance * self._coefficient)
    # cmd 最后一个参数 press_time 为按压时间，按压时间为 距离x按压系数，至于按压系数是
    # 多少则要根据每个人的手机分辨率而定，可自行测试调整
    # 100 100 200 200 这四个数字其实无所谓，只是模拟 swipe 操作时的坐标点而已
    cmd = 'adb shell input swipe 100 100 200 200 {}'.format(press_time)
    print(cmd)
    # 执行命令
    os.system(cmd)
```

基本上函数已经完成了，最后整理一下，将 on_click 函数绑定到图片上，循环操作
```python
def run(self):
    # 循环执行操作
    while True:
        # 这里执行两次截图操作，不然会提示远程图片未找到的问题（可以注释其中一行试试看）
        self.generate_screenshot()
        self.generate_screenshot()
        figure = plt.figure()
        # 绑定 on_click 操作
        figure.canvas.mpl_connect('button_press_event', self.on_click)
        # 打开并显示图片
        img = Image.open('screenshot.png')
        plt.imshow(img)
        plt.show()
```

最后，只需要运行 run 函数即可，参数调得好的话，落点可以说是非常准了。手动刷到个上千分完全没问题，只要你要耐心.....
```python
wechat_jump = WechatJump()
wechat_jump.run()
```

怎么样，是不是觉得其实也不难写出来。（其实原作者的第一版大概就长这样子）不过现在该项目，已经推出了自动跳跃的版本，兼容 iphone 的版本，甚至有大牛直接上了深度学习的版本！（有兴趣的同学可以阅读一下其源码，相信会有收获的。）不过这都是后来的事啦，总之一句话，想法才是最重要的！

附上本教程完整代码

```python
# -*- coding: utf-8 -*-
import os
import math
import matplotlib.pyplot as plt
from PIL import Image


class WechatJump:

    def __init__(self):
        self._coefficient = 1.35
        self._click_count = 0
        self._coords = []

    def generate_screenshot(self):
        os.system('adb shell screencap -p /sdcard/screenshot.png')
        os.system('adb pull /sdcard/screenshot.png .')

    def jump_to_next(self, distance):
        press_time = int(distance * self._coefficient)
        cmd = 'adb shell input swipe 100 100 200 200 {}'.format(press_time)
        print(cmd)
        os.system(cmd)

    def on_click(self, event):
        self._coords.append((event.xdata, event.ydata))
        self._click_count += 1
        if self._click_count == 2:
            self._click_count = 0
            _next = self._coords.pop()
            _prev = self._coords.pop()
            self.jump_to_next(
                math.sqrt((_next[0] - _prev[0]) ** 2 + (_next[1] - _prev[1]) ** 2))

    def run(self):
        while True:
            self.generate_screenshot()
            self.generate_screenshot()
            figure = plt.figure()
            figure.canvas.mpl_connect('button_press_event', self.on_click)
            img = Image.open('screenshot.png')
            plt.imshow(img)
            plt.show()


if __name__ == "__main__":
    wechat_jump = WechatJump()
    wechat_jump.run()
```

