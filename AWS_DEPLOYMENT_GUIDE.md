# AWS EC2 Server Deployment Guide (IP & Port - No Domain Required)

This guide walks you through deploying **KnowledgeAI** onto an AWS EC2 instance using your instance's public IP address without needing a domain name or SSL certificate.

---

## 1. AWS EC2 Instance Setup

### Recommended Instance Specs
- **OS**: Ubuntu Server 24.04 LTS or 22.04 LTS
- **Instance Type**: `t3.small` (2 vCPU, 2 GB RAM) or `t3.medium` (4 GB RAM).
  > **Note on Free Tier (`t2.micro` / 1GB RAM)**: If using `t2.micro`, you **must** configure 2 GB swap space (detailed in Section 5) to prevent out-of-memory errors during build.

### Configure AWS Security Group (Inbound Rules)
In your AWS EC2 Console, navigate to **Security Groups** attached to your instance and add these inbound rules:

| Type | Protocol | Port Range | Source | Purpose |
|------|----------|------------|--------|---------|
| SSH | TCP | `22` | Your IP (or `0.0.0.0/0`) | SSH Terminal Access |
| Custom TCP | TCP | `5173` | `0.0.0.0/0` | Frontend UI (Docker Compose) |
| Custom TCP | TCP | `8000` | `0.0.0.0/0` | Backend API & Swagger Docs |
| HTTP | TCP | `80` | `0.0.0.0/0` | Web Port (if using Nginx) |

---

## 2. Connect to Your EC2 Instance via SSH

On your local machine (Terminal / PowerShell):
```bash
ssh -i /path/to/your-key.pem ubuntu@<YOUR_AWS_PUBLIC_IP>
```

---

## 3. Quick Deployment via Docker Compose (Recommended)

### Step 3.1: Install Docker & Docker Compose on Ubuntu
Run the following commands on your EC2 instance:
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y curl git ca-certificates gnupg lsb-release

# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Allow your user to run docker without sudo
sudo usermod -aG docker ubuntu
newgrp docker
```

### Step 3.2: Clone Your GitHub Repository
```bash
git clone https://github.com/engrabhishekyadav/Knowledge_AI.git
cd Knowledge_AI
```

### Step 3.3: Set Up Environment Variables
Create the `.env` file from the example:
```bash
cp .env.example .env
nano .env
```
Fill in your configuration:
```env
# Gemini API Key (Required for AI chat & embeddings)
GEMINI_API_KEY=your_actual_gemini_api_key

# OpenRouter (Optional fallback)
OPENROUTER_API_KEY=your_actual_openrouter_api_key

# Generate a strong 64-character hex secret for JWT:
JWT_SECRET_KEY=9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b

# Allow all origins (so browser can access from your IP)
CORS_ORIGINS=["*"]
```
Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 3.4: Launch the Containers
```bash
docker compose up -d --build
```

### Step 3.5: Verify the Running Services
```bash
docker compose ps
```
You should see:
- `knowledge_ai_postgres` running on port `5433`
- `knowledge_ai_backend` running on port `8000`
- `knowledge_ai_frontend` running on port `5173`

### Step 3.6: Access Your Application
Open your browser and navigate to:
- **Frontend App**: `http://<YOUR_AWS_PUBLIC_IP>:5173`
- **Backend API Docs (Swagger UI)**: `http://<YOUR_AWS_PUBLIC_IP>:8000/docs`
- **Health Check**: `http://<YOUR_AWS_PUBLIC_IP>:8000/api/v1/health`

---

## 4. Useful Management Commands

### View Live Logs
```bash
# All services
docker compose logs -f

# Backend only
docker compose logs -f backend

# Frontend only
docker compose logs -f frontend
```

### Restart Services
```bash
docker compose restart
```

### Pull Latest Code from GitHub and Redeploy
```bash
git pull origin main
docker compose up -d --build
```

### Stop Services
```bash
docker compose down
```

---

## 5. (Important) Adding Swap Space on Small EC2 Instances

If your EC2 instance has 1GB or 2GB of RAM (like `t2.micro` or `t3.micro`), running npm builds or AI embeddings can trigger the Linux Out-Of-Memory (OOM) killer. Run this once on the EC2 instance to add 2 GB of swap:

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```
Verify with:
```bash
free -h
```
