import openai
from openai.error import RateLimitError, APIConnectionError, Timeout, APIError, TryAgain, ServiceUnavailableError
import random
import yaml
from time import sleep
import sys

name = "chatgpt"

# Set up the configuration file
with open("inference/chatgpt/config.yaml") as f:
    config = yaml.safe_load(f)
    openai.api_key = config["api_key"]
    openai.organization = config["organization_id"]

def completions(prompt: str, max_tokens: int, temperature: float, n: int, top_p, stop):
    completion_messages = complete_or_fail_after_n_tries(lambda: openai.ChatCompletion.create(
        model=config["model"],
        messages=[
            # This tells the chatbot what role it is fulfilling.
            {"role": "system", "content": "Your job is to write just the functions asked of you by the user. Write only the functions."},
            {"role": "user", "content": f"I have a function prompt ```{prompt}```\n Please produce the function for me which completes this prompt."}
        ],
        temperature=temperature,
        top_p=top_p,
        n=n,
        max_tokens=max_tokens
    ), config["max_retries"])
    if config["debug"]:
        print(completion_messages)
    # pull out the code body
    return get_code_body(completion_messages, stop)

def complete_or_fail_after_n_tries(func, n):
    if n == 0:
        # Ran out of tries, return nothing
        if config["debug"]:
            print("Failed to get response from chatgpt API, max retries reached, leaving completions blank.")
        return []
    try:
        # Get completion messages
        completions_response =  func()
        return [choice.message.content for choice in completions_response.choices]
    except (RateLimitError, APIConnectionError, Timeout, APIError, ServiceUnavailableError, TryAgain):
        # If can't connect, keep retrying, giving longer pauses between each retry
        seconds = 1.5 ** (config["max_retries"] - n) + random.random()
        if config["debug"]:
            print(f"Failed to get completions from chatgpt API, applying exponential backoff: {seconds}")
        sleep(seconds)
        return complete_or_fail_after_n_tries(func, n-1)

def get_code_body(completion_messages, stop):
    cleaned_messages = []
    for m in completion_messages:
        # Get code section
        if m.count("```") >= 2:
            # Select first code section
            start = m.index("```") + 3
            end = m[start:].index("```") + start
        else:
            # No code sections or one incomplete code section
            start, end = 0, len(m)
        m = m[start:end]
        """
        After we have extracted the code the model produced, we will select everything starting on the first 
        indented line. This makes the assumption that the first unindented line is the function declaration
        and then everything else is part of the function.
        """
        code_body = m[m.index("  "):]
        if "d" in sys.argv:
            # Add back opening curly to d
            code_body = "{\n"  + code_body
        # Apply stop token logic at this level
        for stop_token in stop:
            if stop_token in code_body:
                code_body = code_body[:code_body.index(stop_token)]
                break
        cleaned_messages.append(code_body)
    return cleaned_messages