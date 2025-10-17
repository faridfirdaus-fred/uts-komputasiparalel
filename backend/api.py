#!/usr/bin/env python3
"""
FastAPI Backend untuk Hybrid Computing Analyzer
Menyediakan REST API untuk menjalankan analisis Thread+Process dan MPI
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import subprocess
import json
import os
import time
from pathlib import Path

app = FastAPI(title="Hybrid Computing Analyzer API")

# CORS middleware untuk Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path ke scripts
BASE_DIR = Path(__file__).parent
ANALYZE_FILES_SCRIPT = BASE_DIR / "analyze_files.py"
ANALYZE_MPI_SCRIPT = BASE_DIR / "analyze_mpi.py"
DATA_DIR = BASE_DIR.parent / "data"
VENV_PYTHON = BASE_DIR / "venv" / "bin" / "python3"

# Use venv python if available, otherwise use system python3
PYTHON_CMD = str(VENV_PYTHON) if VENV_PYTHON.exists() else "python3"

# Model untuk request
class ThreadProcessRequest(BaseModel):
    io_workers: int = 3
    cpu_workers: int = 2
    limit_data: int = 810
    detailed: bool = True
    nim: Optional[str] = None

class MPIRequest(BaseModel):
    mpi_ranks: int = 4
    io_workers: int = 3
    cpu_workers: int = 2
    limit_data: int = 810
    detailed: bool = True
    nim: Optional[str] = None

# Model untuk response
class AnalysisResult(BaseModel):
    success: bool
    execution_time: float
    speedup: Optional[float] = None
    throughput: Optional[float] = None
    efficiency: Optional[float] = None
    output: str
    config: Dict[str, Any]
    stats: Optional[Dict[str, Any]] = None

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "running",
        "api": "Hybrid Computing Analyzer",
        "version": "1.0.0"
    }

@app.get("/api/status")
def get_status():
    """Check if data directory exists and count files"""
    try:
        if not DATA_DIR.exists():
            return {
                "data_dir_exists": False,
                "file_count": 0,
                "message": "Data directory not found. Please run main.py to generate sample files."
            }
        
        txt_files = list(DATA_DIR.glob("*.txt"))
        return {
            "data_dir_exists": True,
            "file_count": len(txt_files),
            "message": f"Found {len(txt_files)} text files ready for analysis."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/thread-process", response_model=AnalysisResult)
async def analyze_thread_process(request: ThreadProcessRequest):
    """
    Run Thread + ProcessPool analysis
    """
    try:
        # Build command
        cmd = [
            "python3",
            str(ANALYZE_FILES_SCRIPT),
            "--folder", str(DATA_DIR),
            "--io-workers", str(request.io_workers),
            "--cpu-workers", str(request.cpu_workers),
            "--limit-data", str(request.limit_data)
        ]
        
        # Use venv python if available
        if VENV_PYTHON.exists():
            cmd[0] = str(VENV_PYTHON)
        
        if request.detailed:
            cmd.append("--detailed")
        
        if request.nim:
            cmd = [
                PYTHON_CMD,
                str(ANALYZE_FILES_SCRIPT),
                "--folder", str(DATA_DIR),
                "--nim", request.nim,
                "--detailed"
            ]
        
        # Execute
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        execution_time = time.time() - start_time
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.stderr}"
            )
        
        # Parse output
        output = result.stdout
        stats = parse_analysis_output(output)
        
        return AnalysisResult(
            success=True,
            execution_time=execution_time,
            speedup=stats.get("speedup"),
            throughput=stats.get("throughput"),
            efficiency=stats.get("efficiency"),
            output=output,
            config={
                "io_workers": request.io_workers,
                "cpu_workers": request.cpu_workers,
                "limit_data": request.limit_data,
                "detailed": request.detailed
            },
            stats=stats
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Analysis timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/mpi", response_model=AnalysisResult)
async def analyze_mpi(request: MPIRequest):
    """
    Run MPI + ProcessPool analysis
    """
    try:
        # Build command with --oversubscribe flag to allow more processes than available cores
        cmd = [
            "mpiexec",
            "--oversubscribe",
            "-n", str(request.mpi_ranks),
            PYTHON_CMD,
            str(ANALYZE_MPI_SCRIPT),
            "--folder", str(DATA_DIR),
            "--io-workers", str(request.io_workers),
            "--cpu-workers", str(request.cpu_workers),
            "--limit-data", str(request.limit_data)
        ]
        
        if request.detailed:
            cmd.append("--detailed")
        
        if request.nim:
            cmd = [
                "mpiexec",
                "--oversubscribe",
                "-n", str(request.mpi_ranks),
                PYTHON_CMD,
                str(ANALYZE_MPI_SCRIPT),
                "--folder", str(DATA_DIR),
                "--nim", request.nim,
                "--detailed"
            ]
        
        # Execute
        start_time = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(BASE_DIR)
        )
        execution_time = time.time() - start_time
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"MPI Analysis failed: {result.stderr}"
            )
        
        # Parse output
        output = result.stdout
        stats = parse_mpi_output(output)
        
        return AnalysisResult(
            success=True,
            execution_time=execution_time,
            speedup=stats.get("speedup"),
            throughput=stats.get("throughput"),
            efficiency=stats.get("efficiency"),
            output=output,
            config={
                "mpi_ranks": request.mpi_ranks,
                "io_workers": request.io_workers,
                "cpu_workers": request.cpu_workers,
                "limit_data": request.limit_data,
                "detailed": request.detailed
            },
            stats=stats
        )
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="MPI Analysis timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def parse_analysis_output(output: str) -> Dict[str, Any]:
    """Parse output dari analyze_files.py"""
    stats = {}
    
    try:
        # Parse speedup
        for line in output.split('\n'):
            if "Speedup:" in line:
                speedup_str = line.split("Speedup:")[1].strip().replace('x', '')
                stats["speedup"] = float(speedup_str)
            
            if "Throughput:" in line:
                throughput_str = line.split("Throughput:")[1].strip().split()[0]
                stats["throughput"] = float(throughput_str)
            
            if "Efficiency:" in line:
                efficiency_str = line.split("Efficiency:")[1].strip()
                stats["efficiency"] = float(efficiency_str)
            
            if "Sequential time:" in line:
                seq_time = line.split("Sequential time:")[1].strip().replace('s', '')
                stats["sequential_time"] = float(seq_time)
            
            if "Parallel time:" in line:
                par_time = line.split("Parallel time:")[1].strip().replace('s', '')
                stats["parallel_time"] = float(par_time)
            
            if "Total files processed:" in line:
                files = line.split("Total files processed:")[1].strip()
                stats["files_processed"] = int(files)
            
            if "Total words:" in line:
                words = line.split("Total words:")[1].strip()
                stats["total_words"] = int(words)
    
    except Exception as e:
        print(f"Error parsing output: {e}")
    
    return stats

def parse_mpi_output(output: str) -> Dict[str, Any]:
    """Parse output dari analyze_mpi.py"""
    stats = {}
    
    try:
        # MPI output biasanya dari rank 0
        lines = output.split('\n')
        
        for line in lines:
            if "Speedup:" in line:
                speedup_str = line.split("Speedup:")[1].strip().replace('x', '')
                try:
                    stats["speedup"] = float(speedup_str)
                except:
                    pass
            
            if "Throughput:" in line:
                throughput_str = line.split("Throughput:")[1].strip().split()[0]
                try:
                    stats["throughput"] = float(throughput_str)
                except:
                    pass
            
            if "Efficiency:" in line:
                efficiency_str = line.split("Efficiency:")[1].strip()
                try:
                    stats["efficiency"] = float(efficiency_str)
                except:
                    pass
            
            if "Sequential time:" in line:
                seq_time = line.split("Sequential time:")[1].strip().replace('s', '')
                try:
                    stats["sequential_time"] = float(seq_time)
                except:
                    pass
            
            if "Parallel wall time:" in line:
                par_time = line.split("Parallel wall time:")[1].strip().replace('s', '')
                try:
                    stats["parallel_time"] = float(par_time)
                except:
                    pass
            
            if "Total files processed:" in line:
                files = line.split("Total files processed:")[1].strip()
                try:
                    stats["files_processed"] = int(files)
                except:
                    pass
    
    except Exception as e:
        print(f"Error parsing MPI output: {e}")
    
    return stats

@app.get("/api/presets")
def get_presets():
    """Get preset configurations"""
    return {
        "thread_process": [
            {"name": "1. Baseline (NIM 237006081)", "nim": "237006081", "io_workers": 3, "cpu_workers": 2, "limit_data": 810},
            {"name": "2. Thread Heavy (16 threads)", "io_workers": 16, "cpu_workers": 2, "limit_data": 810},
            {"name": "3. Process Heavy (16 workers)", "io_workers": 2, "cpu_workers": 16, "limit_data": 810},
            {"name": "4. Balanced (8/8)", "io_workers": 8, "cpu_workers": 8, "limit_data": 810},
            {"name": "5. High Parallelism", "io_workers": 12, "cpu_workers": 12, "limit_data": 810},
            {"name": "6. I/O Focused", "io_workers": 20, "cpu_workers": 4, "limit_data": 810},
            {"name": "7. CPU Focused", "io_workers": 4, "cpu_workers": 20, "limit_data": 810},
            {"name": "8. Medium Load", "io_workers": 6, "cpu_workers": 6, "limit_data": 500},
            {"name": "9. Light Load", "io_workers": 4, "cpu_workers": 4, "limit_data": 200},
            {"name": "10. Quick Test (100 files)", "io_workers": 2, "cpu_workers": 2, "limit_data": 100},
        ],
        "mpi": [
            {"name": "1. Baseline (4 ranks)", "mpi_ranks": 4, "nim": "237006081", "io_workers": 3, "cpu_workers": 2, "limit_data": 810},
            {"name": "2. Minimal (2 ranks)", "mpi_ranks": 2, "io_workers": 4, "cpu_workers": 4, "limit_data": 810},
            {"name": "3. Medium Scale (6 ranks)", "mpi_ranks": 6, "io_workers": 3, "cpu_workers": 3, "limit_data": 810},
            {"name": "4. High Scale (8 ranks)", "mpi_ranks": 8, "io_workers": 2, "cpu_workers": 2, "limit_data": 810},
            {"name": "5. Balanced (4/6/6)", "mpi_ranks": 4, "io_workers": 6, "cpu_workers": 6, "limit_data": 810},
            {"name": "6. High Parallelism (4/8/4)", "mpi_ranks": 4, "io_workers": 8, "cpu_workers": 4, "limit_data": 810},
            {"name": "7. CPU Heavy (4/2/8)", "mpi_ranks": 4, "io_workers": 2, "cpu_workers": 8, "limit_data": 810},
            {"name": "8. Medium Test (4 ranks/500)", "mpi_ranks": 4, "io_workers": 4, "cpu_workers": 4, "limit_data": 500},
            {"name": "9. Light Test (2 ranks/200)", "mpi_ranks": 2, "io_workers": 3, "cpu_workers": 3, "limit_data": 200},
            {"name": "10. Quick Test (2 ranks/100)", "mpi_ranks": 2, "io_workers": 2, "cpu_workers": 2, "limit_data": 100},
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
