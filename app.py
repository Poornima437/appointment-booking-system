
import re
import streamlit as st
from pathlib import Path
from datetime import date

from database import (
    ALL_TIMES,
    create_database,
    get_appointments,
    get_booked_times,
    search_appointments,
    save_appointment,
    cancel_appointment,
)
from assistant import get_assistant_response


# -----------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------

st.set_page_config(
    page_title="Appointment Booking Agent",
    page_icon="🏥",
    layout="wide",
)

# Load the existing CSS file
css_path = Path(__file__).parent / "style.css"

if css_path.exists():
    with open(css_path, encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True,
        )

# Initialize the existing database and any required columns
create_database()


# -----------------------------------------
# 2. SESSION STATE
# -----------------------------------------

defaults = {
    "messages": [],
    "toast_message": "",
    "toast_icon": "✅",
    "selected_date": date.today(),
    "selected_time": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

if st.session_state.toast_message:
    st.toast(
        st.session_state.toast_message,
        icon=st.session_state.toast_icon,
    )
    st.session_state.toast_message = ""


# -----------------------------------------
# 3. HELPER FUNCTIONS
# -----------------------------------------

def show_appointment(appointment):
    """Display only non-sensitive appointment information."""

    appointment_id, patient_name, appointment_date, appointment_time = (
        appointment[:4]
    )

    with st.container(border=True):
        st.write(f"**Appointment ID:** {appointment_id}")
        st.write(f"**Patient:** {patient_name}")
        st.write(f"**Date:** {appointment_date}")
        st.write(f"**Time:** {appointment_time}")

        if st.button(
            "Cancel Appointment",
            key=f"cancel_{appointment_id}",
            use_container_width=True,
        ):
            deleted = cancel_appointment(appointment_id)

            if deleted:
                st.session_state.toast_message = (
                    f"Appointment {appointment_id} cancelled."
                )
                st.session_state.toast_icon = "✅"
                st.rerun()
            else:
                st.error("This appointment could not be cancelled.")


def valid_email(email):
    """Perform a basic email-format check."""
    return bool(
        re.fullmatch(
            r"[^@\s]+@[^@\s]+\.[^@\s]+",
            email.strip(),
        )
    )


# -----------------------------------------
# 4. DASHBOARD HEADER
# -----------------------------------------

st.title("🏥 Appointment Booking Agent")
st.caption(
    "Manage patient appointments, check available slots, "
    "and get assistance in one place."
)

appointments = get_appointments()
today = date.today()

today_appointments = [
    item for item in appointments if item[2] == str(today)
]

booked_today = get_booked_times(today)
available_today = len(
    [t for t in ALL_TIMES if t not in booked_today]
)

metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("Total Appointments", len(appointments))

with metric2:
    st.metric("Today's Appointments", len(today_appointments))

with metric3:
    st.metric("Available Slots Today", available_today)

st.divider()


# -----------------------------------------
# 5. THREE-COLUMN DASHBOARD
# -----------------------------------------

left, centre, right = st.columns(
    [1.15, 1.7, 1.1],
    gap="medium",
)


# =========================================
# LEFT PANEL: APPOINTMENTS AND SEARCH
# =========================================

with left:
    st.subheader("📋 Appointments")

    search_name = st.text_input(
        "Search by patient name",
        placeholder="Enter patient name",
        key="appointment_search",
    )

    if search_name.strip():
        displayed_appointments = search_appointments(
            search_name.strip()
        )
        st.caption(
            f"{len(displayed_appointments)} matching appointment(s)"
        )
    else:
        displayed_appointments = get_appointments()
        st.caption(
            f"{len(displayed_appointments)} saved appointment(s)"
        )

    if displayed_appointments:
        for item in displayed_appointments:
            show_appointment(item)
    else:
        st.info("No appointments found.")


# =========================================
# CENTRE PANEL: PATIENT DETAILS AND CHAT
# =========================================

with centre:
    st.subheader("👤 Patient Details")
    st.caption("Enter the patient's information to make a booking.")

    patient_name = st.text_input(
        "Patient name",
        placeholder="Enter full name",
        key="patient_name_input",
    )

    patient_email = st.text_input(
        "Email address",
        placeholder="patient@example.com",
        key="patient_email_input",
    )

    patient_phone = st.text_input(
        "Phone number",
        placeholder="Enter 10-digit mobile number",
        key="patient_phone_input",
    )

    patient_age = st.number_input(
        "Age",
        min_value=1,
        max_value=120,
        value=25,
        step=1,
        key="patient_age_input",
    )

    st.divider()

    st.subheader("💬 Appointment Assistant")
    st.caption(
        "Ask about booking, availability, or existing appointments."
    )

    # Show conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Use a regular input and button to keep the chat in this column
    with st.form("assistant_chat_form", clear_on_submit=True):
        chat_message = st.text_input(
            "Your message",
            placeholder="Try: book appointment",
        )

        send_message = st.form_submit_button(
            "Send",
            use_container_width=True,
        )

    if send_message and chat_message.strip():
        st.session_state.messages.append(
            {"role": "user", "content": chat_message.strip()}
        )

        try:
            response = get_assistant_response(
                chat_message.strip()
            )
        except Exception:
            response = (
                "I couldn't process that request. "
                "Please try again or use the booking panel."
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )
        st.rerun()


# =========================================
# RIGHT PANEL: CALENDAR AND BOOKING
# =========================================

with right:
    st.subheader("📅 Book Appointment")

    appointment_date = st.date_input(
        "Choose a date",
        min_value=date.today(),
        key="booking_date_input",
    )

    booked_times = get_booked_times(appointment_date)

    available_times = [
        time for time in ALL_TIMES
        if time not in booked_times
    ]

    st.write("**Available time slots**")

    if available_times:
        selected_time = st.radio(
            "Select a time",
            options=available_times,
            key="booking_time_input",
            label_visibility="collapsed",
        )
    else:
        selected_time = None
        st.warning(
            "All slots are booked for this date. "
            "Please choose another date."
        )

    st.divider()
    st.subheader("🧾 Booking Summary")

    st.write(
        f"**Patient:** {patient_name.strip() or 'Not entered'}"
    )
    st.write(f"**Date:** {appointment_date}")
    st.write(f"**Time:** {selected_time or 'No slot available'}")

    st.divider()

    book_clicked = st.button(
        "Confirm Booking",
        type="primary",
        use_container_width=True,
        disabled=selected_time is None,
    )

    if book_clicked:
        clean_name = patient_name.strip()
        clean_email = patient_email.strip()
        clean_phone = patient_phone.strip()

        if len(clean_name) < 2:
            st.error("Please enter a valid patient name.")

        elif not valid_email(clean_email):
            st.error("Please enter a valid email address.")

        elif not re.fullmatch(r"\d{10}", clean_phone):
            st.error(
                "Enter a valid 10-digit phone number without country code."
            )

        elif not 1 <= patient_age <= 120:
            st.error("Please enter a valid age.")

        elif appointment_date < date.today():
            st.error("Choose today or a future date.")

        else:
            try:
                success = save_appointment(
                    clean_name,
                    appointment_date,
                    selected_time,
                    patient_email=clean_email,
                    patient_phone=clean_phone,
                    patient_age=int(patient_age),
                )

                if success:
                    st.session_state.toast_message = (
                        "Appointment booked successfully!"
                    )
                    st.session_state.toast_icon = "🎉"

                    st.session_state.toast_message = "Appointment booked successfully!"
                    st.session_state.toast_icon = "🎉"
                    st.rerun()

                else:
                    st.error(
                        "This slot is already booked. "
                        "Please choose another time."
                    )

            except Exception as error:
                st.error(
                    "Unable to save the appointment. "
                    "Check that database.py has been updated "
                    "to support email, phone, and age."
                )
                print(f"Booking error: {error}")


# -----------------------------------------
# 6. FOOTER
# -----------------------------------------

st.divider()
st.caption(
    "Appointment Booking Agent | "
    "Built with Python, Streamlit, and SQLite"
)