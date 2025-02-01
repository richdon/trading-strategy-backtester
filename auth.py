from flask_restx import Namespace, Resource, fields
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import User
from extensions import db, jwt
from namespace_auth import auth_ns, auth_response, error_response, register_request, login_request, user_model


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_request, validate=True)
    @auth_ns.response(201, 'User registered successfully', auth_response)
    @auth_ns.response(400, 'Validation error', error_response)
    @auth_ns.response(409, 'User already exists', error_response)
    def post(self):
        """
        Register a new user account

        Creates a new user account with the provided username, email, and password.
        Returns a JWT token for immediate authentication after successful registration.
        """
        try:
            data = request.get_json()

            # Check if user already exists
            if User.query.filter_by(username=data['username']).first():
                return {'error': 'Username already exists'}, 409
            if User.query.filter_by(email=data['email']).first():
                return {'error': 'Email already registered'}, 409

            # Create new user
            new_user = User(
                username=data['username'],
                email=data['email']
            )
            new_user.set_password(data['password'])

            # Save user to database
            db.session.add(new_user)
            db.session.commit()

            # Generate access token
            access_token = create_access_token(identity=new_user.id)

            return {
                'access_token': access_token,
                'user': new_user.to_dict()
            }, 201

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_request, validate=True)
    @auth_ns.response(200, 'Login successful', auth_response)
    @auth_ns.response(401, 'Invalid credentials', error_response)
    def post(self):
        """
        User login

        Authenticate user with username/email and password.
        Returns a JWT token upon successful authentication.
        """
        try:
            data = request.get_json()

            # Find user by username or email
            user = User.query.filter(
                (User.username == data['username']) |
                (User.email == data['username'])
            ).first()

            # Validate credentials
            if user and user.check_password(data['password']):
                access_token = create_access_token(identity=user.id)
                return {
                    'access_token': access_token,
                    'user': user.to_dict()
                }, 200

            return {'error': 'Invalid credentials'}, 401

        except Exception as e:
            return {'error': str(e)}, 400


@auth_ns.route('/profile')
class Profile(Resource):
    @auth_ns.response(200, 'Success', user_model)
    @auth_ns.response(401, 'Unauthorized', error_response)
    @auth_ns.doc(security='jwt')
    @jwt_required()
    def get(self):
        """
        Get current user profile

        Returns the profile information for the currently authenticated user.
        Requires a valid JWT token.
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return {'error': 'User not found'}, 404

            return user.to_dict(), 200

        except Exception as e:
            return {'error': str(e)}, 400

    @auth_ns.expect(user_model, validate=True)
    @auth_ns.response(200, 'Profile updated successfully', user_model)
    @auth_ns.response(401, 'Unauthorized', error_response)
    @auth_ns.doc(security='jwt')
    @jwt_required()
    def put(self):
        """
        Update current user profile

        Update the profile information for the currently authenticated user.
        Requires a valid JWT token.
        """
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            if not user:
                return {'error': 'User not found'}, 404

            data = request.get_json()

            # Update fields
            if 'username' in data and data['username'] != user.username:
                if User.query.filter_by(username=data['username']).first():
                    return {'error': 'Username already exists'}, 409
                user.username = data['username']

            if 'email' in data and data['email'] != user.email:
                if User.query.filter_by(email=data['email']).first():
                    return {'error': 'Email already registered'}, 409
                user.email = data['email']

            db.session.commit()
            return user.to_dict(), 200

        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 400


# Error handlers
@auth_ns.errorhandler(Exception)
def handle_generic_error(error):
    """Handle generic errors"""
    return {
        'error': 'Internal server error',
        'details': str(error)
    }, 500


@auth_ns.errorhandler(ValueError)
def handle_validation_error(error):
    """Handle validation errors"""
    return {
        'error': 'Validation error',
        'details': str(error)
    }, 400
