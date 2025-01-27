from flask import Blueprint, flash, render_template, request

from utils.email_utils import send_contact_form

contacts_bp = Blueprint('contacts_bp', __name__)

@contacts_bp.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        if not name or not email or not message:
            flash("Please fill in all fields.", "error")
            return render_template("contacts.jinja", title="Contacts", page="contacts"), 200
        try:
            send_contact_form(email, name, message)
            flash("Your message has been sent successfully!", "success")
        except Exception as e:
            flash(f"Failed to send your message. Please try again later. Error: {e}", "error")
        return render_template("contacts.jinja", title="Contacts", page="contacts"), 200
    return render_template("contacts.jinja", title="Contacts", page="contacts"), 200