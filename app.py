import os

from flask import Flask, render_template, request, redirect, url_for, session, flash

from werkzeug.security import generate_password_hash, check_password_hash

from supabase import create_client


# ==================================================
# FLASK APP
# ==================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "change-this-secret-key"
)


# ==================================================
# SUPABASE CONNECTION
# ==================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(
        SUPABASE_URL,
        SUPABASE_KEY
    )


# ==================================================
# HOME
# ==================================================

@app.route("/")
def home():

    username = session.get("username")

    return render_template(
        "index.html",
        username=username
    )


# ==================================================
# CREATE ACCOUNT
# ==================================================

@app.route("/signup", methods=["POST"])
def signup():

    if supabase is None:

        flash("Supabase connection नहीं हुई।")

        return redirect(url_for("home"))


    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    # Username check

    if len(username) < 3:

        flash(
            "Username कम से कम 3 characters का होना चाहिए।"
        )

        return redirect(url_for("home"))


    # Password check

    if len(password) < 6:

        flash(
            "Password कम से कम 6 characters का होना चाहिए।"
        )

        return redirect(url_for("home"))


    try:

        # Check existing username

        result = (
            supabase
            .table("profiles")
            .select("id")
            .eq("username", username)
            .limit(1)
            .execute()
        )


        if result.data:

            flash(
                "यह username पहले से मौजूद है।"
            )

            return redirect(url_for("home"))


        # Password को सीधे database में नहीं रखेंगे

        password_hash = generate_password_hash(
            password
        )


        # Create profile

        new_user = (
            supabase
            .table("profiles")
            .insert({
                "username": username,
                "password_hash": password_hash
            })
            .execute()
        )


        if new_user.data:

            session["username"] = username

            flash(
                "Account बन गया! Welcome to Billiustan 😺"
            )

            return redirect(url_for("home"))


        flash(
            "Account create नहीं हो पाया।"
        )


    except Exception as error:

        print("SIGNUP ERROR:", error)

        flash(
            "Database error आया।"
        )


    return redirect(url_for("home"))


# ==================================================
# LOGIN
# ==================================================

@app.route("/login", methods=["POST"])
def login():

    if supabase is None:

        flash(
            "Supabase connection नहीं हुई।"
        )

        return redirect(url_for("home"))


    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )


    try:

        # Find user

        result = (
            supabase
            .table("profiles")
            .select("*")
            .eq("username", username)
            .limit(1)
            .execute()
        )


        if not result.data:

            flash(
                "Username या password गलत है।"
            )

            return redirect(url_for("home"))


        user = result.data[0]


        # Check password

        correct_password = check_password_hash(
            user["password_hash"],
            password
        )


        if correct_password:

            session["username"] = user["username"]

            flash(
                "Welcome back 😺"
            )

            return redirect(url_for("home"))


        flash(
            "Username या password गलत है।"
        )


    except Exception as error:

        print("LOGIN ERROR:", error)

        flash(
            "Login में database error आया।"
        )


    return redirect(url_for("home"))


# ==================================================
# LOGOUT
# ==================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ==================================================
# HEALTH CHECK
# ==================================================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "app": "BAGALVILLA",
        "supabase": bool(supabase)
    }


# ==================================================
# RUN APP
# ==================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
            )
