# Adwords-for-RAG-LLMs

This is a demo of the basis of monetizing RAG-enriched LLMs through advertising. 

OpenAI seems to be doing well monetizing GPT by building a centralized platform, but I believe companies like Google and Perplexity will have to monetize their LLMs through advertising - something similar to AdWords. 

I expect to see "AdWords for Gemini" and some equivalent on Perplexity coming soon.

I recommend running this in Colab (wjleece_AdWords_RAG_LLM_API_final.ipynb) vs. locally (Adwords-for-RAG-LLMs.py ) as you can leverage Colab's GPU for better performance.

# Description of "Adwords for RAG LLMs"

1. Ingests product information and product review data from Amazon (currently limited to Nike shoes with reviews from Jan 1, 2022 until mid Jan 2024) --> note that Amazon URLs may change so as get further from Jan 2024, landing pages are more likely to 'break'
2. Creates a product dictionary of the product + review data
3. Creats a Retrieval Augmented Generation (RAG) system which is enriched with Nike product review data from Amazon 
4. Generates relevant responses to customer queries based on the Nike product review data (the base LLM used is OpenAI's gpt-4)
5. Creates a dictionary from the response
6. Replaces any product names in the response with hyperlinked versions of the product name (pointing to an Amazon landing page URL)
7. Puts together a full response with the now hyperlinked product names
8. Creates an external API on Gradio so this tool can be shared  
