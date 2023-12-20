# gtsport-spider
gtsport爬虫，用来在gtsport网站关闭前下载共享的svg源文件

## 使用方法
### 安装 scrapy

```bash
pip install scrapy
```

### 替换cookie
把gtsport.py中的cookie替换为你账号自己的cookie
```python
    # Cookie 字段
    cookies = {
        '_ga_E2XXY4HG64': 'deleted',
        'JSESSIONID': '1701234987_4DF8865289F3FD87790F245C3E07EAFDFB2345CC47F36846.worker31',
        '_ga_LR8MJ7Y2JR': 'GS1.1.1701749668.4.1.1701749710.0.0.0',
        '_ga_E2XXY4HG64': 'GS1.1.1701749716.14.1.1701749909.0.0.0',
        '_ga_LYRFZRSR5Y': 'GS1.1.1701756250.3.0.1701756250.0.0.0',
        '_gid': 'GA1.2.755045214.1701847629',
        '_ga_XJ6EBN4C5B': 'GS1.1.1701939060.25.0.1701939060.0.0.0',
        '_ga': 'GA1.2.1192036415.1697356518',
    }
```

### 启动爬虫
```bash
cd gtsport
scrapy crawl gtsport
```
