import mysql.connector
import datetime
from tabulate import tabulate
import re
from datetime import timedelta

obj = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Beni@9900',
    database='CLINICALMANAGEMENTSYSTEM'
)

clinic = obj.cursor()

clinic.execute('''
    CREATE DATABASE IF NOT EXISTS CLINICALMANAGEMENTSYSTEM
''')
clinic.execute('''
    CREATE TABLE IF NOT EXISTS LoginInfoTable(
        userid VARCHAR(50) PRIMARY KEY,
        password VARCHAR(50),
        first_name VARCHAR(50),
        last_name VARCHAR(50),
        role VARCHAR(50)
    )
''')
clinic.execute('''
    CREATE TABLE IF NOT EXISTS patient_details(
        op_id INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(50),
        Gender VARCHAR(50),
        Age INT,
        blood_group VARCHAR(50),
        address VARCHAR(50),
        mobile_number BIGINT
    )
''')
clinic.execute('''
    CREATE TABLE IF NOT EXISTS doctor(
        doctor_id INT AUTO_INCREMENT PRIMARY KEY,
        doctor_name VARCHAR(50),
        specification VARCHAR(50),
        consultation_fee DECIMAL(10, 2)
    )
''')
clinic.execute('''
    CREATE TABLE IF NOT EXISTS APPOINTMENT(
        op_id INT,
        doctor_id INT,
        Date DATE,
        time time,
        FOREIGN KEY(op_id) REFERENCES patient_details(op_id),
        FOREIGN KEY(doctor_id) REFERENCES doctor(doctor_id)
    )
''')
clinic.execute('''
    CREATE TABLE IF NOT EXISTS diagnosis(
        op_id INT not null,
        symptoms VARCHAR(50),
        diagnosis VARCHAR(50),
        medicine VARCHAR(50),
        Lab_test VARCHAR(50),
        foreign key(op_id) references patient_details(op_id)
    )
''')


def optionpage():
    while True:
        print("""                --------------------------
                    WELCOME RECEPTIONIST
                  --------------------------

               1. Book Appointment
               2. List of Patients
               3. Search by op_id
               4. search by name
               5. Edit
               6. Log Out""")
        choice = input("Enter your choice from above list: ")
        if choice == '1':
            bookappointment()
        elif choice == '2':
            view()
        elif choice == '3':
            search_by_op_id()
        elif choice == '4':
            search_by_name()
        elif choice == '5':
            edit()
        elif choice == '6':
            main()

        else:
            print("Invalid option")


def view():
    query = "SELECT * FROM patient_details"
    try:
        clinic.execute(query)
        query_result = clinic.fetchall()
        if query_result:
            print(tabulate(query_result,
                           headers=["op_id", "Name", "Gender", "Age", "blood_group", "Address", "mobile_number"]))
        else:
            print("The list is empty")
    except Exception as e:
        print("An error occurred:", e)


def check_patient_existence(name, mobile_number):
    # Assuming `clinic` is your database connection object
    select_query = "SELECT * FROM patient_details WHERE name = %s OR mobile_number = %s"
    clinic.execute(select_query, (name, mobile_number))
    result = clinic.fetchone()
    return result is not None


def viewlist():
    # This function should contain your database connection and cursor initialization.
    pass


def validate_name(name):
    # This function should validate the name format.
    return re.match(r'^[a-zA-Z]+$', name)


def validate_mobile_number(mobile_number):
    # This function should validate the mobile number format.
    return re.match(r'^\d{10}$', mobile_number)


def check_patient_existence(name, mobile_number):
    # This function should check if the patient already exists in the database.
    clinic.execute("SELECT op_id FROM patient_details WHERE Name = %s AND mobile_number = %s", (name, mobile_number))
    op_id = clinic.fetchone()
    return op_id


def validate_age(age):
    try:
        age = int(age)
        if 0 < age < 150:  # Assuming a realistic age range
            return True
        else:
            return False
    except ValueError:
        return False


def is_appointment_available(doctor_id, appointment_date, appointment_time):
    query = "SELECT * FROM APPOINTMENT WHERE doctor_id = %s AND Date = %s AND time = %s"
    clinic.execute(query, (doctor_id, appointment_date, appointment_time))
    existing_appointment = clinic.fetchone()
    return existing_appointment is None


def is_appointment_time_available(doctor_id, appointment_date, appointment_time):
    query = "SELECT * FROM APPOINTMENT WHERE doctor_id = %s AND Date = %s"
    clinic.execute(query, (doctor_id, appointment_date))
    existing_appointments = clinic.fetchall()
    for appointment in existing_appointments:
        if appointment[3] == appointment_time:
            return False
    return True


def validate_blood_group(blood_group):
    # Assuming a simplified validation for blood group (e.g., A+, B-, AB+, O+, etc.)
    valid_blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    return blood_group.upper() in valid_blood_groups


def validate_address(address):
    # You might want to implement more specific validation depending on your requirements
    return len(address) > 0


def convert_to_24_hour_format(time_str):
    # Convert time from 'HH:MM AM/PM' format to 'HH:MM:SS' format
    return datetime.datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M:%S')


def bookappointment():
    global mobile_number
    viewlist()
    query = "SELECT doctor_id, doctor_name, specification FROM doctor"
    clinic.execute(query)
    query_result = clinic.fetchall()
    if query_result:
        print(tabulate(query_result, headers=["doctor_id", "doctor_name", "specification"]))
    else:
        print("The doctor list is empty.")

    while True:
        patient_name = input("Enter the name of the patient: ")
        if validate_name(patient_name):
            break
        else:
            print("Enter a valid name.")

    while True:
        mobile_number = input("Enter patient's mobile number: ")
        if validate_mobile_number(mobile_number):
            break
        else:
            print("Enter a valid 10-digit mobile number.")

    op_id = check_patient_existence(patient_name, mobile_number)
    if op_id:
        print("Patient is existing and thir op_id is:", op_id[0])
        query = "SELECT name, age, gender, blood_group, address, mobile_number FROM patient_details WHERE op_id = %s"
        clinic.execute(query, (op_id[0],))
        patient_details = clinic.fetchone()

        if patient_details:
            name, age, gender, blood_group, address, mobile_number = patient_details
            print("Patient Details:")
            print("----------------")
            print(f"Name:         {name}")
            print(f"Age:          {age}")
            print(f"Gender:       {gender}")
            print(f"Blood Group:  {blood_group}")
            print(f"Address:      {address}")
            print(f"Mobile Number: {mobile_number}")
        while True:
            doctor_id = input("Enter the doctor_id to book the doctor: ")
            query = "SELECT doctor_id FROM doctor WHERE doctor_id = %s"
            clinic.execute(query, (doctor_id,))
            result = clinic.fetchone()

            if result:
                print("Doctor ID is valid.")
                break
            else:
                print("Doctor ID is not valid. Please enter a valid doctor ID.")
        while True:
            appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
            if re.match(r'^\d{4}-\d{2}-\d{2}$', appointment_date):
                try:
                    input_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d").date()
                    current_date = datetime.datetime.now().date()
                    if input_date >= current_date:
                        break
                    else:
                        print("Invalid date. Appointment date should be today or a future date.")
                except ValueError:
                    print("Invalid date format. Please enter in YYYY-MM-DD format.")
            else:
                print("Invalid date format. Please enter in YYYY-MM-DD format.")
        while True:
            appointment_time = input("Enter appointment time (HH:MM AM/PM): ")
            if re.match(r'^\d{2}:\d{2} (AM|PM)$', appointment_time):
                appointment_time = convert_to_24_hour_format(appointment_time)
                if is_appointment_available(doctor_id, appointment_date, appointment_time):
                    if is_appointment_time_available(doctor_id, appointment_date, appointment_time):
                        break
                    else:
                        print("Appointment not available at this time for this doctor on this date.")
                else:
                    print("Appointment already booked for this date and time.")
            else:
                print("Invalid time format. Please enter in HH:MM AM/PM format.")
        insert_query = "INSERT INTO APPOINTMENT(op_id, doctor_id, Date,time) VALUES (%s, %s, %s,%s)"
        try:
            clinic.execute(insert_query, (op_id[0], doctor_id, appointment_date, appointment_time))
            obj.commit()
            print("Appointment successfully booked.")
        except Exception as e:
            obj.rollback()
            print("Error:", e)

        generate_bill = input('''Do you want to generate Bill? 
                                            1. YES
                                            2. NO
                 Enter the Option''')
        while True:
            if generate_bill == "1":
                pay = "SELECT consultation_fee FROM doctor WHERE doctor_id = %s"
                clinic.execute(pay, (doctor_id,))
                consultation_fee = clinic.fetchone()
                if consultation_fee:
                    consultation_fee = float(consultation_fee[0])
                else:
                    consultation_fee = 0  # If consultation fee is not found, set to 0

                # Fetch patient name based on op_id
                clinic.execute("SELECT Name FROM patient_details WHERE op_id = %s", (op_id[0],))
                patient_name = clinic.fetchone()[0]  # Assuming the name is the first column
                # Fetch doctor name based on doctor_id
                clinic.execute("SELECT doctor_name FROM doctor WHERE doctor_id = %s", (doctor_id,))
                doctor_name = clinic.fetchone()[0]  # Assuming the name is the first column

                print(f"Patient name: {patient_name}")
                print(f"Consulted with Dr. {doctor_name}")
                print(f"Consultation fee for the doctor is {consultation_fee:.2f}")  # Formatting to two decimal places
                print(f"The Total fee for the patient is {consultation_fee:.2f}")  # Formatting to two decimal places
                break
                # Fetch consultation fee from the database

            elif generate_bill == "2":
                print("Generate bill later...")
                break
            else:
                print("Enter a valid option.")


    else:
        print("Patient not found.")
        add_patient = input("Do you want to add a new patient? (YES/NO): ")
        if add_patient.upper() == "YES":
            while True:
                name = input("Enter the name of the patient: ")
                if validate_name(name):
                    break
                else:
                    print("Enter a valid name.")

            while True:
                mobile_number = input("Enter patient's mobile number: ")
                if validate_mobile_number(mobile_number):
                    break
                else:
                    print("Enter a valid 10-digit mobile number.")

            while True:
                gender = input("Enter Gender[F/M]: ")
                if gender.upper() in ['F', 'M']:
                    break
                else:
                    print("Invalid gender (F/M)")

            while True:
                age = input("Enter the age: ")
                if validate_age(age):
                    break
                else:
                    print("Enter a valid age.")

            while True:
                blood_group = input("Enter the blood group: ")
                if validate_blood_group(blood_group):
                    break
                else:
                    print("Enter a valid blood group.")

            while True:
                address = input("Enter the Address: ")
                if validate_address(address):
                    break
                else:
                    print("Enter a valid address.")

            clinic.execute("SELECT * FROM patient_details WHERE mobile_number = %s", (mobile_number,))
            existing_contact = clinic.fetchone()
            if existing_contact:
                print("patient with this mobile number already exists.")
                return

            insert_query = ("INSERT INTO patient_details(Name, Age, Gender, blood_group, address, mobile_number) "
                            "VALUES (%s, %s, %s, %s, %s, %s)")
            try:
                clinic.execute(insert_query, (name, age, gender, blood_group, address, mobile_number))
                obj.commit()
                print("Patient details added successfully.")
                op_id = check_patient_existence(name, mobile_number)
                print("Patient op_id:", op_id[0])
            except Exception as e:
                obj.rollback()
                print("Error:", e)
        else:
            return

        doctor_id = input("Enter the doctor_id to book the doctor: ")

        while True:
            appointment_date = input("Enter appointment date (YYYY-MM-DD): ")
            if re.match(r'^\d{4}-\d{2}-\d{2}$', appointment_date):
                try:
                    input_date = datetime.datetime.strptime(appointment_date, "%Y-%m-%d").date()
                    current_date = datetime.datetime.now().date()
                    if input_date >= current_date:
                        break
                    else:
                        print("Invalid date. Appointment date should be today or a future date.")
                except ValueError:
                    print("Invalid date format. Please enter in YYYY-MM-DD format.")
            else:
                print("Invalid date format. Please enter in YYYY-MM-DD format.")
        while True:
            appointment_time = input("Enter appointment time (HH:MM AM/PM): ")
            if re.match(r'^\d{2}:\d{2} (AM|PM)$', appointment_time):
                appointment_time = convert_to_24_hour_format(appointment_time)
                if is_appointment_available(doctor_id, appointment_date, appointment_time):
                    if is_appointment_time_available(doctor_id, appointment_date, appointment_time):
                        break
                    else:
                        print("Appointment not available at this time for this doctor on this date.")
                else:
                    print("Appointment already booked for this date and time.")
            else:
                print("Invalid time format. Please enter in HH:MM AM/PM format.")

        insert_query = "INSERT INTO APPOINTMENT(op_id, doctor_id, Date,time) VALUES (%s, %s, %s,%s)"

        try:
            clinic.execute(insert_query, (op_id[0], doctor_id, appointment_date, appointment_time))
            obj.commit()
            print("Appointment successfully booked.")
        except Exception as e:
            obj.rollback()
            print("Error:", e)

        generate_bill = input('''Do you want to generate Bill? 
                                    1. YES
                                    2. NO
                    Enter the option: ''')
        while True:
            if generate_bill == "1":
                if op_id:
                    registration_fee = 100
                    pay = "SELECT consultation_fee FROM doctor WHERE doctor_id = %s"
                    clinic.execute(pay, (doctor_id,))
                    consultation_fee = clinic.fetchone()
                    if consultation_fee:
                        consultation_fee_value = float(consultation_fee[0])
                        total_payment = registration_fee + consultation_fee_value
                        # Fetch doctor name based on doctor_id
                        clinic.execute("SELECT doctor_name FROM doctor WHERE doctor_id = %s", (doctor_id,))
                        doctor_name = clinic.fetchone()[0]  # Assuming the name is the first column
                        print('''-----------Bill Generated---------------''')
                        print(f"The patient Name is {name}")
                        print(f"Consulted with Dr. {doctor_name}")
                        print("The registration fee is 100")
                        print(f"Consultation Fee is {consultation_fee_value}")
                        print(f"The total Payment is {total_payment}")
                        print("----------------------------------------------")
                        break
            elif generate_bill == "2":
                print("Generate bill later...")
                break
            else:
                print("Enter a valid option.")


def search_by_name():
    while True:
        search_term = input("Enter the name to search: ")
        if search_term.strip():
            break
        else:
            print("Invalid input. Please enter a valid name.")

    query = "SELECT * FROM patient_details WHERE Name LIKE %s"
    clinic.execute(query, ('%' + search_term + '%',))
    query_result = clinic.fetchall()

    if query_result:
        print("Search Results:")
        print(tabulate(query_result,
                       headers=["op_id", "Name", "Gender", "Age", "blood_group", "Address", "Mobile Number"]))
    else:
        print("No patients found matching the search criteria.")


def search_by_op_id():
    while True:
        search_term = input("Enter the op_id to search: ")
        if search_term.strip() and search_term.isdigit():
            break
        else:
            print("Invalid op_id. Please enter a valid op_id.")

    query = "SELECT * FROM patient_details WHERE op_id = %s"
    clinic.execute(query, (search_term,))
    query_result = clinic.fetchall()

    if query_result:
        print("Search Results:")
        print(tabulate(query_result,
                       headers=["op_id", "Name", "Gender", "Age", "blood_group", "Address", "Mobile Number"]))
    else:
        print("No patients found with the provided op_id.")


def edit():
    print('''The area which need to to edited
            1. Address
            2. Mobile number''')
    give = input("Enter the Area to be edited : ")

    if give == '1':
        id = input("Enter the op_id: ")
        select_query = 'SELECT address FROM patient_details WHERE op_id = %s'
        clinic.execute(select_query, (id,))
        query_res = clinic.fetchone()
        if query_res:
            current_address = query_res[0]
            print(f"Current address: {current_address}")
            new_address = input("Enter the new address: ")
            update_query = 'UPDATE patient_details SET address = %s WHERE op_id = %s'
            clinic.execute(update_query, (new_address, id))
            obj.commit()
            print("Address updated successfully.")
        else:
            print("Patient with provided op_id not found.")
    elif give == '2':
        id = input("Enter the op_id: ")
        select_query = 'SELECT mobile_number FROM patient_details WHERE op_id = %s'
        clinic.execute(select_query, (id,))
        query_res = clinic.fetchone()
        if query_res:
            current_number = query_res[0]
            print(f"Current mobile number: {current_number}")
            new_number = input("Enter the new mobile number: ")
            update_query = 'UPDATE patient_details SET mobile_number = %s WHERE op_id = %s'
            clinic.execute(update_query, (new_number, id))
            obj.commit()
            print("Mobile number updated successfully.")
        else:
            print("Patient with provided op_id not found.")
    else:
        print("Invalid option")


import datetime

import datetime


def doc(result1):
    while True:
        current_date = datetime.datetime.now().date()

        print('''       --------------------------
                        WELCOME DOCTOR
                   --------------------------
                   1. Appointments available Today
                   2. Search Patient
                   3. Edit the diagnosis
                   4. Log Out ''')

        choose = input("Enter the option: ")
        if choose == '1':
            select_query = ("""
                SELECT patient_details.op_id, patient_details.name, patient_details.Age, 
                       patient_details.gender, patient_details.blood_group, appointment.time 
                FROM patient_details 
                INNER JOIN appointment ON patient_details.op_id = appointment.op_id 
                WHERE appointment.doctor_id = %s
                AND DATE(appointment.date) = %s

                """)
            clinic.execute(select_query, (result1[0], current_date))
            sel_query = clinic.fetchall()

            if sel_query:
                print("The Appointments Available today:")
                print(tabulate(sel_query, headers=["op_id", "Name", "Age", "Gender", "Blood Group", "Time"]))
            else:
                print("No Appointments Available Today.")
                continue

            valid_op_ids = [appointment[0] for appointment in sel_query]
            while True:
                op_id = input("Enter the op_id for Diagnosis: ")
                try:
                    op_id = int(op_id)  # Convert user input to integer
                    # Check if op_id exists in the list of appointments available today
                    if op_id in valid_op_ids:
                        break  # Break the loop if op_id exists
                    else:
                        print(
                            "The provided op_id is not in the list of appointments available today. Please enter a valid op_id.")
                except ValueError:
                    print("Invalid input. Please enter a valid op_id.")

            query = "SELECT op_id, Name, Gender, Age, blood_group FROM patient_details WHERE op_id = %s"
            clinic.execute(query, (op_id,))
            query_result = clinic.fetchall()
            print('\n')
            if query_result:
                print("----------The Patient Details----------:")
                print(tabulate(query_result, headers=["op_id", "Name", "Gender", "Age", "Blood Group"]))
            else:
                print("Patient with op_id {} not found.".format(op_id))
                continue

            # Check if op_id exists in diagnosis table
            select_diagnosis_query = "SELECT * FROM diagnosis WHERE op_id = %s"
            clinic.execute(select_diagnosis_query, (op_id,))
            previous_diagnosis = clinic.fetchall()
            if previous_diagnosis:
                print("Previous Diagnosis History:")
                print(tabulate(previous_diagnosis, headers=["op_id", "Symptoms", "Diagnosis", "Medicine", "Lab Test"]))
            else:
                print("No previous diagnosis history.")

            symptoms = input("Symptoms for the Patient: ")
            diagnosis = input("Diagnosis for the Patient: ")
            medicine = input("Medicine for the Patient: ")
            print('''----Lab Test----
                        1) Blood Test 
                        2) Urine Test
                        3) X-ray''')
            lab_test = input("Lab Test for the Patient: ")

            insert_query = """
               INSERT INTO diagnosis (op_id, symptoms, diagnosis, medicine, lab_test)
               VALUES (%s, %s, %s, %s, %s)
               """
            clinic.execute(insert_query, (op_id, symptoms, diagnosis, medicine, lab_test))
            obj.commit()
            print("Diagnosis added successfully.")

            # After diagnosis, re-fetch the patient details including diagnosis
            query = """
                SELECT patient_details.op_id, patient_details.Name, patient_details.Age, patient_details.Gender, 
                       appointment.date, diagnosis.symptoms, diagnosis.medicine, diagnosis.lab_test, diagnosis.diagnosis
                FROM patient_details
                INNER JOIN appointment ON patient_details.op_id = appointment.op_id
                LEFT JOIN diagnosis ON patient_details.op_id = diagnosis.op_id
                WHERE (patient_details.name LIKE %s OR patient_details.op_id = %s)
                AND appointment.doctor_id = %s
            """

            try:
                clinic.execute(query, (op_id,))
                query_result = clinic.fetchall()
                print('\n')
                if query_result:
                    print("----------The Patient Details----------:")
                    print(tabulate(query_result,
                                   headers=["op_id", "Name", "Age", "Gender", "Appointment Date", "Symptoms",
                                            "Medicine",
                                            "Lab Test", "Diagnosis"]))
                else:
                    print("Patient with op_id {} not found.".format(op_id))
                    continue
            except Exception as e:
                pass
                # print("An error occurred:", str(e))

        elif choose == '2':
            doctor_id = result1[0]
            search_query = """
                SELECT patient_details.op_id, patient_details.Name, patient_details.Age, patient_details.gender, 
                       appointment.date
                FROM patient_details
                INNER JOIN appointment ON patient_details.op_id = appointment.op_id
                WHERE appointment.doctor_id = %s
                ORDER BY appointment.date DESC
            """
            clinic.execute(search_query, (doctor_id,))
            search_result = clinic.fetchall()
            if search_result:
                print("Previous Patients seen by the Doctor:")
                print(tabulate(search_result, headers=["op_id", "Name", "Age", "Gender", "Appointment Date"]))
                op_id_search = input("Enter the op_id to find the previous history: ")
                if op_id_search:
                    select_diagnosis_query = "SELECT * FROM diagnosis WHERE op_id = %s"
                    clinic.execute(select_diagnosis_query, (op_id_search,))
                    diagnosis_history = clinic.fetchall()
                    if diagnosis_history:
                        print("Diagnosis History for op_id", op_id_search)
                        print(tabulate(diagnosis_history,
                                       headers=["op_id", "symptoms", "diagnosis", "medicine", "lab_test"]))
                    else:
                        print("No diagnosis history found for op_id", op_id_search)
            else:
                print("No previous patients found for this doctor.")
        elif choose == '3':
            select_diagnosis_query = """
                                SELECT patient_details.op_id, patient_details.Name, diagnosis.symptoms, diagnosis.diagnosis
                                FROM patient_details
                                INNER JOIN diagnosis ON patient_details.op_id = diagnosis.op_id"""
            clinic.execute(select_diagnosis_query, )
            diagnosis_history = clinic.fetchall()

            print(tabulate(diagnosis_history,
                           headers=["op_id", "Name", "Symptoms", "Diagnosis"]))
            op_id_edit = input("Enter the op_id to edit diagnosis: ")
            if op_id_edit:
                select_diagnosis_query = "SELECT * FROM diagnosis WHERE op_id = %s"
                clinic.execute(select_diagnosis_query, (op_id_edit,))
                diagnosis_history = clinic.fetchall()

                if diagnosis_history:
                    print("Diagnosis History for op_id", op_id_edit)
                    print(tabulate(diagnosis_history,
                                   headers=["op_id", "symptoms", "diagnosis", "medicine", "lab_test"]))

                    # Let's assume you only want to update the latest diagnosis entry for the given op_id_edit
                    latest_diagnosis = diagnosis_history[-1]
                    symptoms = input("Update Symptoms: ")
                    diagnosis = input("Update Diagnosis: ")
                    medicine = input("Update Medicine: ")
                    lab_test = input("Update Lab Test: ")

                    update_query = """
                                   UPDATE diagnosis 
                                   SET symptoms = %s, diagnosis = %s, medicine = %s, lab_test = %s
                                   WHERE op_id = %s
                                   """
                    clinic.execute(update_query,
                                   (symptoms, diagnosis, medicine, lab_test, op_id_edit))
                    obj.commit()
                    print("Diagnosis updated successfully.")
                else:
                    print("No diagnosis history found for op_id", op_id_edit)
            else:
                print("Invalid input.")
        elif choose == '4':
            print("""             ------------------------
                         LOGGED OUT 
                  -------------------------""")
            main()
            break
        else:
            print("Invalid option. Please choose a valid option.")


# Your main() function should be defined to call the doc() function.
# Ensure the connection to the database is established before calling main().


def login():
    global username
    for i in range(100):
        while True:
            role = input("Enter the role (receptionist/doctor): ")
            if role == "":
                print("This field cannot be empty")
            elif role.lower() not in ['receptionist', 'doctor']:
                print("Please enter 'receptionist' or 'doctor'")
            else:
                break

        while True:
            username = input("Enter the username: ")
            if username == "":
                print("This field cannot be empty")
            else:
                break

        while True:
            password = input("Enter the password: ")
            if password == "":
                print("This field cannot be empty")
            else:
                break

        if role.lower() == "doctor":
            # Check the password for each doctor
            if password == "doctor1":
                doctor_id = 1
            elif password == "doctor2":
                doctor_id = 2
            elif password == "doctor3":
                doctor_id = 3
            else:
                print("Invalid doctor password")
                continue

            # Retrieve doctor details based on doctor_id
            select_query = "SELECT doctor_id FROM doctor WHERE doctor_id=%s "
            clinic.execute(select_query, (doctor_id,))
            result1 = clinic.fetchone()

            # Check login credentials
            select_query = "SELECT * FROM LoginInfotable WHERE role=%s AND userid=%s AND password=%s"
            clinic.execute(select_query, (role, username, password))
            result = clinic.fetchone()
            if result is not None:
                doc(result1)
                break
            else:
                print("Incorrect userid or password")
        elif role.lower() == "receptionist":
            # Check login credentials for receptionist
            select_query = "SELECT * FROM LoginInfotable WHERE role=%s AND userid=%s AND password=%s"
            clinic.execute(select_query, (role, username, password))
            result = clinic.fetchone()
            if result is not None:
                optionpage()
                break
            else:
                print("Incorrect userid or password")


def main():
    while True:
        print("""                                    --------------------
                                WELCOME TO CLINICAL MANAGEMENT SYSTEM
                                    -------------------
                     Choose an option to continue
                     1. Login
                     2. Exit""")
        number = input("Enter a number from above list: ")
        if number == '1':
            login()
            break
        elif number == '2':
            print("""                        ------------------------
                                LOGGED OUT 
                       -------------------------""")
            break
        else:
            print("Invalid choice. Please choose from the options.")


main()

# Close the cursor and database connection
clinic.close()
obj.close()