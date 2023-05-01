import os
import json
import glob
import random
import argparse
import jsonlines
import pandas as pd
from dotenv import load_dotenv
from collections import defaultdict
from utils import get_context_data, extract_context_for_file, styled_print, \
      get_generated_paragraphs, create_prompt_completion_data, upload_file, finetune_gpt_model

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Context Dataset')
    parser.add_argument('-cf', '--chapter-files-dir', type=str, default="../data/processed-data/context-data", help="Path to JSON file Directory")
    parser.add_argument('-o', '--output-dir', type=str, default="../data/processed-data/fine-tunning-data", help="Path to Ouput directory")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    all_files = glob.glob(os.path.join(args.chapter_files_dir,'*.json'))
    training_files = all_files[:int(0.8 * len(all_files))]
    validation_files = all_files[int(0.8 * len(all_files)):]

    # Prepare Dataset File
    with jsonlines.open(os.path.join(args.output_dir, 'training.jsonl'), 'w') as train_file:
        for chapter in training_files:
            styled_print(f"Processig File {os.path.basename(chapter)}", header=True)
            prompt_prefix = ""
            with open(chapter) as chapter_file:
                parsed_json = json.load(chapter_file)
            paragraphs_context = parsed_json[os.path.splitext(os.path.basename(chapter))[0]]
            prompt_comp_data = create_prompt_completion_data(paragraphs_context)
            for d in prompt_comp_data:
                train_file.write(d)
    
    with jsonlines.open(os.path.join(args.output_dir, 'validation.jsonl'), 'w') as validation_file:
        for chapter in validation_files:
            styled_print(f"Processig File {os.path.basename(chapter)}", header=True)
            prompt_prefix = ""
            with open(chapter) as chapter_file:
                parsed_json = json.load(chapter_file)
            paragraphs_context = parsed_json[os.path.splitext(os.path.basename(chapter))[0]]
            prompt_comp_data = create_prompt_completion_data(paragraphs_context)
            for d in prompt_comp_data:
                validation_file.write(d)

    training_file_id = upload_file(os.path.join(args.output_dir, 'training.jsonl'), api_key)
    validation_file_id = upload_file(os.path.join(args.output_dir, 'validation.jsonl'), api_key)

    response = finetune_gpt_model(training_file_id, validation_file_id, api_key, suffix='test-fire-and-blood', model='davinci', n_epochs=4)
    print(response)