from apps.auth_user.models import UserProfile

def user_mode(chat_id):
    user = UserProfile.objects.filter(chat_id=chat_id).first()
    return user.user_mode