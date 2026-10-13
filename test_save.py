from database import create_database,save_appointment

create_database()

result = save_appointment(
    "test patient ",
    "2026-10-20",
    "10:00 AM"
)
if result:
    print("appointment saved successfully ")
else:
    print("this time slot is already booked ")


    