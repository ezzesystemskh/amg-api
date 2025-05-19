from apps.auth_user.models import User, UserProfile
from lang import en, kh


LANGUAGES = {
    "en": en.translations,
    "kh": kh.translations,
}

_default_lang = "en"  # Default language


def translate(key, chat_id):
    user = User.objects.filter(chat_id=chat_id).first()
    if not user:
        lang = _default_lang
        return LANGUAGES.get(lang, {}).get(key, key)

    try:
        profile = user.user_profile
        lang = profile.language or _default_lang
        return LANGUAGES.get(lang, {}).get(key, key)

    except UserProfile.DoesNotExist:
        print(f"No profile found for user: {user}")
        return


# def translate(key, chat_id):
#     lang = _default_lang
#     return LANGUAGES.get(lang, {}).get(key, key)