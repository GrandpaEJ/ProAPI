"""
User Account Management for ProAPI.

This module provides user account management features for ProAPI applications,
similar to Flask-User. It allows you to:
- Register new users
- Confirm email addresses
- Reset passwords
- Manage user profiles
- Integrate with the login system

Example:
    from proapi import ProAPI
    from proapi.auth.login import LoginManager, login_required, current_user
    from proapi.auth.user import UserManager, UserMixin

    app = ProAPI(enable_sessions=True)
    login_manager = LoginManager(app)
    user_manager = UserManager(app)

    class User(UserMixin):
        def __init__(self, id, username, email, password):
            self.id = id
            self.username = username
            self.email = email
            self.password = password
            self.email_confirmed = False

    # User database
    users = {}

    @login_manager.user_loader
    def load_user(user_id):
        return users.get(user_id)

    @user_manager.password_hasher
    def hash_password(password):
        # In a real app, use a secure password hashing algorithm
        return password

    @user_manager.password_verifier
    def verify_password(user, password):
        # In a real app, use a secure password verification
        return user.password == password

    @user_manager.user_creator
    def create_user(username, email, password):
        user_id = str(len(users) + 1)
        user = User(id=user_id, username=username, email=email, password=password)
        users[user_id] = user
        return user

    @user_manager.user_finder
    def find_user_by_email(email):
        for user in users.values():
            if user.email == email:
                return user
        return None
"""

import functools
import hashlib
import os
import re
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Callable, Dict, List, Optional, Union

from proapi.server.server import Request, Response
from proapi.routing.request_proxy import get_current_request
from proapi.core.logging import app_logger
from proapi.auth.login import login_user, logout_user

# Use app_logger with a specific context for user management logs
user_logger = app_logger.bind(context="user_manager")


class UserManager:
    """
    User Manager for ProAPI.
    
    This class manages user accounts for ProAPI applications.
    """
    
    def __init__(self, app=None, login_manager=None, 
                 enable_email_confirmation=True, enable_password_reset=True,
                 enable_registration=True, enable_change_password=True,
                 enable_change_username=False, enable_change_email=True):
        """
        Initialize the user manager.
        
        Args:
            app: ProAPI application (optional)
            login_manager: LoginManager instance (optional)
            enable_email_confirmation: Whether to enable email confirmation
            enable_password_reset: Whether to enable password reset
            enable_registration: Whether to enable user registration
            enable_change_password: Whether to enable password change
            enable_change_username: Whether to enable username change
            enable_change_email: Whether to enable email change
        """
        self.app = app
        self.login_manager = login_manager
        
        # Feature flags
        self.enable_email_confirmation = enable_email_confirmation
        self.enable_password_reset = enable_password_reset
        self.enable_registration = enable_registration
        self.enable_change_password = enable_change_password
        self.enable_change_username = enable_change_username
        self.enable_change_email = enable_change_email
        
        # Email settings
        self.email_sender = None
        self.email_server = None
        self.email_port = 587
        self.email_use_tls = True
        self.email_username = None
        self.email_password = None
        
        # URL settings
        self.login_url = '/login'
        self.logout_url = '/logout'
        self.register_url = '/register'
        self.confirm_email_url = '/confirm-email'
        self.reset_password_url = '/reset-password'
        self.change_password_url = '/change-password'
        self.change_username_url = '/change-username'
        self.change_email_url = '/change-email'
        
        # Token settings
        self.token_expiration = 86400  # 24 hours
        
        # Callback functions
        self._password_hasher = None
        self._password_verifier = None
        self._user_creator = None
        self._user_finder = None
        self._email_sender = None
        
        user_logger.info("UserManager initialized")
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """
        Initialize the user manager with an application.
        
        Args:
            app: ProAPI application
        """
        self.app = app
        
        # Get login manager from app if not provided
        if self.login_manager is None and hasattr(app, '_login_manager'):
            self.login_manager = app._login_manager
            user_logger.debug("Using login manager from app")
        
        # Check if sessions are enabled
        if not getattr(app, 'enable_sessions', False):
            user_logger.warning(
                "Sessions are not enabled. User management requires sessions. "
                "Enable sessions by setting enable_sessions=True when creating the app."
            )
        
        # Store user manager in app for access from routes
        app._user_manager = self
        user_logger.info(f"UserManager initialized for application: {app.__class__.__name__}")
        
        # Register routes if app is provided
        if self.enable_registration:
            self._register_routes(app)
    
    def _register_routes(self, app):
        """
        Register routes for user management.
        
        Args:
            app: ProAPI application
        """
        # Register route
        @app.get(self.register_url)
        def register_get(request):
            return self._render_register_form()
        
        @app.post(self.register_url)
        def register_post(request):
            return self._handle_register_form(request)
        
        # Login route (if login manager is not provided)
        if self.login_manager is None:
            @app.get(self.login_url)
            def login_get(request):
                return self._render_login_form()
            
            @app.post(self.login_url)
            def login_post(request):
                return self._handle_login_form(request)
        
        # Logout route (if login manager is not provided)
        if self.login_manager is None:
            @app.get(self.logout_url)
            def logout(request):
                logout_user()
                return self._redirect_to_login()
        
        # Email confirmation routes
        if self.enable_email_confirmation:
            @app.get(self.confirm_email_url)
            def confirm_email_get(request):
                token = request.query_params.get('token')
                return self._handle_confirm_email(token)
            
            @app.get(self.confirm_email_url + '/resend')
            def resend_confirmation_email(request):
                return self._handle_resend_confirmation_email(request)
        
        # Password reset routes
        if self.enable_password_reset:
            @app.get(self.reset_password_url)
            def reset_password_get(request):
                return self._render_reset_password_form()
            
            @app.post(self.reset_password_url)
            def reset_password_post(request):
                return self._handle_reset_password_form(request)
            
            @app.get(self.reset_password_url + '/confirm')
            def reset_password_confirm_get(request):
                token = request.query_params.get('token')
                return self._render_reset_password_confirm_form(token)
            
            @app.post(self.reset_password_url + '/confirm')
            def reset_password_confirm_post(request):
                token = request.query_params.get('token')
                return self._handle_reset_password_confirm_form(request, token)
        
        # Change password route
        if self.enable_change_password:
            @app.get(self.change_password_url)
            def change_password_get(request):
                return self._render_change_password_form()
            
            @app.post(self.change_password_url)
            def change_password_post(request):
                return self._handle_change_password_form(request)
        
        # Change username route
        if self.enable_change_username:
            @app.get(self.change_username_url)
            def change_username_get(request):
                return self._render_change_username_form()
            
            @app.post(self.change_username_url)
            def change_username_post(request):
                return self._handle_change_username_form(request)
        
        # Change email route
        if self.enable_change_email:
            @app.get(self.change_email_url)
            def change_email_get(request):
                return self._render_change_email_form()
            
            @app.post(self.change_email_url)
            def change_email_post(request):
                return self._handle_change_email_form(request)
    
    def password_hasher(self, callback: Callable) -> Callable:
        """
        Decorator to register a password hasher function.
        
        Args:
            callback: Function that hashes a password
            
        Returns:
            The callback function
        """
        self._password_hasher = callback
        user_logger.debug(f"Password hasher function registered: {callback.__name__}")
        return callback
    
    def password_verifier(self, callback: Callable) -> Callable:
        """
        Decorator to register a password verifier function.
        
        Args:
            callback: Function that verifies a password
            
        Returns:
            The callback function
        """
        self._password_verifier = callback
        user_logger.debug(f"Password verifier function registered: {callback.__name__}")
        return callback
    
    def user_creator(self, callback: Callable) -> Callable:
        """
        Decorator to register a user creator function.
        
        Args:
            callback: Function that creates a user
            
        Returns:
            The callback function
        """
        self._user_creator = callback
        user_logger.debug(f"User creator function registered: {callback.__name__}")
        return callback
    
    def user_finder(self, callback: Callable) -> Callable:
        """
        Decorator to register a user finder function.
        
        Args:
            callback: Function that finds a user by email
            
        Returns:
            The callback function
        """
        self._user_finder = callback
        user_logger.debug(f"User finder function registered: {callback.__name__}")
        return callback
    
    def email_sender(self, callback: Callable) -> Callable:
        """
        Decorator to register an email sender function.
        
        Args:
            callback: Function that sends an email
            
        Returns:
            The callback function
        """
        self._email_sender = callback
        user_logger.debug(f"Email sender function registered: {callback.__name__}")
        return callback
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password.
        
        Args:
            password: Password to hash
            
        Returns:
            Hashed password
        """
        if self._password_hasher:
            return self._password_hasher(password)
        
        # Default password hasher (not secure, use a proper one in production)
        salt = os.urandom(16).hex()
        hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return f"{salt}${hash}"
    
    def verify_password(self, user: Any, password: str) -> bool:
        """
        Verify a password.
        
        Args:
            user: User object
            password: Password to verify
            
        Returns:
            True if the password is correct, False otherwise
        """
        if self._password_verifier:
            return self._password_verifier(user, password)
        
        # Default password verifier (not secure, use a proper one in production)
        if not hasattr(user, 'password'):
            user_logger.error("User object must have a password attribute")
            return False
        
        stored_password = user.password
        if '$' not in stored_password:
            user_logger.error("Invalid password format")
            return False
        
        salt, hash = stored_password.split('$', 1)
        expected_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return hash == expected_hash
    
    def create_user(self, username: str, email: str, password: str) -> Any:
        """
        Create a new user.
        
        Args:
            username: Username
            email: Email address
            password: Password
            
        Returns:
            User object
        """
        if self._user_creator:
            # Hash the password before creating the user
            hashed_password = self.hash_password(password)
            return self._user_creator(username, email, hashed_password)
        
        user_logger.error("No user creator function registered")
        raise ValueError("No user creator function registered")
    
    def find_user_by_email(self, email: str) -> Optional[Any]:
        """
        Find a user by email.
        
        Args:
            email: Email address
            
        Returns:
            User object or None if not found
        """
        if self._user_finder:
            return self._user_finder(email)
        
        user_logger.error("No user finder function registered")
        raise ValueError("No user finder function registered")
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        if self._email_sender:
            return self._email_sender(to_email, subject, html_body, text_body)
        
        # Default email sender
        if not all([self.email_sender, self.email_server, self.email_username, self.email_password]):
            user_logger.error("Email settings not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_sender
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add text body
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            
            # Add HTML body
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            server = smtplib.SMTP(self.email_server, self.email_port)
            if self.email_use_tls:
                server.starttls()
            server.login(self.email_username, self.email_password)
            server.sendmail(self.email_sender, to_email, msg.as_string())
            server.quit()
            
            user_logger.debug(f"Email sent to {to_email}")
            return True
        except Exception as e:
            user_logger.error(f"Error sending email: {str(e)}")
            return False
    
    def generate_token(self, data: Dict[str, Any]) -> str:
        """
        Generate a token for email confirmation or password reset.
        
        Args:
            data: Data to encode in the token
            
        Returns:
            Token
        """
        # Add timestamp to data
        data['timestamp'] = int(time.time())
        
        # Convert data to string
        data_str = '&'.join(f"{key}={value}" for key, value in data.items())
        
        # Generate signature
        secret_key = getattr(self.app, 'session_secret_key', 'default-secret-key')
        signature = hashlib.sha256((data_str + secret_key).encode('utf-8')).hexdigest()
        
        # Encode token
        token = f"{data_str}&signature={signature}"
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a token.
        
        Args:
            token: Token to verify
            
        Returns:
            Decoded data or None if the token is invalid
        """
        try:
            # Parse token
            parts = token.split('&')
            data = {}
            for part in parts:
                if '=' in part:
                    key, value = part.split('=', 1)
                    data[key] = value
            
            # Extract signature
            if 'signature' not in data:
                user_logger.warning("Token has no signature")
                return None
            
            signature = data.pop('signature')
            
            # Verify signature
            data_str = '&'.join(f"{key}={value}" for key, value in data.items())
            secret_key = getattr(self.app, 'session_secret_key', 'default-secret-key')
            expected_signature = hashlib.sha256((data_str + secret_key).encode('utf-8')).hexdigest()
            
            if signature != expected_signature:
                user_logger.warning("Invalid token signature")
                return None
            
            # Check expiration
            if 'timestamp' in data:
                timestamp = int(data['timestamp'])
                if time.time() - timestamp > self.token_expiration:
                    user_logger.warning("Token has expired")
                    return None
            
            return data
        except Exception as e:
            user_logger.error(f"Error verifying token: {str(e)}")
            return None
    
    def send_confirmation_email(self, user: Any) -> bool:
        """
        Send a confirmation email to a user.
        
        Args:
            user: User object
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        if not hasattr(user, 'email'):
            user_logger.error("User object must have an email attribute")
            return False
        
        # Generate token
        token = self.generate_token({'user_id': user.get_id(), 'action': 'confirm_email'})
        
        # Create confirmation URL
        confirmation_url = f"{self.confirm_email_url}?token={token}"
        
        # Send email
        subject = "Confirm your email address"
        html_body = f"""
        <p>Please confirm your email address by clicking the link below:</p>
        <p><a href="{confirmation_url}">{confirmation_url}</a></p>
        <p>If you did not register for this account, you can ignore this email.</p>
        """
        
        return self.send_email(user.email, subject, html_body)
    
    def send_password_reset_email(self, user: Any) -> bool:
        """
        Send a password reset email to a user.
        
        Args:
            user: User object
            
        Returns:
            True if the email was sent successfully, False otherwise
        """
        if not hasattr(user, 'email'):
            user_logger.error("User object must have an email attribute")
            return False
        
        # Generate token
        token = self.generate_token({'user_id': user.get_id(), 'action': 'reset_password'})
        
        # Create reset URL
        reset_url = f"{self.reset_password_url}/confirm?token={token}"
        
        # Send email
        subject = "Reset your password"
        html_body = f"""
        <p>You have requested to reset your password. Click the link below to reset it:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>If you did not request a password reset, you can ignore this email.</p>
        """
        
        return self.send_email(user.email, subject, html_body)
    
    def _render_register_form(self):
        """
        Render the registration form.
        
        Returns:
            Response object
        """
        # This is a placeholder. In a real application, you would render a template.
        return Response(
            status=200,
            body={"message": "Registration form"},
            content_type="application/json"
        )
    
    def _handle_register_form(self, request):
        """
        Handle the registration form submission.
        
        Args:
            request: HTTP request
            
        Returns:
            Response object
        """
        try:
            # Get form data
            data = request.json or {}
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            
            # Validate data
            if not all([username, email, password]):
                return Response(
                    status=400,
                    body={"error": "Missing required fields"},
                    content_type="application/json"
                )
            
            # Check if email is valid
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return Response(
                    status=400,
                    body={"error": "Invalid email address"},
                    content_type="application/json"
                )
            
            # Check if user already exists
            existing_user = self.find_user_by_email(email)
            if existing_user:
                return Response(
                    status=400,
                    body={"error": "Email address already registered"},
                    content_type="application/json"
                )
            
            # Create user
            user = self.create_user(username, email, password)
            
            # Send confirmation email if enabled
            if self.enable_email_confirmation:
                self.send_confirmation_email(user)
            
            # Log in the user
            login_user(user)
            
            return Response(
                status=200,
                body={"message": "Registration successful"},
                content_type="application/json"
            )
        except Exception as e:
            user_logger.error(f"Error handling registration: {str(e)}")
            return Response(
                status=500,
                body={"error": "Internal server error"},
                content_type="application/json"
            )
    
    def _handle_confirm_email(self, token):
        """
        Handle email confirmation.
        
        Args:
            token: Confirmation token
            
        Returns:
            Response object
        """
        if not token:
            return Response(
                status=400,
                body={"error": "Missing token"},
                content_type="application/json"
            )
        
        # Verify token
        data = self.verify_token(token)
        if not data or data.get('action') != 'confirm_email':
            return Response(
                status=400,
                body={"error": "Invalid or expired token"},
                content_type="application/json"
            )
        
        # Get user
        user_id = data.get('user_id')
        if not user_id or not self.login_manager:
            return Response(
                status=400,
                body={"error": "Invalid token"},
                content_type="application/json"
            )
        
        user = self.login_manager._load_user(user_id)
        if not user:
            return Response(
                status=400,
                body={"error": "User not found"},
                content_type="application/json"
            )
        
        # Confirm email
        if hasattr(user, 'email_confirmed'):
            user.email_confirmed = True
            user_logger.debug(f"Email confirmed for user: {user_id}")
        
        return Response(
            status=200,
            body={"message": "Email confirmed successfully"},
            content_type="application/json"
        )
    
    def _redirect_to_login(self):
        """
        Redirect to the login page.
        
        Returns:
            Response object
        """
        from proapi.utils.helpers import redirect
        return redirect(self.login_url)


# Convenience function to get the user manager
def get_user_manager():
    """
    Get the user manager for the current request.
    
    Returns:
        UserManager instance or None if not available
    """
    request = get_current_request()
    if not request or not hasattr(request, 'app') or not hasattr(request.app, '_user_manager'):
        return None
    
    return request.app._user_manager
