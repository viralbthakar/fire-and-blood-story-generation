import os
import json
import argparse
import pandas as pd
from dotenv import load_dotenv
from collections import defaultdict
from utils import get_context_data, extract_context_for_file, styled_print, get_generated_paragraphs

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Context Dataset')
    parser.add_argument('-cf', '--chapter-files', type=str, nargs='+', help="Path to JSON file")
    parser.add_argument('-o', '--output-dir', type=str, default="../data/processed-data/context-data", help="Path to Ouput directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    
    data_dict = defaultdict(dict)
    for chapter in args.chapter_files:
        styled_print(f"Processig File {os.path.basename(chapter)}", header=True)
        with open(chapter) as chapter_file:
            parsed_json = json.load(chapter_file)
        paragraphs_context = parsed_json[f"{os.path.splitext(os.path.basename(chapter))[0]}.txt"]
        gen_data_dict = get_generated_paragraphs(paragraphs_context, api_key, parakey='test-model')
        
        data_dict[os.path.splitext(os.path.basename(chapter))[0]] = gen_data_dict
        with open(os.path.join(args.output_dir, f"{os.path.splitext(os.path.basename(chapter))[0]}.json"), 'w') as fp:
            json.dump(data_dict, fp, indent=4)
