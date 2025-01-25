from flask import Blueprint, request, jsonify
from extensions import db
from models import User
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from marshmallow import Schema, fields, validate, ValidationError

auth_bp = Blueprint('auth', __name__)


class UserSchema(Schema):
    """
    Marshmallow schema for user registration and validation
    """
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        load_only=True  # Don't serialize password
    )


user_schema = UserSchema()


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    User registration endpoint
    """
    try:
        # Validate incoming data
        data = user_schema.load(request.get_json())

        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400

        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.set_password(data['password'])

        # Save user to database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': 'User registered successfully',
            'user': new_user.to_dict()
        }), 201

    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint with JWT token generation
    """
    try:
        data = request.get_json()

        # Find user by username or email
        user = User.query.filter(
            (User.username == data.get('username')) |
            (User.email == data.get('username'))
        ).first()

        # Validate credentials
        if user and user.check_password(data.get('password')):
            # Generate access token
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'access_token': access_token,
                'user': user.to_dict()
            }), 200

        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify(user.to_dict()), 200
