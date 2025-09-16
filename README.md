🛒 E-Commerce Chatbot

An AI-powered chatbot for e-commerce product search and customer support.
Built with FastAPI for backend, vanilla JS frontend (can be upgraded to React/Next.js), and supports deployment on AWS EC2.
📂 Project Structure
ecommerce_chat_bot/
│
├── backend/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── services/
│   │   ├── chatbot_service.py
│   │   └── retriever_service.py
│   ├── ingestion/
│   │   ├── csv_loader.py
│   │   ├── api_loader.py
│   │   └── data_ingestion.py
│   ├── config/
│   │   ├── settings.py
│   │   └── config.yaml
│   ├── utils/
│   │   ├── logging.py
│   │   └── exceptions.py
│   ├── prompt_library/
│   │   └── system_prompt.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│
├── frontend/
│   ├── index.html        # Chat UI page
│   ├── styles.css        # Styling for chatbot UI
│   └── app.js            # JavaScript logic to call FastAPI backend
│
├── data/
│   └── flipkart_product_review.csv
│
├── logs/
├── .env
├── setup.py
├── docker-compose.yml
└── README.md


⚙️ Setup Instructions
1️⃣ Clone the repository
conda create -p ./venv python=3.10 -y
conda activate ./venv

Option B: Virtualenv

python3 -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

3️⃣ Install dependencies

pip install -r backend/requirements.

Then freeze the environment:

pip freeze > backend/requirements.txt


That will lock every library (LangChain, FastAPI, etc.) to the exact versions you have installed — which is what professionals do before deploying to AWS/production.

4️⃣ Environment Variables

Create a .env file inside the project root:
OPENAI_API_KEY=your_api_key
ASTRADB_TOKEN=your_astra_db_token
DB_URI=your_database_uri

5️⃣ Run the Application
Backend (FastAPI)

cd backend
uvicorn main:app --host 0.0.0.0 --port 5000 --reload

Frontend

Simply open frontend/index.html in your browser.

🐳 Docker Setup

Build and run containers using Docker Compose:
docker-compose up --build

☁️ AWS EC2 Deployment
1. Launch EC2 Instance

Ubuntu 20.04 or later

Allow port 5000 in security group (Inbound Rule: TCP, 0.0.0.0/0).

2. Install system dependencies
sudo apt update -y
sudo apt install git curl unzip tar make sudo vim wget python3-pip -y

3. Clone repository & setup
git clone <your-repo-url>
cd ecommerce_chat_bot

4. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt --break-system-packages

Create .env file on server:
vi .env
# Add environment variables here

cd backend
uvicorn main:app --host 0.0.0.0 --port 5000

Access your chatbot at:
👉 http://<your-ec2-public-ip>:5000

🧪 Running Tests
cd backend
pytest tests/

🚀 Features

✅ FastAPI-based backend with modular structure

✅ Frontend chatbot interface (HTML/CSS/JS)

✅ Embedding & vector search for product queries

✅ Logging & exception handling

✅ Dockerized for deployment

✅ Deployable on AWS EC2














conda activate E:\ecommerce_chat_bot\venv
Create a Conda environment:
If you don't have anaconda download from here Link

conda create -p <env_name> python=3.10 -y


Activate your conda environment

Conda activate <env_path>


If activating on bash terminal use this command:

Source activate ./<env_name>

Conda activate <env_path>


Create a requirement.txt file and install it.

pip install -r requirements.txt

pip freeze > backend/requirements.txt


Create a .env file for keeping your environment variable.


Use setup.py for installing your local package.

<either mention -e . inside your requirements.txt
Or run python setup.py install >


Checkout here with full video of end to end project setup Link



AWS Deployment:

Push your entire code to github
Login to your AWS account Link
Launch your EC2 Instance
Configure your EC2 Instance
Command for configuring EC2 Instance.
sudo apt-get update and sudo apt update are used to update the package index on a Debian-based system like Ubuntu, but they are slightly different in terms of the tools they use and their functionality:

sudo apt-get update


This command uses apt-get, the traditional package management tool.

sudo apt update -y


This command uses apt, a newer, more user-friendly command-line interface for the APT package management system.

Install required tools
sudo apt install git curl unzip tar make sudo vim wget -y


Clone git repository

git clone <.git url>


Create a .env file there

touch .env


Open file in VI editor

vi .env


Press insert and Mention env variable then press esc for saving and write :wq for exit.

cat .env #for checking the value


For installing python and pip here is a command:

sudo apt install python3-pip


Then install the requirements.txt

The --break-system-packages flag in pip allows to override the externally-managed-environment error and install Python packages system-wide.

pip3 install -r requirements.txt

pip3 install -r  requirements.txt --break-system-packages




The --break-system-packages flag in pip allows to override the externally-managed-environment error and install Python packages system-wide.
pip install package_name --break-system-packages

Then run your application

python3 app.py



Configure your inbound rule:
Go inside the security
Click on security group
Configure your inbound rule with certain values

Port 5000 0.0.0.0/0 for anywhere traffic TCP/IP protocol


Save it and now run it again.


