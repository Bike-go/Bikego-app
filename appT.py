from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def view_Home():
    return render_template("homePage.jinja", title="Domů"), 200

@app.route('/Novinky')
def view_Novinky():
    return render_template("novinky.jinja", title="Novinky")

@app.route('/Půjčovná')
def view_Pujcovna():
    return render_template("pujcovna.jinja", title="Půjčovná")

@app.route('/Foto')
def view_Foto():
    return render_template("foto.jinja", title="Foto")

@app.route('/Kontakt')
def view_Kontakt():
    return render_template("kontakt.jinja", title="Kontakt")

@app.route('/login')
def view_login():
    return render_template("login.jinja", title="Přihlášení", page="login")

@app.route('/register')
def view_register():
    return render_template("register.jinja", title="Registrace", page="register")

@app.route('/confirm_password')
def view_new_pass():
    return render_template("new_pass.jinja", title="Obnovení hesla", page="confirm_password")

@app.route('/reset_password')
def view_reset_pass():
    return render_template("reset_pass.jinja", title="Obnovení hesla", page="reset_password")

@app.route('/profile')
def view_profile():
    return render_template("profile.jinja", title="Profil")


@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'message': 'pong'}), 200

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)