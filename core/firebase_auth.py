"""
Firebase Authentication Backend for Django REST Framework.
Verifies Firebase ID tokens and maps them to UserProfile.
"""
import logging
from django.conf import settings
from rest_framework import authentication, exceptions

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_app = None


def get_firebase_app():
    """Lazy-initialize Firebase Admin SDK."""
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app

    try:
        import firebase_admin
        from firebase_admin import credentials

        cred_path = settings.FIREBASE_CREDENTIALS_PATH
        if cred_path and cred_path != 'firebase-credentials.json':
            cred = credentials.Certificate(cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
        else:
            # Try default credentials or skip
            try:
                _firebase_app = firebase_admin.get_app()
            except ValueError:
                logger.warning("Firebase credentials not configured. Using session auth only.")
                return None
    except ImportError:
        logger.warning("firebase-admin not installed.")
        return None
    except Exception as e:
        logger.warning(f"Firebase init error: {e}")
        return None

    return _firebase_app


def verify_firebase_token(id_token):
    """Verify a Firebase ID token and return decoded claims."""
    app = get_firebase_app()
    if not app:
        return None

    try:
        from firebase_admin import auth
        decoded = auth.verify_id_token(id_token)
        return decoded
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        return None


class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    DRF Authentication class that verifies Firebase ID tokens.
    Expects header: Authorization: Bearer <firebase-id-token>
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        id_token = auth_header.split('Bearer ')[1].strip()
        if not id_token:
            return None

        decoded = verify_firebase_token(id_token)
        if not decoded:
            raise exceptions.AuthenticationFailed('Invalid or expired Firebase token.')

        # Get or create UserProfile
        from core.models import UserProfile
        firebase_uid = decoded.get('uid')
        email = decoded.get('email', '')

        try:
            user_profile = UserProfile.objects.get(firebase_uid=firebase_uid)
        except UserProfile.DoesNotExist:
            # Check if user exists by email (registered but not yet linked)
            try:
                user_profile = UserProfile.objects.get(email=email)
                user_profile.firebase_uid = firebase_uid
                user_profile.save(update_fields=['firebase_uid'])
            except UserProfile.DoesNotExist:
                raise exceptions.AuthenticationFailed('User not registered. Please register first.')

        if not user_profile.is_active:
            raise exceptions.AuthenticationFailed('Account deactivated.')
        if not user_profile.is_approved and user_profile.role != 'admin':
            raise exceptions.AuthenticationFailed('Account pending admin approval.')

        # Attach user_profile to a simple auth user object for DRF
        return (FirebaseUser(user_profile), None)


class FirebaseUser:
    """Wrapper to make UserProfile work with DRF's request.user."""

    def __init__(self, profile):
        self.profile = profile
        self.pk = profile.pk
        self.id = profile.pk
        self.email = profile.email
        self.is_authenticated = True
        self.is_active = profile.is_active
        self.is_staff = profile.role == 'admin'
        self.is_superuser = profile.role == 'admin'

    def __str__(self):
        return f"{self.profile.name} ({self.profile.role})"
