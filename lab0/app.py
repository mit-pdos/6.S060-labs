#!/usr/bin/env python3

"""
Local Flask web server to photo client
"""

from flask import Flask, request, abort, redirect, url_for
from string import Template
from markupsafe import escape

from dummy_server import DummyServer
from client import Client

app = Flask(__name__)

client = None
remote = DummyServer()

user_secrets = {}

@app.route("/", methods=["GET"])
def root():
    if client is None:
        return redirect(url_for("login"))
    else:
        return redirect(url_for("photos"))

@app.route("/login", methods=["GET", "POST"])
def login():
    global client

    if request.method == "GET":
        return _handle_verbatim("login.html")

    if "username" not in request.form:
        abort(400)

    username = request.form["username"]
    if username not in user_secrets:
        abort(401)

    attempt = Client(username, remote, user_secrets[username])
    try:
        attempt.login()
        client = attempt
        return redirect(url_for("photos"))
    except:
        abort(401)

@app.route("/logout", methods=["POST"])
def logout():
    global client

    client = None
    return redirect(url_for("login"))

@app.route("/register", methods=["POST"])
def register():
    global client

    if "username" not in request.form:
        abort(400)

    username = request.form["username"]
    attempt = Client(username, remote)
    try:
        attempt.register()
        client = attempt
        user_secrets[username] = client.user_secret
        return redirect(url_for("photos"))
    except:
        abort(401)

@app.route("/photos", methods=["GET"])
def photos():
    if client is None:
        return redirect(url_for("login"))

    return _list_photos()

@app.route("/photo", methods=["POST"])
def photo():
    if client is None:
        return redirect(url_for("login"))

    if "photo" not in request.files:
        abort(400)

    data = request.files["photo"].read()
    if len(data) == 0:
        abort(400)

    if client.put_photo(data) is None:
        abort(500)

    return _list_photos()

@app.route("/photo/<num>", methods=["GET"])
def photo_num(num=-1):
    if client is None:
        return redirect(url_for("login"))

    photo = client.get_photo(int(num))
    if photo is None:
        abort(404)

    with open("static/photo-{}".format(num), "wb") as f:
        f.write(photo)

    with open("static/get_photo.html") as f:
        photo_html = Template(f.read())
    photo_html = photo_html.substitute(username=escape(client.username),
                                       num=num)
    return photo_html


def _handle_verbatim(filename):
    with open("static/"+filename) as f:
        return f.read()

def _list_photos():
    photos = client.list_photos()
    if photos == None:
        abort(500)

    if len(photos) == 0:
        contents = "You have no photos yet."
    else:
        contents = ""
        for name in photos:
            contents += '<a href="photo/{name}">{name}</a>\n'.format(name=name)

    with open("static/list_photos.html") as f:
        list_html = Template(f.read())
    list_html = list_html.substitute(username=escape(client.username),
                                     contents=contents)
    return list_html

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if client is None:
        return redirect(url_for("login"))

    infos = {}
    profile = client.get_friend_public_profile(client.username)
    if profile is not None:
        infos = profile.infos

    if request.method == "POST":
        if "add-attr" in request.form:
            if ("add-key" not in request.form or
                "add-value" not in request.form):
                abort(400)
            infos[request.form["add-key"]] = request.form["add-value"]
            client.update_public_profile_infos(infos)
        else:
            order = sorted(list(infos.items()))
            for attr in request.form:
                if attr.startswith("del-attr-"):
                    index = int(attr[len("del-attr-"):])
                    key = order[index][0]
                    infos.pop(key)
                    client.update_public_profile_infos(infos)
                    break

    fields = ""
    order = sorted(list(infos.items()))
    for i, pair in enumerate(order):
        key = pair[0]
        fields += '<div id="field-{key}"><span class="profile-key">{key}</span>: {val} <button name="del-attr-{index}" formaction="profile">Delete</button></div>'.format(
            index=i,
            key=escape(key),
            val=escape(profile.infos[key]),
        )
    if fields == "":
        fields = '<em>no attributes added yet</em>'

    with open("static/profile.html") as f:
        profile_html = Template(f.read())
    profile_html = profile_html.substitute(username=escape(client.username),
                                           fields=fields)
    return profile_html
