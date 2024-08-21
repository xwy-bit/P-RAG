from sentence_transformers import SentenceTransformer
import numpy as np
import sqlite3  
import json
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def get_top_k(db_path , query, k=5,num_mask_idxs= 0,args = None):

    # get query
    task_name = query['task_name']
    obs = query['obs']

    task_name_embedding = embedding_model.encode(task_name)
    obs_embedding = embedding_model.encode(obs)

    # get all columns in db（sqlite3）8
    db_name = db_path.split('/')[-1].split('.')[0]
    # database is [ task_name text, history text, scene_graph text, done text,task_name_embedding text, obs_embedding text]
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT * FROM {}".format(db_name))
    all_items = c.fetchall()
    conn.close()
    
    # get all lines 
    all_task_names = [item[0] for item in all_items]
    all_histories = [eval(item[1]) for item in all_items]
    all_scene_graphs = [eval(item[2]) for item in all_items]
    all_dones = [eval(item[3]) for item in all_items]
    all_task_name_embeddings = json.load(open('db/{}_task_name_embeddings.json'.format(db_name)))
    all_scene_graph_embeddings = json.load(open('db/{}_scene_graph_embeddings.json'.format(db_name)))
    # calculate similarity
    task_name_similarities = np.dot(np.array(task_name_embedding).reshape(1,-1), np.array(all_task_name_embeddings).T).flatten()
    ## get obs similarity
    obs_similarities = []
    for i in range(len(all_scene_graph_embeddings)):
        if len(all_scene_graph_embeddings[i]) == 0:
            obs_similarities.append(-1)
        else:   
            obs_similarity = np.dot(obs_embedding, np.array(all_scene_graph_embeddings[i]).T)
            obs_similarities.append(np.max(obs_similarity))
    if args.enable_scene_graph:
        total_similarities = task_name_similarities + np.array(obs_similarities)
    else:
        total_similarities = task_name_similarities
    if num_mask_idxs == 0:
        top_k_idxs = np.argsort(total_similarities)[::-1][:k]
    else: # disable some idxs
        # random select num_mask_idxs idxs
        mask_idxs = np.random.choice(len(total_similarities), num_mask_idxs, replace=False)
        mask = np.zeros(len(total_similarities))
        mask[mask_idxs] = 1
        total_similarities = total_similarities - mask * 1000
        top_k_idxs = np.argsort(total_similarities)[::-1][:k]
    top_k_task_names = [all_task_names[idx] for idx in top_k_idxs]
    top_k_histories = [all_histories[idx] for idx in top_k_idxs]
    top_k_scene_graphs = [all_scene_graphs[idx] for idx in top_k_idxs]
    top_k_dones = [all_dones[idx] for idx in top_k_idxs]
    # print(top_k_task_names)
    # print(top_k_histories)
    # print(top_k_scene_graphs)
    # print(top_k_dones)

    # remove nothing from scene graph
    new_top_k_scene_graphs = []
    for scene_graph in top_k_scene_graphs:
        new_scene_graph = []
        for item in scene_graph:
            if ' nothing' not in item and 'nothing' not in item:
                new_scene_graph.append(item)
        new_top_k_scene_graphs.append(new_scene_graph)

    return top_k_task_names, top_k_histories, new_top_k_scene_graphs, top_k_dones
        

    



if __name__ == '__main__':
    db_path = 'db/validunseen.db'
    query = {'task_name': 'Examine a black statue in the light of a tall lamp.', 'obs': 'armchair 1'}
    get_top_k(db_path, query,k = 1)


