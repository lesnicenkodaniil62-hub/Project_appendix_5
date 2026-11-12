from urllib.parse import urlparse

from rest_framework import serializers


def validate_youtube_url(value: str):
    """
    Валидатор для проверки, что ссылка ведет на youtube.com.
    """
    if not value:
        return value

    parsed_url = urlparse(value)
    # Проверяем, содержит ли сетевое расположение (netloc) youtube.com
    # (это покроет и www.youtube.com, и m.youtube.com)
    if "youtube.com" not in parsed_url.netloc:
        raise serializers.ValidationError(
            "Разрешены только ссылки на youtube.com. Сторонние ресурсы запрещены."
        )

    return value