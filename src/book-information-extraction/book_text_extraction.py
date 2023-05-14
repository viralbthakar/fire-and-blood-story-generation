import re
import os

BASE_PATH = "data/book/"
class ChapterExtractor: #This class is meant to split a given text(str) into chapters
    def __init__(self, text:str):
        self.text = text #Actual book text 
    
    def extract_chapters(self):
        chapter_delimiter = re.compile(r'(?:(?<=\n)|(?<=^))((?:\d+|chapter|[IVXLMC]+)\s+)') #An attempted all encompassing chapter delimeter regex
        chapter_count = -1 #Variable to store how many chapters have been processed
        lines = self.text.split("\n") #Get each line of the book
        chapter_name = '' #String which will hold the current chapter's name
        chapter = '' #String whivh will hold the current chapter's text
        #The following iteration will split our text into chapters
        for line in lines:
            #If the current line is a chapter delimeter, we will store the current chapter's name
            #The intuition behind the follwing logic is, if we have reached a new chapter delimeter, let's return the current chapter text being stored
            if bool(chapter_delimiter.search(line.lower())):  # is it a chapter line?
                chapter_name = line.strip()
                #If the chapter string has len > 0 we will increment the chapter count, and yeild/return the current chapter text
                if chapter:
                    chapter_count += 1
                    yield chapter_count, chapter_name, chapter
                    chapter = '' #Reset chapter text to nothing
                #If chapter has no data, just go to the next line, as current one is just the chapter delimeter
                else:
                    continue 
            #For any line which isn't a chapter delimeter, place it in the current chapter text string
            else:
                chapter += '\n' + line.strip()
        yield chapter_count, chapter_name, chapter

    def generate_all_chapter(self, start_str, end_str):
        # start = False
        chapter_dict = {} #A dictionary which will store the {"chapter_number": chapter_text}
        #For each yeilded value in the extract chapters generator
        for i in self.extract_chapters():
            chapter_dict[f"{i[0]}-{i[1]}"] = i[2] #Set the current chapter number key to the current chapter text value

            # if start_str in i:
            #     start = True
            # if not start:
            #     continue
            # print(i)
            # if end_str in i:
            #     break
        return chapter_dict
    

def write_to_file(chapter_files_dict:dict, title:str):
        #Take a dictionary of chapter file names
        os.mkdir(f"{BASE_PATH}{title}") #Make a directory specifically for the book title
        #For each chapter, write it's text to a file named from the chapter number, in the title drectory
        for chapter in chapter_files_dict: 
            print(f"Writing to file: {chapter}")
            with open(f"data/{title}/{chapter}", "w") as file:
                file.write(chapter_files_dict[chapter])
    
class ParagraphExtractor:
    def __init__(self, data_path:str, title:str):
        self.data_path = data_path #The current file's path
        self.title = title #The title of the book
    
    def extract_paragraphs(self):
        quoted_text = re.compile(r'“.*”') #Delimeter for quoted text
        #Store the lines of the current file, so we can parse them into paragraphs
        with open(f"data/{self.title}/{self.data_path}", "r") as f:
            lines = f.readlines()

        paragraph = '' #Text containg current paragraph
        skip = False #Boolean to allow us to skip blank lines
        for i,line in enumerate(lines):
            #We want to add each non-empty line to the paragraph, and once an empty line is reached, yeild paragraph, then reset it
            #However, if we

            if bool(quoted_text.search(line)):
                skip = True
                
            if line.isspace():  # is it an empty line?
                if skip: #Since dialogue usually has a space right afterwards, this will allow for a single dialogue to be in a full paragraph
                    skip=False
                    continue
                if paragraph:
                    yield paragraph
                    paragraph = ''
                    skip = False
                else:
                    continue
            else:
                paragraph += ' ' + line.strip()
             # If the next line is also a dialogue line, continue adding it to the current paragraph
            if i < len(lines) - 1 and bool(quoted_text.search(lines[i + 1])):
                continue
        yield paragraph

    def generate_all_paragraphs(self):

        #Let's create new cleaned chapter files, with proper paragraphs
        #But let's also add to our json file, where eahc book will have a chapters key, with a list of the clean chapter directories
        with open(f"data/{self.title}/{self.data_path}_cleaned.txt", "w+") as file:
            for i in self.extract_paragraphs():
                print("WRITING")
                file.write(i)
                file.write("\n")
        yield f"data/books/{self.title}/{self.data_path}_cleaned.txt"


        