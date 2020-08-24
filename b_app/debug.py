# -*- coding:utf-8 -*-

import os
import sys
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.split(os.path.dirname(__file__))[0])


if __name__ == '__main__':
    from b_app.manager import app
    app.run(debug=True)
