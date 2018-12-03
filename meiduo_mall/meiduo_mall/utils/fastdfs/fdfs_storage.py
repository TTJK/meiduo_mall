from django.core.files.storage import Storagefrom fdfs_client.client import Fdfs_clientfrom django.conf import settingsclass FastDFSStorage(Storage):    """自定义文件管理系统类"""    def __init__(self, client_conf=None, base_url=None):        """初始化方法"""        # self.client_conf = client_conf        # if self.client_conf == None:        #     self.client_conf = settings.FDFS_CLIENT_CONF        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF        self.base_url = base_url or settings.FDFS_BASE_URL    def _open(self, name, mode='rb'):        """        储存类用于打开文件的,因为我们只做上传文件不打开文件,所以此方法重写后什么也不做        :param name: 要打开的文件名        :param mode: 文件读取模式 read bytes        :return: None        """        pass    def _save(self, name, content):        """        让Django把图片用FdFS进行图片的上传存储        :param name: 要存储的文件名字        :param content: 要存储的文件的对象        :return: file_id        """        # 加载fdfs的客户端配置文件来创建出一个fdfs客户端        # client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')        # client = Fdfs_client(settings.FDFS_CLIENT_CONF)        client = Fdfs_client(self.client_conf)        # 下面这种上传方式需要知道当前要上传文件的本地路径        # ret = client.upload_by_filename('/Users/chao/Desktop/01.jpg')  此方法上传到storage中的文件会有后缀        ret = client.upload_appender_by_buffer(content.read())  # 此方法上传的文件无后缀        # 判断文件是否上传成功        status = ret.get('Status')  # 取出当前图片上传后响应的状态        if status != 'Upload successed.':            raise Exception('Upload file failed')  # 文件上传失败        # 如果能执行到这里,说明文件上传成功了        file_id = ret.get('Remote file_id')        return file_id    def exists(self, name):        """        判断要上传的文件在storage服务器中是否已经存在        :param name: 要判断的文件名        :return: True(文件已存在,就不会再上传了)  False(文件不存,需要上传,然后马上调用save)        """        return False    def url(self, name):        """        返回要下载的图片的绝对路径        :param name: file_id  文件的存储在storage中的路径(文件在storage中的相对路径)        :return: 文件的绝对路径  http://192.168.103.210:8888/group1/M00/00/00/wKhn0lv_SoaAQdpsAAKK5JRebvg271.jpg        """        # return 'http://192.168.103.210:8888' + name        # return settings.FDFS_BASE_URL + name        return self.base_url + name #        """ #        {'Group name': 'group1', # 'Remote file_id': 'group1/M00/00/00/wKhn0lv_SoaAQdpsAAKK5JRebvg271.jpg', # 'Status': 'Upload successed.', # 'Local file name': '/Users/chao/Desktop/01.jpg', # 'Uploaded size': '162.00KB', # 'Storage IP': '192.168.103.210'} #        """