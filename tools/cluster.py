from typing import List, Dict, Set
import json
from tqdm import tqdm
from collections import Counter
import os
import random

from .chatgpt import chat
from .prompts import classifier_system_prompt, classifier_user_prompt_with_abstract, classifier_user_prompt_without_abstract,\
    topic_generator_system_prompt, topic_generator_usr_prompt,\
    reallocator_system_prompt, reallocator_user_prompt_with_abstract


class Agent:
    def __init__(self, system_prompt:str, user_prompt:str=None):
        self.system_prompt = system_prompt.strip()
        self.user_prompt = user_prompt.strip() if user_prompt else None

    def chat(self, msgs=[{"role": "user", "content": "Say nothing"}]):
        msgs = [{"role": "system", "content": self.system_prompt}] + msgs
        return chat(msgs)
    
    def set_user_prompt(self, prompt:str):
        self.user_prompt = prompt
    
def classify(reqs: List[str], topics:Set[str], agent: Agent, allocated_topics: List[str]=[], ids: List[str]=None, reallocate=False) -> Dict[str, str]:

    assign = []
    abstracts = []
    last_idx = 0
    checkpoint = {
        "idx": 0,
        "contents": []
    }

    # load checkpoint
    if os.path.exists("classify_checkpoint/checkpoint.json"):
        with open("classify_checkpoint/checkpoint.json") as f:
            checkpoint = json.load(f)
        assert checkpoint["idx"] + 1 == len(checkpoint["contents"])
        last_idx = checkpoint["idx"]
        abstracts =[item["abstract"] for item in checkpoint["contents"]]
        assign = [item["assign"] for item in checkpoint["contents"]]

    progress_bar = tqdm(desc=f"Allocating Topics", total=len(reqs))
    for idx, req in enumerate(reqs):
        if idx <= last_idx: 
            progress_bar.update(1)
            continue

        if ids:
            progress_bar.set_description(f"Allocating Topics ({ids[idx]})")

        if allocated_topics and allocated_topics[idx]:
            assign.append(allocated_topics[idx])
            continue

        req = agent.user_prompt.replace("{CONTENT}", req).replace("{TOPICS}", json.dumps(list(topics)))

        response = agent.chat([{"role": "user", "content": req}])
        
        if not reallocate:
            if "Content Overview:" in response:
                abstract, remain = response.split("New Topic Created:")
            else:
                abstract, remain = "", response
            isNew, topic = remain.split("Assigned to Topic:")

            abstract = abstract.replace("Content Overview:", "").strip()
            isNew = isNew.strip().strip("[]").lower()
            topic = topic.strip().strip("[]").lower()
        else:
            if "Content Overview:" in response:
                abstract, remain = response.split("Assigned to Topic:")
            else:
                abstract, remain = "", response
            
            abstract = abstract.replace("Content Overview:", "").strip()
            topic = remain.replace("Assigned to Topic:", "").strip().strip("[]").lower()
    
        if abstract:
            abstracts.append(abstract)
        assign.append(topic)
        topics.add(topic)

        checkpoint["idx"] = idx
        checkpoint["contents"].append({"id": ids[idx] ,"abstract": abstract, "assign": topic})

        # save checkpoint
        if not os.path.exists("classify_checkpoint"):
            os.makedirs("classify_checkpoint")
        with open(f"classify_checkpoint/checkpoint.json", "w") as f:
            json.dump(checkpoint, f, indent=2)

        progress_bar.update(1)

    progress_bar.close()
    # # clean checkpoint file
    # os.remove("classify_checkpoint/checkpoint.json")

    abstracts =[item["abstract"] for item in checkpoint["contents"]]
    assign = [item["assign"] for item in checkpoint["contents"]]
    topics = set(assign)

    return assign, abstracts, topics

def cohen_kappa(assignA: List[str], assignB: List[str]) -> float:
    # get all categories
    categories = set(assignA) | set(assignB)
    
    # compute total agreements
    total_agreements = sum(1 for a, b in zip(assignA, assignB) if a == b)
    
    # compute observed agreement
    observed_agreement = total_agreements / len(assignA)
    
    # compute expected agreement
    counterA = Counter(assignA)
    counterB = Counter(assignB)
    expected_agreement = sum(counterA[key] * counterB[key] for key in categories) / (len(assignA) ** 2)
    
    # compute kappa
    kappa = (observed_agreement - expected_agreement) / (1 - expected_agreement)
    
    return kappa

def find_common_cluster(assignA: List[str], assignB: List[int]) -> List[List[int]]:
    strong_connection_graph = {}
    weak_connection_graph = {}
    
    for i in range(len(assignA)):
        for j in range(i+1, len(assignA)):
            connection = (assignA[i]==assignA[j]) + (assignB[i]==assignB[j])
            if connection == 2:
                if i not in strong_connection_graph:
                    strong_connection_graph[i] = []
                strong_connection_graph[i].append(j)
            elif connection == 1:
                if i not in weak_connection_graph:
                    weak_connection_graph[i] = []
                weak_connection_graph[i].append(j)
    clusters = []
    for i in strong_connection_graph:
        cluster = [i] + strong_connection_graph[i]
        clusters.append(cluster)
    
    if len(clusters) == 0:
        for i in weak_connection_graph:
            cluster = [i] + weak_connection_graph[i]
            clusters.append(cluster)
    
    return clusters, [assignA[i[0]] for i in clusters], [assignB[i[0]] for i in clusters]

def gen_cluster_topic(reqs: List[str], label1, label2, agent) -> List[str]:
    if label1 == label2:
        return label1
    
    req = ''
    random.shuffle(reqs) # shuffle requirements
    for id, r in enumerate(reqs):
        req += f"conversation {id}: {r}\n"
    req = agent.user_prompt.replace("{CONTENT}", req).replace("{TOPIC1}", label1).replace("{TOPIC2}", label2)
    response = agent.chat([{"role": "user", "content": req}])

    topic = response.replace("Topic Name:", "").strip().strip("[]")
    return topic

def cluster(reqs: List[str], ids: List[str]=None) -> List[str]:

    seed_topics = ["Numerical Computation", "Text Processing", "Image Processing", "Audio Processing", "Machine Learning", "Web Development", "System Integration"]

    topics = set(seed_topics)

    classifierA = Agent(classifier_system_prompt, classifier_user_prompt_with_abstract)
    classifierB = Agent(classifier_system_prompt, classifier_user_prompt_without_abstract)
    topicGenerator = Agent(topic_generator_system_prompt, topic_generator_usr_prompt)
    score = 0
    round = 0
    allocated_topics = [""]*len(reqs)

    while round < 5:
        # classify requirements A
        if round == 0:
            assignA, abstractsA, topicsA = classify(reqs, topics, classifierA, allocated_topics, ids)
        else:
            assignA, _, topicsA = classify(reqs, topics, classifierA, allocated_topics, ids)

        # classify requirements B, reqs reversed, using topicsA
        if ids:
            assignB, _, _ = classify(reqs[::-1], topicsA, classifierB, allocated_topics[::-1], ids[::-1])
        else:
            assignB, _, _ = classify(reqs[::-1], topicsA, classifierB, allocated_topics[::-1])

        # assessment
        score = cohen_kappa(assignA, assignB)
        print(f"Round {round}: Cohen's Kappa: {score}")
        if score > 0.9:
            break

        # generate new seed topics
        common_clusters, tAs, tBs = find_common_cluster(assignA, assignB)
        topics = set([])
        for cc, tA, tB in zip(common_clusters, tAs, tBs):
            cc_reqs = [reqs[i] for i in cc]
            gen_topic = gen_cluster_topic(cc_reqs, tA, tB, topicGenerator)
            topics.add(gen_topic)
            for i in cc:
                allocated_topics[i] = gen_topic

        round += 1
        if round == 1: # remove abstracts generation
            classifierA.set_user_prompt(classifier_user_prompt_without_abstract)

        # save checkpoint
        if not os.path.exists("checkpoint"):
            os.makedirs("checkpoint")
        with open(f"checkpoint/checkpoint_{round}.json", "w") as f:
            json.dump({"abstractsA": abstractsA, "assignA": assignA, "topics": list(topics), "score": score}, f, indent=2)

    return assignA, abstractsA, topicsA

def reallocate_topics(reqs, ids):
    # Algorithm Design and Optimization, Web Development, Data Processing, Software Development, Human-Computer Interaction, Teaching, Unknown
    topics = ["Algorithm Design and Optimization", "Data Processing", "Software Development", "Web Development", "Human-Computer Interaction", "Unknown"]
    classifier = Agent(reallocator_system_prompt, reallocator_user_prompt_with_abstract)

    assign, abstracts, topics = classify(reqs, set(topics), classifier, ids=ids, reallocate=True)
    return assign, abstracts, topics



# # Example usage
# requirements = [
#     "User can login using email and password",
#     "The system shall provide encrypted data storage",
#     "Implement password recovery feature",
#     "System must perform data backup every 24 hours",
#     "User shall be able to export data as CSV",
#     "Ensure the user interface is responsive on mobile devices",
# ]

# if __name__ == "__main__":
#     print(cluster(requirements))

