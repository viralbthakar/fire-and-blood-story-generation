import json
import openai
import tiktoken
from collections import defaultdict

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
