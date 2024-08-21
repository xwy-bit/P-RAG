
import requests
import time
import random

def get_llm_plan(api_key, prompt, engine,logger, images=None, stop=["\n"]):
    for try_id in range(1):
        try:
            # random sleep to avoid rate limit
            time.sleep(random.uniform(0.5, 5))
            if try_id > 0:
                time.sleep(3 * try_id)
            message=[
                {"role": "system", "content": "You are a helpful assistant that can plan household tasks."},
                {"role": "user", "content": prompt},
            ]
            data = {
            "model": engine,
            "messages": message,
            "temperature": 0.05
            }
            header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            response = requests.post('https://api.openai.com/v1/chat/completions', json=data, headers=header)
            llm_output = response.json()['choices'][0]['message']['content']
            if llm_output == '':
                continue
            
            # check if the response is valid
            begin_idx = llm_output.rfind('[')
            end_idx = llm_output.rfind(']')
            if begin_idx == -1 or end_idx == -1:
                return None
            command = llm_output[begin_idx:end_idx+1]
            result = eval(command)
            logger.info(f'[LLM RESPONSE]:\n{response.json()["choices"][0]["message"]["content"]}\n')

            return result
        except Exception as e:
            logger.error(f'[TRY ERROR]:\n{e}\n')
            logger.error(str(response))
            continue
