EcoGrid

Smart Energy Monitoring, Forecasting & 3D Digital Twin Platform

EcoGrid is an intelligent energy monitoring and visualization platform that combines data analytics, machine learning, backend development, and 3D visualization to demonstrate a smarter approach to energy management.

The project integrates a centralized dashboard, energy analytics, sensor information, machine learning-based forecasting experiments, and an interactive 3D Digital Twin environment.

⸻

1. Project Overview

EcoGrid is designed to demonstrate how digital technologies can improve the monitoring, analysis, and visualization of energy-related information in buildings and residential communities.

The platform brings different components together into one application:

* Energy monitoring and analytics
* Machine learning-based energy forecasting experiments
* Sensor information visualization
* Flask backend and API integration
* Interactive 3D Digital Twin
* Infrastructure status visualization

The main objective is to create a unified digital environment where energy-related information can be accessed and interpreted more easily.

2. Problem Statement

Energy monitoring in buildings and residential communities can become challenging when information is distributed across different systems.

Some common challenges include:

* Lack of centralized energy monitoring.
* Difficulty interpreting energy consumption patterns.
* Limited visualization of building infrastructure.
* Difficulty understanding sensor-related information.
* Limited use of predictive analytics for energy planning.

EcoGrid explores a unified solution through data processing, analytics, forecasting experiments, and interactive visualization.

3. Project Objectives

The major objectives of EcoGrid are:

1. Develop a centralized energy monitoring dashboard.
2. Display energy-related KPIs and analytics.
3. Present available sensor readings in a structured format.
4. Experiment with machine learning models for energy forecasting.
5. Develop a Flask-based backend and API.
6. Create an interactive 3D Digital Twin using Three.js.
7. Visualize infrastructure components and their statuses.
8. Integrate data science and software engineering into one application.

4. Key Features

4.1 Introductory Landing Page

* Dedicated EcoGrid introduction screen.
* Professional visual presentation.
* Project branding.
* Navigation to the main dashboard.

4.2 Energy Monitoring Dashboard

* Centralized dashboard interface.
* Energy-related KPI cards.
* Hourly energy information.
* Interactive charts.
* Sensor information.
* Infrastructure overview.

4.3 Energy Analytics

The analytics section presents energy-related information through visual representations.

Features include:

* Total energy consumption information.
* Hourly energy data.
* Energy trend visualization.
* Analytical summaries through dashboard charts.

4.4 Sensor Monitoring

The sensor monitoring section displays available sensor-related information in a structured table.

The backend API provides the information used by the dashboard, including available readings and sensor-related details.

4.5 3D Digital Twin

EcoGrid includes a Three.js-powered 3D visualization environment.

Society Scene

* 3D representation of the society environment.
* Building-level visual exploration.
* Interactive camera controls.

Proposed Integration

* Conceptual visualization of the proposed smart infrastructure.
* Visual representation of the planned integrated environment.

4.6 Infrastructure Status

The dashboard includes infrastructure-related status visualization, including:

* Generator
* Security
* Water Pump
* Entrance Gate

5. Technology Stack

Technology	Purpose
Python	Backend and data processing
Flask	Backend framework and API
HTML5	Frontend structure
CSS3	Styling and layout
JavaScript	Frontend functionality
Three.js	3D Digital Twin visualization
Pandas	Data processing
NumPy	Numerical operations
Scikit-learn	Machine learning experimentation
Matplotlib	Data visualization, where used

Note: The final dependency list should match the packages actually used in the project.

6. System Architecture

EcoGrid follows a layered application architecture.

Layer 1: Data Layer

Contains energy-related datasets and data used for analysis and model experimentation.

Layer 2: Data Processing and Machine Learning

Python-based processing is used to prepare data and evaluate forecasting models.

Layer 3: Backend Layer

Flask handles backend routes and provides dashboard information through API endpoints.

Layer 4: Frontend Layer

HTML, CSS, and JavaScript provide the user interface, dashboard interactions, and data presentation.

Layer 5: Visualization Layer

Three.js provides the interactive 3D Digital Twin environment.

Architecture Flow

Energy Dataset
      |
      v
Data Processing
      |
      v
Machine Learning
      |
      v
Python / Flask Backend
      |
      v
Dashboard API
      |
      v
HTML + CSS + JavaScript
      |
      +----------------------+
      |                      |
      v                      v
Energy Dashboard       Three.js Digital Twin
      |
      v
Analytics, Sensors and Infrastructure

7. Machine Learning and Energy Forecasting

EcoGrid includes an energy forecasting experimentation module implemented in Python.

The model comparison script is:

energy_ensemble_forecasting.py

The objective is to compare different regression approaches and evaluate their predictive performance using standard regression metrics.

7.1 Models Evaluated

Five approaches were compared:

1. Linear Regression
2. Persistence Baseline
3. Gradient Boosting
4. Random Forest
5. Decision Tree

7.2 Evaluation Metrics

Mean Absolute Error (MAE)

Measures the average absolute difference between actual and predicted values. Lower values indicate smaller average prediction errors.

Mean Squared Error (MSE)

Measures the average squared prediction error. Lower values indicate better performance.

Root Mean Squared Error (RMSE)

Measures the square root of the mean squared error. Lower values indicate better predictive performance according to this metric.

R² Score

Measures how well a model explains variation in the target values. A score closer to 1 generally indicates better explanatory performance. Negative values indicate performance worse than a mean-based prediction baseline.

7.3 Final Model Comparison

The following results were obtained from the model comparison output.

Model	MAE	MSE	RMSE	R² Score
Linear Regression	0.3543	0.2186	0.4676	0.0552
Persistence Baseline	0.3190	0.2305	0.4801	0.0040
Gradient Boosting	0.5108	0.4073	0.6382	-0.7601
Random Forest	0.5626	0.5250	0.7245	-1.2686
Decision Tree	0.6238	0.7353	0.8575	-2.1778

7.4 Best Performing Model

Linear Regression achieved the lowest RMSE among the evaluated models.

Its evaluation results were:

Metric	Value
MAE	0.3543
MSE	0.2186
RMSE	0.4676
R² Score	0.0552

Therefore, Linear Regression was selected as the best-performing model based on RMSE.

Although Persistence Baseline achieved a lower MAE of 0.3190, Linear Regression achieved the lowest RMSE.

7.5 Model Evaluation Observations

* Linear Regression achieved the lowest RMSE.
* Persistence Baseline achieved the lowest MAE.
* Gradient Boosting, Random Forest, and Decision Tree produced higher prediction errors.
* Negative R² scores indicate weak predictive performance for those models on the evaluation data.
* The results show that forecasting performance has room for improvement.

7.6 Future Improvements

Potential improvements include:

* Feature engineering.
* Hyperparameter optimization.
* Additional historical energy data.
* Improved temporal features.
* Cross-validation.
* Testing additional forecasting algorithms.
* Evaluation on unseen data.

8. Backend and API

EcoGrid uses Flask to serve backend routes and dashboard information.

Dashboard Route

http://127.0.0.1:5000/dashboard

This route opens the main dashboard.

Dashboard Data API

http://127.0.0.1:5000/api/dashboard-data

This endpoint provides structured JSON data for the frontend.

API Response Structure

The dashboard API includes fields such as:

* project
* status
* total_energy_kwh
* hourly_energy
* hourly_labels
* active_sensors
* sensors

Example API Structure

{
  "project": "EcoGrid",
  "status": "Success",
  "total_energy_kwh": "...",
  "hourly_energy": [],
  "hourly_labels": [],
  "active_sensors": "...",
  "sensors": []
}

The example illustrates the response structure. Actual values are supplied by the running backend.

9. Frontend Development

The frontend is developed using HTML, CSS, and JavaScript.

Its responsibilities include:

* Displaying dashboard information.
* Presenting energy analytics.
* Rendering sensor information.
* Handling user interactions.
* Connecting to the Flask API.
* Supporting the 3D visualization interface.

The frontend communicates with the backend through the dashboard API.

10. 3D Digital Twin Implementation

Three.js is used to develop the interactive 3D visualization environment.

The Digital Twin section contains two scenes.

Society Scene

* Building visualization.
* Interactive 3D environment.
* Camera movement and exploration.

Proposed Integration

* Conceptual visualization of proposed infrastructure.
* Representation of the planned integration environment.

The 3D environment provides a more intuitive visual understanding of the infrastructure.

11. Testing and Validation

Manual testing was performed to verify the main application components.

Test Area	Validation
Flask Backend	Backend server startup
Dashboard Route	Dashboard accessibility
Dashboard API	JSON response and Success status
KPI Cards	Dashboard data presentation
Energy Analytics	Chart rendering
Sensor Table	Sensor information display
Society Scene	3D visualization
Proposed Integration	3D scene rendering
Infrastructure	Component status presentation
Camera Controls	3D navigation

Known Testing Observations

* Some B2 building readings were not appearing.
* Live readings were not available in the Proposed Integration scene.
* A missing favicon.ico browser request may appear in the console. This does not prevent the main dashboard from operating.

These observations are documented as areas for further improvement.

12. Project Directory Structure

The project is organized into application files, datasets, and supporting folders.

EcoGrid/
|
|-- .git/
|-- .gitignore
|-- README.md
|-- requirements.txt
|
|-- app.py
|-- energy_ensemble_forecasting.py
|-- index.html
|-- style.css
|-- script.js
|
|-- data/
|
|-- screenshots/
|   |-- 01_Introduction.png
|   |-- 02_Main_Dashboard.png
|   |-- 03_Energy_Analytics.png
|   |-- 04_Sensor_Readings.png
|   |-- 05_Society_3D.png
|   |-- 06_Proposed_Integration.png
|   |-- 07_Infrastructure.png
|   |-- 08_API_Data.png
|
|-- tests/
|   |-- testing_checklist.md
|
|-- notebooks/

This is an illustrative structure. Keep only the files and folders that actually exist in the repository.

13. Installation and Local Setup

Prerequisites

* Python 3.x
* pip
* Git
* Visual Studio Code (recommended)
* A modern web browser

Step 1: Clone the Repository

git clone https://github.com/YOUR_USERNAME/EcoGrid.git

Step 2: Navigate to the Project

cd EcoGrid

Step 3: Create a Virtual Environment

For Windows:

python -m venv .venv

Step 4: Activate the Environment

.venv\Scripts\Activate.ps1

Step 5: Install Dependencies

pip install -r requirements.txt

Step 6: Start the Flask Application

python app.py

Step 7: Open the Dashboard

Visit:

http://127.0.0.1:5000/dashboard

Step 8: Check the API

Visit:

http://127.0.0.1:5000/api/dashboard-data

The API should return a JSON response containing project information and dashboard data.

14. Screenshots and Project Evidence

The screenshots/ directory contains visual evidence of the application’s main features.

Screenshot	Description
01_Introduction.png	EcoGrid introductory page
02_Main_Dashboard.png	Main dashboard
03_Energy_Analytics.png	Energy analytics
04_Sensor_Readings.png	Sensor table
05_Society_3D.png	Society 3D scene
06_Proposed_Integration.png	Proposed Integration scene
07_Infrastructure.png	Infrastructure status
08_API_Data.png	Dashboard API response

15. Current Project Status

EcoGrid demonstrates an integrated approach to energy monitoring and visualization through:

* Flask-based backend.
* Centralized dashboard.
* Energy analytics.
* Sensor information.
* Machine learning forecasting experiments.
* Three.js-based 3D Digital Twin.
* Infrastructure status visualization.

Some building-level readings and live integration features remain areas for improvement.

16. Future Scope

Future development can expand EcoGrid into a more comprehensive smart energy management platform.

Potential enhancements include:

1. Real-time IoT sensor integration.
2. Live energy consumption monitoring.
3. Improved building-level data availability.
4. More accurate forecasting models.
5. Automated anomaly detection.
6. Building-level energy comparisons.
7. Predictive maintenance.
8. Advanced 3D Digital Twin interactions.
9. Cloud deployment and remote accessibility.
10. Alerts and notifications for unusual energy patterns.
11. Historical reporting and downloadable analytics.
12. Role-based access for administrators and users.

17. Learning Outcomes

The development of EcoGrid provides practical experience in:

* Python programming.
* Data processing and analytics.
* Machine learning model evaluation.
* Regression metrics.
* Flask backend development.
* API communication.
* HTML, CSS, and JavaScript.
* Three.js 3D visualization.
* Software integration and testing.
* Git and GitHub version control.
* Technical documentation.

18. Conclusion

EcoGrid demonstrates how data science, machine learning, backend development, frontend engineering, and 3D visualization can be combined into a unified smart energy monitoring concept.

The project provides a foundation for exploring intelligent energy management and digital infrastructure visualization.

Although some building readings and live integration features require further improvement, EcoGrid establishes a practical starting point for developing a more connected and intelligent energy management platform.

19. Project Information

Field	Details
Project Name	EcoGrid
Project Category	Smart Energy Monitoring and Digital Twin
Domain	Artificial Intelligence, Data Science and Software Development
Backend	Python and Flask
Frontend	HTML, CSS and JavaScript
3D Visualization	Three.js
Machine Learning	Regression Model Evaluation
Repository	Add GitHub repository URL
Deployment	Add live deployment URL

⸻

EcoGrid — Making Energy Data More Visible, Understandable, and Intelligent.