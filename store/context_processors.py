from django.contrib.auth.models import User
from users.models import Notification

def notifications(request):
    context = {}

    if not request.user.is_authenticated:
        return context

    try:
        shop = request.user

        # Notifications sent to user
        user_notifications = Notification.objects.filter(shop=shop).exclude(is_read_by=shop).order_by('-created_at')

        # Global notifications from admin
        try:
            admin_user = User.objects.get(username='admin')
            global_notifications = Notification.objects.filter(shop=admin_user).exclude(is_read_by=shop)
        except User.DoesNotExist:
            global_notifications = []

        all_notifications = list(user_notifications) + list(global_notifications)
        context["notify"] = all_notifications

    except Exception as e:
        print("Error in notifications context:", e)

    return context
