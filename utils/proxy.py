import re

from tools import generate_random_string as rs


class Proxy:
    """
    based on the proxy provider 'goproxy', usage example:

    from curl_cffi.requests import Session
    proxy_string = "http://customer-xxxxxx:xxxxxx@proxy.goproxy.com:30000"
    proxy = Proxy.from_str(proxy_string)
    session = Session(proxy=str(proxy.session_proxy()))

    """
    def __init__(self, username: str, password: str, host: str, port: int, session: bool = False,
                 session_time: int = 10, protocol: str = "http"):
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._protocol = protocol
        if session:
            self._username += f"-session-{rs()}-time-{session_time}"

    @property
    def protocol(self):
        return self._protocol

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    def __str__(self) -> str:
        return f"socks5://{self._username}:{self._password}@{self._host}:{self._port}" if self._protocol == "socks5" \
            else f"http://{self._username}:{self._password}@{self._host}:{self._port}"

    def session_proxy(self, session_time: int = 10):
        return Proxy(self._username, self._password, self._host, self._port, True, session_time, self._protocol)

    @classmethod
    def from_str(cls, proxy_str: str):
        pattern = r"(http|socks5)://([^:]+):([^@]+)@([^:]+):(\d+)"
        match = re.match(pattern, proxy_str)
        if not match:
            raise ValueError("字符串格式不正确，无法解析为Proxy对象")
        protocol, username, password, host, port = match.groups()
        return cls(username, password, host, int(port), protocol=protocol)
