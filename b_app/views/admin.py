# -*- coding:utf-8 -*-

from flask import Blueprint, request, render_template, \
    redirect, url_for
from flask_login import login_required, login_user, logout_user
from ..models import Admin, Article
from ..setting import lg_manager


admin_view = Blueprint("admin", __name__)


@lg_manager.user_loader
def load_user(user_id):
    return Admin.get_admin(user_id)


@admin_view.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@admin_view.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        form = request.form
        user = form.get("UserName")
        pwd = form.get("PassWord")
        nxt = request.args.get("next")
        if Admin.verify(user, pwd):
            login_user(Admin(user, pwd))
            return redirect(nxt or "/", 302)
        return redirect(url_for('login'), 302)


@admin_view.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "GET":
        return render_template("editor.html")
    else:
        form = request.form
        category = form.get("category")
        title = form.get("title")
        brief = form.get("brief")
        content = form.get("content")
        article = Article(category, title, brief, content)
        article.upsert([article])
        return "success"


@admin_view.route("/re_edit", methods=["GET", "POST"])
@login_required
def re_edit():
    if request.method == "GET":
        category = request.args.get("category")
        title = request.args.get("title")
        articles = list(Article.load_one(category, title))
        if articles:
            return render_template("re_edit.html", **articles[0].to_dict())
        else:
            redirect(url_for("edit"))
    else:
        form = request.form
        category = form.get("category")
        title = form.get("title")
        brief = form.get("brief")
        content = form.get("content")
        article = Article(category, title, brief, content)
        article.upsert([article])
        return "success"


@admin_view.route("/delete", methods=["GET"])
@login_required
def delete():
    category = request.args.get("category")
    title = request.args.get("title")
    Article.delete(category, title)
    return "success"
