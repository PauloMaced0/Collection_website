import os
import shutil
import sqlite3
import cherrypy
import string
import random
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont


DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cromos.db")


def allow(*methods):
    methods = list(methods)
    if not methods:
        methods = ['GET', 'HEAD']
    elif 'GET' in methods and 'HEAD' not in methods:
        methods.append('HEAD')

    def wrap(f):
        def inner(*args, **kwargs):
            cherrypy.response.headers['Allow'] = ', '.join(methods)
            if cherrypy.request.method not in methods:
                raise cherrypy.HTTPError(405)
            return f(*args, **kwargs)
        inner.exposed = True
        return inner
    return wrap


def user_is_logged(request):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        try:
            username = request.cookie["username"]
            token = request.cookie["token"]
        except KeyError:
            return False

        cursor.execute("SELECT token from users WHERE username=?", [
                       username.value])

        row = cursor.fetchone()
        return row and row[0] != None and row[0] == token.value

# metodos para sqlite


def db_store_image(collection_name, file, username):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        # retornar id do utilizador
        cursor.execute("SELECT id FROM users WHERE username=?;", [username])
        username_id = cursor.fetchone()[0]

        # verificar se a collection ja existe
        cursor.execute("SELECT id_collection FROM collections WHERE name=?;", [
                       collection_name])
        row = cursor.fetchone()

        collection_id = -1
        if row:
            collection_id = row[0]
        else:
            # adicionar colecao
            cursor.execute("INSERT INTO collections(name) VALUES(?);", [
                           collection_name])
            collection_id = cursor.lastrowid

        cursor.execute("INSERT INTO images(img_name, collection_id, creation_date, uploaded_by) VALUES(?, ?, ?, ?);",
                       [file.filename, collection_id, datetime.now(timezone.utc), username_id])

        return (collection_id, cursor.lastrowid)


def get_image_name(id):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT img_name FROM images WHERE image_id=?", [id])

        return cursor.fetchone()[0]


def get_collections():
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM collections;")
        return cursor.fetchall()


def get_collection_image(id):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT img_name FROM images WHERE collection_id=?;", [id])
        return cursor.fetchone()[0]


def get_images_from_collection(id):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM images WHERE collection_id=?;", [id])
        return cursor.fetchall()


def get_user(id):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE id=?", [id])

        return cursor.fetchone()[0]


def get_user_id(username):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=?", [username])
        row = cursor.fetchone()

        if not row:
            raise cherrypy.HTTPError(404)

        return row[0]


def draft_image(id):
    username = cherrypy.request.cookie["username"].value

    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        user_id = get_user_id(username)
        cursor.execute(
            "UPDATE images SET owner_id=? WHERE image_id=?", [user_id, id])

        cursor.execute("INSERT INTO transactions(current_owner_id, ts, image_id) VALUES(?, ?, ?);",
                       [user_id, datetime.now(timezone.utc), id])


def get_collection_name(id):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM collections WHERE id_collection=?;", [id])
        return cursor.fetchone()[0]


def get_image_transactions(id):
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE image_id=?;", [id])
        return cursor.fetchall()


def get_image_information(id):
    username = cherrypy.request.cookie["username"].value

    ret = {"id": id}
    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM images WHERE image_id=?;", [id])
        row = cursor.fetchone()

        if row[5]:
            ret["owner"] = get_user(row[5])
        else:
            ret["owner"] = ""

        ret["able_to_transfer"] = get_user_id(username) == row[5]
        ret["creation_date"] = row[3]
        ret["uploaded_by"] = get_user(row[4])
        ret["collection_name"] = get_collection_name(row[2])
        ret["img_name"] = row[1]
        ret["img_url"] = f"/labiproj6/static/images/{row[1]}"

        image_transactions = get_image_transactions(id)
        ret["transactions"] = []

        for transaction in image_transactions:
            ret["transactions"].append({
                "ts": transaction[3],
                "owner": get_user(transaction[1])
            })

        return ret


def db_update_image_owner(id, new_owner):
    username = cherrypy.request.cookie["username"].value

    with sqlite3.connect(DB) as conn:
        cursor = conn.cursor()

        # atualizar owner da imagem
        owner_id = get_user_id(new_owner)
        cursor.execute(
            "UPDATE images SET owner_id=? WHERE image_id=?;", [owner_id, id])

        # adicionar mais uma transferencia
        cursor.execute("INSERT INTO transactions(current_owner_id, previous_owner_id, ts, image_id) VALUES(?, ?, ?, ?);",
                       [owner_id, get_user_id(username), datetime.now(timezone.utc), id])


def watermark(destination, owner):
    # Create an Image Object from an Image
    im = Image.open(destination)
    width, height = im.size

    typeFont = "./public/fonts/arial.ttf"
    draw = ImageDraw.Draw(im)
    font = ImageFont.truetype(typeFont, 15)

    w, h = font.getsize(owner)
    pos = (width - w + 10, height - h + 5)

    
    rectangle_pos = (width - w - 100, height - h - 10, width, height)
    draw.rectangle(rectangle_pos, fill="white")

    draw.text(pos, owner, fill="black", anchor="mm", font=font) # Marca
    
    im.save(destination)

class Users(object):
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @allow('POST')
    def auth(self, username=None, password=None):
        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password FROM users WHERE username=?", [username])
            query_result = cursor.fetchone()

            if not query_result or username != query_result[0] or password != query_result[1]:
                cherrypy.response.status = 404
                return {
                    "authentication": "failed"
                }

            letters = string.ascii_letters
            token = ''.join(random.choice(letters) for i in range(8))
            cursor.execute("UPDATE users SET token=? WHERE username=?", [
                           token, username])

            cherrypy.response.status = 200
            return {
                "authentication": "OK",
                "token": token
            }

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @allow('POST')
    def create(self, username=None, password=None):
        if not username or not password:
            cherrypy.response.status = 400
            return

        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "SELECT username FROM users WHERE username=?", [username])
            query_result = cursor.fetchone()

            if query_result:
                cherrypy.response.status = 409
                return

            cherrypy.response.status = 200
            cursor.execute("INSERT INTO users(username, password) VALUES (?,?)", [
                           username, password])
        return "success"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def valid(self):
        if user_is_logged(cherrypy.request):
            return "valid"
        return "invalid"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def profile(self):
        username = cherrypy.request.cookie["username"].value

        ret = []
        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT img_name FROM images WHERE owner_id=?", [
                        get_user_id(username)])
            images = cursor.fetchall()

            for image_name in images:
                ret.append({
                    "username": username,
                    "img_name": image_name[0],
                    "img_path": f"/labiproj6/static/images/{image_name[0]}"
                })

        return ret


class CreateImage(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create(self, name=None, file=None):
        destination = os.path.join("public/images/", file.filename)
        with open(destination, 'wb') as f:
            shutil.copyfileobj(file.file, f)

        username = cherrypy.request.cookie["username"].value

        collection_id, image_id = db_store_image(
            name, file, username)

        return {
            "id": collection_id,
            "image_id": image_id
        }


class Cromos(object):
    def __init__(self):
        self.name = CreateImage()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self, id=None):
        if not user_is_logged(cherrypy.request):
            return "unauthorized"

        if id:
            image_rows = get_images_from_collection(int(id))

            ret = []
            for row in image_rows:
                image_owner = None
                if row[5]:
                    image_owner = get_user(row[5])

                image = {
                    "id_image": row[0],
                    "img_path": f"/labiproj6/static/images/{row[1]}",
                    "name": row[1],
                    "owner": image_owner
                }

                ret.append(image)
            return ret

        ret = []
        collection_rows = get_collections()

        for row in collection_rows:
            collection_image = get_collection_image(row[0])
            collection = {
                "id_collection": row[0],
                "name": row[1],
                "img_path": f"/labiproj6/static/images/{collection_image}"
            }

            ret.append(collection)

        return ret

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def draft(self, id=None):

        if not user_is_logged(cherrypy.request):
            raise cherrypy.HTTPError(401)

        if not id:
            raise cherrypy.HTTPError(500)

        destination = os.path.join("./public/images/", get_image_name(id))
        username = cherrypy.request.cookie["username"].value

        draft_image(id)
        watermark(destination, username)

        return "Draft made successfully"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def image(self, id=None):
        if not user_is_logged(cherrypy.request):
            raise cherrypy.HTTPError(401)

        if not id:
            raise cherrypy.HTTPError(500)

        return get_image_information(int(id))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def transfer(self, id=None, new_owner=None):
        destination = os.path.join("./public/images/", get_image_name(id))

        db_update_image_owner(int(id), new_owner)
        watermark(destination, new_owner)

        return "Transfer made successfully"

class Root(object):
    def __init__(self):
        self.users = Users()
        self.cromos = Cromos()

    @cherrypy.expose
    def login(self):
        return open("./public/html/login.html")

    @cherrypy.expose
    def register(self):
        return open("./public/html/register.html")

    @cherrypy.expose
    def index(self):
        if user_is_logged(cherrypy.request):
            return open("./public/html/index.html")

        raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def about(self):
        if user_is_logged(cherrypy.request):
            return open("./public/html/about.html")

        raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def collection(self, id=None):
        if user_is_logged(cherrypy.request):
            return open("./public/html/collection.html")

        raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def profile(self):
        if user_is_logged(cherrypy.request):
            return open("./public/html/myprofile.html")

        raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def image(self, id=None):
        if user_is_logged(cherrypy.request):
            return open("./public/html/image.html")

        raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def upload(self):
        if user_is_logged(cherrypy.request):
            return open("./public/html/upload.html")

        raise cherrypy.HTTPRedirect("/login")

    @cherrypy.expose
    def logout(self):
        if not user_is_logged(cherrypy.request):
            cherrypy.response.status = 401
            raise cherrypy.HTTPRedirect("/login")

        username = cherrypy.request.cookie["username"]

        with sqlite3.connect(DB) as conn:
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE users SET token=null WHERE username=?", [username.value])

        cherrypy.request.cookie["username"] = ''
        cherrypy.request.cookie["username"]['expires'] = 0
        cherrypy.request.cookie["username"]['max-age'] = 0

        cherrypy.request.cookie["token"] = ''
        cherrypy.request.cookie["token"]['expires'] = 0
        cherrypy.request.cookie["token"]['max-age'] = 0

        raise cherrypy.HTTPRedirect("/")


if __name__ == "__main__":
    conf = {
        "/": {
            "tools.staticdir.root": os.path.abspath(os.getcwd())
        },
        "/static": {
            "tools.staticdir.on": True,
            "tools.staticdir.dir": "./public"
        },


    }

    webapp = Root()
    cherrypy.config.update({'server.socket_port': 10006})
    cherrypy.quickstart(webapp, "/", conf)
