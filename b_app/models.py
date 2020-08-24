# -*- coding:utf-8 -*-

from .setting import admins_users, sqlite_proxy_port
from flask_login import UserMixin
from functools import wraps
from atexit import register
import warnings
import sqlite3
import select
import socket
import threading
import pickle
import os
import base64
from typing import List


class Admin(UserMixin):
    def __init__(self, user, password):
        self._user = user
        self._password = password

    def get_id(self):  # 必须被继承
        return self._user

    @staticmethod
    def get(user_id):
        if not user_id:
            return Admin(None, None)
        for admin in admins_users:
            if admin["user"] == user_id:
                return Admin(**admin)
        return Admin(None, None)

    @property
    def user(self):
        return self._user

    @property
    def password(self):
        return self._password

    @property
    def isvalid(self):
        return self.user is not None

    @classmethod
    def verify(cls, user, password):
        u = cls(user, password)
        for admin in admins_users:
            t = cls(**admin)
            if u == t:
                return True
        return False

    @classmethod
    def get_admin(cls, user_id):
        for admin in admins_users:
            if admin["user"] == user_id:
                return cls(**admin)
        return cls(None, None)

    def __eq__(self, other):
        return self.isvalid and self.user == other.user and self.password == other.password


def ignore_errors(func):
    @wraps(func)
    def f(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            warnings.warn("sqlite error %s" % repr(e))
            return pickle.dumps([])
    return f


class SqlitePipeProxy:
    """保证只有一个线程占用sqlite
       通过socket(限制端口)，保证只有一个连接访问sqlite某个库
       用于解决tornaod, 或者uwsgi, gunicorn等启用多个process的问题
    """
    db = os.path.join(os.path.dirname(__file__), "sqlite_db", "article.db")

    def __init__(self):
        self._con = None
        self._client = None
        self._server = None
        self._input = []
        self._errors = []
        if self._create_server():
            t = threading.Thread(target=self._create_msg_handle)
            t.setDaemon(True)
            t.start()
        self._create_client()

    def _connect(self):
        fold = os.path.split(self.__class__.db)[0]
        if not os.path.exists(fold):
            os.mkdir(fold)
        self._con = sqlite3.connect(self.__class__.db)

    def _create_table(self):
        sql = """CREATE TABLE IF NOT EXISTS article(
            pno INTEGER PRIMARY KEY  AUTOINCREMENT,
            category text,
            title text,
            brief text,
            content text,
            UNIQUE (category, title) ON CONFLICT REPLACE
        )
        """
        cur = self._con.cursor()
        cur.execute(sql)

    def _create_server(self) -> bool:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", sqlite_proxy_port))
            s.listen(5)
            self._input.append(s)
            return True
        except Exception as e:
            warnings.warn("端口被占用, 若是多进程启动则忽略: %s" % repr(e))
            return False

    def _create_client(self):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.connect(("127.0.0.1", sqlite_proxy_port))
        self._client = sk

    @ignore_errors
    def _execute_sql(self, sql: bytes):
        sql = sql.decode("utf-8")
        flag = ord(sql[0]) - ord('0')
        sql = sql[1:]
        if flag in (0, 1):
            need_commit = flag
            cur = self._con.cursor()
            cur.execute(sql)
            obj = cur.fetchall()
            if need_commit:
                self._con.commit()
            return pickle.dumps(obj)
        else:
            self._con.close()
            return pickle.dumps([])

    def _create_msg_handle(self):
        self._connect()
        self._create_table()
        register(self._client.send, b"2")  # callback所在线程会不一样,
        # 间接方式关闭connect,防止数据丢失
        while True:
            reads, *_ = select.select(self._input, [], [])
            for read in reads:
                if read is self._input[0]:
                    connection, client_address = read.accept()
                    connection.setblocking(0)
                    self._input.append(connection)
                else:
                    sql = read.recv(2**16)
                    ret = self._execute_sql(sql)
                    read.send(ret)

    def execute(self, sql, need_commit=True):
        if isinstance(sql, str):
            sql = sql.encode("utf-8")
        sql = (b'1' if need_commit else b'0') + sql
        self._client.send(sql)
        b = self._client.recv(2**16)
        return pickle.loads(b)


class Article:
    sqlite_cmd_proxy = SqlitePipeProxy()

    def __init__(self, category="", title="", brief="", content=""):
        self.title = base64.b64encode(title.encode("utf-8")).decode()
        self.category = base64.b64encode(category.encode("utf-8")).decode()
        self.brief = base64.b64encode(brief.encode("utf-8")).decode()
        self.content = base64.b64encode(content.encode("utf-8")).decode()

    def from_base64(self, category="", title="", brief="", content=""):
        self.title = title
        self.category = category
        self.brief = brief
        self.content = content
        return self

    def __str__(self):
        return "'%s', '%s', '%s', '%s'" % (self.category, self.title,
                                           self.brief, self.content)

    def to_dict(self):
        return {k: base64.b64decode(v).decode("utf8") for k, v in self.__dict__.items()}

    @classmethod
    def upsert(cls, articles: List["Article"]):
        ret = []
        for article in articles:
            sql = """insert or replace into article(category, title, brief, content) values(%s)  """ % article
            ret.append(cls.sqlite_cmd_proxy.execute(sql))
        return ret

    @classmethod
    def delete(cls, category: str, title: str):
        category = base64.b64encode(category.encode("utf-8")).decode()
        title = base64.b64encode(title.encode("utf-8")).decode()
        sql = "delete from article where category='%s' and title='%s' " % (category, title)
        return cls.sqlite_cmd_proxy.execute(sql)

    @classmethod
    def load_all(cls):
        sql = "select category, title, brief, content from article"
        ret = cls.sqlite_cmd_proxy.execute(sql, need_commit=False)
        for x in ret:
            yield cls().from_base64(*x)

    @classmethod
    def load_one(cls, category, title):
        if not (category or title):
            return []
        category = base64.b64encode(category.encode("utf-8")).decode()
        title = base64.b64encode(title.encode("utf-8")).decode()
        sql = "select category, title, brief, content from article where category='%s' and title='%s' " \
              % (category, title)
        ret = cls.sqlite_cmd_proxy.execute(sql, need_commit=False)
        for x in ret:
            yield cls().from_base64(*x)
