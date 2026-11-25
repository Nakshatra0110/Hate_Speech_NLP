# HateLess: How to Run the Project (Step-by-Step Guide)

This guide provides end-to-end, step-by-step instructions to set up, configure, run, test, and interact with the **HateLess** Multimodal Hate Speech Detection & Explainable AI platform.

---

## 1. System Prerequisites

Ensure you have the following installed on your machine:

- **Python**: Version `3.10`, `3.11`, `3.12`, or `3.13` (64-bit).
- **Git**: For cloning or version management.
- **Node.js & npm** *(Optional)*: Required only if running npm shortcut scripts or Puppeteer UI screenshot scripts.
- **Hardware Acceleration**: CPU is fully supported by default. CUDA-capable GPU is optional.

---

## 2. Step 1: Open Terminal & Navigate to Project Directory

Open your preferred terminal (PowerShell, Command Prompt, or Bash/Zsh) and navigate to the project root directory:

```bash
cd Hate_Speech_NLP
```

Confirm that you are in the directory containing `backend/`, `src/`, `config/`, and `requirements.txt`.

---

## 3. Step 2: Set Up a Python Virtual Environment

It is strongly recommended to use an isolated Python virtual environment.

### Option A: Using `venv` (Standard Python)

#### On Windows (PowerShell):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```
> *Note for PowerShell users:* If you encounter an execution policy error, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once.

#### On Windows (Command Prompt - CMD):
```cmd
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate.bat
```

#### On Linux / macOS (Bash / Zsh):
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Option B: Using Conda
```bash
# Create conda environment with Python 3.11
conda create -n hateless python=3.11 -y

# Activate conda environment
conda activate hateless
```

---

## 4. Step 3: Install Dependencies

1. **Upgrade pip, setuptools, and wheel:**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. *(Optional)* **Install Node.js dependencies** (Only needed if running automated screenshot scripts):
   ```bash
   npm install
   ```

> **Note on EasyOCR & Model Weights:**  
> Pre-trained models and offline EasyOCR weights are already bundled in the repository inside `models/checkpoints/` and `models/easyocr/` (`craft_mlt_25k.pth`, `devanagari.pth`, `english_g2.pth`). No external download is required during startup.

---

## 5. Step 4: Configure Environment Variables (`.env`)

A sample configuration file `.env.example` is provided in the repository root.

1. **Create your `.env` file:**
   - **On Windows (PowerShell):**
     ```powershell
     Copy-Item .env.example .env
     ```
   - **On Windows (CMD):**
     ```cmd
     copy .env.example .env
     ```
   - **On Linux / macOS:**
     ```bash
     cp .env.example .env
     ```

2. **Verify `.env` parameters:**
   Open `.env` in an editor to review or adjust the settings:
   ```ini
   # Environment Configuration
   APP_ENV=development
   APP_HOST=127.0.0.1
   APP_PORT=8000
   DEBUG=True

   # Storage Paths
   DATABASE_URL=sqlite:///./data/hate_speech_detector.db
   DATA_DIR=./data
   MODELS_DIR=./models
   CONFIG_DIR=./config

   # Compute Device ('cpu', 'cuda', or 'auto')
   DEVICE=cpu
   TORCH_THREADS=4

   # Logging
   LOG_LEVEL=INFO
   ```

---

## 6. Step 5: Initialize the Database (Optional / Verification)

The SQLite database (`data/hate_speech_detector.db`) is automatically initialized and migrated when the FastAPI backend starts up.

If you wish to initialize or verify the database tables manually before starting the server, run:
```bash
python backend/database/db.py
```
*Expected Output:* `Database schema successfully initialized.`

---

## 7. Step 6: Run the Application Server

You can launch the backend and web application using any of the following methods:

### Method 1: Direct Python Execution (Recommended)
```bash
python backend/main.py
```

### Method 2: Using Uvicorn Directly (with Hot Reloading)
```bash
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### Method 3: Using npm Scripts (If Node.js is installed)
```bash
npm start
# or
npm run dev
```

Once executed, the terminal will display the ASGI server log:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 8. Step 7: Access the Web Application & Documentation

Open your browser and navigate to the following endpoints:

| Interface / Resource | URL | Description |
| :--- | :--- | :--- |
| **Research Studio UI** | [http://127.0.0.1:8000/](http://127.0.0.1:8000/) | Interactive web UI for text, meme OCR, and multimodal detection & XAI |
| **Interactive Swagger API** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) | OpenAPI interactive documentation and test bench |
| **ReDoc API Reference** | [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) | Alternative formatted API specification |
| **Health Check Endpoint** | [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) | Real-time JSON health check, compute device, and DB connection |
| **Presentation Deck** | [http://127.0.0.1:8000/presentation/](http://127.0.0.1:8000/presentation/) | Academic presentation slides and viva artifacts |

---

## 9. Step 8: Run the Test Suite

The test suite validates model inference, temperature calibration, Shapley attribution, multi-variant OCR, and adversarial robustness.

### Run All Tests:
```bash
pytest tests/ -v
```

### Run Specific Test Modules:
- **Unit Tests:**
  ```bash
  pytest tests/unit/ -v
  ```
- **Integration Tests:**
  ```bash
  pytest tests/integration/ -v
  ```
- **OCR Verification Suite:**
  ```bash
  pytest tests/test_ocr.py -v
  ```
- **Adversarial Evaluation Suite (240 held-out cases):**
  ```bash
  pytest tests/test_adversarial_suite.py -v
  ```
- **End-to-End Pipeline Test:**
  ```bash
  pytest tests/test_end_to_end_pipeline.py -v
  ```

---

## 10. Step 9: Running Research & Audit Scripts

The `scripts/` directory provides utilities for research validation and data auditing:

- **Audit Database Integrity and Records:**
  ```bash
  python scripts/audit_database.py
  ```
- **Execute Empirical Model Probes (Text, OCR, and Multimodal Fusion):**
  ```bash
  python scripts/run_audit_probes.py
  ```
- **Regenerate Adversarial Held-Out Suite:**
  ```bash
  python scripts/generate_adversarial_suite.py
  ```
- **Generate Synthetic Meme Templates:**
  ```bash
  python scripts/generate_meme_templates.py
  ```
- **Capture Viewport UI Screenshots (Requires Node.js & npm install):**
  ```bash
  node scripts/capture_screenshots.js
  ```

---

## 11. Troubleshooting & Frequently Asked Questions

### 1. `OMP: Error #15: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized` (Windows)
This occurs when multiple libraries (e.g., PyTorch, NumPy, or OpenCV) bundle OpenMP runtime on Windows.  
**Fix:** Set the environment variable before running:
- **PowerShell:**
  ```powershell
  $env:KMP_DUPLICATE_LIB_OK="TRUE"
  ```
- **CMD:**
  ```cmd
  set KMP_DUPLICATE_LIB_OK=TRUE
  ```
- **Bash:**
  ```bash
  export KMP_DUPLICATE_LIB_OK=TRUE
  ```
*(Note: HateLess scripts and tests already set this automatically in code).*

### 2. `[WinError 10013]` or `Address already in use` (Port 8000 Conflict)
On Windows, `[WinError 10013] An attempt was made to access a socket in a way forbidden by its access permissions` means **another process is already running on port 8000** (or port 8000 is reserved by Windows).

**Option A: Stop the process currently using port 8000**
In PowerShell, check and terminate the process holding port 8000:
```powershell
# Find the PID holding port 8000
Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess

# Terminate that process (replace <PID> with the actual ID, e.g. 9468)
Stop-Process -Id <PID> -Force
```
Or via CMD:
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Option B: Run on a different port (e.g. 8080)**
- In `.env`, change:
  ```ini
  APP_PORT=8080
  ```
- Or pass `--port 8080` to Uvicorn:
  ```bash
  uvicorn backend.main:app --host 127.0.0.1 --port 8080 --reload
  ```

### 3. ModuleNotFoundError (`No module named 'backend'` or `No module named 'src'`)
Always ensure commands are executed from the **root directory** of the repository (`Hate_Speech_NLP`), where `backend` and `src` reside.

### 4. GPU vs CPU Execution
By default, the project runs on CPU (`DEVICE=cpu` in `.env`). If you have a CUDA-compatible NVIDIA GPU and PyTorch with CUDA installed, update `.env`:
```ini
DEVICE=cuda
```

---

## 12. Quick Command Summary Cheatsheet

```bash
# 1. Activate Environment
.\venv\Scripts\Activate.ps1       # Windows PowerShell
# source venv/bin/activate         # Linux / macOS

# 2. Install Requirements
pip install -r requirements.txt

# 3. Setup Configuration
copy .env.example .env

# 4. Start Server
python backend/main.py

# 5. Run Verification Tests
pytest tests/ -v
```
