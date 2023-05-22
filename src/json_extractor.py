import json
import os
import utils
import argparse
##This file attempts to extract a model's generated data from a json file, and create a text file with a schema like:
## paragraph 1
## paragraph 2
## paragraph 3
## .....
## paragraph N
#Where N is the amount of json elements in jsonFilePath
class ParagraphExtractor: #Create a class which will extract paragraphs from a given json file, and place them into .txt files with the same name
    def __init__(self, jsonChapterPath, model_dir):
        self.jsonChapterPath = jsonChapterPath
        self.jsonChapterData = None
        self.jsonChapterName = os.path.basename(jsonChapterPath)
        self.txtChapterPath = f"{model_dir}{self.jsonChapterName.split('.')[0]}.txt"
        self.txtChapterFile = open(self.txtChapterPath, "w")
    
    def loadJson(self):
        with open(self.jsonChapterPath) as jsonFile:
            self.jsonChapterData = json.load(jsonFile)
            self.jsonChapterData = self.jsonChapterData[
                list(self.jsonChapterData.keys())[0]
            ]

    def extract_write_paragraphs(self, model_id):
        for paragraph in self.jsonChapterData:
            paragraphText = paragraph[model_id].replace('\n', '')
            self.txtChapterFile.write(f"{paragraphText}\n")
        self.txtChapterFile.close()
        return self.txtChapterPath

def main(model_id):
    ##Actually create and fill files below here :)
    #May have to iterate over values given in cmdline but maybe not idk
    ##But the iteration will just wrap the code below...not too difficile :D
    paragraph_extractor = ParagraphExtractor("test.json", model_dir=f"data/processed-data/generated-chapters/{model_id}/")
    paragraph_extractor.loadJson()
    paragraph_extractor.extract_paragraphs(model_id)
if __name__=="__main__":
    #EXAMPLE USAGE: python json_extractor.py -c "chapter_file1" "chapter_file2" "chapter_filen" -m "text-davinci-003"
    parser = argparse.ArgumentParser(description='Create generated chapter files')
    parser.add_argument('-c', '--chapter-json-files', type=str, nargs='+', help="Path to chapter JSON file")
    parser.add_argument('-m', '--model-id', type=str)
    parser.add_argument('-o', '--output-dir', type=str, default="../data/processed-data/context-data", help="Path to Ouput directory")
    args = parser.parse_args()
    parent_directory = f"..data/processed-data/generated-chapters/{args.model_id}/"
    
    utils.styled_print(f"Creating Generated Paragraph Files in {parent_directory}", header=True)
    os.makedirs(parent_directory, exist_ok=True)

    for chapter_file in args.chapter_json_files:
        paragraph_extractor = ParagraphExtractor(chapter_file, model_dir=f"../data/processed-data/generated-chapters/{args.model_id}/")
        paragraph_extractor.loadJson()
        utils.styled_print(f"Extracted {args.model_id} generated data from {chapter_file}")
        paragraph_extractor.extract_write_paragraphs(args.model_id)
        utils.styled_print(f"Created {chapter_file}.txt file")
    utils.styled_print(F"Done extracting {args.model_id} generated data")

