# -*- coding:utf-8 -*-

from flask import Blueprint, render_template, jsonify, request, abort
from ..models import Article

anon = Blueprint("anonymous", __name__)


@anon.route("/")
def index():
    return render_template("index.html")


@anon.route("/article/list", methods=["GET"])
def load_article():
    ret = []
    for article in Article.load_all():
        ret.append(article.to_dict())
    return jsonify(ret)


@anon.route("/article/detail", methods=["GET"])
def load_article_detail():
    category = request.args.get("category") or ""
    title = request.args.get("title") or ""
    articles = list(Article.load_one(category, title))
    if articles:
        kwargs = articles[0].to_dict()
        kwargs.pop("brief", None)
        return render_template("detail.html", **kwargs)
    else:
        abort(404)
