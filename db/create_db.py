import sqlite3
import re
from sentence_transformers import SentenceTransformer
import numpy as np
import json

embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def starts_with_number_dot(text):
    pattern = r'^([1-9]|1[0-9])\..*'
    return re.match(pattern, text) is not None

# connect to the database
db_name = 'validunseenRA5'
conn = sqlite3.connect('db/{}.db'.format(db_name))
task_name_embedings = []
scene_graph_embedings = []
c = conn.cursor()

# create the table
c.execute('''CREATE TABLE IF NOT EXISTS {}
             (task_name text, history text, scene_graph text, done text)'''.format(db_name))

# read the file
original_file = open('log/0/merged.log', 'r')
text = original_file.readlines()
original_file.close()

# split index table
split_idxs = [i for i, line in enumerate(text) if 'Start testing single task idx -' in line]
task_chunks = [text[split_idxs[i]:split_idxs[i+1]] for i in range(len(split_idxs)-1)]

for task_idx , task_chunk in enumerate(task_chunks):
    # try:
        # get task name
        task_name = ''
        for i , line in enumerate(task_chunk):
            if '[PROMPT]:' in line and 'Task: ' in task_chunk[i+1]:
                task_name = task_chunk[i+1].split('Task: ')[1].strip()
                break

        # get history & scene graph
        history = []
        scene_graph = []
        for i , line in enumerate(task_chunk):
            if '[ACTION]:' in line:
                history.append((task_chunk[i].split('[ACTION]:')[1].strip(), task_chunk[i+2].split('[FEEDBACK]: ')[1].strip()))
                if ', you see ' in task_chunk[i+2]:
                     candidate_str = task_chunk[i+2].split(', you see ')[1].strip()
                     first_obj = ' '.join(task_chunk[i].split(' ')[-2:]).replace('\n','')
                     candidate_obj_list = candidate_str.split(',')
                     scene_graph.append([first_obj] + [obj.replace('a ','').replace('and','').replace('.','').strip() for obj in candidate_obj_list if obj.strip() != '' and 'nothing' not in obj.lower()])

        # get done 
        done = False 
        for i , line in enumerate(task_chunk):
            if '[DONE]: True' in line:
                done = True
                break
        print('[{idx}] {task_name} - {done}'.format(idx=task_idx, task_name=task_name, done=done))
        print(history)
        print(scene_graph)
        
        # get task_name_embedding & scene_graph_embedding
        task_name_embedding = embedding_model.encode(task_name)
        scene_graph_node = []
        scene_graph_node = [embedding_model.encode(scene[0]).tolist() for scene in scene_graph]
        
        
        # insert a row of data
        c.execute("INSERT INTO {} VALUES (?, ?, ?, ?)".format(db_name)
                  , (task_name, str(history), str(scene_graph), str(done)))
        conn.commit()
        task_name_embedings.append(task_name_embedding.tolist())
        scene_graph_embedings.append(scene_graph_node)

    # except Exception as e:
    #     print(e)
    #     exit()
    #     pass
json.dump(task_name_embedings, open('db/{}_task_name_embeddings.json'.format(db_name), 'w'))
json.dump(scene_graph_embedings, open('db/{}_scene_graph_embeddings.json'.format(db_name), 'w'))




