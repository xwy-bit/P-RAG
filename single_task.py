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
from alfworld.info import ALFWORLD_DATA
from utils.prompts import (
    action_prompt,
    task_desc,
    retrievaled_prompt,
    invalid_action_response,
    retrievaled_prompt_no_scene_graph,
    chain_of_thought_prompt
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

from utils.chatgpt import get_llm_plan
from utils.tools import has_digits, add_underscore_before_digits
from utils.retrieval import get_top_k
def setup_scene(env, traj_data, r_idx, args, reward_type='dense'):
    # scene setup
    scene_num = traj_data['scene']['scene_num']
    object_poses = traj_data['scene']['object_poses']
    dirty_and_empty = traj_data['scene']['dirty_and_empty']
    object_toggles = traj_data['scene']['object_toggles']

    scene_name = 'FloorPlan%d' % scene_num
    env.reset(scene_name)
    env.restore_scene(object_poses, object_toggles, dirty_and_empty)

    # initialize to start position
    env.step(dict(traj_data['scene']['init_action']))

    # print goal instr
    print("Task: %s" % (traj_data['turk_annotations']['anns'][r_idx]['task_desc']))

    # setup task for reward
    env.set_task(traj_data, args, reward_type=reward_type)

def test_single_task(api_key,traj_data, args,logger):
    history = []
    # start THOR
    env = ThorEnv()

    # setup scene
    setup_scene(env, traj_data, 0, args)
    cmd = ''
    agent = OracleAgent(env, traj_data, traj_root=args.problem, load_receps=args.load_receps, debug=args.debug)
    # task_desc = agent.feedback.replace('Your task is to: ','')
    for step_idx in range(20):
        admissble_command_ = agent.get_admissible_commands()
        # remove 'look' 'inventory' 'examine' from admissble_command
        admissble_command = [cmd for cmd in admissble_command_ if 'look' not in cmd and 'inventory' not in cmd and 'examine' not in cmd]
        if not 'Nothing' in agent.feedback:
            ob_text = add_underscore_before_digits(agent.feedback) # Get text after the last \n\n
        else:
            ob_text = add_underscore_before_digits(f'You choose {cmd}'.format(cmd) + ':'+ agent.feedback)
        

        if args.enable_retrieval:
            if args.enable_scene_graph:
            # get retireval prompt
                top_k_task_names, top_k_histories, top_k_scene_graphs, top_k_dones = get_top_k(
                    args.db_path, {'task_name':traj_data['turk_annotations']['anns'][0]['task_desc'], 'obs':ob_text}, k=args.k, num_mask_idxs=args.mask_num, args=args)
                retrievaled_prompt_to_insert = retrievaled_prompt.format(k=args.k, top_k_results= \
                    '\n---\n'.join([f'{i+1}. Task name: {top_k_task_names[i]}\n History : {top_k_histories[i]}\n Scene graph: {top_k_scene_graphs[i]}\n Finished: {top_k_dones[i]}' for i in range(len(top_k_task_names))])
                )
            else:
                top_k_task_names, top_k_histories, top_k_scene_graphs, top_k_dones = get_top_k(
                    args.db_path, {'task_name':traj_data['turk_annotations']['anns'][0]['task_desc'], 'obs':ob_text}, k=args.k, num_mask_idxs=args.mask_num,args = args)
                retrievaled_prompt_to_insert = retrievaled_prompt_no_scene_graph.format(k=args.k, top_k_results= \
                    '\n---\n'.join([f'{i+1}. Task name: {top_k_task_names[i]}\n History : {top_k_histories[i]}\n Finished: {top_k_dones[i]}' for i in range(len(top_k_task_names))])
                )

        else:
            retrievaled_prompt_to_insert = ''
        
        # prompt = task_desc.format(detail_task_desc= traj_data['turk_annotations']['anns'][0]['task_desc']) + '\n' + retrievaled_prompt_to_insert +\
        #      "\nThe history of what you have done so far is:\n" + '\n'.join([f'{i+1}. {h[0]}: {h[1]}' for i, h in enumerate(history)]) +'\n'  \
        #     + action_prompt.format(admissible_commands=admissble_command)
        
        prompt = task_desc.format(detail_task_desc= traj_data['turk_annotations']['anns'][0]['task_desc']) + '\n'  + \
            "\nThe history of what you have done so far is:\n" + '\n'.join([f'{i+1}. {h[0]}: {h[1]}' for i, h in enumerate(history)]) +'\n'  \
            + chain_of_thought_prompt.format(admissible_commands=admissble_command)


        logger.info(f'[PROMPT]:\n{prompt}\n')
        for try_idx in range(1):
            try:
                plan = get_llm_plan(api_key, prompt, args.engine,logger) # get plan from chatgpt
                cmd = plan[0] # use the first command
                if cmd not in admissble_command:
                    prompt += invalid_action_response.format(invalid_action=cmd)
                    continue
                break
            except Exception as e:
                logger.info(f'[CMD ERROR]: {e}\n')
                continue
        if not has_digits(cmd):
            break
        agent.step(cmd)
        logger.info(f'[GC]: {env.get_goal_conditions_met()}\n')
        logger.info(f'[ACTION]: {cmd}\n')
        logger.info(f'[FEEDBACK]: {agent.feedback}\n')
        history.append((cmd, agent.feedback))
        done = env.get_goal_satisfied()
        if done:
            logger.info(f'[DONE]: {done}\n')
            break


