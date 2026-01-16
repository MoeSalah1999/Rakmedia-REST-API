import secrets
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_q.tasks import async_task

from .models import Employee

# Uncomment this block if you want to automatically create an employee profile when a new employee is added to the database.
# We're already using a signal that automatically creates a new user when and employee is added to the database,
# and we're using the user instance as the employee profile object.

#@receiver(post_save, sender=settings.AUTH_USER_MODEL)
#def create_employee_profile(sender, instance, created, **kwargs):
    #'''
    #Automatically create an Employee profile when a new user is created.
    #'''
    #if created:
        #department = Department.objects.get(id=1)
        #position = EmployeePosition.objects.get(id=1)

        #Fetch default company - adjust logic if your app allows multiple companies
        #default_company = Company.objects.first()
        #if not default_company:
           # print('!!! No company found. Skipping employee profile creation')
           # return
        

        #Avoid duplicates just in case
       # if hasattr(instance, 'employee_profile'):
       #     return
        
      #  Employee.objects.create(
        #    user=instance,
       #     company=default_company,
       #     first_name=instance.first_name or instance.username,
       #     last_name=instance.last_name or '',
       #     email=instance.email or '',
       #     employee_code=Employee.objects.count() + 1 #Simple auto code for now
       # )
       # print(f'Created Employee profile for user "{instance.username}" ')


    
User = get_user_model()



def generate_username(first_name, last_name):
    ''' Generate a unique username like john.doe or john.doe.2 '''
    base = f'{first_name.lower()}.{last_name.lower()}'.replace(' ', '')
    username = base
    counter = 1 
    while User.objects.filter(username=username).exists():
        counter += 1
        username = f'{base}.{counter}'
    return username



def generate_secure_password(length=12):
    ''' Generate a secure random password '''
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))



# Automatically creates a new user when an employee is added to the Database.
@receiver(post_save, sender=Employee)
def create_user_for_employee(sender, instance, created, **kwargs):
    if created and not instance.user:
        # Create a new user for this employee
        username = generate_username(instance.first_name, instance.last_name)
        password = generate_secure_password()

        user = User.objects.create_user(
            username=username,
            email=instance.email,
            password=password,
        )
        
        instance.user = user
        instance.save(update_fields=['user'])



@receiver(post_save, sender=User)
def enqueue_welcome_for_user(sender, instance, created, **kwargs):
    """
    Triggered when a Django user is created.
    Assumes Employee is created separately (if your logic creates both, adapt accordingly).
    """
    if not created:
        return

    # If you're creating user elsewhere and not creating Employee model, you can still send email.
    email = instance.email
    username = instance.username

    # ------ Preferred: create a one-time password reset link ------
    # You can use Django's PasswordResetTokenGenerator and build a link to frontend that accepts the token.
    # Example (backend generates token + uid):
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.encoding import force_bytes
    from django.utils.http import urlsafe_base64_encode

    token = default_token_generator.make_token(instance)
    uid = urlsafe_base64_encode(force_bytes(instance.pk))

    # Build a password reset URL pointing at your frontend route, include uid & token.
    # Example: https://your-frontend.com/auth/reset-password/?uid=<uid>&token=<token>
    frontend_base = getattr(settings, "FRONTEND_BASE_URL", None) or "http://localhost:3000"
    reset_path = f"/auth/reset-password/?uid={uid}&token={token}"
    password_reset_url = frontend_base + reset_path

    # Enqueue the safer reset-link email
    async_task("api.tasks.send_welcome_with_reset_link", username, email, password_reset_url)

    # ---------------- Alternative (not recommended): send plaintext password ----------------
    # If you created a random password and stored it temporarily during creation,
    # you could use that here. Example commented code:
    # plain_password = getattr(instance, "_plain_password", None)
    # if plain_password:
    #     async_task("api.tasks.send_welcome_email_plain", username, plain_password, email)