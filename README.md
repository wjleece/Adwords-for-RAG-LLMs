# adwords-for-openai
Matching products from OpenAI responses to a product dictionary containing URLs.

This is a demo that takes a response from an LLM (in this case OpenAI, because I'm somewhat familiar with its API) and looks up any product information in a product dictionary. 

The product dictionary contains product attributes, including URL. 

The OpenAI response is amended such that the product names in the response that match the names in the dictionary are returned as hyperlinked text. 

Something like this would be the basis of monetizing LLMs through advertising. 

OpenAI might do this at some point, but Microsoft isn't really dependent on search revenues from Bing. 

Google, though, is a different story. 

I'm sure Bard will start doing this soon as LLMs are going to disrupt internet search and Google's main cash cow. 

So I expect to see "AdWords for Bard" soon. 


Next steps:

1. Get all Nike shoe information available from the Amazon product API
2. Use a RAG system (even though it might not strictly be necessary) to suppliment OpenAI's Nike product knowledge
3. Publish an API for this

Longer term:

1. Build some type of interface that makes it really easy for non-technical users to upload files and/or include URLs as documents to the RAG system
