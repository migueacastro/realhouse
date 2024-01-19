from flask import Flask, flash, render_template, redirect, request, session
from flask_session import Session
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL
from helpers import apology, login_required
from datetime import date
from random import randint

import os
import us

def create_app():
    STATES = [state.name for state in us.states.STATES]
    app = Flask(__name__)

    UPLOAD_FOLDER = "static/uploads/"
    ALLOWED_EXTENSIONS = set(["txt", "pdf", "png", "jpg", "jpeg", "gif"])

    # Configure session type
    app.config["SECRET_KEY"] = "hakunamatata"
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


    # Configure database
    db = SQL("sqlite:///realhouse.db")
    Session(app)


    @app.route("/")
    def index():
        deals = db.execute("SELECT * FROM deals ORDER BY RANDOM() LIMIT 3")

        return render_template("index.html", deals=deals)


    @app.route("/signup", methods=["GET", "POST"])
    def signin():
        # Register user
        if request.method == "POST":
            # Make sure passwords are equal
            if request.form.get("password") != request.form.get("rpassword"):
                return apology("Passwords should be the same", 400)

            # Query db for username confirmation
            rows = db.execute(
                "SELECT * FROM users WHERE username = (?) OR email = (?)",
                request.form.get("username"),
                request.form.get("email"),
            )

            # Ensure username doesnt exist
            if len(rows) != 0:
                return apology("User already exists", 400)

            # Submit account
            db.execute(
                "INSERT INTO users (username, hash, email, phone) VALUES (?,?,?,?)",
                request.form.get("username"),
                generate_password_hash(request.form.get("password")),
                request.form.get("email"),
                request.form.get("phone"),
            )
            rows = db.execute(
                "SELECT * FROM users WHERE username = (?) OR email = (?)",
                request.form.get("username"),
                request.form.get("email"),
            )
            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]
            session["email"] = rows[0]["email"]
            session["username"] = rows[0]["username"]
            return redirect("/")
        else:
            return render_template("signup.html")


    @app.route("/login", methods=["GET", "POST"])
    def login():
        # Log user in
        # Erase user_id

        session.clear()

        # Submiting form method
        if request.method == "POST":
            # Query database for username
            rows = db.execute(
                "SELECT * FROM users WHERE username = (?)", request.form.get("username")
            )

            # Make sure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(
                rows[0]["hash"], request.form.get("password")
            ):
                return apology("Invalid username or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]
            session["email"] = rows[0]["email"]
            session["username"] = rows[0]["username"]
            return redirect("/")
        else:
            return render_template("login.html")


    @app.route("/logout")
    def logout():
        # Forget user
        session.clear()

        # Redirect user to index
        return redirect("/")


    @app.route("/about")
    def about():
        return render_template("about.html")


    @app.route("/marketplace")
    def marketplace():
        # Import deals from database
        deals = db.execute("SELECT * FROM deals ORDER BY RANDOM()")
        return render_template("marketplace.html", deals=deals)


    @app.route("/marketplace/houses")
    def marketplace_houses():
        # Import house deals from database
        deals = db.execute("SELECT * FROM deals WHERE placetype = 'house'")
        return render_template("marketplace.html", deals=deals)


    @app.route("/marketplace/apartments")
    def marketplace_apartments():
        # Import house deals from database
        deals = db.execute("SELECT * FROM deals WHERE placetype = 'apartment'")
        return render_template("marketplace.html", deals=deals)


    @app.route("/marketplace/premises")
    def marketplace_premises():
        # Import house deals from database
        deals = db.execute("SELECT * FROM deals WHERE placetype = 'premise'")
        return render_template("marketplace.html", deals=deals)


    @app.route("/account")
    @login_required
    def account():
        username = session["username"]
        # Import deals from database
        deals = db.execute("SELECT * FROM deals WHERE user_id = (?)", session["user_id"])

        # Import images from the database

        return render_template(
            "account.html", username=username, deals=deals, route="/account"
        )


    @app.route("/create_deal", methods=["GET", "POST"])
    @login_required
    def create_deal():
        if request.method == "POST":
            prefix = f"SWM-{randint(10,900)}-{date.today()}"

            # Retrieve data from the form into variables
            name = request.form.get("name")
            description = request.form.get("description")
            state = request.form.get("state")
            placetype = request.form.get("placetype")
            stories = request.form.get("stories")
            rooms = request.form.get("rooms")
            bathrooms = request.form.get("bathrooms")
            squaremeters = request.form.get("squaremeters")
            # Image retrieval
            files = request.files.getlist("imageup")
            if files[0].filename != "":
                filename = secure_filename(files[0].filename)
                image_filename = f"{prefix}-{filename}"

            else:
                apology("Invalid image")
            # Upload deal to database
            db.execute(
                "INSERT INTO deals (name, description, state, placetype, rooms, bathrooms, stories, user_id, image, squaremeters) VALUES (?,?,?,?,?,?,?,?,?,?)",
                name,
                description,
                state,
                placetype,
                rooms,
                bathrooms,
                stories,
                session["user_id"],
                image_filename,
                squaremeters,
            )

            # Select the deal_id to subtmit it to image database
            dealist = db.execute(
                "SELECT id FROM deals WHERE user_id = (?) and name = (?) and description = (?)",
                session["user_id"],
                name,
                description,
            )

            deal_id = dealist[0]["id"]

            # Upload images to database

            for file in files:
                if file.filename != "":
                    filename = secure_filename(file.filename)
                    filename = f"{prefix}-{filename}"
                    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                else:
                    apology("Invalid image")

                db.execute(
                    "INSERT INTO images (image_path, deal_id) VALUES (?,?)",
                    filename,
                    deal_id,
                )
            return redirect("/account")

        return render_template("create_deal.html", states=STATES)


    @app.route("/marketplace/<int:dealid>/")
    def itemdetails(dealid=None):
        # Load product details
        deal = db.execute("SELECT * FROM deals WHERE id = (?)", dealid)

        # Load listing
        otherdeals = db.execute(
            "SELECT * FROM deals WHERE placetype = (?) LIMIT 4", deal[0]["placetype"]
        )
        images = db.execute("SELECT * FROM images WHERE deal_id = (?)", dealid)
        userdata = db.execute("SELECT * FROM users WHERE id = (?)", deal[0]["user_id"])
        user = userdata[0]["username"]
        return render_template(
            "itemdetails.html",
            deal=deal[0],
            deals=otherdeals,
            images=images,
            username=user,
            userdata=userdata[0],
        )


    @app.route("/delete/<int:dealid>/")
    @login_required
    def delete(dealid=None):
        if session["user_id"] == (
            db.execute("SELECT user_id FROM deals WHERE id = (?)", dealid)[0]["user_id"]
        ):
            # Delete a deal from the database
            db.execute("DELETE FROM images WHERE deal_id = (?)", dealid)
            db.execute("DELETE FROM deals WHERE id = (?)", dealid)
            return redirect("/account")
        else:
            return redirect("/")
    return app
