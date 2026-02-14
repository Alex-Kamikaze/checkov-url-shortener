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

class ConnectionNotEstablishedError(Exception):
    """
    Возникает, если кто-то пытается использовать методы репозитория без контекстного менеджера
    """
    ...