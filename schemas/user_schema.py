from marshmallow import Schema, fields, validate, EXCLUDE
from models.user_model import User

class AdminUserSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        
    id = fields.UUID(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    phone_number = fields.Str(required=False, validate=validate.Length(max=15))
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    profile_picture_url = fields.Str(dump_only=True)
    darkmode = fields.Bool(required=True)
    role = fields.Str(dump_only=True, required=True, validate=validate.OneOf(['Admin', 'Employee', 'Customer', 'Service']))

class RegularUserSchema(Schema):
    class Meta:
        unknown = EXCLUDE
        
    username = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    phone_number = fields.Str(required=False, validate=validate.Length(max=15))
    created_at = fields.DateTime(dump_only=True)
    last_login = fields.DateTime(dump_only=True)
    profile_picture_url = fields.Str(dump_only=True)
    darkmode = fields.Bool(required=True)
    role = fields.Str(dump_only=True, required=True, validate=validate.OneOf(['Admin', 'Employee', 'Customer', 'Service']))

class UserSignupSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True, validate=validate.Length(max=100))
    username = fields.Str(required=True, validate=validate.Length(min=1, max=45))
    password0 = fields.Str(required=True, validate=validate.Length(min=8))
    password1 = fields.Str(required=True, validate=validate.Length(min=8))

class UserLoginSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=8))

class SendResetPasswordEmailSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    email = fields.Email(required=True, validate=validate.Length(max=100))

class ChangePasswordSchema(Schema):
    password0 = fields.Str(required=True, validate=validate.Length(min=8))
    password1 = fields.Str(required=True, validate=validate.Length(min=8))

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