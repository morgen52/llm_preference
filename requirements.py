import json
import os
import random
from tqdm import tqdm
from typing import List

from tools.cluster import cluster, reallocate_topics
from tools.chatgpt import chat

def find_raw_data(dataset_path, id):
    with open(dataset_path) as f:
        dataset = json.load(f)
    for item in dataset:
        if item['id'] == id:
            return item

def requirements_markup(file_path, save_path): # obtain detailed requirements
    with open(file_path) as f:
        data = json.load(f)
    save_name = file_path.split('.')[0].split('_')[-1]
    
    filtered_data = {}

    cnt = 0

    for dataset_path, itemset in data.items():
        for id, item in itemset.items():
            # if len(item['human']['exactly']) == 0 and len(item['gpt']['exactly']) > 0:
            if item['human']['unknown'] and (not item['human']['has_code']) and len(item['gpt']['exactly']) > 0:
                cnt += 1
                if len(item['gpt']['exactly']) > 1:
                    print(f'Warning: {dataset_path} {id} has multiple gpt exactly pl {item["gpt"]["exactly"]}')
                for pl in item['gpt']['exactly']:
                    if pl not in filtered_data:
                        filtered_data[pl] = []
                    filtered_data[pl].append({
                        'dataset_path': dataset_path,
                        'id': id,
                        'value': find_raw_data(dataset_path, id)
                    })

    print(f'Found {cnt} requirements')

    with open(save_path, 'w') as f:
        json.dump(filtered_data, f, indent=2)

    # with open(f'requirement_{save_name}.json', 'w') as f:
    #     json.dump(filtered_data, f, indent=2)

def requirements_cluster(file_path):
    N = 100
    save_name = file_path.split('.')[0].split('_')[-1]
    save_path = f"cluster_req_{save_name}_{N}.json"

    if not os.path.exists(f"picked_{save_name}_{N}.json"):
        with open(file_path, 'r') as f:
            data = json.load(f)
        metadata = {}
        pickdata = {}
        for language, items in data.items():
            metadata[language] = len(items)
        total = sum(metadata.values())
        pick = 0
        for language, count in metadata.items():
            print(f'{language}: {count/total*N:.2f}% ({count})')
            pickdata[language] = random.sample(data[language], max(1, int(count/total*N)))
            pick += len(pickdata[language])
        # save picked data
        print(f'Picked {pick} requirements')
        with open(f"picked_{save_name}_{N}.json", 'w') as f:
            json.dump(pickdata, f, indent=2)
    
    with open(f"picked_{save_name}_{N}.json") as f:
        pickdata = json.load(f)
    pick = 0
    for language, items in pickdata.items():
        pick += len(items)
    print(f'Load {pick} picked requirements')

    reqs = []
    ids = []
    for language, items in pickdata.items():
        for item in items:
            req = json.dumps(item['value']["conversations"])
            reqs.append(req)
            ids.append(item['id'])
    labels, abstracts, topics = cluster(reqs, ids)

    print(f"{len(topics)} topics generated: {topics}")

    for language in pickdata.keys():
        # add labels and abstracts to items
        for idx, item in enumerate(pickdata[language]):
            id = item['id']
            pickdata[language][idx]['label'] = labels[ids.index(id)]
            pickdata[language][idx]['abstract'] = abstracts[ids.index(id)]
            # remove value
            pickdata[language][idx].pop('value')

    with open(save_path, 'w') as f:
        json.dump(pickdata, f, indent=2)

def read_cluster_results(file_path):
    with open(file_path) as f:
        data = json.load(f)

    topics = []
    for language, items in data.items():
        for item in items:
            topics.append(item['label'])
    topics = list(set(topics))
    print(f"Found {len(topics)} topics")
    print(topics)

def read_total_datapoint(file_path):
    with open(file_path, 'r') as f:
            data = json.load(f)
    metadata = {}
    for language, items in data.items():
        metadata[language] = len(items)
    total = sum(metadata.values())
    print(f'Total: {total} datapoints from {len(metadata)} languages in {file_path}')

def requirement_topic_allocate(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    reqs = []
    ids = []
    for language, items in data.items():
        for item in items:
            req = json.dumps(item['value']["conversations"])
            reqs.append(req)
            ids.append(item['id'])
    labels, abstracts, topics = reallocate_topics(reqs, ids)
    print(f"{len(topics)} topics generated: {topics}")

    for language in data.keys():
        # add labels and abstracts to items
        for idx, item in enumerate(data[language]):
            id = item['id']
            data[language][idx]['label'] = labels[ids.index(id)]
            data[language][idx]['abstract'] = abstracts[ids.index(id)]
            # remove value
            data[language][idx].pop('value')
    
    save_name = file_path.split('.')[0].split('_')[-1]
    save_path = f"requiremnet_topic_{save_name}.json"
    with open(save_path, 'w') as f:
        json.dump(data, f, indent=2)

def check_topic_allocate(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    topics = []
    print("Items that need double check:")
    for language, items in data.items():
        for item in items:
            if (not item["abstract"]) or (not item["label"]) or (item["label"]=="unknown"):
                print(item["id"])

def add_topic_to_dataset(file_no_topics, file_with_topics):
    with open(file_no_topics, "r") as f1,\
        open(file_with_topics, "r") as f2:
        data = json.load(f1)
        topics = json.load(f2)
    save_name = file_no_topics.split(".")[0].split("_")[-1]

    def find_topics(language, id):
        try:
            for item in topics[language]:
                if item['id'] == id:
                    return item['label'], item['abstract']
            assert False
        except:
            return "", ""

    for language, items in data.items():
        for item in items:
            label, abstract = find_topics(language, item['id'])
            item['label'] = label
            item['abstract'] = abstract
    with open(f"requirement_topic_{save_name}.json", "w") as f:
        json.dump(data, f, indent=2)

def manual_filter(file_path, filterpath, save_path):
    with open(file_path, 'r') as f1,\
        open(filterpath, 'r') as f2:
        data = json.load(f1)
        filter = json.load(f2)

    def has_item(lst, id):
        for exist_item in lst:
            if exist_item['id'] == id:
                return True
        return False

    filtered_data = {}
    cnt = 0
    for language, items in data.items():
        for item in items:
            if item['id'] in filter["remove"]:
                print(f"remove {item['id']}")
                continue
            
            if item['id'] in filter.keys():
                if "topic" in filter[item['id']]:
                    print(f"change topic {filter[item['id']]['topic']} to {item['id']}")
                    item["label"] = filter[item['id']]["topic"]
                if "language" in filter[item['id']]:
                    for lang in filter[item['id']]["language"]:
                        print(f"{item['id']} add to {lang}")
                        if lang not in filtered_data:
                            filtered_data[lang] = []
                        if not has_item(filtered_data[lang], item['id']):
                            filtered_data[lang].append(item)
                            cnt += 1
                    continue
            
            if language not in filtered_data:
                filtered_data[language] = []
            if not has_item(filtered_data[language], item['id']):
                filtered_data[language].append(item)
                cnt += 1

    # print duplicated items with the same human prompts.
    human_prompts = {}
    for language, items in filtered_data.items():
        for item in items:
            hp = ""
            for conv in item['value']['conversations']:
                if conv["from"] == "human" and len(conv['value']) > 10: # skip continue/keep doing/etc.
                    hp += conv['value']
            if hp not in human_prompts:
                human_prompts[hp] = []
            human_prompts[hp].append((language, item['id']))
    for hp, ids in human_prompts.items():
        if len(ids) > 1:
            print(f"duplicate {ids}")
    
    print(f"Got {cnt} items after manual filter process")
    
    with open(save_path, 'w') as f:
        json.dump(filtered_data, f, indent=2)

def llm_check_pl(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    def ask_llm_pl(conv):
        prompt = f"""
In this conversation, which programming language(s) did the large language model generate to meet the user's needs?
Conversation: [{conv}]"

Your response should follow this format, separated by commas if multiple programming languages are involved:
Programming Language: [Programming Language(s)]
        """.strip()
        ans = chat([{"role": "user", "content": prompt}])
        pls = ans.replace("Programming Language: ", "").split(",")
        return [pl.strip() for pl in pls]

    if not os.path.exists("llm_pl.json"):
        llm_pl = {}
        for label_pl, items in tqdm(data.items()):
            for item in items:
                id = item['id']
                if id in llm_pl:
                    continue
                conv = json.dumps(item['value']['conversations'])
                pls = ask_llm_pl(conv)
                llm_pl[id] = pls
                with open("llm_pl.json", 'w') as f:
                    json.dump(llm_pl, f, indent=2)
    with open("llm_pl.json", 'r') as f:
        llm_pl = json.load(f)

    for id, pl in llm_pl.items():
        llm_pl[id] = []
        for p in pl:
            if p.lower() == "c#":
                llm_pl[id].append("csharp")
            else:
                llm_pl[id].append(p.lower())                
    
    for label_pl, items in data.items():
        for item in items:
            id = item['id']
            try:
                assert id in llm_pl 
            except:
                raise Exception(f"Missing {id}")

            if label_pl not in llm_pl[id]:
                print(f"""
label_pl: {label_pl}
    "{id}": {{
        "language": {json.dumps(llm_pl[id])}
    }},
                    """.strip())
            
def llm_check_topic(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    def ask_llm_topic(conv):
        prompt = f"""
Accroding to this provided conversation, please select the most suitable topic from the following options: algorithm design and optimization, data processing, web development, software development. 
If none of the topics are appropriate, output "unknown". 
Ensure that you match the conversation content with these four topics as closely as possible.

Conversation: [{conv}]"

Your response should follow this format:
Topic: [topic]
        """.strip()
        ans = chat([{"role": "user", "content": prompt}])
        topic = ans.replace("Topic:", "").lower().strip().strip("[]\"'")
        return topic

    if not os.path.exists("llm_topic.json"):
        llm_topic = {}
        for _, items in tqdm(data.items()):
            for item in items:
                id = item['id']
                if id in llm_topic:
                    continue
                conv = json.dumps(item['value']['conversations'])
                topic = ask_llm_topic(conv)
                llm_topic[id] = topic
                with open("llm_topic.json", 'w') as f:
                    json.dump(llm_topic, f, indent=2)
    
    with open("llm_topic.json", 'r') as f:
        llm_topic = json.load(f)

    cnt = 0
    for _, items in data.items():
        for item in items:
            id = item['id']
            label_topic = item['label']
            assert id in llm_topic 
            if label_topic != llm_topic[id]:
                cnt += 1
                print(f"""
label_topic: {label_topic}
    "{id}": {{
        "topic": "{llm_topic[id]}"
    }},
                """.strip())

    print(f"Found {cnt} items that need to be checked")

if __name__ == '__main__':
    # operation for tmp data
    # requirements_markup("counter_vicuna.json", "tmp_requirement_vicuna_nohumaninstruct.json")
    # add_topic_to_dataset("tmp_requirement_vicuna_nohumaninstruct.json", "requiremnet_topic_vicuna.json")
    # manual_filter("requirement_topic_nohumaninstruct.json", "manual_check_id.json", "requirement_topic_filtered_nohumaninstruct.json")

    ## First Cluster
    # requirements_markup('counter_vicuna.json', 'equirement_topic_vicuna_nohumaninstruct.json')
    # requirements_cluster('requirement_vicuna.json')
    # read_cluster_results('cluster_req_vicuna_100.json')
    # read_total_datapoint('requirement_vicuna.json')
    # requirement_topic_allocate('requirement_vicuna.json')
    # check_topic_allocate("requiremnet_topic_vicuna.json")

    # add_topic_to_dataset("requirement_vicuna_nohumaninstruct.json", "requiremnet_topic_vicuna.json")
    # manual_filter("requirement_topic_vicuna_nohumaninstruct.json", "manual_check_id.json", "requirement_topic_vicuna_filtered_nohumaninstruct.json")
    # llm_check_pl("requirement_topic_vicuna_filtered_nohumaninstruct.json")
    # llm_check_topic("requirement_topic_vicuna_filtered_nohumaninstruct.json")