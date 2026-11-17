
# BridgeTwin AI – Technical Documentation

## 1. Project Overview

BridgeTwin AI is an AI-powered digital twin platform designed to support bridge infrastructure monitoring, structural assessment, and predictive maintenance.

Traditional bridge inspections often depend on periodic manual assessments, which can make it difficult to identify potential structural issues at an early stage. BridgeTwin AI addresses this challenge through a software-based approach that combines synthetic structural data, machine learning, digital twin visualization, and simulation.

The platform allows users to explore bridge conditions, simulate possible future scenarios, assess structural risks, and generate maintenance recommendations without requiring physical sensors or external monitoring hardware.

## 2. Key Features

- **Digital Twin Visualization:** Provides a virtual representation of bridge infrastructure for exploring structural conditions.
- **AI-Based Structural Assessment:** Uses machine learning to analyze structural parameters and estimate potential risks.
- **Synthetic Dataset Generation:** Generates simulated structural data for model development and testing.
- **Structural Simulations:** Allows users to simulate future structural conditions under different scenarios.
- **Predictive Maintenance:** Provides recommendations based on predicted structural conditions and risk assessments.
- **Automated Reports:** Generates reports containing assessment results and maintenance insights.
- **Interactive Dashboard:** Presents structural information and simulation results through a user-friendly interface.

## 3. Technology Stack

The project uses the following technologies:

| Component | Technology |
|---|---|
| Frontend | React |
| Styling | Tailwind CSS |
| Backend | Python, FastAPI |
| API Server | Uvicorn |
| Machine Learning | Python-based ML models |
| Data Processing | Python |
| Testing | Pytest |
| Deployment | Vercel (Frontend) |

The frontend communicates with the backend through REST API endpoints. The backend handles simulation requests, structural assessment, and report generation.

## 4. System Architecture

BridgeTwin AI follows a frontend-backend architecture.

### Frontend Layer
The frontend provides an interactive dashboard where users can explore the digital twin, enter structural parameters, initiate simulations, and view assessment results.

### Backend Layer
The backend is developed using FastAPI. It receives requests from the frontend, processes structural data, executes simulation logic, and returns results through REST APIs.

### Machine Learning Layer
The machine learning component analyzes structural parameters and supports risk assessment and predictive maintenance workflows.

### Simulation Layer
The simulation engine processes different structural scenarios and estimates possible future conditions using generated or supplied data.

### Data Flow

1. The user interacts with the frontend dashboard.
2. Structural parameters are submitted to the backend.
3. The backend processes the input and executes the relevant simulation.
4. The assessment and prediction results are returned through API responses.
5. The frontend displays the results through visualizations and reports.

## 5. Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.12 or later
- Node.js and npm
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/pranavv-7124/BridgeTwin-AI.git
cd BridgeTwin-AI
```

### Step 2: Set Up the Backend

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Step 3: Start the Backend Server

From the backend directory, execute:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend server will be available at:

http://127.0.0.1:8000

Interactive API documentation:

http://127.0.0.1:8000/docs

### Step 4: Set Up the Frontend

Open a second terminal and navigate to the project root:

```bash
cd BridgeTwin-AI
```

Install frontend dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Open the local URL displayed in the terminal to access the application.

## 6. How It Works

The application follows a structured workflow:

1. **Input:** Users interact with the dashboard and provide or select structural parameters.
2. **Processing:** The backend receives the input through REST API requests.
3. **Simulation:** The simulation engine evaluates the selected structural scenario.
4. **Assessment:** The system processes structural indicators and generates assessment results.
5. **Prediction:** The predictive component estimates possible future structural conditions.
6. **Recommendation:** Maintenance insights are generated based on the assessment.
7. **Reporting:** Results are presented through the dashboard and report-generation functionality.

The platform uses software-generated data and simulations rather than relying on physical bridge sensors.

## 7. Troubleshooting

| Issue | Possible Solution |
|---|---|
| Python command not recognized | Verify Python installation and PATH configuration. |
| Virtual environment activation fails | Run PowerShell with an appropriate process-level execution policy. |
| ModuleNotFoundError | Activate the virtual environment and install requirements. |
| Backend server fails to start | Check dependencies, working directory, and port availability. |
| Frontend dependencies missing | Run `npm install` from the project root. |
| API connection error | Ensure the backend is running and the frontend API configuration is correct. |
| Port 8000 already in use | Stop the existing process or configure another available port. |

## 8. Future Improvements

Potential future enhancements include:

- Integration of more advanced machine learning models for structural risk prediction.
- Improved 3D visualization and interactive digital twin capabilities.
- Support for additional bridge structures and environmental scenarios.
- Enhanced simulation accuracy using validated engineering datasets.
- More detailed predictive maintenance scheduling.
- Expanded reporting and data visualization capabilities.
- Integration with real-world structural monitoring systems as an optional future extension.

## 9. Project Repository

GitHub: https://github.com/pranavv-7124/BridgeTwin-AI

Live Application: https://bridge-twin-ai-ten.vercel.app/

---

**Note:** BridgeTwin AI is a software-based prototype. Its predictions and simulations should not be treated as certified structural engineering assessments or substitutes for professional bridge inspections.
