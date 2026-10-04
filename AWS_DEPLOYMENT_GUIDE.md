# AWS EC2 Manual Deployment Guide (No Docker: PM2 & Systemd)

Deploy **KnowledgeAI** directly on your AWS Ubuntu EC2 instance using **PM2** and **Systemd** without Docker.

---

## 1. AWS Security Group (Ports to Open)

In your AWS EC2 Console > **Security Groups** attached to your instance, ensure these Inbound rules are added:

| Type | Protocol | Port Range | Source | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **SSH** | TCP | `22` | Your IP (or `0.0.0.0/0`) | Terminal Access |
| **Custom TCP** | TCP | `5173` | `0.0.0.0/0` | Frontend Web UI |
| **Custom TCP** | TCP | `8000` | `0.0.0.0/0` | Backend API & Swagger Docs |

---

## 2. Connect to EC2 (via AWS Browser Console)

1. Go to **AWS Console** > **EC2** > **Instances**.
2. Select your instance and click the **Connect** button at the top.
3. Select **EC2 Instance Connect** tab and click **Connect**.
4. A browser terminal will open. Run the steps below inside it.

---

## 3. Server Prerequisites Installation (Python, Node.js, PostgreSQL & PM2)

Run these commands in the terminal:

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3, pip, venv, and build tools
sudo apt install -y python3 python3-pip python3-venv git curl build-essential

# 3. Install Node.js 20 & PM2
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2

# 4. Install PostgreSQL and pgvector extension
sudo apt install -y postgresql postgresql-contrib

# Install pgvector (from official apt or source)
sudo apt install -y postgresql-16-pgvector 2>/dev/null || sudo apt install -y postgresql-14-pgvector 2>/dev/null || {
  sudo apt install -y postgresql-server-dev-all
  git clone --branch v0.7.4 https://github.com/pgvector/pgvector.git /tmp/pgvector
  cd /tmp/pgvector && make && sudo make install && cd -
}
```

---

## 4. Configure PostgreSQL Database

Create the database user, database, and enable the `vector` extension:

```bash
# Set password for postgres user and create database
sudo -u postgres psql <<EOF
ALTER USER postgres WITH PASSWORD 'postgre123';
CREATE DATABASE knowledge_ai;
\c knowledge_ai;
CREATE EXTENSION IF NOT EXISTS vector;
\q
EOF
```

---

## 5. Clone the Repository

```bash
cd ~
git clone https://github.com/engrabhishekyadav/Knowledge_AI.git
cd Knowledge_AI
```

---

## 6. Backend Setup (Python + PM2 / Systemd)

### 6.1 Create Virtual Environment & Install Dependencies
```bash
cd ~/Knowledge_AI/backend

# Create virtualenv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 6.2 Configure Backend `.env`
```bash
cp .env.example .env
nano .env
```
Ensure your configuration looks like this:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_gemini_api_key
OPENROUTER_API_KEY=your_actual_openrouter_api_key

# PostgreSQL connection string
DATABASE_URL=postgresql+asyncpg://postgres:postgre123@localhost:5432/knowledge_ai

# Security
JWT_SECRET_KEY=9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b
CORS_ORIGINS=["*"]
```
*(Save and exit: `Ctrl + O`, `Enter`, `Ctrl + X`)*

### 6.3 Test Database Initialization
```bash
# Seed initial tables/data
python app/seed_data.py
```

### 6.4 Start Backend with PM2
```bash
pm2 start "venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000" --name "knowledge-backend"
```

---

## 7. Frontend Setup (React/Vite + PM2)

### 7.1 Install Dependencies & Configure API URL
```bash
cd ~/Knowledge_AI/frontend

# Install node dependencies
npm install

# Create frontend .env with your EC2 Public IP
nano .env
```
Add the following line (replace `<YOUR_AWS_PUBLIC_IP>` with your instance's actual IP):
```env
VITE_API_URL=http://<YOUR_AWS_PUBLIC_IP>:8000
```
*(Save and exit: `Ctrl + O`, `Enter`, `Ctrl + X`)*

### 7.2 Build Frontend for Production
```bash
npm run build
```

### 7.3 Serve Frontend with PM2
```bash
# PM2 serves the production build directly on port 5173
pm2 serve dist 5173 --spa --name "knowledge-frontend"
```

---

## 8. Persist PM2 Across System Reboots

Run these two commands so your backend and frontend start automatically if the EC2 instance restarts:
```bash
pm2 save
pm2 startup
```
*(Follow the single command line that `pm2 startup` prints on screen).*

---

## 9. Check Status & Logs

```bash
# Check if both are online
pm2 status

# View live backend logs
pm2 logs knowledge-backend

# View live frontend logs
pm2 logs knowledge-frontend
```

---

## 10. Access Your Live Application

Open your web browser and visit:
- **Frontend Web UI:** `http://<YOUR_AWS_PUBLIC_IP>:5173`
- **Backend Swagger API Docs:** `http://<YOUR_AWS_PUBLIC_IP>:8000/docs`
- **Health Endpoint:** `http://<YOUR_AWS_PUBLIC_IP>:8000/api/v1/health`

---

## Updating the App in the Future
Whenever you push changes to GitHub:
```bash
cd ~/Knowledge_AI
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
pm2 restart knowledge-backend

# Update frontend
cd ../frontend
npm install
npm run build
pm2 restart knowledge-frontend
```
