# DBMS Python GUI Interface

## Description
This project is a DBMS interface built using Python for my CP363 Assignment 10.

## Installation

To run this project locally, you need to install the required dependencies and set up the environment.

### Prerequisites
- Python 3.x
- `mysql-connector`
- `tkinter`

### Steps to Install

1. **Clone the Repository:**
   Clone this repository to your local machine using:
   ```bash
   git clone https://github.com/emaadq/DBMSInterface.git

2. **Setup a Virtual environment**
  Create a virtual environment to manage dependencies
'''bash
python -m venv .venv

3. **Activate the virtual environment**
On Windows
'''bash
.venv\Scripts\Activate
On MacOS
'''bash
source .venv/bin/activate

4. **Install dependencies (We used mysql-connector and tkinter)
   '''bash
   pip install mysql-connector tkinter

5. **Finally, run the application**
   '''bash
   python main.py

## Notes
- You need a functioning MySQL Database setup on MySQL Workbench to properly run this project; it will connect to your local server
- Modify the database connection in main.py to your local MySQL setup if you are trying to run it yourself


