## Install Required Packages
1. Use the following command in the terminal to install packages:
   ```bash
   pip install -r requirements.txt
   
## Setup Instructions
1. Create a `.env` file in the project
2. Copy `.env.example` to `.env`:
   ```bash
   DATABASE_URL=postgresql://postgres:{DB_PASSWORD}@{ENDPOINT}/{DB_NAME}

## Run The Application
1. Use the following command in the terminal to run the server:
   ```bash
   uvicorn main:app --reload

