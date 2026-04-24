import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduevent.settings')
django.setup()

from core.models import UserProfile

def promote_admin(email):
    try:
        # Find user by email
        user = UserProfile.objects.get(email=email.lower().strip())
        
        # Promote to admin
        user.role = 'admin'
        user.is_approved = True
        user.save()
        
        print(f"\n[SUCCESS]: User '{user.name}' ({user.email}) has been promoted to Admin!")
        print("You can now login at the Admin Portal with this email.\n")
        
    except UserProfile.DoesNotExist:
        print(f"\n[ERROR]: No user found with email '{email}'.")
        print("Please register on the website first (e.g., as a teacher), then run this script again.\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promote_admin.py <user_email>")
        print("Example: python promote_admin.py admin@college.edu")
    else:
        promote_admin(sys.argv[1])
