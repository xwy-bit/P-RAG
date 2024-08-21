import os
import base64
import sys
import json
import re
import yaml
import cv2
import argparse
from openai import OpenAI
import requests
import random  
# from alfworld.info import ALFWORLD_DATA
from utils.prompts import (
    action_prompt,
    task_desc  
)
import glob
from os.path import join as pjoin
import alfworld.agents
from alfworld.info import ALFWORLD_DATA
from alfworld.env.thor_env import ThorEnv
from alfworld.agents.detector.mrcnn import load_pretrained_model
from alfworld.agents.controller import OracleAgent, OracleAStarAgent, MaskRCNNAgent, MaskRCNNAStarAgent

import alfworld.agents.environment
from alfworld.agents.controller import OracleAgent, OracleAStarAgent, MaskRCNNAgent, MaskRCNNAStarAgent
from test_single_main import test_single_task
from utils.logger import make_logger
description = "Play the abstract text version of an ALFRED environment."
parser = argparse.ArgumentParser(description=description)
parser.add_argument("problem", nargs="?", default=None,
                    help="Path to a folder containing PDDL and traj_data files."
                            f"Default: pick one at random found in {ALFWORLD_DATA}")
parser.add_argument("--controller", default="oracle", choices=["oracle", "oracle_astar", "mrcnn", "mrcnn_astar"])
parser.add_argument("--debug", action="store_true")
parser.add_argument('--load_receps', action="store_true")
parser.add_argument('--reward_config', type=str, default=pjoin(alfworld.agents.__path__[0], 'config', 'rewards.json'))
parser.add_argument('--engine', type=str, default='gpt-4-1106-preview') # MAY NOT UP TO DATE
parser.add_argument('--env_idx', type=int, default=0)
parser.add_argument('--k', type=int, default=3)
parser.add_argument('--db_path', type=str, default='db/validunseen.db')
parser.add_argument('--log_name', type=str, default='testx')
parser.add_argument('--api_key', type=str, default='')
parser.add_argument('--dataset', type=str, default='validseen')
parser.add_argument('--enable_retrieval', action="store_true")
parser.add_argument('--mask_num', type=int, default=0)
parser.add_argument('--enable_scene_graph', action="store_true")
args = parser.parse_args()

if args.dataset == 'validseen':
    ALFWORLD_DATA = 'alfworld/data/json_2.1.1/valid_seen'
elif args.dataset == 'validunseen':
    ALFWORLD_DATA = 'alfworld/data/json_2.1.1/valid_unseen'
elif args.dataset == 'train100':
    traj_data_paths = json.load(open('db/traj_file_paths.json', 'r'))
    traj_data_paths = [traj_data_path.replace('/traj_data.json','') for traj_data_path in traj_data_paths]
    args.problem = traj_data_paths[args.env_idx]



if args.problem is None:
    problems = glob.glob(pjoin(ALFWORLD_DATA, "**", "initial_state.pddl"), recursive=True)
    # args.problem = os.path.dirname(random.choice(problems))
    args.problem = problems[args.env_idx].replace('/initial_state.pddl','')


api_key = args.api_key

# load traj_data
root = args.problem
json_file = os.path.join(root, 'traj_data.json')
with open(json_file, 'r') as f:
    traj_data = json.load(f)
logger = make_logger('log/{}.log'.format(args.log_name))
logger.info('Start testing single task idx - {}'.format(args.env_idx))
for i in range(1):
    test_single_task(api_key,traj_data, args,logger)