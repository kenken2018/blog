# Python 中的编码和解码

Tags: `<python>`

* Unicode 字符转换为二进制数据，使用 encode 方法
* 二进制数据转换为 Unicode 字符，使用 decode 方法

python3 中的 str 为 unicode 类型，bytes 是包含原始的 8 位值，在 python3 中 str 和 bytes 不会等价，即使是空字符串也不行

### 函数接受 str 或 bytes，并总是返回 str 类型，**解码（码：二进制）**
```python
def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return bytes_or_str
```

### 函数接受 str 或 bytes，并总是返回 bytes 类型，**编码**
```python
def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return bytes_or_str
```

