from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import os
import mysql.connector
from twilio.rest import Client
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key_123'  # Change this to a random string in production
app.config['UPLOAD_FOLDER'] = 'uploads'
account_sid = 'AC0e1d195ede94576b82898924fd43a68b'
auth_token = 'ec9d56f48a6b8da079b151dce0fe0952'
client = Client(account_sid, auth_token)

# MySQL database connection
mydb = mysql.connector.connect(
    
    host="localhost",
    user="root",
    password="root",
    database="db"
)
mycursor = mydb.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    mycursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = mycursor.fetchone()

    if user:
        # Successful login
        flash('Login successful!', 'success')
        return redirect(url_for('select_choice'))
    else:
        # Invalid credentials
        flash('Invalid username or password!', 'danger')
        return redirect(url_for('index'))

@app.route('/signup', methods=['GET', 'POST'])
def signingup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        mycursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = mycursor.fetchone()

        if existing_user:
            flash('Username already exists!', 'danger')
        else:
            # Create a new user
            mycursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            mydb.commit()
            flash('Sign up successful! You can now login.', 'success')

        return redirect(url_for('index'))

    return render_template('signup.html')

@app.route('/select-choice', methods=['GET'])
def select_choice():
    return render_template('choice_selection.html')

# Route to handle the form submission
@app.route('/select-choice', methods=['POST'])
def handle_choice():
    choice = request.form.get('choice')
    if choice == 'marks':
        return redirect(url_for('upload'))  # Redirect to the upload page for sending marks
    elif choice == 'informative':
        return redirect(url_for('uploading'))  # Redirect to the informative SMS page
    else:
        # Handle invalid choice
        return "Invalid choice selected"

@app.route('/uploading')
def uploading1():
    return render_template('uploading.html')

@app.route('/uploading', methods=['POST'])
def uploading():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File uploaded successfully', 'success')

        # Extract details from the Excel file
        try:
            df = pd.read_excel(file_path)

            # Get column names from the Excel sheet
            column_names = df.columns.tolist()
            print("Column names extracted from Excel:", column_names)

            # Construct SQL query to create table dynamically
            create_table_query = f"CREATE TABLE IF NOT EXISTS students1 (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join([f'{col} VARCHAR(255)' for col in column_names])})"
            print("Create table query:", create_table_query)

            # Execute SQL query to create table
            mycursor.execute(create_table_query)
            mydb.commit()

            # Insert values into the dynamically created table
            for index, row in df.iterrows():
                # Adjust phone number column if present
                adjusted_row = [value if column_name != 'phone' else '+' + str(value) for column_name, value in row.items()]

                # Construct placeholders dynamically
                placeholders = ', '.join(['%s' for _ in range(len(column_names))])

                # Adjust values accordingly
                values = tuple(adjusted_row)

                insert_query = f"INSERT INTO students1 ({', '.join(column_names)}) VALUES ({placeholders})"
                print("Insert query:", insert_query)

                mycursor.execute(insert_query, values)
                mydb.commit()

            flash('Data inserted into dynamically created MySQL table successfully', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

        return redirect(url_for('send_sms1'))

    return render_template('uploading.html')

@app.route('/')
def index3():
    return render_template('send_sms1.html')

@app.route('/send-sms1')
def send_sms1():
    
    try:
        # Fetch column names from the students table
        # Fetch column names from the students table
        mycursor.execute("SHOW COLUMNS FROM students1")
        columns = [column[0] for column in mycursor.fetchall()]

        # Exclude 'id' and 'phone' columns from subject names
        subjects = [col for col in columns if col not in ['id', 'phone']]

        # Query students from MySQL table
        mycursor.execute("SELECT * FROM students1")
        students = mycursor.fetchall()

        # Send SMS messages to each student
        for student in students:
            # Convert the tuple to a dictionary for easier access
            student_dict = {columns[i]: student[i] for i in range(len(columns))}
            excluded_subjects = ['name']  # Specify the subjects you want to exclude

            # Construct message dynamically based on column names (subjects)
            message = f"Dear parent,\n"
            for subject in subjects:
                if subject != 'name' or subject not in excluded_subjects and student_dict[subject] is not None:
                    message += f"{student_dict[subject]}\n"
            
            try:
                client.messages.create(
                    to=student_dict['phone'],
                    from_='+12242796481',
                    body=message
                )
                print(f"Message sent successfully to {student_dict['phone']}")
            except Exception as e:
                print(f"Failed to send message to {student_dict['phone']}: {str(e)}")


        flash('SMS messages sent successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('index2'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload')
def upload1():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.url)
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        flash('File uploaded successfully', 'success')

        # Extract details from the Excel file
        try:
            df = pd.read_excel(file_path)

            # Get column names from the Excel sheet
            column_names = df.columns.tolist()
            print("Column names extracted from Excel:", column_names)

            # Construct SQL query to create table dynamically
            create_table_query = f"CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join([f'{col} VARCHAR(255)' for col in column_names])})"
            print("Create table query:", create_table_query)

            # Execute SQL query to create table
            mycursor.execute(create_table_query)
            mydb.commit()

            # Insert values into the dynamically created table
            for index, row in df.iterrows():
                # Adjust phone number column if present
                adjusted_row = [value if column_name != 'phone' else '+' + str(value) for column_name, value in row.items()]

                # Construct placeholders dynamically
                placeholders = ', '.join(['%s' for _ in range(len(column_names))])

                # Adjust values accordingly
                values = tuple(adjusted_row)

                insert_query = f"INSERT INTO students ({', '.join(column_names)}) VALUES ({placeholders})"
                print("Insert query:", insert_query)

                mycursor.execute(insert_query, values)
                mydb.commit()

            flash('Data inserted into dynamically created MySQL table successfully', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')

        return redirect(url_for('send_sms'))

    return render_template('upload.html')



# Route to render the upload file form
@app.route('/')
def index2():
    return render_template('send_sms.html')

@app.route('/send-sms')
def send_sms():
    try:
        # Fetch column names from the students table
        # Fetch column names from the students table
        mycursor.execute("SHOW COLUMNS FROM students")
        columns = [column[0] for column in mycursor.fetchall()]

        # Exclude 'id' and 'phone' columns from subject names
        subjects = [col for col in columns if col not in ['id', 'phone']]

        # Query students from MySQL table
        mycursor.execute("SELECT * FROM students")
        students = mycursor.fetchall()

        # Send SMS messages to each student
        for student in students:
            # Convert the tuple to a dictionary for easier access
            student_dict = {columns[i]: student[i] for i in range(len(columns))}
            excluded_subjects = ['name']  # Specify the subjects you want to exclude

            # Construct message dynamically based on column names (subjects)
            message = f"Dear parent, your ward {student_dict['name']} marks:\n"
            for subject in subjects:
                if subject != 'name' or subject not in excluded_subjects and student_dict[subject] is not None:
                    message += f"{subject}: {student_dict[subject]}\n"
            
            try:
                client.messages.create(
                    to=student_dict['phone'],
                    from_='+12242796481',
                    body=message
                )
                print(f"Message sent successfully to {student_dict['phone']}")
            except Exception as e:
                print(f"Failed to send message to {student_dict['phone']}: {str(e)}")


        flash('SMS messages sent successfully', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('index2'))


if __name__ == '__main__':
    app.run(debug=True)
