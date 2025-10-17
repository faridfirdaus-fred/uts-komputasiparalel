# 🚀 Hybrid Computing Analyzer - Full Stack Application

**Nama:** Farid Firdaus  
**NPM:** 237006081  
**Kelas:** C

Aplikasi full-stack untuk analisis performa hybrid computing dengan GUI web-based. Backend menggunakan Python FastAPI, frontend menggunakan Next.js.

## 📁 Struktur Proyek

```
.
├── backend/                 # Python FastAPI Backend
│   ├── api.py              # FastAPI REST API
│   ├── analyze_files.py    # Thread + ProcessPool analyzer
│   ├── analyze_mpi.py      # MPI + ProcessPool analyzer
│   ├── modules/            # Helper modules
│   └── requirements.txt    # Python dependencies
│
├── frontend/               # Next.js Frontend
│   ├── app/
│   │   ├── page.js        # Home page
│   │   ├── layout.js      # Layout with navigation
│   │   ├── thread-process/ # Thread+Process analysis page
│   │   └── mpi/           # MPI analysis page
│   └── package.json       # Node.js dependencies
│
└── data/                   # Dataset (810 text files)
```

## 🎯 Features

### 1. **Thread + ProcessPool Analysis**
- Configure I/O threads (1-32)
- Configure CPU processes (1-32)
- Analyze up to 810 files
- Real-time results with speedup, throughput, efficiency metrics
- Preset configurations for quick testing

### 2. **MPI + ProcessPool Analysis**
- Configure MPI ranks for distributed computing
- Hybrid parallelization per rank
- Distributed file processing
- Comprehensive performance metrics

### 3. **Web GUI**
- Form-based input (no terminal commands needed)
- Real-time analysis feedback
- Visual metrics display
- Full output logs

## 🛠️ Setup Instructions

### Prerequisites

```bash
# Python 3.9+ required
python --version

# Node.js 18+ required
node --version

# For MPI analysis (optional)
sudo apt-get install mpich
```

### 1. Setup Backend (Python)

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Generate dataset (if not exists)
python main.py   # Creates 810 sample files in ../data/
```

### 2. Setup Frontend (Next.js)

```bash
cd frontend

# Install dependencies
npm install
# or
yarn install
```

## 🚀 Running the Application

### Step 1: Start Backend Server

```bash
cd backend
source .venv/bin/activate
python api.py
```

Backend akan berjalan di: **http://localhost:8000**

### Step 2: Start Frontend Server

```bash
# Open new terminal
cd frontend
npm run dev
```

Frontend akan berjalan di: **http://localhost:3000**

### Step 3: Open Browser

Buka browser dan akses: **http://localhost:3000**

## 📊 How to Use

### Thread + ProcessPool Analysis

1. Navigate to **Thread + Process** page
2. Configure parameters:
   - **I/O Threads:** Number of threads for file reading (1-32)
   - **CPU Processes:** Number of processes for analysis (1-32)
   - **Files to Process:** Number of files to analyze (1-810)
   - **Detailed Analysis:** Enable for comprehensive stats
3. Click **"Start Analysis"**
4. View results:
   - Speedup: How much faster than sequential
   - Efficiency: Resource utilization efficiency
   - Throughput: Files processed per second
   - Full output log

### MPI Analysis

1. Navigate to **MPI** page
2. Configure parameters:
   - **MPI Ranks:** Number of MPI processes (1-16)
   - **I/O Threads per rank:** Threads for each MPI process
   - **CPU Processes per rank:** Worker processes per rank
   - **Files to Process:** Total files (distributed across ranks)
3. Click **"Start MPI Analysis"**
4. View distributed computing results

### Quick Presets

Both pages include preset configurations:
- **Baseline (NIM):** Standard configuration based on NPM 237006081
- **Thread Heavy:** Emphasizes thread parallelization
- **Process Heavy:** Emphasizes process parallelization
- **Balanced:** Equal thread and process distribution
- **Quick Test:** Fast test with limited files

## 🔌 API Endpoints

Backend menyediakan REST API:

### GET /
Health check

### GET /api/status
Check data directory and file count

### POST /api/analyze/thread-process
Run Thread + ProcessPool analysis

**Request body:**
```json
{
  "io_workers": 3,
  "cpu_workers": 2,
  "limit_data": 810,
  "detailed": true
}
```

### POST /api/analyze/mpi
Run MPI analysis

**Request body:**
```json
{
  "mpi_ranks": 4,
  "io_workers": 3,
  "cpu_workers": 2,
  "limit_data": 810,
  "detailed": true
}
```

### GET /api/presets
Get preset configurations

## 📈 Performance Metrics Explained

### Speedup
```
Speedup = Sequential Time / Parallel Time
```
Measures how much faster parallel execution is compared to sequential.

### Efficiency
```
Efficiency = Speedup / Number of Workers
```
Indicates how well resources are utilized (ideal = 1.0 or 100%).

### Throughput
```
Throughput = Files Processed / Time (files per second)
```
Measures processing rate.

## 🐛 Troubleshooting

### Backend Issues

**Error: "Module not found"**
```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

**Error: "No data directory"**
```bash
cd backend
python main.py  # Generate sample files
```

**Error: "MPI not found"**
```bash
sudo apt-get install mpich
pip install mpi4py
```

### Frontend Issues

**Error: "npm not found"**
```bash
# Install Node.js from https://nodejs.org/
```

**Error: "Connection refused to localhost:8000"**
```bash
# Make sure backend is running
cd backend
python api.py
```

**CORS Errors**
- Backend API sudah dikonfigurasi untuk allow origin dari localhost:3000
- Pastikan tidak menggunakan port lain

## 🔧 Development

### Backend Development

```bash
cd backend
source .venv/bin/activate
python api.py  # Auto-reload enabled with uvicorn
```

### Frontend Development

```bash
cd frontend
npm run dev  # Hot reload enabled
```

### Testing Manually

```bash
# Test backend API
curl http://localhost:8000/api/status

# Test analysis endpoint
curl -X POST http://localhost:8000/api/analyze/thread-process \
  -H "Content-Type: application/json" \
  -d '{"io_workers": 2, "cpu_workers": 2, "limit_data": 100, "detailed": true}'
```

## 📝 Notes

- Dataset 810 files adalah requirement sesuai tugas
- Aplikasi mendukung konfigurasi fleksibel untuk eksperimen
- Output lengkap tersimpan dan dapat di-export
- Cocok untuk analisis performa parallel computing

## 🎓 Academic Context

Project ini dibuat untuk:
- **Mata Kuliah:** Komputasi Paralel
- **Topik:** Hybrid Computing dengan Thread, Process, dan MPI
- **Tujuan:** Membandingkan performa berbagai strategi parallelization

---

**Happy Computing! 🚀**

Farid Firdaus - 237006081 - Kelas C
