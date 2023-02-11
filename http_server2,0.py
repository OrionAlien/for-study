from socket import *
from select import *
import re


class Http_service:
    def __init__(self, host="0.0.0.0", post=8888, dir=None):
        self.host = host
        self.post = post
        self.dir = dir
        self.addr = (host, post)
        self.sockfd = socket()
        self.dict_io = {}

    # 提供服务
    def serve_forever(self):
        # 创建套接字
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.sockfd.bind(self.addr)
        self.sockfd.listen(5)
        # 多路IO复用
        self.ep = epoll()
        self.ep.register(self.sockfd, EPOLLIN | EPOLLHUP)
        self.dict_io[self.sockfd.fileno()] = self.sockfd
        while True:
            events = self.ep.poll()
            # 监听行为
            for fn, event in events:
                # 处理连接
                if fn == self.sockfd.fileno():
                    connfd, addr_c = self.sockfd.accept()
                    print("connect to %s %s" % addr_c)
                    self.dict_io[connfd.fileno()] = connfd  # 维护字典
                    self.ep.register(connfd, EPOLLIN | EPOLLHUP)  # 监听connfd套接字
                # 给客户收发消息
                else:
                    # 收消息
                    response = self.get_http_request(self.dict_io[fn])
                    # print(response)
                    # 回复
                    # self.send_http_feeback(response, self.dict_io[fn])

    # 收消息
    def get_http_request(self, connfd):
        # print("get_http_request") #测试程序能不能进入该模块
        data = connfd.recv(2048)
        if not data:  # 客户端断开连接
            self.ep.unregister(connfd)  # 解除监听
            addr_temp = connfd.getpeername()
            print("%s %s exit" % addr_temp)
            del self.dict_io[connfd.fileno()]  # 更新字典
            connfd.close()
            return
        # print(data.decode())
        self.handle(data.decode(),connfd)  # 处理消息

    # 处理消息
    def handle(self, data,connfd):
        pattern = r"[A-Z]{3,7}\s+(?P<target>.+)\s+(HTTP/1.1)"
        regex_http = re.compile(pattern)
        http_req = regex_http.match(data).group("target")
        if http_req == "/" or http_req[-5:] == ".html":
            self.get_html(http_req,connfd)
        else:
            # print(http_req)
            self.get_data(connfd)

    def get_html(self, http_req,connfd):
        # print(http_req)
        if http_req == "/":  # 请求主页
            filename = self.dir + "/index.html"
        else:
            filename = self.dir + http_req
        try:
            fd = open(filename, "rb")
        except Exception:  # 网页不存在
            response = "HTTP/1.1 404 Not Found\r\n"
            response += "Content-Typy:text/html\r\n"
            response += "\r\n"
            response += "<h1>Sorry...</h1>"
            response = response.encode()
            return response
        else:  # 网页存在
            response = "HTTP/1.1 200 OK\r\n"
            response += "Content-Type:text/html\r\n"
            response += "\r\n"
            response += fd.read().decode()
            # print(response.decode())
            response = response.encode()
            connfd.send(response)

    def get_data(self,connfd):
        response = "HTTP/1.1 404 Not Found\r\n"
        response += "Content-Typy:text/html\r\n"
        response += "\r\n"
        response += "<h1>get data function is not ready</h1>"
        response = response.encode()
        connfd.send(response)

    # 回复
    def send_http_feeback(self, data, connfd):
        print(data)
        # print(connfd)
        connfd.send(data)


# 确定用户功能和用法
if __name__ == "__main__":
    # 用户要传递的参数
    HOST = "0.0.0.0"
    POST = 8888
    DIR = r"./static"  # 网页的存储位置

    # 使用方法
    h = Http_service(HOST, POST, DIR)
    h.serve_forever()
