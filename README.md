# Delivery Pattern Analytics Platform

## Project Overview

The Delivery Pattern Analytics Platform is a Python-based analytics solution designed to help food delivery companies identify delivery patterns that contribute to SLA (Service Level Agreement) violations during peak hours.

This project demonstrates a production-style Python workflow by separating data ingestion, data processing, and output generation into a modular script. It follows best practices for reproducibility, maintainability, and automation.

---

# Tech Stack

- Python 3.13
- Pandas
- Flask
- Flask SQLAlchemy
- Flask Login
- Flask Migrate

---

# Project Structure

```
SW2627-Python-DeliveryPatternAnalytics/

│
├── app/
│   ├── database/
│   ├── models/
│   ├── routes/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/
│   └── utils/
│
├── data/
│   ├── raw/
│   │   └── deliveries.csv
│   └── processed/
│
├── logs/
│   └── workflow.log
│
├── output/
│   └── processed_deliveries.csv
│
├── scripts/
│   └── delivery_workflow.py
│
├── requirements.txt
├── README.md
├── WORKFLOW.md
└── run.py
```

---

# Setup Instructions

### Clone Repository

```bash
git clone https://github.com/<your-github-username>/SW2627-Python-DeliveryPatternAnalytics.git
```

### Navigate to Project

```bash
cd SW2627-Python-DeliveryPatternAnalytics
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

Git Bash

```bash
source venv/Scripts/activate
```

Windows Command Prompt

```cmd
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Python Workflow

This project follows a simple production workflow consisting of three stages:

### 1. Ingest Data

The workflow reads delivery records from:

```
data/raw/deliveries.csv
```

The `ingest_data()` function is responsible only for loading the data into a Pandas DataFrame.

---

### 2. Process Data

The `process_data()` function performs the business logic by:

- Removing duplicate records
- Comparing delivery time with SLA limits
- Creating an **SLA_Status** column
- Identifying whether a delivery is **On Time** or **Violated**

---

### 3. Output Results

The `output_results()` function saves the processed data to:

```
output/processed_deliveries.csv
```

Execution details are automatically recorded in:

```
logs/workflow.log
```

---

# Running the Workflow

Execute the workflow using:

```bash
python scripts/delivery_workflow.py
```

Successful execution displays:

```
Starting Delivery Workflow...

Processed file saved at:
output/processed_deliveries.csv

Workflow Completed Successfully.
```

---

# Output Files

After execution, the workflow generates:

### Processed Dataset

```
output/processed_deliveries.csv
```

This file contains all delivery records along with the generated **SLA_Status** column.

### Log File

```
logs/workflow.log
```

The log file records workflow execution details, including:

- Workflow started
- Data loaded
- Data processed
- Output generated
- Workflow completed

---

# Features

- Production-style Python script
- Modular workflow using three-function pattern
- CSV data ingestion
- SLA violation detection
- Processed CSV generation
- Logging support
- Well-documented functions with docstrings

---

# Team Workflow

The repository follows a feature-branch workflow.

- Main branch contains stable code.
- New work is developed in feature branches.
- Pull Requests are created before merging.
- Conventional Commit messages are used.

---

# Author

SW2627 – Delivery Pattern Analytics Platform