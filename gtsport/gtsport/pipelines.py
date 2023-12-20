from scrapy.pipelines.files import FilesPipeline
from urllib.parse import urlparse
from os.path import basename, join

class SVGFilesPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        # 获取保存路径和文件名
        file_name = item.get('files', {}).get('filename')
        return join('svg', file_name)