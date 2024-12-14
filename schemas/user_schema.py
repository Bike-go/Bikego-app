from flask_wtf import FlaskForm
from wtforms import EmailField, FileField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, Optional
from flask_wtf.file import FileAllowed
from marshmallow import Schema, fields, validate, EXCLUDE
from models.user_model import User

class ForgotPasswordForm(FlaskForm):
    email = StringField('E-mail', validators=[
        DataRequired(), Email(message="Invalid email format"), Length(max=100)
    ])
    submit = SubmitField('odeslat ověřovací kód')

class ChangePasswordForm(FlaskForm):
    password0 = PasswordField('Heslo', validators=[
        DataRequired(), Length(min=8, message="Password must be at least 8 characters long")
    ])
    password1 = PasswordField('Potvrdit heslo', validators=[
        DataRequired(), EqualTo('password0', message="Passwords must match")
    ])
    submit = SubmitField('Nastavit nové heslo')

class LoginForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[
        DataRequired(), Length(min=1)
    ])
    password0 = PasswordField('Heslo', validators=[
        DataRequired(), Length(min=8)
    ])
    submit = SubmitField('Přihlásit')

class UserSignupForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[
        DataRequired(), Length(min=1, max=45, message="Username must be between 1 and 45 characters long.")
    ])
    email = EmailField('Email', validators=[
        DataRequired(), Email(), Length(max=100, message="Email must be less than 100 characters.")
    ])
    password0 = PasswordField('Heslo', validators=[
        DataRequired(), Length(min=8, message="Password must be at least 8 characters long.")
    ])
    password1 = PasswordField('Potvrdit heslo', validators=[
        DataRequired(), EqualTo('password0', message="Passwords must match.")
    ])
    submit = SubmitField('Vytvořit účet')

class AdminUserForm(FlaskForm):
    id = StringField("ID", render_kw={"readonly": True})
    username = StringField("Uživatelské jméno", validators=[
        DataRequired(),
        Length(min=1, max=45, message="Uživatelské jméno musí mít mezi 1 a 45 znaky.")
    ])
    email = StringField("Email", validators=[
        DataRequired(),
        Email(message="Zadejte platnou emailovou adresu."),
        Length(max=100, message="Email nesmí být delší než 100 znaků.")
    ])
    phone_number = StringField("Telefonní číslo", validators=[
        Optional(),
        Length(max=15, message="Telefonní číslo nesmí být delší než 15 znaků."),
        Regexp(r'^\+?[0-9]*$', message="Telefonní číslo může obsahovat pouze čísla a +.")
    ])
    darkmode = SelectField("Tmavý režim", choices=[
        ("True", "Zapnuto"),
        ("False", "Vypnuto")
    ], validators=[DataRequired()])
    profile_picture = FileField("Profilový obrázek", validators=[
        Optional(),
        FileAllowed(["jpg", "png", "jpeg"], "Povolené formáty obrázků: jpg, png, jpeg.")
    ])
    submit = SubmitField("Uložit změny")

class RegularUserForm(FlaskForm):
    username = StringField("Uživatelské jméno", validators=[
        DataRequired(),
        Length(min=1, max=45, message="Uživatelské jméno musí mít mezi 1 a 45 znaky.")
    ])
    email = StringField("Email", validators=[
        DataRequired(),
        Email(message="Zadejte platnou emailovou adresu."),
        Length(max=100, message="Email nesmí být delší než 100 znaků.")
    ])
    phone_number = StringField("Telefonní číslo", validators=[
        Optional(),
        Length(max=15, message="Telefonní číslo nesmí být delší než 15 znaků."),
        Regexp(r'^\+?[0-9]*$', message="Telefonní číslo může obsahovat pouze čísla a +.")
    ])
    darkmode = SelectField("Tmavý režim", choices=[
        ("true", "Zapnuto"),
        ("false", "Vypnuto")
    ], validators=[DataRequired()])
    profile_picture = FileField("Profilový obrázek", validators=[
        Optional(),
        FileAllowed(["jpg", "png", "jpeg"], "Povolené formáty obrázků: jpg, png, jpeg.")
    ])
    submit = SubmitField("Uložit změny")

def get_user_form(user):
    if user.role == "Admin":
        return AdminUserForm()
    return RegularUserForm()

class UserSchema(Schema):
    class Meta:
        model = User
        load_instance = True
        unknown = EXCLUDE

    id = fields.UUID(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    password_hash = fields.Str(load_only=True, required=True)
    email = fields.Email(required=True, validate=validate.Length(max=100))
    phone_number = fields.Str(required=False, validate=validate.Length(max=15))
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    profile_picture_url = fields.Str(required=False, validate=validate.Length(max=255))
    picture_delete_hash = fields.Str(required=False, validate=validate.Length(max=255))
    email_verified = fields.Bool(required=True)
    darkmode = fields.Bool(required=True)
    role = fields.Str(required=True, validate=validate.OneOf(['Admin', 'Employee', 'Customer', 'Service']))