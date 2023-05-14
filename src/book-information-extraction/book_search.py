import requests
import urllib.parse
import json
from collections import defaultdict
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg.query import get_etexts


##This file is meant to search in the OpenLibrary API, and return a list of books
##Then, this file will search for the text of those books in Gutenberg


class Search:
    'Search from openlibrary, then find those books on gutenberg, and save them'
    def __init__(self, data_path):
        self.data_path = data_path
        self.book_dict = {}
    
    def search_openlibrary(self, genre_list):
        """
        This script will search openlibrary N times, where N is the amount of genres you want to have for your dataset
        """
        #For each genre, search openlibrary
        for genre in genre_list:
            print(genre)
            try:
                OL_req = requests.get(f'http://openlibrary.org/subjects/{genre}.json?&limit=1')
            except:
                raise Exception(ConnectionRefusedError)
            OL_req_dict = json.loads(OL_req.text)
            for book in OL_req_dict["works"]:
                self.book_dict[book["title"]] = {"date":book["first_publish_year"], "authors":[author["name"] for author in book["authors"]], "genre":genre,"pages":0}
        return self.book_dict
    
    def search_gutenberg(self, json_path):
        #For each book title found 
        for book in self.book_dict:
            #Query should be authorname%20title
            query = f'{self.book_dict[book]["authors"][0]+" "+book}'.replace(" ", "%20")

            #Request Gutendex for the gutenberg ID
            gut_req = requests.get(f'http://gutendex.com/books?search={query}')
            gut_req_dict = json.loads(gut_req.text)
            
            #If there are no results from gutindex, skip the book title
            if gut_req_dict["count"] < 1:
                print(f'No search results for {urllib.parse.quote(self.book_dict[book]["authors"][0]+book)}')
                continue
            #Find the actual text fro the book from the Gutenberg python module, and add it to the book's dictionary
            gut_info = gut_req_dict["results"][0]
            self.book_dict[book]["gutenberg_id"] = int(gut_info["id"])
            self.book_dict[book]["text"] = strip_headers(load_etext(self.book_dict[book]["gutenberg_id"])).strip()
            print(f"Found text for {book}")

            #Save the book dictionary to a json file
        with open(json_path, "a") as json_file:
            json.dump(self.book_dict, json_file)
        
    


