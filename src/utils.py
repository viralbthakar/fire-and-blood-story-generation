import json
import openai
import tiktoken
from collections import defaultdict
##Imports from A1 utils.py
import os
# import docx
import time
import string
import random
import zipfile
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
from nltk.tokenize import RegexpTokenizer


def is_json(myjson):
  try:
    json.loads(myjson)
  except ValueError as e:
    return False
  return True

def styled_print(text, header=False):
    """Custom Print Function"""
    class style:
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    if header:
        print(f'{style.BOLD}› {style.UNDERLINE}{text}{style.END}')
    else:
        print(f'    › {text}')

def upload_file(file_path, api_key):
    openai.api_key = api_key
    response = openai.File.create(
        file=open(file_path, "rb"),
        purpose='fine-tune'
    )
    return response["id"]

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def get_context_data(paragraph, api_key):
    openai.api_key = api_key
    prompt_prefix = 'Extract characters, places, events, verbs and adjectives from the give text below. Return valid json following format {"characters":[], "places":[], "events":[], "verbs":[], "adjectives":[]}. Do not escape the double quotes in the output:'
    prompt_ip = prompt_prefix + f"\n\n{paragraph}"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_ip,
        max_tokens=2048,
        top_p=1.0,
        frequency_penalty=0.8,
        presence_penalty=0.8
    )
    if is_json(response["choices"][0]["text"]):
        return json.loads(response["choices"][0]["text"]), 1.0, response
    else:
       return {"characters":[], "places":[], "events":[], "verbs":[], "adjectives":[]}, 0.0, response

def get_written_paragraph(prompt_json, api_key, model):
    openai.api_key = api_key
    if model == "text-davinci-003":
        prompt_prefix = "Pretend you are writing a fictional novel. Write one paragraph of the novel using following JSON data. Use `current_paragraph` to create characters, places, events and keywords for the writing. Use `previous_paragraph` to get the context of the previous paragraph. Creatively add new characters and places in the story by choosing them from `global_context`."
        encoding_name = 'p50k_base'
        mt = 4097
    else:
        prompt_prefix = ""
        encoding_name = 'r50k_base'
        mt = 2049
    
    prompt_ip = prompt_prefix + f"\n\n{prompt_json}"
    
    num_tokens = num_tokens_from_string(prompt_ip, encoding_name)
    max_tokens = mt - num_tokens
    response = openai.Completion.create(
        model=model,
        prompt=prompt_ip,
        max_tokens=max_tokens,
        top_p=1.0,
        frequency_penalty=0.8,
        presence_penalty=0.8
    )
    return response["choices"][0]["text"]

def finetune_gpt_model(train_id, validation_id, api_key, suffix='fire-and-blood', model='davinci', n_epochs=4):
    openai.api_key = api_key
    response = openai.FineTune.create(
        training_file=train_id,
        validation_file=validation_id,
        model=model,
        n_epochs=n_epochs,
        suffix=suffix
    )
    return response

def extract_context_for_file(file, api_key):
    data_dict = []
    with open(file) as chapter:
        for i, paragraph in enumerate(chapter):
            styled_print(f"Extracting Context for Paragraph {i}")
            paragraph_dict = {}
            paragraph_dict["paragraph_id"] = i
            paragraph_dict["paragraph"] = paragraph.strip()
            context_data, valid, response = get_context_data(paragraph.strip(), api_key)
            context_keys = context_data.keys()
            paragraph_dict["valid"] = valid
            if valid == 0.0:
                styled_print(f"Invalid JSON Response for Paragraph {i}")
                styled_print(response["choices"][0]["text"])
            for key in context_keys:
                paragraph_dict[key.lower()] = context_data[key]
            data_dict.append(paragraph_dict)
    return data_dict

def get_global_context(paragraphs_context):
    global_context = defaultdict(list)
    for i, paragraph_dict in enumerate(paragraphs_context):
        global_context["characters"].extend(paragraph_dict["characters"])
        global_context["places"].extend(paragraph_dict["places"])
    global_context['characters'] = list(set(global_context["characters"]))
    global_context['places'] = list(set(global_context["places"]))
    return global_context

def get_prompt_json(global_context, paragraphs_context, paragraph_dict, id):
    prompt_json = {}
    if id == 0:
        prompt_json["previous_paragraph"] = {}
    else:
        prompt_json["previous_paragraph"] = {
            "characters": paragraphs_context[id-1]["characters"],
            "places": paragraphs_context[id-1]["places"],
            "events": paragraphs_context[id-1]["events"],
            "keywords": paragraphs_context[id-1]["verbs"] + paragraphs_context[id-1]['adjectives']
        }
    prompt_json["current_paragraph"] = {
            "characters": paragraph_dict["characters"],
            "places": paragraph_dict["places"],
            "events": paragraph_dict["events"],
            "keywords": paragraph_dict["verbs"] + paragraph_dict['adjectives']
    }
    prompt_json["global_context"] = {
        "characters": global_context["characters"],
        "places": global_context["places"]
    }
    return prompt_json


def get_generated_paragraphs(paragraphs_context, api_key, model="text-davinci-003"):
    data_dict = []
    global_context = get_global_context(paragraphs_context)
    for i, paragraph_dict in enumerate(paragraphs_context):
        styled_print(f"Extracting Context for Paragraph {paragraph_dict['paragraph_id']}")
        prompt_json = get_prompt_json(global_context, paragraphs_context, paragraph_dict, i)
        generated_paragraph = get_written_paragraph(prompt_json, api_key, model=model)
        paragraph_dict[model] = generated_paragraph
        styled_print(generated_paragraph)
        data_dict.append(paragraph_dict)
    return data_dict
    
def create_prompt_completion_data(paragraphs_context):
    prompt_comp_data = []
    global_context = get_global_context(paragraphs_context)
    for i, paragraph_dict in enumerate(paragraphs_context):
        styled_print(f"Extracting Context for Paragraph {paragraph_dict['paragraph_id']}")
        prompt_json = get_prompt_json(global_context, paragraphs_context, paragraph_dict, i)
        prompt_prefix = "Pretend you are writing a fictional novel. Write one paragraph of the novel using following JSON data. Use `current_paragraph` to create characters, places, events and keywords for the writing. Use `previous_paragraph` to get the context of the previous paragraph. Creatively add new characters and places in the story by choosing them from `global_context`."
        prompt_ip = prompt_prefix + f"\n\n{prompt_json}"
        completion = paragraph_dict['paragraph']
        d = {"prompt": prompt_ip, "completion":completion}
        prompt_comp_data.append(d)
    return prompt_comp_data


##STARTING HERE IS FROM A1 utils.py
big_data_dict = defaultdict(list)


def styled_print(text, header=False):
    """Custom Print Function"""
    class style:
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        END = '\033[0m'

    if header:
        print(f'{style.BOLD}› {style.UNDERLINE}{text}{style.END}')
    else:
        print(f'    › {text}')
    time.sleep(0.5)


def create_dir(root_dir, new_dir, header=True):
    styled_print(
        f'creating directory ... {os.path.join(root_dir, new_dir)}', header=header)
    os.makedirs(os.path.join(root_dir, new_dir), exist_ok=True)
    return os.path.join(root_dir, new_dir)


def random_select_dict(ip_dict, num_items):
    list_keys = random.choices(list(ip_dict.keys()), k=num_items)
    out_dict = {}
    for key in list_keys:
        out_dict[key] = ip_dict[key]
    return out_dict


def read_docx_file(file_path):
    zip_obj = zipfile.ZipFile(file_path)
    return zip_obj


def extract_images(file_path, out_path, extensions=[".jpg", ".jpeg", ".png", ".bmp"], verbose=0):
    styled_print(f"Extracting Images from {file_path}", header=True)
    image_file_paths = []
    zip_obj = read_docx_file(file_path)
    file_list = zip_obj.namelist()
    for file_name in file_list:
        _, extension = os.path.splitext(file_name)
        if extension in extensions:
            out_file_name = os.path.join(out_path, os.path.basename(file_name))
            if verbose:
                styled_print(f"Writing Image {file_name} to {out_file_name}")
            image_file_paths.append(out_file_name)
            with open(out_file_name, "wb") as out_file:
                out_file.write(zip_obj.read(file_name))
    return image_file_paths


def extract_paragraphs(file_path, out_path=None, min_char_count=1):
    styled_print(f"Extracting Paragraphs from {file_path}", header=True)
    paragraphs = {}
    document = docx.Document(file_path)
    for i in range(2, len(document.paragraphs)):
        if min_char_count is not None:
            if len(document.paragraphs[i].text) >= min_char_count:
                paragraphs[i] = document.paragraphs[i].text
        else:
            paragraphs[i] = document.paragraphs[i].text
    return paragraphs


def plot_box_plot_hist_plot(df, column, title="Distribution Plot", figsize=(16, 16),
                            dpi=300, save_flag=False, file_path=None):
    fig, (ax_box, ax_hist) = plt.subplots(
        nrows=2,
        sharex=True,
        figsize=figsize,
        gridspec_kw={"height_ratios": (.20, .80)},
        dpi=dpi,
        constrained_layout=False
    )
    sns.boxplot(data=df, x=column, ax=ax_box)
    sns.histplot(data=df, x=column, ax=ax_hist, kde=True, bins='sqrt')
    ax_box.set(xlabel='')
    ax_box.set_facecolor('white')
    ax_hist.set_facecolor('white')
    plt.title(title)
    if save_flag:
        fig.savefig(file_path, dpi=dpi, facecolor='white')
        plt.close()


def plot_count_plot(df, column, hue=None, title="Count Plot", figsize=(24, 24), dpi=300,
                    save_flag=False, file_path=None):
    fig, axs = plt.subplots(1, 1, figsize=figsize,
                            dpi=dpi, constrained_layout=False)
    pt = sns.countplot(data=df, x=column, hue=hue,
                       palette=sns.color_palette("Set2"))
    pt.set_xticklabels(pt.get_xticklabels(), rotation=30)
    if hue is not None:
        axs.legend(loc="upper right", title=hue)
    axs.set_facecolor('white')
    plt.title(title)
    if save_flag:
        fig.savefig(file_path, dpi=dpi, facecolor='white')
        plt.close()


def combine_multiple_text_files(data_path):
    import glob
    if os.path.exists(os.path.join(data_path, "combined.txt")):
        os.remove(os.path.join(data_path, "combined.txt"))

    read_files = glob.glob(os.path.join(data_path, "*.txt"))
    with open(os.path.join(data_path, "combined.txt"), "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())
    return os.path.join(data_path, "combined.txt")