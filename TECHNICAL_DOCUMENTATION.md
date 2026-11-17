# BridgeTwin AI
## AI-Powered Bridge Digital Twin and Predictive Maintenance System

### 1. Project Overview

BridgeTwin AI is a software-based bridge monitoring and digital twin platform designed to demonstrate how artificial intelligence, simulation, and predictive maintenance can support infrastructure management.

The project creates a virtual representation of a bridge and uses data-driven simulations to explore its condition under different scenarios. It helps users understand potential structural risks, evaluate maintenance requirements, and generate reports based on simulation results.

The platform is designed as a software-only solution and does not require physical sensors or external monitoring hardware.

### 2. Key Features

- **Digital Twin Visualization:** Provides a virtual representation of a bridge and its structural components.
- **AI-Based Analysis:** Uses a trained machine learning model to support condition assessment.
- **Simulation Engine:** Allows users to simulate different bridge conditions and future scenarios.
- **Predictive Maintenance:** Evaluates maintenance actions and helps prioritize possible interventions.
- **Synthetic Dataset Support:** Uses generated datasets to demonstrate different structural conditions.
- **Reporting:** Generates reports containing relevant simulation and analysis results.
- **Interactive Dashboard:** Provides a centralized interface for exploring bridge information and simulation outputs.

### 3. Technology Stack

The project uses a frontend and backend architecture.

| Component | Technology |
|---|---|
| Frontend | React and Vite |
| Styling | Tailwind CSS |
| Backend | Python and FastAPI |
| API Server | Uvicorn |
| Machine Learning | Python-based ML model |
| Testing | Pytest |
| Deployment | Vercel for the frontend |

### 4. System Architecture

The application follows a frontend-backend architecture.

**Frontend Layer**

The frontend provides the user interface for visualizing the bridge, accessing datasets, running simulations, and viewing maintenance recommendations.

**Backend Layer**

The Python backend handles API requests, simulation operations, model-related functionality, and report generation.

**Machine Learning and Simulation Layer**

This layer processes available data and supports condition analysis and simulated future scenarios.

**Data Layer**

The system uses synthetic and project datasets to demonstrate bridge condition analysis without requiring physical sensor installations.

### 5. Backend API Overview

The backend exposes API endpoints for the application's main operations.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/model-info` | Retrieves model information |
| GET | `/api/bridge` | Retrieves bridge information |
| GET | `/api/datasets` | Retrieves available datasets |
| POST | `/api/simulate` | Runs a simulation |
| POST | `/api/simulate/future` | Runs a future scenario simulation |
| POST | `/api/simulate/reset` | Resets simulation state |
| GET | `/api/maintenance/actions` | Retrieves maintenance actions |
| GET | `/api/report` | Retrieves report information |

### 6. Running the Project Locally

#### Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Activate the virtual environment if one has already been created:

```powershell
.\.venv\Scripts\Activate.ps1
```

Start the backend server:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

The backend will be available at:

`http://127.0.0.1:8000`

#### Frontend Setup

Open a separate terminal and navigate to the frontend directory.

Install dependencies using the project's package manager and start the development server using the scripts defined in `package.json`.

### 7. Typical Application Workflow

1. Open the BridgeTwin AI application.
2. Explore the virtual bridge representation.
3. Review the available datasets and model information.
4. Run a simulation using the available parameters.
5. Examine the generated simulation results.
6. Explore future scenario predictions.
7. Review suggested maintenance actions.
8. Generate and inspect the resulting report.

### 8. Testing and Validation

The project includes backend tests to verify important application functionality.

Testing focuses on API behavior, simulation operations, and backend reliability. The frontend production build and application workflows are also checked during development.

### 9. Project Limitations

- The project is a software-based demonstration and does not directly monitor real-world bridges.
- Results depend on the quality and assumptions of the available datasets.
- Synthetic data is used to demonstrate simulation and analysis workflows.
- Predictions should not replace professional structural inspections or engineering assessments.

### 10. Future Enhancements

Potential improvements include:

- Integration of larger and more diverse structural datasets.
- Improved machine learning models and validation.
- More detailed structural simulation capabilities.
- Advanced maintenance scheduling and optimization.
- Additional visualization and reporting features.
- Deployment improvements for continuous availability.

### 11. Conclusion

BridgeTwin AI demonstrates how digital twin concepts, machine learning, and simulation can be combined in a software platform for infrastructure analysis.

The project brings together frontend development, backend API engineering, data processing, machine learning, and interactive visualization to explore a practical infrastructure management use case.

---

**Repository:** https://github.com/pranavv-7124/BridgeTwin-AI

**Live Application:** https://bridge-twin-ai-ten.vercel.app/