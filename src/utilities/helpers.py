
import re
from datetime import datetime as dts
import yaml

def load_yaml_file(file_path):
    """
    Reads a YAML file and returns its contents as a Python dictionary.
    
    Args:
        file_path (str): The path to the YAML file.
        
    Returns:
        dict: The contents of the YAML file as a Python dictionary.
    """
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data



def get_day_date_month_year_time():
    """
    Get the current date and time with the day of the week as separate variables.

    Returns:
    tuple: A tuple containing current_date, day_of_week, day, month, year, hour, minute, and second.
    """
    current_datetime = dts.now()

    current_date = current_datetime.strftime('%m-%d-%Y')
    day_of_week = current_datetime.strftime('%A')
    day = current_datetime.day
    month = current_datetime.month
    year = current_datetime.year
    hour = current_datetime.hour
    minute = current_datetime.minute
    second = current_datetime.second

    return current_date, day_of_week, day, month, year, hour, minute, second


def check_final_answer_exist(string_to_check):
    """
    Check if 'final' and 'answer' exist in any form in the given string using regex.

    Parameters:
    string_to_check (str): The input string to check.

    Returns:
    bool: True if both 'final' and 'answer' exist, False otherwise.
    """
    # Define the regex pattern for 'final' and 'answer' in any form
    pattern = re.compile(r'\bfinal[_\s]*answer\b|\banswer[_\s]*final\b', re.IGNORECASE)

    # Check if the pattern is found in the string
    return bool(pattern.search(string_to_check))

# Static responses for recurrent sentences
static_responses = {
    "hello": "Hello! How can I assist you today?",
    "hi": "Hi there! How can I help you?",
    "are you online": "Yes, I am online and ready to assist you.",
    "are you there": "Yes, I am here. How can I assist you?",
    "good morning": "Good morning! How can I help you today?",
    "good afternoon": "Good afternoon! How can I assist you today?",
    "good evening": "Good evening! How can I help you today?"
}

async def static_response_generator(sentence):
    # Check if the sentence matches any static response
    lower_sentence = sentence.lower()
    return lower_sentence