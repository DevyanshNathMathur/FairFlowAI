# FairFlow AI

**Adaptive Queue, Service Flow & Accessibility Optimizer**

🌐 Live Application: https://fairflowai.onrender.com/

FairFlow AI is a web-based decision-support system designed to analyse service queues, identify bottlenecks, compare visitor waiting experiences, and recommend better use of available service counters.

The system combines service-flow simulation, machine-learning-based waiting-time prediction, staffing optimization, and fairness-aware recommendation logic.

It is designed for settings such as hospitals and OPDs, health camps, government service centres, admission centres, and other high-volume public-service environments.

---

## Problem

Service facilities often experience long and uneven queues because staff and counters are not distributed according to actual demand.

A single overloaded stage can delay the entire service journey even when other stages have spare capacity.

The impact may also differ across visitor groups such as elderly people, pregnant women, and mobility-limited visitors.

FairFlow AI helps study these issues before making staffing changes.

---

## What FairFlow AI Does

FairFlow allows the user to:

- Define the expected number of visitors.
- Specify the operating session duration.
- Create between 2 and 6 service stages.
- Rename service stages according to the actual workflow.
- Add the number of counters available at each stage.
- Enter average service time for each stage.
- Define the visitor-group distribution.
- Simulate visitor movement through the complete service journey.
- Identify the primary bottleneck.
- Estimate average and maximum waiting time.
- Estimate maximum queue size and counter utilization.
- Compare waiting times across visitor groups.
- Calculate a fairness gap between priority groups and general visitors.
- Screen alternative staffing allocations using machine learning.
- Verify shortlisted configurations through simulation.
- Recommend a better counter allocation without increasing the total number of counters.
- Generate a downloadable PDF analysis report.

---

## Dynamic Service Stages

FairFlow is not limited to a fixed workflow.

The user can configure between **2 and 6 ordered service stages** and give each stage a custom name.

For example:

```text
Reception
Triage
Doctor Consultation
Billing
Pharmacy
```

Each stage has its own:

- Stage name
- Number of counters
- Average service time

Visitors pass through the stages in the order configured by the user.

---

## Visitor Groups

The current system models four visitor groups:

- General
- Elderly
- Pregnant
- Mobility-limited

Different service-time multipliers are used during simulation to represent variation in service requirements across these groups.

The submitted visitor percentages must total 100%.

---

## How the System Works

FairFlow uses a hybrid decision-support pipeline.

### 1. Service-Flow Simulation

Virtual visitors arrive during the configured session and move through each service stage.

The simulation calculates:

- Average waiting time
- Maximum waiting time
- Maximum queue size
- Counter utilization
- Stage-level congestion
- Visitor-group waiting time
- Fairness gap

### 2. Alternative Staffing Generation

FairFlow generates feasible alternative counter allocations while keeping the total number of counters unchanged.

For large search spaces, candidate configurations are sampled to keep the analysis responsive.

### 3. Machine-Learning Screening

A machine-learning model estimates average waiting time for candidate staffing configurations.

The current model uses an `ExtraTreesRegressor` from scikit-learn.

It is trained on simulator-generated service-flow scenarios covering different:

- Visitor volumes
- Session durations
- Numbers of stages
- Counter allocations
- Service times
- Visitor-group distributions
- Stage pressures

The model supports service flows containing up to six stages.

### 4. Simulation Verification

The strongest ML-ranked configurations are tested again using the detailed service-flow simulation.

This prevents the final recommendation from relying only on the machine-learning estimate.

### 5. Final Recommendation

FairFlow compares verified configurations using:

- Average waiting time
- Bottleneck severity
- Counter utilization
- Fairness gap

The system then recommends the strongest staffing configuration found during the analysis.

---

## Machine-Learning Model

The ML model predicts **average waiting time**.

Fairness is calculated separately using the service-flow simulation and is not predicted by the ML model.

The model is stored as:

```text
models/fairflow_wait_model.joblib
```

If a compatible saved model is available, FairFlow loads it automatically.

If the model is missing or incompatible with the current model version, FairFlow trains a new model and saves it for future use.

Model performance shown in the application is measured on held-out simulator-generated scenarios.

These metrics should not be interpreted as real-world operational validation.

---

## Example Analysis

One demonstration scenario uses:

```text
Expected visitors: 160
Session duration: 6 hours

Registration
Counters: 2
Average service time: 2 minutes

Verification
Counters: 1
Average service time: 3 minutes

Service
Counters: 3
Average service time: 4 minutes

Visitor mix:
General: 60%
Elderly: 15%
Pregnant: 15%
Mobility-limited: 10%
```

### Current Setup

```text
Average waiting time: 77.77 minutes
Maximum waiting time: 142.63 minutes
Primary bottleneck: Verification
Fairness gap: 6.52 minutes
```

Verification operates at approximately 99.5% utilization in this scenario and becomes the main source of congestion.

### FairFlow Recommendation

```text
Registration: 2 → 2 counters
Verification: 1 → 2 counters
Service: 3 → 2 counters
```

The total number of counters remains unchanged at six.

### Recommended Result

```text
Simulated average waiting time: 6.58 minutes
Estimated waiting-time reduction: 91.5%
Recommended fairness gap: -0.09 minutes
```

The ML wait-time forecast changes from approximately:

```text
73.56 minutes → 9.39 minutes
```

The final recommendation is based on simulation verification rather than the ML prediction alone.

---

## Application Sections

The result interface is organised into:

1. Overview
2. Bottleneck
3. Stage Performance
4. Visitor Groups
5. Fairness
6. Machine Learning
7. Recommendation
8. Staffing
9. Methodology

A PDF version of the complete analysis can also be generated from the result page.

---

## Technology Stack

### Backend

- Python
- Flask

### Simulation and Optimization

- Custom Python service-flow simulation
- Custom staffing-allocation logic

### Machine Learning

- NumPy
- scikit-learn
- ExtraTreesRegressor
- Joblib

### Reporting

- ReportLab

### Frontend

- HTML
- CSS
- JavaScript
- Jinja templates

---

## Project Structure

```text
FairFlowAI/
│
├── .vscode/
│   └── settings.json
│
├── engine/
│   ├── ai_engine.py
│   ├── ml_model.py
│   ├── optimizer.py
│   ├── report_generator.py
│   └── simulation.py
│
├── models/
│   └── fairflow_wait_model.joblib
│
├── static/
│   ├── script.js
│   └── style.css
│
├── templates/
│   ├── index.html
│   ├── results.html
│   └── simulate.html
│
├── app.py
├── requirements.txt
└── README.md
```

---

## Installation

### 1. Create or activate the Python environment

The project was developed using Python 3.12.

If using the existing Conda environment:

```bat
call D:\Anaconda3\Scripts\activate.bat D:\Anaconda3\envs\fairflow
```

### 2. Install dependencies

From the project folder:

```bat
pip install -r requirements.txt
```

### 3. Run the application

```bat
python app.py
```

The local Flask application will start at:

```text
http://127.0.0.1:5000
```

Open this address in a web browser.

---

## Input Validation

FairFlow validates the submitted configuration before analysis.

Examples include:

- Visitor count must be a positive whole number.
- Session duration must be valid.
- At least 2 and no more than 6 stages may be configured.
- Every stage must have a unique name.
- Stage names cannot be blank.
- Counter counts must be positive whole numbers.
- Service time must be greater than zero.
- Visitor-group percentages must each be between 0 and 100.
- Visitor-group percentages must total exactly 100%.

Validation is performed on both the client side and server side.

---

## PDF Analysis Report

The application can generate a downloadable PDF containing:

- Executive summary
- Submitted service setup
- Visitor mix
- Current stage performance
- Visitor-group waiting experience
- Fairness analysis
- Machine-learning analysis
- Recommended action
- Current vs recommended staffing
- Methodology
- Important interpretation note

The generated report is named:

```text
FairFlow_Analysis_Report.pdf
```

---

## Important Interpretation Note

FairFlow is a decision-support prototype.

Its outputs are estimates derived from:

- User-supplied service assumptions
- Simulated visitor journeys
- Machine-learning models trained on simulator-generated scenarios

The current project has not been validated using real-world operational datasets.

Results should therefore not be interpreted as real-world operational, clinical, or safety validation.

---

## Future Scope

Possible future development may include:

- Validation using real-world queue data
- Arrival patterns based on historical facility data
- Stage-specific visitor routing
- Visitors who skip selected stages
- Appointment and walk-in streams
- Shift-level staffing constraints
- Cost-aware staffing optimization
- Layout and walking-distance analysis
- Multi-day demand forecasting
- Institutional dashboards
- Comparison of multiple service-layout scenarios

These are future possibilities and are not part of the current implemented version.

---

## Author

**Devyansh Nath Mathur**

FairFlow AI was developed as an academic technology project exploring the use of simulation, machine learning, optimization, and fairness-aware analysis for service-flow decision support.

---

## Copyright

© 2026 Devyansh Nath Mathur. FairFlow AI. All rights reserved.
