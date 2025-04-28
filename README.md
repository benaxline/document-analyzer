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

## Docker Setup

1. In the root directory of this project, run this script to install Docker:

  `./docker_setup.sh`

2. In the same directory, run this command to build the Docker image:

  `sudo docker build -t my-app .`

3. Run this command to boot the image :

  `sudo docker run -p 8000:8000 -p 8001:8001 my-app`

4. Navigate to `http://localhost:8001` and use the app as intended.

   
