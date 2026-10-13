
import sqlite3

ALL_TIMES = [
    "09:00 AM",
    "10:00 AM",
    "11:00 AM",
    "02:00 PM",
    "03:00 PM",
]

DATABASE_NAME = str(
    __import__("pathlib").Path(__file__).parent / "appointments.db"
)


# --------------------------------------------------
# 1. DATABASE CONNECTION
# --------------------------------------------------

def get_connection():
    return sqlite3.connect(DATABASE_NAME)


# --------------------------------------------------
# 2. CREATE DATABASE AND UPDATE EXISTING TABLE
# --------------------------------------------------

def create_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                UNIQUE(appointment_date, appointment_time)
            )
        """)

        # Read the columns that already exist
        cursor.execute("PRAGMA table_info(appointments)")
        existing_columns = {
            column[1] for column in cursor.fetchall()
        }

        # Add private fields without deleting old appointments
        new_columns = {
            "patient_email": "TEXT",
            "patient_phone": "TEXT",
            "patient_age": "INTEGER",
        }

        for column_name, column_type in new_columns.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE appointments "
                    f"ADD COLUMN {column_name} {column_type}"
                )

        connection.commit()

    finally:
        connection.close()


# --------------------------------------------------
# 3. SAVE APPOINTMENT
# --------------------------------------------------


def save_appointment(
    patient_name,
    appointment_date,
    appointment_time,
    patient_email="",
    patient_phone="",
    patient_age=None,
):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO appointments (
                patient_name,
                appointment_date,
                appointment_time,
                patient_email,
                patient_phone,
                patient_age
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                patient_name.strip(),
                str(appointment_date),
                appointment_time,
                patient_email.strip(),
                patient_phone.strip(),
                patient_age,
            ),
        )

        connection.commit()
        return True

    except sqlite3.IntegrityError:
        connection.rollback()
        return False

    finally:
        connection.close()


# --------------------------------------------------
# 4. GET ALL APPOINTMENTS
# Only public appointment information is returned
# --------------------------------------------------

def get_appointments():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                patient_name,
                appointment_date,
                appointment_time
            FROM appointments
            ORDER BY appointment_date, appointment_time
        """)

        return cursor.fetchall()

    finally:
        connection.close()


# --------------------------------------------------
# 5. GET BOOKED TIME SLOTS
# --------------------------------------------------

def get_booked_times(appointment_date):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT appointment_time
            FROM appointments
            WHERE appointment_date = ?
            """,
            (str(appointment_date),),
        )

        return [row[0] for row in cursor.fetchall()]

    finally:
        connection.close()


# --------------------------------------------------
# 6. CANCEL APPOINTMENT
# --------------------------------------------------

def cancel_appointment(appointment_id):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM appointments WHERE id = ?",
            (appointment_id,),
        )

        deleted = cursor.rowcount > 0
        connection.commit()

        return deleted

    except sqlite3.Error:
        connection.rollback()
        raise

    finally:
        connection.close()


# --------------------------------------------------
# 7. SEARCH APPOINTMENTS
# Only public appointment information is returned
# --------------------------------------------------

def search_appointments(patient_name):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                patient_name,
                appointment_date,
                appointment_time
            FROM appointments
            WHERE patient_name LIKE ?
            ORDER BY appointment_date, appointment_time
            """,
            (f"%{patient_name.strip()}%",),
        )

        return cursor.fetchall()

    finally:
        connection.close()

if __name__ == "__main__":
    create_database()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(appointments)")
    print("Database columns:")

    for column in cursor.fetchall():
        print(column[1])

    connection.close()