class URLAlreadyExistsError(Exception):
    """
    Возникает, когда происходит попытка вставить уже существующий URL в базу
    """
    ...

class URLNotFoundError(Exception):
    """
    Возникает, когда URL не найден в базе
    """
    ...