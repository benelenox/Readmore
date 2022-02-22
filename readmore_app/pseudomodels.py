import requests
from .models import *
from django.db.models.query import QuerySet

class Book:
    def __init__(self, isbn):
        self.isbn = str(isbn)
        self.book_data = {}
        
        book_api_key = 'AIzaSyCrRXmYA10KFK9bFearnoAGZ8Suzn1aFgI'
        book_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+isbn:{isbn}&key={book_api_key}').json()
        if 'items' in book_info.keys():
            self.book_data = book_info['items'][0]['volumeInfo']
        
        self.title = self.book_data.get('title', '')
        self.authors = self.book_data.get('authors', '')
        self.publisher = self.book_data.get('publisher', '')
        self.published_date = self.book_data.get('publishedDate', '')
        self.description = self.book_data.get('description', '')
        self.isbn10 = self.book_data.get("industryIdentifiers", [{}])[0].get('identifier', '')
        self.isbn13 = self.book_data.get("industryIdentifiers", [{},{}])[1].get('identifier', '')
        self.page_count = self.book_data.get('pageCount', '')
        self.categories = self.book_data.get('categories', '')
        self.rating = self.book_data.get('averageRating', '')
        self.maturity_rating = self.book_data.get('maturityRating', '')
        self.small_thumbnail = self.book_data.get('imageLinks', {}).get('smallThumbnail', '')
        self.thumbnail = self.book_data.get('imageLinks', {}).get('thumbnail', '')
        self.language = self.book_data.get('language', '')
    
    @staticmethod
    def strings_to_book(list_or_isbn):
        """
        Converts strings to Book objects
        """
        if type(iterable_or_isbn) is list:
            return [Book(isbn) for isbn in list_or_isbn]
        else:
            return Book(isbn)
    
    @staticmethod
    def booklike_to_book(queryset_or_booklike):
        """
        Converts Book-Like Objects (e.g. ClubBook) to Book objects
        """
        if type(queryset_or_booklike) is QuerySet:
            bookslist = [Book(book.isbn) for book in queryset_or_booklike]
            for book, booklike in zip(bookslist, queryset_or_booklike):
                book.id = booklike.id
            return bookslist
        else:
            book = Book(queryset_or_booklike.isbn)
            book.id = queryset_or_booklike.id
            return book
            
    @staticmethod
    def search_googlebooks(query, type='general'):
        """
        Searches Google Books API For The Query
        *** IMPORTANT: THIS METHOD RETURNS JSON, NOT BOOK OBJECTS ***
        """
        book_api_key = 'AIzaSyCrRXmYA10KFK9bFearnoAGZ8Suzn1aFgI'
        if type == "general":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=40&key={book_api_key}').json()
        elif type == "title":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+intitle:{query}&maxResults=40&key={book_api_key}').json()
        elif type == "author":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+inauthor:{query}&maxResults=40&key={book_api_key}').json()
        elif type == "isbn":
            books_info = requests.get(f'https://www.googleapis.com/books/v1/volumes?q=+isbn:{query}&maxResults=40&key={book_api_key}').json()
        if 'items' in books_info.keys():
            books = [book for book in books_info['items'] if 'ISBN_13' in [x.get('type') for x in book['volumeInfo'].get('industryIdentifiers', [{}])]]
        else:
            books = []
        
        return books