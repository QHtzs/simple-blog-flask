# -*- coding:utf-8 -*-


from flask import Flask, render_template
from jinja2.filters import do_mark_safe
from flask_login import LoginManager
import os

"""
不采用前后端分离形式
不采用csrf
"""


def monkey_hook():
    """猴子补丁, 使得填充beian, mm_title默认值"""
    def hook(*args, **kwargs):
        if kwargs.get("beian") is None:
            kwargs["beian"] = ""
        if kwargs.get("mm_title") is None:
            kwargs["mm_title"] = "A DEMO"
        return render_template(*args, **kwargs)
    import flask
    setattr(flask, "render_template", hook)


monkey_hook()

config = {'SECRET_KEY': os.urandom(24),
          'TEMPLATES_AUTO_RELOAD': True,
          "JSON_AS_ASCII": False
          }
admins_users = [{"user": "admin", "password": "admin"}]
sqlite_proxy_port = 35000  # 保证只有一个连接操作sqlite

static_fold = os.path.join(os.path.dirname(__file__), "static")
template_fold = os.path.join(os.path.dirname(__file__), "templates")
app = Flask(__name__, static_folder=static_fold, template_folder=template_fold)
app.config.update(config)
lg_manager = LoginManager()
lg_manager.init_app(app)
lg_manager.login_view = "admin.login"
app.add_template_filter(do_mark_safe, "user_define_safe")  # |safe, rename
