# Adwords-for-RAG-LLMs

This is a demo of the basis of monetizing RAG-enriched LLMs through advertising. 

OpenAI seems to be doing well monetizing GPT by building a centralized platform, but I believe companies like Google and Perplexity will have to monetize their LLMs through advertising - something similar to AdWords. 

I expect to see "AdWords for Bard" and some equivalent on Perplexity coming soon.

A ready-to-run version of this using gpt-4 (you just supply your OpenAI API key) exists at: https://colab.research.google.com/drive/1vl0-w_87c_wtAE9cLXTOlRabnwkBsk2R

If you run this on a Google Colab GPU insteand of a CPU, it's significantly faster - one of the many reasons I prefer Colab vs. running this locally in PyCharm. 

Going forward, I'm also more likely to update the Colab notebook vs. what I have here.

I haven't made this Colab notebook public, but I'm happy to share with you if you contact me.


# Description of Adwords-for-RAG-LLMs.py

1. Ingests product information and product review data from Amazon (currently limited to Nike shoes with reviews from Jan 1, 2022 until mid Jan 2024) --> note that Amazon URLs may change so as get further from Jan 2024, landing pages are more likely to 'break'
2. Creates a product dictionary of the product + review data
3. Creats a Retrieval Augmented Generation (RAG) system which is trained on the Nike product review data from Amazon 
4. Generates relevant responses to customer queries based on the Nike product review data (the base LLM used is OpenAI's gpt-4)
5. Creates a dictionary form the response
6. Replaces any product names in the response with hyperlinked versions of the product name (pointing to an Amazon landing page URL)
7. Puts together a full response with the now hyperlinked product names
8. Creates an external API on Gradio so this tool can be shared  

# Next steps

1. Build some type of user interface that makes it really easy for non-technical users to upload files and/or include URLs as documents to the RAG system
2. Update the model so it can handle follow up questions
