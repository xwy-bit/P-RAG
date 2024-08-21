import sqlite3
import re
from sentence_transformers import SentenceTransformer
import numpy as np
import json
import re
import os
import sys
import argparse

def starts_with_number_dot(text):
    pattern = r'^([1-9]|1[0-9])\..*'
    return re.match(pattern, text) is not None

def get_retirevaled_task_name(text):
    # \d+\.\sTask\sname:\s.*
    pattern = r'\d+\.\sTask\sname:\s.*'
    match = re.search(pattern, text)
    if match is not None:
        return match.group().split('Task name: ')[1]
    else:
        return None

def get_chunck(log_file):
    # read the file
    original_file = open(log_file, 'r')
    text = original_file.readlines()
    original_file.close()

    # split index table
    split_idxs = [i for i, line in enumerate(text) if 'Start testing single task idx -' in line]
    task_chunks = [text[split_idxs[i]:split_idxs[i+1]] for i in range(len(split_idxs)-1)]
    return task_chunks

def get_task_names(task_chunks):
    task_names = []
    for task_chunk in task_chunks:
        for i , line in enumerate(task_chunk):
            if 'Your task is to: ' in line:
                task_name = line.split('Your task is to: ')[1].strip()
                task_names.append(task_name)
                break
    return task_names

def get_retrievaled_task_names(task_chunks):
    retrievaled_task_names = []
    for task_chunk in task_chunks:
        retrievaled_task_name_single_task = []
        for i , line in enumerate(task_chunk):
            result = get_retirevaled_task_name(line)
            if result is not None:
                retrievaled_task_name_single_task.append(result)
        retrievaled_task_names.append(retrievaled_task_name_single_task)
    return retrievaled_task_names

def get_histories(task_chunks):
    histories = []
    for task_chunk in task_chunks:
        history = []
        header_idxs = []
        for offset , line in enumerate(task_chunk):
            if 'The history of what you have done so far is:' in line:
                header_idxs.append(offset)

        actual_header_idx = header_idxs[-1]
        for text_line in task_chunk[actual_header_idx+1:]:
            if not starts_with_number_dot(text_line):
                break
            prefix = text_line[2:].split(': ')[0]
            subfix = text_line[2:].split(': ')[1].strip()
            history.append([prefix, subfix])
        histories.append(history)
    return histories

def get_scene_graphs(task_chunks):
    scene_graphs = []
    for task_chunk in task_chunks:
        scene_graph = []
        for i , line in enumerate(task_chunk):
            if 'you see' in line:
                object_items = line.split('you see')[1].split(',')
                object_items = [item.replace('a ','').replace('and ','').replace('.','') for item in object_items]
                first_item = line.split(' ')[-2:]
                scene_graph.append([first_item] + object_items)
        scene_graphs.append(scene_graph)
    return scene_graphs

def get_dones(task_chunks):
    dones = []
    for task_chunk in task_chunks:
        done = False
        for i , line in enumerate(task_chunk):
            if '[DONE]: True' in line:
                done = True
                break
        dones.append(done)
    return dones

def get_recall_rate(task_names, retrievaled_task_names):
    count = 0
    total_retrievaled_counter = 0
    for i, task_name in enumerate(task_names):
        if task_name in retrievaled_task_names[i]:
            count += 1
        total_retrievaled_counter += len(retrievaled_task_names[i])
    return count/total_retrievaled_counter

def get_mistake_metrics(log_file1,log_file2):
    task_chunks1 = get_chunck(log_file1)
    task_chunks2 = get_chunck(log_file2)

    dones1 = get_dones(task_chunks1)
    dones2 = get_dones(task_chunks2)
    # M00: 1 true 2 true, M01: 1 true 2 false, M10: 1 false 2 true, M11: 1 false 2 false
    M00 = 0
    M01 = 0
    M10 = 0
    M11 = 0
    for i in range(min(len(dones1),len(dones2))):
        if dones1[i] and dones2[i]:
            M00 += 1
        elif dones1[i] and not dones2[i]:
            M01 += 1
        elif not dones1[i] and dones2[i]:
            M10 += 1
        else:
            M11 += 1

    R00 = M00/(M00+M01)
    R01 = M01/(M00+M01)
    R10 = M10/(M10+M11)
    R11 = M11/(M10+M11)
    return  R00, R01, R10, R11

def merge_file(log_dir):
    if not os.path.exists(os.path.join(log_dir, 'merged.log')):
            # get sorted log files (0.log 1.log 2.log ...)
        log_files = [f for f in os.listdir(log_dir) if f.endswith('.log') and 'error' not in f]
        log_files.sort(key=lambda x: int(x.split('.')[0]))
        with open(os.path.join(log_dir, 'merged.log'), 'w') as outfile:
            for log_file in log_files:
                with open(os.path.join(log_dir, log_file), 'r') as infile:
                    outfile.write(infile.read())
    return os.path.join(log_dir, 'merged.log')

if __name__ == '__main__':
    # constants
    
    # get args
    parser = argparse.ArgumentParser()
    parser.add_argument('--func', type=str, default='merge')
    parser.add_argument('--log_dir', type=str, default='log/0/merged') # create file for merge function
    parser.add_argument('--log_file1', type=str, default='log/0/merged.log') # existing file 1 for compare function
    parser.add_argument('--log_file2', type=str, default='/log/1/merged.log') # existing file 2 for compare function
    args = parser.parse_args()
    if args.func == 'merge':
        merge_file(args.log_dir)
    elif args.func == 'compare':
        M00, M01, M10, M11 = get_mistake_metrics(args.log_file1,args.log_file2)
        print(f'M00: {M00}')
        print(f'M01: {M01}')
        print(f'M10: {M10}')
        print(f'M11: {M11}')

