import os
import json

import book_text_extraction 
import book_search

#In this file, we will take books from a given search and extract their paragraphs.
#Specifically, it creates N*C text files, where N is the amount of text files, and C is the total amount of chapters found in each book
#Each book will have a folder created for it, and this will contain c+1 files, c chapter files, and 1 text file of the whole book


if __name__ == "__main__":

    m = book_search.Search(0)
    m.search_openlibrary(["fiction"])
    m.search_gutenberg("raw_data.json")

    for book in m.book_dict:
        title = book
        chapter_extractor = book_text_extraction.ChapterExtractor(m.book_dict[title]["text"])
        chapter_extractor.extract_chapters()
        x = chapter_extractor.generate_all_chapter(start_str="LIII", end_str="*** END OF THE PROJECT GUTENBERG EBOOK OLIVER TWIST ***")
        book_text_extraction.write_to_file(x, title)
        m.book_dict[book]["chapters"] = []
        m.book_dict[book].pop("text")
        for file in x:
            p_extractor = book_text_extraction.ParagraphExtractor(file, title)
            p_extractor.extract_paragraphs()
            for path in p_extractor.generate_all_paragraphs():
                m.book_dict[book]["chapters"].append(path)
            os.remove(f"data/{title}/{file}")
    with open("new_data.json", "w") as json_file:
            json.dump(m.book_dict, json_file)
    