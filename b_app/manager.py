# -*- coding:utf-8 -*-

from flask_script import Manager
try:
    from b_app.setting import app
    from b_app.views import admin_view, anon
except ImportError:
    import os
    import sys
    sys.path.append(os.path.dirname(__file__))
    sys.path.append(os.path.split(os.path.dirname(__file__))[0])
    from b_app.setting import app
    from b_app.views import admin_view, anon


app.register_blueprint(admin_view, url_prefix="/admin")
app.register_blueprint(anon, url_prefix="/")
manager = Manager(app)


@manager.option("-h", "--host", dest="host", help="host", default="127.0.0.1")
@manager.option("-p", "--port", dest="port", help="port", default=5000)
def run(host, port):
    app.run(host, port)


if __name__ == '__main__':
    manager.run()
