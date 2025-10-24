# Собственные исключения


class LibraryError(Exception):
    pass


class BookNotAvailableError(LibraryError):
    def __init__(self, title: str):
        self.title = title
        super().__init__(f"Книга '{title}' недоступна: она уже выдана другому читателю.")


class BookNotFoundError(LibraryError):
    def __init__(self, isbn: str):
        self.isbn = isbn
        super().__init__(f"Книга с ISBN '{isbn}' не найдена в каталоге.")


class ReaderHasBooksError(LibraryError):
    def __init__(self, first_name: str, last_name: str, book_count: int):
        self.first_name = first_name
        self.last_name = last_name
        self.book_count = book_count
        super().__init__(
            f"Невозможно удалить читателя '{first_name} {last_name}': "
            f"он не вернул {book_count} книга(и)."
        )


class DuplicateBookError(LibraryError):
    def __init__(self, isbn: str):
        self.isbn = isbn
        super().__init__(f"Книга с ISBN '{isbn}' уже существует в каталоге.")