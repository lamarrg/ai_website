This a base creation of an AI based website.

It uses a Flask front end, a local LLM of your choice, Ollama, Boostrap and Faiss database. 

Essentially, you can upload items to a folder, they are ingested and their data is to the Faiss database. The built in instructions tell the LLM to ony use data from said database to answer all questions. If the question is out of scope, let the user know. 

It's not as formal as training an LLM, but it works pretty darn well with as far as I got. 

As this was the beginning stages, there are things that can be improved (see below). As this is not being used, it will be seen if the improvements are made of my own accord. For now, it shows a starting point, and that I am furthering my education. 

Items that could be improved...
    - Code cleanup and clarification
    - Include file upload interface
    - Improve database structure so when files are removed from upload folder, associated data is removed from database(s)