# 🚀 Quick Start Guide - Hybrid Computing Analyzer

**Farid Firdaus - NPM 237006081 - Kelas C**

## ⚡ Fastest Way to Run

### Option 1: Automatic Script (Recommended)

```bash
./start.sh
```

Kemudian buka browser di: **http://localhost:3000**

### Option 2: Manual Step-by-Step

#### 1. Backend (Terminal 1)

```bash
cd backend
./venv/bin/python3 -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

#### 3. Open Browser

http://localhost:3000

## 📋 First Time Setup

### Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend Setup  

```bash
cd frontend
npm install
```

### Generate Data (if needed)

```bash
cd backend
python3 main.py  # Creates 810 sample files
```

## 🛑 Stop Servers

```bash
./stop.sh
```

Or press `Ctrl+C` in each terminal.

## 📊 Usage

### 1. Thread + ProcessPool Analysis

1. Go to **Thread + Process** page
2. Set parameters:
   - I/O Threads: 1-32
   - CPU Processes: 1-32
   - Files: 1-810
3. Click **Start Analysis**
4. View metrics: Speedup, Efficiency, Throughput

### 2. MPI Analysis

1. Go to **MPI** page  
2. Set parameters:
   - MPI Ranks: 1-16
   - I/O Threads per rank
   - CPU Processes per rank
3. Click **Start MPI Analysis**
4. View distributed computing results

## 🔍 API Testing

```bash
# Health check
curl http://localhost:8000/

# Check data status
curl http://localhost:8000/api/status

# Run analysis
curl -X POST http://localhost:8000/api/analyze/thread-process \
  -H "Content-Type: application/json" \
  -d '{"io_workers": 4, "cpu_workers": 4, "limit_data": 100, "detailed": true}'
```

## 🐛 Common Issues

### "Module not found" Error

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### "npm not found" Error

Install Node.js from: https://nodejs.org/

### Backend not responding

Check if backend is running on port 8000:
```bash
lsof -i :8000
```

### MPI not working

```bash
sudo apt-get install mpich
cd backend
source venv/bin/activate
pip install mpi4py
```

## 📁 Project Structure

```
.
├── start.sh                # Quick start script
├── stop.sh                 # Stop servers script
├── backend/                # Python FastAPI
│   ├── api.py             # REST API
│   ├── analyze_files.py   # Thread+Process
│   ├── analyze_mpi.py     # MPI
│   └── venv/              # Virtual environment
├── frontend/               # Next.js
│   ├── app/
│   │   ├── page.js        # Home
│   │   ├── thread-process/ # Analysis page
│   │   └── mpi/           # MPI page
│   └── node_modules/
└── data/                   # 810 text files
```

## 🎯 Features

✅ Web-based GUI (no terminal commands!)  
✅ Real-time analysis results  
✅ Multiple preset configurations  
✅ Visual performance metrics  
✅ Full output logs  
✅ Support for 810 files dataset  

## 📞 Ports

- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000

---

**Ready to analyze! 🚀**
