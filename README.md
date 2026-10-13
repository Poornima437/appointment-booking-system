# Appointment Booking Agent

## Project Overview

The Appointment Booking Agent is a Python-based application designed to help users manage appointment bookings through a simple interface. It uses a database to store and manage appointment information.

This project demonstrates Python programming, database operations, application interface design, and basic automated testing.

## Features

* Book appointments through the application interface.
* Store appointment information in a local SQLite database.
* Manage appointment data using Python.
* Use a custom CSS stylesheet to improve the interface.
* Test database operations and appointment-saving functionality.

## Technologies Used

* **Python** – Application logic
* **Streamlit** – Web application interface
* **SQLite** – Local database
* **CSS** – Interface styling
* **Git and GitHub** – Version control and project sharing

## Project Structure

```text
AppointmentBookingAgent/
├── app.py
├── assistant.py
├── database.py
├── style.css
├── requirements.txt
├── test_database.py
├── test_save.py
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Poornima437/appointment-booking-system.git
```

### 2. Open the project folder

```bash
cd appointment-booking-system
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

### 4. Activate the virtual environment

On Windows:

```bash
.venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

## Run the Application

Start the application using Streamlit:

```bash
streamlit run app.py
```

The application should open in your browser. If it does not, follow the local URL displayed in the terminal.

## Testing

The project includes test files for database operations and appointment-saving functionality.

Review the test files and run the applicable tests using the appropriate commands for the testing framework configured in the project.

## Learning Objectives

This project helps demonstrate practical experience with:

* Python application development
* SQLite database integration
* Separating application logic into different modules
* Basic interface styling
* Testing and debugging
* Git-based version control

## Author

**Poornima N.**

GitHub: [Poornima437](https://github.com/Poornima437)

## Future Improvements

* Add appointment cancellation and rescheduling.
* Improve input validation and error handling.
* Add appointment search and filtering.
* Enhance automated test coverage.
* Explore deployment for online access.

---

*This project was developed as a hands-on learning project to practice Python application development and database integration.*
