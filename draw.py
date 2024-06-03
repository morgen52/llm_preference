import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def draw_pl(file_path): # draw bar chart for different programming languages

    save_name = file_path.split('.')[0]

    with open(file_path) as f:
        data = json.load(f)

    human = {}
    gpt = {}

    for file in data:
        for item in data[file]:
            record = data[file][item]
            if record['human']['unknown'] or record['gpt']['unknown']:
                continue

            for k, langs in record['human'].items():
                if k in ['unknown', "has_code"]:
                    continue
                for lang in langs:
                    if lang not in human:
                        human[lang] = {"exactly": [], "involve": []}
                    human[lang][k].append(item)

            for k, langs in record['gpt'].items():
                if k in ['unknown', "has_code"]:
                    continue
                for lang in langs:
                    if lang not in gpt:
                        gpt[lang] = {"exactly": [], "involve": []}
                    gpt[lang][k].append(item)
    
    # remove empty keys
    human = {k: v for k, v in human.items() if len(v['exactly']) + len(v['involve']) > 0}
    gpt = {k: v for k, v in gpt.items() if len(v['exactly']) + len(v['involve']) > 0}

    # sort by the total number of exactly and involve
    human = dict(sorted(human.items(), key=lambda x: len(x[1]['exactly']) + len(x[1]['involve']), reverse=True))
    # gpt = dict(sorted(gpt.items(), key=lambda x: len(x[1]['exactly']) + len(x[1]['involve']), reverse=True))
    gpt = dict(sorted(gpt.items(), key=lambda x: len(x[1]['exactly']), reverse=True))
    
    # draw two bar chart respectively for human and gpt
    plt.figure(figsize=(10, 5))
    plt.bar(human.keys(), [len(human[k]['exactly']) for k in human.keys()], label='exactly')
    # plt.bar(human.keys(), [len(human[k]['involve']) for k in human.keys()], bottom=[len(human[k]['exactly']) for k in human.keys()], label='involve')
    plt.legend()
    plt.xticks(rotation=90, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('#', fontsize=15)
    plt.savefig(f"human_{save_name}.pdf", format='pdf', dpi=300, bbox_inches='tight')
    plt.cla()

    plt.figure(figsize=(10, 5))
    plt.bar(gpt.keys(), [len(gpt[k]['exactly']) for k in gpt.keys()], label='exactly')
    # plt.bar(gpt.keys(), [len(gpt[k]['involve']) for k in gpt.keys()], bottom=[len(gpt[k]['exactly']) for k in gpt.keys()], label='involve')
    plt.legend(fontsize=15)
    plt.xticks(rotation=90, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('#', fontsize=15)
    plt.savefig(f"gpt_{save_name}.pdf", format='pdf', dpi=300, bbox_inches='tight')

def draw_requirement(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    save_name = file_path.split(".")[0]

    reqs = {}
    topics = {}
    for language, items in data.items():
        reqs[language] = {}
        for item in items:
            reqs[language][item["label"]] = reqs[language].get(item["label"], 0) + 1
            topics[item["label"]] = topics.get(item["label"], 0) + 1
    print(topics)
    plt.figure(figsize=(10, 5))
    plt.bar(topics.keys(), topics.values())
    plt.xticks(rotation=90, fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('#', fontsize=15)
    plt.savefig(f"{save_name}.pdf", format='pdf', dpi=300, bbox_inches='tight')
    plt.cla()

    # draw Heatmap
    df = pd.DataFrame(reqs)
    plt.figure(figsize=(10, 5))
    sns.heatmap(df, annot=True, cmap='coolwarm', linewidths=1, mask=df.isnull(), cbar_kws={'label': 'Value'})
    plt.xticks(rotation=90, fontsize=15)
    plt.yticks(fontsize=15)
    plt.savefig(f"{save_name}_heatmap.pdf", format='pdf', dpi=300, bbox_inches='tight')
    plt.cla()
    
if __name__ == '__main__':
    draw_pl('counter_s52k.json')
    draw_pl('counter_vicuna.json')

    draw_requirement("requiremnet_topic_vicuna.json")
    draw_requirement("requirement_topic_vicuna_filtered_nohumaninstruct.json")

            