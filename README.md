# adwords-for-LLMs
A ready-to-run version of this with OpenAI (you just supply your OpenAI API key) exists at: https://colab.research.google.com/drive/1vl0-w_87c_wtAE9cLXTOlRabnwkBsk2R#scrollTo=C6sr4Wwu1Z5C

Running this in PyCharm works fine except that PyCharm doesn't render hyperlinks easily (I didn't spend much time figuring out how that could be done), but hyperlinks render just fine in browswer environments like Google Colab (see link above).


# What this code does

1. Ingests product information and product review data from Amazon (currently limited to Nike shoes with reviews from Jan 1, 2022 until mid Jan 2024) --> note that Amazon URLs may change so as get further from Jan 2024, landing pages are more likely to 'break'
2. Creates a product dictionary of the product + review data
3. Creats a Retrieval Augmented Generation (RAG) system which is trained on the Nike product review data from Amazon 
4. Generates relevant responses to customer queries based on the Nike product review data (the base LLM used is OpenAI's gpt-4)
5. Creates a dictionary form the response
6. Replaces any product names in the response with hyperlinked versions of the product name (pointing to an Amazon landing page URL)
7. Puts together a full response with the now hyperlinked product names
8. Creates an external API on Gradio so this tool can be shared 

Something like what's here would be the basis of monetizing LLMs through advertising. 

OpenAI might do this at some point, but Microsoft isn't really dependent on search revenues from Bing. 

Google, though, is a different story. 

I'm sure Bard will start doing this soon as LLMs are going to disrupt internet search and Google's main cash cow. 

So I expect to see "AdWords for Bard" soon. 


Next steps:

1. Build some type of user interface that makes it really easy for non-technical users to upload files and/or include URLs as documents to the RAG system
