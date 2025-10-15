#тут будут все классы
#книга (Book)

#автор (Author)
class Author:
    def __init__(self, first_name: str, last_name: str, bio: str = ""):
        self.first_name: str = first_name
        self.last_name: str = last_name

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

#место книги (Location)
class Location:
    def __init__(self, rack: str, shelf: str):
        self.rack: str = rack
        self.shelf: str = shelf

    def __str__(self) -> str:
        return f"стеллаж {self.rack}, полка {self.shelf}"
    
#читатель (Reader)

#библиотекарь (Librarian)

#школьник (School)

#студент (Student)

#читательный зал (Room)

#читательский билет (Ticket)

#отзыв (Review) 

#читательский клуб (Club)

 