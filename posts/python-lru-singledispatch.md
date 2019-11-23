# Python 两个神奇的装饰器

Tags: `<python>` `<decorator>`

介绍一下 Python3 的两个装饰器 lru_cache 和 singledispatch，网上没什么的中文文章讲这个东西，最近刚好看书学习到的，就来跟大家分享分享。详情请参看官方文档：[https://docs.python.org/3/library/functools.html](https://docs.python.org/3/library/functools.html)

### @functools.lru_cache
```
@functools.lru_cache(maxsize=128, typed=False)
New in version 3.2.
Changed in version 3.3: Added the typed option.
```

这个装饰器实现了备忘的功能，是一项优化技术，把耗时的函数的结果保存起来，避免传入相同的参数时重复计算。lru 是（least recently used）的缩写，即最近最少使用原则。表明缓存不会无限制增长，一段时间不用的缓存条目会被扔掉。

这个装饰器支持传入参数，还能有这种操作的？maxsize 是保存最近多少个调用的结果，最好设置为 2 的倍数，默认为 128。如果设置为 None 的话就相当于是 maxsize 为正无穷了。还有一个参数是 type，如果 type 设置为 true，即把不同参数类型得到的结果分开保存，如 f(3) 和 f(3.0) 会被区分开。

写了个函数追踪结果
```python
def track(func):
    @functools.wraps(func)
    def inner(*args):
        result = func(*args)
        print("{} --> ({}) --> {} ".format(func.__name__, args[0], result))
        return result
    return inner
```

递归函数适合使用这个装饰器，那就拿经典的斐波那契数列来测试吧

不使用缓存
```python
@track
def fib(n):
    if n < 2:
        return n
    return fib(n - 2) + fib(n - 1)
```

使用缓存
```python
@functools.lru_cache()
@track
def fib_with_cache(n):
    if n < 2:
        return n
    return fib_with_cache(n - 2) + fib_with_cache(n - 1)
```

测试代码，本电脑的 cpu 是 i5-5200U
```
fib(10)

 759 function calls (407 primitive calls) in 0.007 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.007    0.007 {built-in method builtins.exec}
        1    0.000    0.000    0.007    0.007 decorator.py:1(<module>)
    177/1    0.000    0.000    0.007    0.007 decorator.py:5(inner)
    177/1    0.000    0.000    0.007    0.007 decorator.py:12(fib)
      177    0.006    0.000    0.006    0.000 {built-in method builtins.print}
      177    0.000    0.000    0.000    0.000 {method 'format' of 'str' objects}
        2    0.000    0.000    0.000    0.000 decorator.py:4(track)
        3    0.000    0.000    0.000    0.000 functools.py:43(update_wrapper)
        1    0.000    0.000    0.000    0.000 functools.py:422(decorating_function)
       21    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
       15    0.000    0.000    0.000    0.000 {built-in method builtins.setattr}
        2    0.000    0.000    0.000    0.000 functools.py:73(wraps)
        3    0.000    0.000    0.000    0.000 {method 'update' of 'dict' objects}
        1    0.000    0.000    0.000    0.000 functools.py:391(lru_cache)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

# 追踪结果

```
fib --> (0) --> 0
fib --> (1) --> 1
fib --> (2) --> 1
fib --> (1) --> 1
fib --> (0) --> 0
fib --> (1) --> 1
fib --> (2) --> 1
fib --> (3) --> 2
fib --> (4) --> 3
fib --> (1) --> 1
fib --> (0) --> 0
fib --> (1) --> 1
fib --> (2) --> 1
fib --> (3) --> 2
fib --> (0) --> 0
fib --> (1) --> 1
fib --> (2) --> 1
fib --> (1) --> 1
fib --> (0) --> 0
fib --> (1) --> 1
fib --> (2) --> 1
fib --> (3) --> 2
fib --> (4) --> 3
fib --> (5) --> 5
fib --> (6) --> 8
fib --> (1) --> 1
fib --> (0) --> 0
fib --> (1) --> 1
fib --> (2) --> 1
往后的省略...
```

fib(10) 调用了 **77** 次， 共花费了 **0.007** 秒

```
fib_with_cache(10)

     95 function calls (75 primitive calls) in 0.002 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.002    0.002 {built-in method builtins.exec}
        1    0.000    0.000    0.002    0.002 decorator.py:1(<module>)
     11/1    0.000    0.000    0.002    0.002 decorator.py:5(inner)
     11/1    0.000    0.000    0.002    0.002 decorator.py:18(fib_with_cache)
       11    0.002    0.000    0.002    0.000 {built-in method builtins.print}
        2    0.000    0.000    0.000    0.000 decorator.py:4(track)
        3    0.000    0.000    0.000    0.000 functools.py:43(update_wrapper)
       11    0.000    0.000    0.000    0.000 {method 'format' of 'str' objects}
        1    0.000    0.000    0.000    0.000 functools.py:422(decorating_function)
       21    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
       15    0.000    0.000    0.000    0.000 {built-in method builtins.setattr}
        2    0.000    0.000    0.000    0.000 functools.py:73(wraps)
        3    0.000    0.000    0.000    0.000 {method 'update' of 'dict' objects}
        1    0.000    0.000    0.000    0.000 functools.py:391(lru_cache)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```
# 追踪结果
```
fib_with_cache --> (0) --> 0
fib_with_cache --> (1) --> 1
fib_with_cache --> (2) --> 1
fib_with_cache --> (3) --> 2
fib_with_cache --> (4) --> 3
fib_with_cache --> (5) --> 5
fib_with_cache --> (6) --> 8
fib_with_cache --> (7) --> 13
fib_with_cache --> (8) --> 21
fib_with_cache --> (9) --> 34
fib_with_cache --> (10) --> 55
```

可以很明显的看到，使用缓存的时候，只调用了 **11** 次就得出了结果，并且花费时间只为 **0.002** 秒

我们再把数字调大，传入的参数改为 31

```
fib(31)

17426519 function calls (8713287 primitive calls) in 168.122 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000  168.122  168.122 {built-in method builtins.exec}
        1    0.000    0.000  168.122  168.122 decorator.py:1(<module>)
4356617/1    8.046    0.000  168.122  168.122 decorator.py:5(inner)
4356617/1    4.250    0.000  168.122  168.122 decorator.py:12(fib)
  4356617  150.176    0.000  150.176    0.000 {built-in method builtins.print}
  4356617    5.650    0.000    5.650    0.000 {method 'format' of 'str' objects}
        2    0.000    0.000    0.000    0.000 decorator.py:4(track)
        3    0.000    0.000    0.000    0.000 functools.py:43(update_wrapper)
        1    0.000    0.000    0.000    0.000 functools.py:422(decorating_function)
       21    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
       15    0.000    0.000    0.000    0.000 {built-in method builtins.setattr}
        2    0.000    0.000    0.000    0.000 functools.py:73(wraps)
        3    0.000    0.000    0.000    0.000 {method 'update' of 'dict' objects}
        1    0.000    0.000    0.000    0.000 functools.py:391(lru_cache)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```
调用了 **4356617** 次，花费 **168.122** 秒

```
fib_with_cache(31)
179 function calls (117 primitive calls) in 0.003 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.003    0.003 {built-in method builtins.exec}
        1    0.000    0.000    0.003    0.003 decorator.py:1(<module>)
     32/1    0.000    0.000    0.003    0.003 decorator.py:5(inner)
     32/1    0.000    0.000    0.003    0.003 decorator.py:18(fib_with_cache)
       32    0.002    0.000    0.002    0.000 {built-in method builtins.print}
       32    0.000    0.000    0.000    0.000 {method 'format' of 'str' objects}
        2    0.000    0.000    0.000    0.000 decorator.py:4(track)
        3    0.000    0.000    0.000    0.000 functools.py:43(update_wrapper)
        1    0.000    0.000    0.000    0.000 functools.py:422(decorating_function)
       21    0.000    0.000    0.000    0.000 {built-in method builtins.getattr}
       15    0.000    0.000    0.000    0.000 {built-in method builtins.setattr}
        2    0.000    0.000    0.000    0.000 functools.py:73(wraps)
        3    0.000    0.000    0.000    0.000 {method 'update' of 'dict' objects}
        1    0.000    0.000    0.000    0.000 functools.py:391(lru_cache)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
```

仅仅调用了 **32** 次，花费 **0.003** 秒...，这...，差别太大了，容我算一算花费时间, **56040** 倍！
再往后的我就不加了，我怕明天没有缓存的那个还没算完

这个装饰器还提供 cache_clear() 用于清理缓存，以及 cache_info() 用于查看缓存信息

官方还提供了另外一个例子，用于缓存静态网页的内容

```python
@lru_cache(maxsize=32)
def get_pep(num):
    'Retrieve text of a Python Enhancement Proposal'
    resource = 'http://www.python.org/dev/peps/pep-%04d/' % num
    try:
        with urllib.request.urlopen(resource) as s:
            return s.read()
    except urllib.error.HTTPError:
        return 'Not Found'
```

### @singledispatch
> New in version 3.4.

使用过别的面向对象语言，如 java 等，肯定熟悉各种方法的重载，但是对于 Python 来说是不支持方法的重载的，不过其为我们提供了一个装饰器，能将普通函数变为泛函数（generic function）

比如你要针对不同类型的数据进行不同的处理，而又不想将它们写到一起，那就可以使用 @singledispatch 装饰器了

```python
@functools.singledispatch
def typecheck():
    pass

@typecheck.register(str)
def _(text):
    print(type(text))
    print("str--")

@typecheck.register(list)
def _(text):
    print(type(text))
    print("list--")

@typecheck.register(int)
def _(text):
    print(type(text))
    print("int--")
```
专门处理的函数无关紧要，所以使用 _ 来表示，当然你也可以写其他你喜欢的

测试
```python
a = 1
typecheck(a)
>>>  
<class 'int'>
int--  

a = "check"
typecheck(a)
>>>
<class 'str'>
str--
```  
singledispatch 机制一个显著特征是，可以在系统的任何地方和任何模块中注册专门的函数，如果后来模块中增加了新的类型，可以轻松地添加一个新的专门函数来处理新类型。很像设计模式中的**策略模式**？
