# document-analyzer
Final Project for EC530. Create material using LLM, provide feedback and grade)


## Set Up Environment

Install required dependencies:

`pip install -r requirements.txt`

Create Environment variables with `.env`:
- create `.env` file in root
- copy and paste `.env.example` into your `.env` and replace the OpenAI key placeholder with your real OpenAI key.

## How to run:

1. Run the server. In terminal,

  `uvicorn src.doc_api:app --reload`

2. Go to `index.html` and open in browser.
   
