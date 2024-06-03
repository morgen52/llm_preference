import json
import os
import re
from tqdm import tqdm

from configs import language_keys, keys2lang
    
def match_programming_language(text):
    results = {"exactly": [], "involve": []}

    text = text.lower()

    ## match ```*\n*``` pattern for programming language
    has_code = False
    if '```' in text:
        has_code = True
    match = re.match(r'```(.*)\n', text)
    if match:
        has_code = True
        for m in match.groups():
            # if m contains not [a-zA-Z+] characters, it is not a programming language
            if re.match(r'^[a-zA-Z+]+$', m):
                results["exactly"].append(keys2lang.get(m, m).lower())

    ### Then search keywords in the language_keys, for programming language
    for key, values in language_keys.items():
        for value in values:
            if value in text:
                results["involve"].append(key.lower())
    
    return results['exactly'], results['involve'], has_code

def clean_pl(lst):
    pl_lst = []
    for pl in lst:
        if pl in ['markdown', 'mdx', 'latex', 'mermaid', 'scss', 'css', 'html', 'xml', 'yaml', 'less', 'json', 'txt', 'plantuml' ,\
                  'shell', 'makefile', 'dockerfile', 'protobuf' ,\
                  'italian', 'const', 'diff', 'import']:
            continue
        pl_lst.append(pl)
    return pl_lst

def handle_json_file(file_path, cnt):
    if file_path not in cnt:
        cnt[file_path] = {}
    
    with open(file_path) as f:
        data = json.load(f)

    for item in data:
        if item['id'] in cnt[file_path]:
            continue
            
        record = {
            'human': {'exactly': [], 'involve': [], 'unknown': False, 'has_code': False},
            'gpt': {'exactly': [], 'involve': [], 'unknown': False, 'has_code': False}
        }

        for turn in item['conversations']:
            speaker = turn['from']

            if speaker in ['chatgpt', 'bing']:
                speaker = 'gpt'
            if speaker in ['system', 'user']:
                speaker = 'human'
            if speaker not in ['human', 'gpt']:
                print(f"Unknown speaker: {speaker} in {file_path}")

            exactly, involve, has_code = match_programming_language(turn['value']) # match programming language
            record[speaker]['exactly'] += exactly

            if not record['gpt']['has_code']: # Only record "has_code" flag When GPT dose not provide code
                record[speaker]['has_code'] = has_code if has_code else record[speaker].get('has_code', False)
                record[speaker]['involve'] += involve
            else:
                if speaker == 'gpt':
                    record[speaker]['involve'] += involve

        # remove duplicates
        record['human']['exactly'] = clean_pl(list(set(record['human']['exactly'])))
        record['human']['involve'] = clean_pl(list(set(record['human']['involve'])))
        record['gpt']['exactly'] = clean_pl(list(set(record['gpt']['exactly'])))
        record['gpt']['involve'] = clean_pl(list(set(record['gpt']['involve'])))
        
        if len(record['human']['exactly']) == 0 and len(record['human']['involve']) == 0:
            record['human']['unknown'] = True
        if len(record['gpt']['exactly']) == 0 and len(record['gpt']['involve']) == 0:
            record['gpt']['unknown'] = True
        
        cnt[file_path][item['id']] = record

    return cnt

def print_all_pl(data):
    pl_set = set()
    for file_path, itemset in data.items():
        for id, item in itemset.items():
            for speaker in ['human', 'gpt']:
                pl_set.update(item[speaker]['exactly'])
                pl_set.update(item[speaker]['involve'])
    print(pl_set)

def main(cfg):
    cnt = {}
    dp = cfg["dataset_path"]
    for file in tqdm(os.listdir(dp), total=len(os.listdir(dp))):
        cnt = handle_json_file(os.path.join(dp, file), cnt)
    print_all_pl(cnt)
    with open(cfg["output_path"], 'w') as f:
        json.dump(cnt, f, indent=2)

import argparse
import yaml

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str, default='sharegpt_vicuna_cfg.yaml')
    # parser.add_argument('--config', type=str, default='sharegpt_s52k_cfg.yaml')
    args = parser.parse_args()

    cfg = yaml.load(open(args.config, 'r'), Loader=yaml.FullLoader)

    main(cfg)