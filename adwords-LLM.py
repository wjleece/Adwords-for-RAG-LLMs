import openai  # I used v 1.0.0
import json
import os
import requests
from difflib import get_close_matches
from IPython.display import HTML


# Define the OpenAI model to be used
model = "gpt-4"


# Get org ID & API key from files
def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read().strip()


script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the script
org_id_file = os.path.join(script_dir, "org-id.txt")  # Construct the path to the org-id.txt file
api_key_file = os.path.join(script_dir, "api-key.txt")  # Construct the path to the api-key.txt file

openai.organization = read_file(org_id_file)
openai.api_key = read_file(api_key_file)

# Add product dictionary file here
url = 'https://raw.githubusercontent.com/wjleece/adwords-for-openai/main/shoe_data.json'

response = requests.get(url)

product_data = []

if response.status_code == 200:
    product_data = json.loads(response.text)
    # print(response.text)
    # 'product_data' is a Python dictionary containing the contents of the .json file
else:
    print('Failed to retrieve the JSON file')

# print(type(product_data))

# convert product_data to a dictionary for future easy of manipulation
product_dict = {}
for product in product_data:
    product_dict[product["product_name"]] = (product["product_category"], product["url"])


# print(product_dict)

# print(type(product_dict))

def get_openai_response(prompt):
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system",
                   "content": "You are a helpful assistant with a specialized knowledge of Nike athletic shoes."},
                  {"role": "user", "content": prompt}],
        temperature=0.5
        # set to 0.5 so that we don't get the same response every time (which would occur if temperature was set to 0)
    )
    return response.choices[0].message.content


prompt = "Can you recommend at least 10 good Nike athletic shoes? " \
         "Provide your response in a set of fluid sentences, not in a numbered list."
# asking for fluid language vs a boring list to make the response more engaging

# Get response from OpenAI
openai_response = get_openai_response(prompt)
# print("OpenAI Response:", openai_response)

# print(type(openai_response))

# get product names and descriptions from OpenAI response.
# This is necessary if OpenAI doesn't return the response in the form of a dictionary

prompt = "Repeat your previous response, but get the product names " \
         "and description from your previous response in JSON format" \
         " using \"product_name\" as the key and \"description\" as the value. " \
         "Any intros or conclusion text should not be JSON formatted, " \
         "but should still be included in this amended response " \
         "at the beginning for the intro and the end of the amended " \
         "response for any conclusions. " \
         "At times you may not have responded with an intro or conclusion, " \
         "in which case you can just leave those entries as an empty string. " \
         "You do not need to tell me when the JSON formatted section begins or ends" \
         " as I expect that to be clearly indicated with \"[\" and \"]\", respectively." \
         " To be clear, your previous response was: " + openai_response
# we still need a dict, but once we get the hyperlink shit integrated
# we'll weave that back into the 'natural' response above.
openai_response_formatted = (get_openai_response(prompt))

# print(openai_response_formatted)

# print(type(openai_response_formatted)) #note that the response is JSON formatted but the data type is still string


# now let's separate the text that contains product descriptions, so we can turn that into a response dictionary

# Finding the start and end of the JSON data
json_start = openai_response_formatted.find('[')
json_end = openai_response_formatted.rfind(']') + 1  # +1 to include the closing bracket

# Extracting the product description data from the response
openai_response_products = openai_response_formatted[json_start:json_end].strip()

# print(openai_response_products)

# print(type(openai_response_products))

# openai_response_products is a string. json.loads() will convert it to a list of dictionaries.
# Not really sure why json.loads() doesn't just produce a single dictionary, will figure that out later
data = json.loads(openai_response_products)

# print(data)

# print(type(data))

# So now we have a list of dictionaries
# lets get the product names out of the dictionaries and put that into its own dictionary
response_product_dict = {}
for item in data:
    response_product_dict[item['product_name']] = item['description']


# print(response_product_dict)

# print(type(response_product_dict))

# print(response_product_dict.keys())

# print(product_dict.keys())

# Shizzoes! The method get_close_matches() expects a list. So I gotta convert some stuff.
# I wonder if there's an easier way to do this.

def find_similar_products(response_product_dict, product_dict):
    # Lowercase and listify the keys for product_dict
    product_keys = []  # declare empty list
    for key in product_dict.keys():
        lowercased_key = key.lower()
        product_keys.append(lowercased_key)  # build full list

    # Lowercase and listify the keys for response_product_dict
    response_product_keys = []  # declare empty list
    for key in response_product_dict.keys():
        lowercased_key = key.lower()
        response_product_keys.append(lowercased_key)  # build full list

    # Find the similar product matches
    similar_matches = {}
    for response_key in response_product_keys:
        # Get close matches for each response_product_key in product_keys
        matches = get_close_matches(response_key, product_keys, cutoff=0.95)  # Adjust cutoff as needed

        # If there are matches, add the first match to the similar_matches dictionary
        if matches:
            similar_matches[response_key] = matches[0]

    return similar_matches


product_matches = find_similar_products(response_product_dict, product_dict)


# print(product_matches)

def create_hyperlink_mapping(product_matches, product_dict):
    """
    Create a mapping of product names to their hyperlinked versions using the closest matches.

    Args:
    product_matches (dict): A dictionary of product name matches.
    product_dict (dict): A dictionary of product names and their URLs.

    Returns:
    dict: A dictionary mapping product names to hyperlinked versions.
    """
    hyperlink_mapping = {}

    # Creating a lower-cased mapping of product names from product_dict for easier access
    product_dict_lower = {key.lower(): value for key, value in product_dict.items()}

    # Iterate over product_matches
    for product, matched_product in product_matches.items():
        # Find the corresponding key in product_dict based on the matched product
        matched_product_lower = matched_product.lower()
        for key in product_dict_lower:
            if matched_product_lower in key:
                # Get the URL from the matched key in product_dict
                url = product_dict_lower[key][
                    1]  # gets the second element in the dictionary, the URL.
                # Recall that the first element is the product type (men's athletic or women's athletic)
                # Create a hyperlink version of the product name using the original name from product_matches
                hyperlink_mapping[product] = f'<a href="{url}">{product.title()}</a>'
                break  # Stop searching once a match is found

    return hyperlink_mapping


hyperlink_match_dict = create_hyperlink_mapping(product_matches, product_dict)
print(hyperlink_match_dict)


# print(type(hyperlink_match_dict))

def linkify_response(response, hyperlink_mapping):
    """
    Update the response text with hyperlinked product names, replace newline characters with HTML
    line breaks, and return HTML display object.

    Args:
    response (str): The original response text.
    hyperlink_mapping (dict): A dictionary mapping product names to hyperlinked versions.

    Returns:
    HTML: An HTML display object with the updated response.
    """
    for product, hyperlink in hyperlink_mapping.items():
        response = response.replace(product.title(), hyperlink)

    # Replace newline characters with HTML line breaks
    response_with_breaks = response.replace('\n', '<br>')

    return response_with_breaks  # necessary when you are working in PyCharm,
    # but this is best demonstrated in Colab by commenting out the line above and uncommenting the one below
    # return HTML(response_with_breaks) #this will work in Google Colab but not in PyCharm
    
    # for a working example, see: https://colab.research.google.com/drive/1AmWZln5B2flvqb1DrkUeQ2mMWLBmOdf1?usp=sharing


# Using the hyperlink mapping from the previous step
final_response = linkify_response(openai_response, hyperlink_match_dict)
print(final_response)
