
import streamlit as st
from datetime import date

from database import (
    ALL_TIMES,
    get_appointments,
    get_booked_times,
    search_appointments,
    save_appointment,
)


def get_assistant_response(user_message):
    message = user_message.strip()
    lower_message = message.lower()

    if not message:
        return "Please enter a message."

    if "booking_step" not in st.session_state:
        st.session_state.booking_step = None

    # STEP 1: Collect patient name
    if st.session_state.booking_step == "name":
        patient_name = message

        if len(patient_name) < 2:
            return "Please enter a valid patient name."

        st.session_state.patient_name = patient_name
        st.session_state.booking_step = "date"

        return (
            f"Thank you, {patient_name}!\n\n"
            "Please enter your appointment date in YYYY-MM-DD format.\n"
            "Example: 2026-10-20"
        )

    # STEP 2: Validate appointment date
    if st.session_state.booking_step == "date":
        try:
            appointment_date = date.fromisoformat(message)
        except ValueError:
            return (
                "Invalid date format. Please use YYYY-MM-DD.\n"
                "Example: 2026-10-20"
            )

        if appointment_date < date.today():
            return "That date is in the past. Please choose today or a future date."

        booked_times = get_booked_times(appointment_date)

        available_times = [
            time for time in ALL_TIMES
            if time not in booked_times
        ]

        if not available_times:
            return (
                "All slots are booked on that date. "
                "Please enter another date in YYYY-MM-DD format."
            )

        st.session_state.appointment_date = appointment_date
        st.session_state.booking_step = "time"

        return (
            f"Date selected: {appointment_date}\n\n"
            "Available times:\n"
            + "\n".join(available_times)
            + "\n\nPlease enter one of these times exactly as shown."
        )

    # STEP 3: Validate time and save appointment
    if st.session_state.booking_step == "time":
        appointment_date = st.session_state.get("appointment_date")
        patient_name = st.session_state.get("patient_name")

        if not patient_name or not appointment_date:
            st.session_state.booking_step = "name"
            return (
                "Your booking session has expired. "
                "Please enter the patient's name again."
            )

        appointment_time = message.upper()
        booked_times = get_booked_times(appointment_date)

        available_times = [
            time for time in ALL_TIMES
            if time not in booked_times
        ]

        if appointment_time not in ALL_TIMES:
            return (
                "Please enter a valid time from the available options:\n"
                + "\n".join(available_times)
            )

        if appointment_time in booked_times:
            if not available_times:
                st.session_state.booking_step = "date"
                return "All slots are booked. Please enter another date."

            return (
                "That time is already booked. Choose another available time:\n"
                + "\n".join(available_times)
            )

        success = save_appointment(
            patient_name,
            appointment_date,
            appointment_time,
        )

        if success:
            st.session_state.booking_step = None
            st.session_state.pop("patient_name", None)
            st.session_state.pop("appointment_date", None)

            return (
                "Appointment booked successfully!\n\n"
                f"Patient: {patient_name}\n"
                f"Date: {appointment_date}\n"
                f"Time: {appointment_time}"
            )

        return (
            "This slot could not be booked. It may have just been taken. "
            "Please choose another available time."
        )

    # STEP 4: Handle normal requests
    if lower_message in ["hello", "hi", "hey"]:
        return (
            "Hello! I can help you book, view, search, or cancel appointments.\n\n"
            "Try: book appointment or show appointments."
        )

    if "book" in lower_message or "schedule" in lower_message:
        st.session_state.booking_step = "name"
        return "Let's book an appointment. What is the patient's name?"

    if (
        "show appointments" in lower_message
        or "all appointments" in lower_message
    ):
        appointments = get_appointments()

        if not appointments:
            return "There are no appointments booked yet."

        lines = ["Booked appointments:"]

        for appointment in appointments:
            lines.append(
                f"ID: {appointment[0]}\n"
                f"Patient: {appointment[1]}\n"
                f"Date: {appointment[2]}\n"
                f"Time: {appointment[3]}"
            )

        return "\n\n".join(lines)

    if lower_message.startswith(("search ", "find ", "check ")):
        search_name = message.split(" ", 1)[1].strip()

        if not search_name:
            return "Please enter the patient's name to search."

        results = search_appointments(search_name)

        if not results:
            return f"No appointments found for {search_name}."

        lines = [f"Appointments matching {search_name}:"]

        for appointment in results:
            lines.append(
                f"ID: {appointment[0]} | "
                f"Patient: {appointment[1]} | "
                f"Date: {appointment[2]} | "
                f"Time: {appointment[3]}"
            )

        return "\n\n".join(lines)

    if lower_message.startswith(("cancel", "delete")):
        return (
            "Use the Search Appointments section to find the booking, "
            "then click Cancel Appointment."
        )

    if "thank" in lower_message:
        return "You're welcome!"

    return (
        "I can help you book, view, search, or cancel appointments.\n"
        "What would you like to do?"
    )