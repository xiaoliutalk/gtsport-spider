import scrapy
from datetime import datetime
import logging


class GTSportSpider(scrapy.Spider):
    name = 'gtsport'
    start_urls = ['https://www.gran-turismo.com/gb/api/gt7sp/discover/']

    @staticmethod
    def sanitize_filename(filename):
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '\'', '<', '>', '|', '&', '!', '$', '#', '%', '@', '^', '(', ')', '[', ']']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    download_delay = 0.2  # 设置延迟为0.2秒
    
    # 初始请求参数
    job_id = 1001
    node_id = -1
    offset = 0

    # 构造请求头
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://www.gran-turismo.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.gran-turismo.com/gb/gtsport/user/discover/search/decal',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
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

    def start_requests(self):
        # 发送第一次请求
        try:
            yield self.create_request()
        except Exception as e:
            self.log(f"start_requests中的错误：{e}")

    def create_request(self):

        # 构造 POST 请求的表单数据
        form_data = {
            'job': self.job_id,
            'keyword_csv': '',
            'node_id': self.node_id,
            'offset': self.offset,
            'tag_csv': '',
        }
        # 将表单数据转换为字符串格式
        body = '&'.join([f'{key}={value}' for key, value in form_data.items()])

        # 构造请求
        return scrapy.Request(url=self.start_urls[0],cookies=self.cookies,method='POST',headers=self.headers,body=body,callback=self.parse)


    def parse(self, response):

        # 获取响应的JSON数据
        data = response.json()

        # 处理返回的数据
        node_id = data.get('node_id')
        decals = data.get('decal', [])



        for decal in decals:
            decal_id = decal.get('decal_id')
            # 如果为None，则设置为空字符串
            user_id = decal.get('user_id', '')
            decal_title = decal.get('title', '')

            # 时间格式化为文件名格式
            filename_format = "%Y%m%d%H%M%S"
            timestamp = datetime.fromisoformat(decal.get('create_time').replace('Z', '+00:00'))
            create_time = timestamp.strftime(filename_format)
            decal_name = self.sanitize_filename(decal_title)

            # 构建下载链接
            download_url = f'https://www.gran-turismo.com/gtsport/decal/{decal_id}_0.svg'

            # 构建文件名
            file_name = f'{create_time}_{decal_name}_{user_id}.svg'
            
            # 使用自定义回调处理302重定向
            yield scrapy.Request(
                download_url,
                callback=self.parse_svg,
                meta={
                    'file_name': file_name,
                    'dont_redirect': False,  # 不禁止自动重定向
                    'handle_httpstatus_list': [302],  # 自定义处理302状态码
                },
            )

        self.log(f"self.node_id is: {self.node_id},self.offset is: {self.offset},len(decals) is: {len(decals)}", level=logging.INFO)


        # 检查是否需要继续请求
        if len(decals) == 200:
            # 判断是否为首次之后进行爬取
            if self.node_id == -1:
                self.node_id = 79
            # 更新参数值
            self.offset += 200
        elif self.node_id != -1 & self.node_id < 9:
            # 当 node_id 小于 9 时停止请求
            self.log("Reached node_id < 9. Stopping further requests.")
            return
        else:
            # 当 decals 小于 200 时，且 node_id 不大于 9，继续请求并减少 node_id
            self.offset = 0
            self.node_id -= 1

        # 发送下一个请求
        yield self.create_request()

    def parse_svg(self, response):
        # 获取实际的SVG文件链接（可能包含重定向）
        redirected_url = response.headers.get('Location', b'').decode('utf-8')
        # 获取文件名
        file_name = response.meta['file_name']

        # 使用FilesPipeline下载文件
        yield {
            'file_urls': [redirected_url],  # 使用重定向后的链接，如果有的话
            'files': {'data': response.body, 'filename': file_name},
        }