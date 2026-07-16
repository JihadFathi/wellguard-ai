# WellGuard AI - Predictive Maintenance System

WellGuard AI is an intelligent predictive maintenance system for Electric Submersible Pumps (ESPs) operating in oil wells. It utilizes sensor data to predict pump failures, calculate a Pump Health Index (PHI), estimate Remaining Useful Life (RUL), and generate PDF analysis reports.

## Project Structure
- `preprocessing/`: Module for cleaning, feature engineering, and labeling raw data.
- `training/`: Machine learning models training, cross-validation, and hyperparameter tuning.
- `prediction/`: Core inference engine, PHI computation, RUL estimation, and PDF reporting.
- `ui/`: Multi-page Streamlit application.
- `tests/`: Automated unit testing scripts.

## Installation
Ensure you have an active Anaconda environment or Python environment, then run:
```bash
pip install -r requirements.txt
```

## Running the Web Dashboard
```bash
streamlit run ui/app.py
```

## Running Tests
```bash
pytest tests/
```
