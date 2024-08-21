action_prompt = """
`Base on the history` you have done for this task,you need and only need to choose what action to do for next one step.
`Nothing happens` means you done the same action as the last step or the action is invalid.
You can only choose from the following admissible commands(any other commands will be invalid):
{admissible_commands}
if you not see the target you require, feel free to choose above action to explore the scene. You can only see part of the scene at a place.
Please give me a plan with action in [] like 
###
['go to target_n']
OR 
['take target_n from source_n']
###
which i can execute with python function `eval()` to be a list of strings.
"""
task_desc = "Task: {detail_task_desc}"

retrievaled_prompt = """
There are some tasks that are similar to the current task another agent have done before. 
Note the object in the same square brackets may occur together.
You cannot directly use the action in the similar task, but you can use the history of the similar task to help you make next step decision.
Here are the top {k} similar tasks, histories, scene graphs and finished status:
{top_k_results}
"""
retrievaled_prompt_no_scene_graph = """
There are some tasks that are similar to the current task another agent have done before. 
You cannot directly use the action in the similar task, but you can use the history of the similar task to help you make next step decision.
Here are the top {k} similar tasks, histories, and finished status:
{top_k_results}
"""

chain_of_thought_prompt = '''
You can only choose from the following admissible commands(any other commands will be invalid):
{admissible_commands}
if you not see the target you require, feel free to choose above action to explore the scene. You can only see part of the scene at a place.
Please give me a plan with action in [] like 
###
['go to target_n']
OR 
['take target_n from source_n']
###
for example, 
Task: put a rinsed off bar of soap in to the cabinet:
you have done the following actions: ['go to cabinet 1','open cabinet 1','go to sinkbasin 1']
On the sinkbasin 1, you see a soapbottle 1, a cloth 1, a faucet 1, a faucet 2, a soapbar 1, and a handtowel 1.
You have found soapbar 1,then you need to get it .
Therefore, output
base on the history, I have found soapbar 1, then I need to take soapbar 1 from sinkbasin 1
['take soapbar 1 from sinkbasin 1']
'''

invalid_action_response = "\n{invalid_action} is not a valid action. Please choose from the admissible commands.\n"