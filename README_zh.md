# Aget 异步下载工具

Aget 将下载请求分成多个小块，依次用异步下载。

### 安装

>   需要 Python >= 3.5

```
pip3 install aget
```

### 用法

```
aget https://cdn.v2ex.co/site/logo@2x.png

# 指定下载路径
aget https://cdn.v2ex.co/site/logo@2x.png -o v2ex.png

# 指定请求头
aget https://cdn.v2ex.co/site/logo@2x.png -H "User-Agent: Mozilla/5.0" -H "Accept-Encoding: gzip"

# 指定并发数量 (无限制)
aget https://cdn.v2ex.co/site/logo@2x.png -s 10

# 指定请求块大小
aget https://cdn.v2ex.co/site/logo@2x.png -k 10k
```

### 参数

```
-o OUT, --out OUT             # 下载路径
-H HEADER, --header HEADER    # 请求头
-X METHOD, --method METHOD    # 请求方法
-d DATA, --data DATA          # 请求 data
-t TIMEOUT, --timeout TIMEOUT # timeout
-s CONCURRENCY, --concurrency CONCURRENCY   # 并发数
-k CHUCK_SIZE, --chuck_size CHUCK_SIZE      # 请求块大小
```

