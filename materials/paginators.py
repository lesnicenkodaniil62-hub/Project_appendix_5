from rest_framework.pagination import PageNumberPagination


class MaterialsPagination(PageNumberPagination):
    """
    Кастомный пагинатор для списков курсов и уроков.
    """

    # Количество элементов на странице по умолчанию
    page_size = 10

    # Имя параметра в URL, через который клиент может запросить свой размер страницы
    # Пример: ?page=2&page_size=5
    page_size_query_param = "page_size"

    # Максимально допустимый размер страницы (защита от запросов типа ?page_size=10000)
    max_page_size = 50
