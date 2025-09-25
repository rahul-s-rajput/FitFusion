#!/usr/bin/env python3
"""
FitFusion Development Server Starter
Starts both backend and frontend in development mode
"""

import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color):
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}")
    print(f"{message}")
    print(f"{'='*60}{Colors.ENDC}\n")

class ProcessManager:
    def __init__(self):
        self.processes = []
        self.running = True
        
    def start_backend(self):
        """Start the FastAPI backend"""
        print_colored("🚀 Starting FitFusion Backend...", Colors.BLUE)
        
        backend_dir = Path("backend")
        if not backend_dir.exists():
            print_colored("❌ Backend directory not found!", Colors.RED)
            return None
        
        # Check if virtual environment exists
        venv_dir = backend_dir / "venv"
        if venv_dir.exists():
            if os.name == 'nt':  # Windows
                python_exe = venv_dir / "Scripts" / "python.exe"
            else:  # Unix/Linux/macOS
                python_exe = venv_dir / "bin" / "python"
        else:
            python_exe = "python"
        
        try:
            process = subprocess.Popen(
                [str(python_exe), "main.py"],
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(("Backend", process))
            
            # Start output reader thread
            threading.Thread(
                target=self.read_output,
                args=(process, "BACKEND", Colors.GREEN),
                daemon=True
            ).start()
            
            return process
            
        except Exception as e:
            print_colored(f"❌ Failed to start backend: {e}", Colors.RED)
            return None
    
    def start_frontend(self):
        """Start the Next.js frontend"""
        print_colored("🎨 Starting FitFusion Frontend...", Colors.BLUE)
        
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print_colored("❌ Frontend directory not found!", Colors.RED)
            return None
        
        # Check if node_modules exists
        if not (frontend_dir / "node_modules").exists():
            print_colored("⚠️  node_modules not found. Running npm install...", Colors.YELLOW)
            try:
                subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
            except subprocess.CalledProcessError:
                print_colored("❌ Failed to install frontend dependencies", Colors.RED)
                return None
        
        try:
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes.append(("Frontend", process))
            
            # Start output reader thread
            threading.Thread(
                target=self.read_output,
                args=(process, "FRONTEND", Colors.YELLOW),
                daemon=True
            ).start()
            
            return process
            
        except Exception as e:
            print_colored(f"❌ Failed to start frontend: {e}", Colors.RED)
            return None
    
    def read_output(self, process, prefix, color):
        """Read and display process output"""
        try:
            for line in iter(process.stdout.readline, ''):
                if self.running and line.strip():
                    print_colored(f"[{prefix}] {line.strip()}", color)
        except Exception:
            pass
    
    def stop_all(self):
        """Stop all processes"""
        self.running = False
        print_colored("\n🛑 Stopping all services...", Colors.YELLOW)
        
        for name, process in self.processes:
            try:
                if process.poll() is None:  # Process is still running
                    print_colored(f"Stopping {name}...", Colors.YELLOW)
                    process.terminate()
                    
                    # Wait for graceful shutdown
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print_colored(f"Force killing {name}...", Colors.RED)
                        process.kill()
                        process.wait()
                    
                    print_colored(f"✅ {name} stopped", Colors.GREEN)
            except Exception as e:
                print_colored(f"Error stopping {name}: {e}", Colors.RED)
        
        print_colored("🎉 All services stopped", Colors.GREEN)

def check_prerequisites():
    """Check if prerequisites are met"""
    print_header("CHECKING PREREQUISITES")
    
    # Check Python
    try:
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 8:
            print_colored(f"✅ Python {python_version.major}.{python_version.minor} found", Colors.GREEN)
        else:
            print_colored("❌ Python 3.8+ required", Colors.RED)
            return False
    except Exception:
        print_colored("❌ Python not found", Colors.RED)
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"✅ Node.js {result.stdout.strip()} found", Colors.GREEN)
        else:
            print_colored("❌ Node.js not found", Colors.RED)
            return False
    except Exception:
        print_colored("❌ Node.js not found", Colors.RED)
        return False
    
    # Check npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_colored(f"✅ npm {result.stdout.strip()} found", Colors.GREEN)
        else:
            print_colored("❌ npm not found", Colors.RED)
            return False
    except Exception:
        print_colored("❌ npm not found", Colors.RED)
        return False
    
    # Check .env file
    if os.path.exists(".env"):
        print_colored("✅ .env file found", Colors.GREEN)
    else:
        print_colored("⚠️  .env file not found - copy from .env.example", Colors.YELLOW)
    
    return True

def main():
    """Main function"""
    print_header("FITFUSION DEVELOPMENT SERVER")
    print_colored("Starting FitFusion in development mode...", Colors.BLUE)
    print_colored("Press Ctrl+C to stop all services", Colors.YELLOW)
    
    # Check prerequisites
    if not check_prerequisites():
        print_colored("❌ Prerequisites not met. Please install required software.", Colors.RED)
        return 1
    
    manager = ProcessManager()
    
    # Setup signal handler for graceful shutdown
    def signal_handler(sig, frame):
        manager.stop_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        print_header("STARTING SERVICES")
        
        # Start backend
        backend_process = manager.start_backend()
        if not backend_process:
            return 1
        
        # Wait a bit for backend to start
        time.sleep(3)
        
        # Start frontend
        frontend_process = manager.start_frontend()
        if not frontend_process:
            manager.stop_all()
            return 1
        
        print_header("SERVICES RUNNING")
        print_colored("🎉 FitFusion is running!", Colors.GREEN)
        print_colored("📱 Frontend: http://localhost:3000", Colors.BLUE)
        print_colored("🔧 Backend API: http://localhost:8000", Colors.BLUE)
        print_colored("📚 API Docs: http://localhost:8000/api/docs", Colors.BLUE)
        print_colored("\nPress Ctrl+C to stop all services", Colors.YELLOW)
        
        # Keep running until interrupted
        while manager.running:
            time.sleep(1)
            
            # Check if processes are still running
            for name, process in manager.processes:
                if process.poll() is not None:
                    print_colored(f"❌ {name} stopped unexpectedly", Colors.RED)
                    manager.stop_all()
                    return 1
    
    except KeyboardInterrupt:
        manager.stop_all()
        return 0
    except Exception as e:
        print_colored(f"❌ Error: {e}", Colors.RED)
        manager.stop_all()
        return 1

if __name__ == "__main__":
    sys.exit(main())
