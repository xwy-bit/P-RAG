import re

def has_digits(input_string):
    return bool(re.search(r'\d', input_string))

def add_underscore_before_digits(input_obs):
    input_obs_processed = ''.join(input_obs.split('\n\n')[-1])
    result = re.sub(r'(\s)(\d)', r'\1_\2', input_obs_processed)
    result = result.replace(' _', '_')
    if result == '':
        return input_obs
    return result