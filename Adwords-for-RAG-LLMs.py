import json
import os
import re
import pandas as pd
import requests
import gradio as gr
from IPython.display import HTML
from getpass import getpass
from langchain_community.document_loaders import CSVLoader
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_openai import OpenAI
from langchain_community.vectorstores import FAISS

# Define the OpenAI model to be used
model = "gpt-4o"

# Get org ID & API key from files
script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the script
api_key_file = os.path.join(script_dir, "api-key.txt")  # Construct the path to the api-key.txt file

# Read the API key from the file
with open(api_key_file, "r") as file:
    api_key = file.read().strip()  # strip() removes any leading/trailing whitespace

# Set the environment variable
os.environ["OPENAI_API_KEY"] = api_key

url = 'https://raw.githubusercontent.com/wjleece/adwords-for-LLMs/main/updated_Amazon_reviews_batch_all.json'  # JSON
# formatted data

response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    all_reviews = response.text
else:
    print(f"Failed to fetch data: HTTP {response.status_code}")

# Now all_reviews contains the data from the URL
product_and_review_dict = json.loads(all_reviews)

# Ensures we have all the data formatted properly. Returns a dictionary.

# print(type(product_and_review_dict))

# Let's get our data in something that makes it easy to view, like a DataFrame
# DataFrame expects a list input, and we have a nested dictionary
# Let's convert the nested dictionary to a list

# Flatten the structure
flattened_reviews = []
for batch in product_and_review_dict.values():
    # batch is the key values in json_data, as all_reviews was created by combining 4 separate batches of Amazon review data
    # I used Octoparse when had a limit (50) on the number of ASINs it could process in one batch.
    # There were 190 or so ASINs, hence 4 batches to get all the review data
    flattened_reviews.extend(batch)  # Modify the flattened_reviews list by adding each review to the end of the list

# Create DataFrame
product_and_reviews_df = pd.DataFrame(flattened_reviews)

#print(f'The DataFrame shape is: ', product_and_reviews_df.shape)

# we do some stuff here b/c FAISS.from_documents required data to be formatted with a page_content key
data = []
product_and_reviews_df.to_csv('data/df_embed.csv', index=False)
path= 'data/df_embed.csv'
loader = CSVLoader(file_path=path, source_column="Combined_Review")
data = loader.load()

#print(data[3])

#for debug
word_count=0
total_word_count=0

for i in range(len(data)):
    word_count = len(data[i].page_content)
    total_word_count = total_word_count + word_count

#print (f'You have {len(data)} review(s) in your data')
#print (f'There are {total_word_count} words in total in all the reviews')

# Only run this once per session as it can get expensive
embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

#embeddings = OpenAIEmbeddings(model="text-embedding-3-small") #use this in the future as its cheaper; currently there's a formatting issue with the hyperlinks with this model

db = FAISS.from_documents(data, embeddings) #generates embeddings for each document in data using the OpenAIEmbeddings instance and then indexes these embeddings using FAISS

#Create RAG Response Function Returning JSON Formatted Data + Response Quality Function

query = "What are some great Nike running shoes that customers love?"
#I only have this here as a seeding input, so that the functions below can successfully initialize so that you can then run greet().
#This item only needs to be run once per session as once functions are initialized, the greet() function will execute taking the 'actual customer query'

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

def get_rag_response_from_query(db, query, k=5):
    # Similarity search
    reviews = db.similarity_search(query, k=k)
    review_content = " ".join([r.page_content for r in reviews])

    # Initialize ChatOpenAI with gpt-4o
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0.5)

    # Main prompt
    prompt = ChatPromptTemplate.from_template("""
    You are a bot has specialized knowledge of Nike shoes, which you have obtained from Nike shoe customer review data from Amazon that has been provided to you.
    When you are asked questions about Nike shoes, make sure to mention specific key phrases from the reviews that you have access to, as long as that information
    is relevant to the question asked. Return the response in the form of an introduction, a recommendation section, and a conclusion.
    Return the data in the recommendation section in JSON format using "product_name" as the key and "description" as the value.
    You do not need to tell me when the JSON formatted section begins or ends as I expect that to be clearly indicated with "[" and "]", respectively.
    Similarly you do not need to tell me what the intro is and what the conclusion is as it will precede and follow the "[" and "]", respectively.

    Answer the following question: {question}
    By searching the following articles: {docs}

    If the question is not related to the information in the Nike shoe customer review data from Amazon
    that you have been given access to, respond that you have expertise in Nike shoes but not on the topic the user has asked.
    """)

    # Create and invoke chain
    chain = prompt | llm | StrOutputParser()
    rag_response_text = chain.invoke({"question": query, "docs": review_content})

    # Evaluation prompt
    prompt_eval = ChatPromptTemplate.from_template("""
    You job is to evaluate if the response to a given context is faithful for the following: {answer}
    By searching the following reviews: {docs}
    Give a reason why they are similar or not, start with a Yes or a No.
    """)

    # Create and invoke evaluation chain
    chain_part_2 = prompt_eval | llm | StrOutputParser()
    evals = chain_part_2.invoke({"answer": rag_response_text, "docs": review_content})

    return rag_response_text, review_content, evals
    
rag_response_text, review_content, evals = get_rag_response_from_query(db, query)

# Create OpenAI Response Dictionary from RAG Response for Later Hyperlinking; Separate JSON Response from Intro and Conclusion.

def create_response_tuple(rag_response_text):
    openai_response_formatted = rag_response_text.strip()

    # Finding the start and end of the JSON data
    json_start = openai_response_formatted.find('[')
    json_end = openai_response_formatted.rfind(']') + 1  # +1 to include the closing bracket

    # Extracting the intro and conclusion text
    intro_text = openai_response_formatted[:json_start].strip()
    conclusion_text = openai_response_formatted[json_end:].strip()

    # Extracting the product description data from the response
    openai_response_products = openai_response_formatted[json_start:json_end].strip()

    # Converting JSON data to a list of dictionaries
    data = json.loads(openai_response_products)

    # Creating a dictionary with product names and descriptions
    response_product_dict = {}
    for item in data:
        response_product_dict[item['product_name']] = item['description']

    return intro_text, response_product_dict, conclusion_text

# Create Hyperlinks and Insert into OpenAI response

# This works well with text-embedding-ada-002 but less well with text-embedding-3-small.
# This is undoubtedly due to some formatting nuances that I'll figure out later
# text-embedding-3-small is cheaper than text-embedding-ada-002 so I should use it

def create_hyperlink_mapping(response_product_dict, product_and_review_dict):
    """
    Create a mapping of product names to their hyperlinked versions using the closest matches.

    Args:
    response_product_dict (dict): A dictionary of product names from an OpenAI response
    product_and_review_dict (dict): A nested dictionary of product details including URLs.

    Returns:
    dict: A dictionary mapping product names to hyperlinked versions.
    """
    hyperlink_mapping = {}

    # Flatten the nested product_and_review_dict
    flattened_product_dict = {}
    for batch in product_and_review_dict.values():
        for product in batch:
            product_title = product['Product_Title'].lower()
            url = product['Link_Url']
            flattened_product_dict[product_title] = url

    # Iterate over products in response_product_dict
    for product_name in response_product_dict.keys():
        # Lowercase the product name for matching
        matched_product_lower = product_name.lower()

        # Find the corresponding URL in flattened_product_dict
        for title, url in flattened_product_dict.items():
            if matched_product_lower in title:
                # Create a hyperlink version of the product name
                hyperlink_mapping[product_name] = f'<a href="{url}">{product_name}</a>'
                break  # Stop searching once a match is found

    return hyperlink_mapping

# Create API

def linkify_response_for_gradio(response_product_dict, hyperlink_match_dict):
    updated_response = ""
    for product, description in response_product_dict.items():
        # Embed hyperlink for the product, if available
        hyperlink = hyperlink_match_dict.get(product, None)
        if hyperlink:
            # Add target="_blank" to open in new tab and embed in the text
            updated_hyperlink = hyperlink.replace('<a href=', '<a target="_blank" href=')
        else:
            # If no hyperlink, use the product name as plain text
            updated_hyperlink = f'<a>{product}</a>'

        # Combine the hyperlinked product with its description
        # Remove the product name from the description to avoid repetition
        description_without_product_name = description.replace(product, '').strip()
        updated_response += f"<p>{updated_hyperlink}: {description_without_product_name}</p>"

    # Replace newline characters with HTML line breaks (if needed)
    response_with_breaks = updated_response.replace('\n', '<br>')
    return response_with_breaks


def main():
  def greet(query):

      # Step 1: Get OpenAI response
      rag_response_text, review_content, evals = get_rag_response_from_query(db, query, k=5)

      # Step 2: Convert string response to product_dict
      response_tuple = create_response_tuple(rag_response_text)
      intro = response_tuple[0]
      response_product_dict = response_tuple[1]
      conclusion = response_tuple[2]

      # Step 3: Create hyperlink mapping
      hyperlink_match_dict = create_hyperlink_mapping(response_product_dict, product_and_review_dict)

      # Step 4: Linkify response for Gradio
      hyperlinked_response = linkify_response_for_gradio(response_product_dict, hyperlink_match_dict)

      # Step 5: Return the response with its intro and conclusion
      intro_html = f"<p>{intro}</p>" #things get messed up if I don't do this, not entirely sure why
      conclusion_html = f"<p>{conclusion}</p>"
      final_response = intro_html + hyperlinked_response + conclusion_html
      final_response = final_response.replace('\n', '<br>')

      return final_response, review_content, evals

  examples = [
      ["Can you recommend some lightweight Nike running shoes that dry easily if they get wet?"],
      ["Can you recommend some lightweight Nike basketball shoes that have good ankle support?"],
      ["Can you recommend some Nike shoes that customers love?"],
      ["Can you recommend some Nike shoes that are comfortable and durable?"],
      ]

  nike_product_search = gr.Interface(fn=greet, title="Bill Leece's Nike Product Sentiment Search & Adwords Simulator", inputs="text",
                            outputs=[ #gr.components.Textbox(lines=3, label="Response"),
                            gr.HTML(label="Response"),
                            gr.components.Textbox(lines=3, label="Source"),
                            gr.components.Textbox(lines=3, label="Evaluation")],
                                    )

  nike_product_search.launch(share=True)

if __name__ == "__main__":
    main()
