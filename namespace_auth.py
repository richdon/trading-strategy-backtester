from flask_restx import Namespace, fields


# Create namespace for auth endpoints
auth_ns = Namespace(
    'auth',
    description='Authentication operations',
    path='/auth'
)

# Request/Response Models
user_model = auth_ns.model('User', {
    'id': fields.String(
        description='User unique identifier',
        example='123e4567-e89b-12d3-a456-426614174000'
    ),
    'username': fields.String(
        required=True,
        description='User username',
        example='trading_user',
        min_length=3,
        max_length=50
    ),
    'email': fields.String(
        required=True,
        description='User email',
        example='trader@example.com'
    )
})

register_request = auth_ns.model('RegisterRequest', {
    'username': fields.String(
        required=True,
        description='Username for the new account',
        example='trading_user',
        min_length=3,
        max_length=50
    ),
    'email': fields.String(
        required=True,
        description='Email address',
        example='trader@example.com',
        pattern=r'^\S+@\S+\.\S+$'
    ),
    'password': fields.String(
        required=True,
        description='Account password',
        example='securepass123',
        min_length=8
    )
})

login_request = auth_ns.model('LoginRequest', {
    'username': fields.String(
        required=True,
        description='Username or email',
        example='trading_user'
    ),
    'password': fields.String(
        required=True,
        description='Account password',
        example='securepass123'
    )
})

auth_response = auth_ns.model('AuthResponse', {
    'access_token': fields.String(
        description='JWT access token',
        example='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
    ),
    'user': fields.Nested(user_model)
})

error_response = auth_ns.model('ErrorResponse', {
    'error': fields.String(
        description='Error message',
        example='Invalid credentials'
    ),
    'details': fields.Raw(
        description='Additional error details',
        example={'field': 'username', 'message': 'Username already exists'}
    )
})
