from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.Config')
app.secret_key = "automotive_secret_key"

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# In-memory storage
teachers_list = [
    {"id": 1, "fullname": "Abebe Kebede", "username": "abebe_auto", "password": "password123"}
]

students_list = [
    {"id": 1, "fullname": "Kebede Tadesse", "username": "kebede_s", "id_no": "ETS001", "password": "password123"}
]

materials_list = []
exams_list = []
assignments_list = []
submissions_list = []
chats_list = []  # ለቻት ሲስተም የሚሆን ማከማቻ
cheating_reports = []

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'Admin' and password == 'Admin123':
            session['user'] = 'Admin'
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard'))
        
        for teacher in teachers_list:
            if teacher['username'] == username and teacher['password'] == password:
                session['user'] = teacher['fullname']
                session['role'] = 'teacher'
                return redirect(url_for('teacher_dashboard'))
        
        for student in students_list:
            if student['username'] == username and student['password'] == password:
                session['user'] = student['fullname']
                session['role'] = 'student'
                session['username'] = student['username']
                return redirect(url_for('student_dashboard'))
            
        flash('Invalid username or password!', 'danger')
            
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if fullname and username and password:
            teachers_list.append({
                "id": len(teachers_list) + 1,
                "fullname": fullname,
                "username": username,
                "password": password
            })
            return redirect(url_for('admin_dashboard'))
            
    return render_template('admin_dashboard.html', teachers=teachers_list)

@app.route('/admin/delete-teacher/<int:teacher_id>')
def delete_teacher_route(teacher_id):
    global teachers_list
    teachers_list = [t for t in teachers_list if t['id'] != teacher_id]
    return redirect(url_for('admin_dashboard'))

@app.route('/teacher', methods=['GET', 'POST'])
def teacher_dashboard():
    if session.get('role') != 'teacher':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        
        # 1. Add Single Student
        if form_type == 'single_student':
            students_list.append({
                "id": len(students_list) + 1,
                "fullname": request.form.get('fullname'),
                "username": request.form.get('username'),
                "id_no": request.form.get('id_no'),
                "password": request.form.get('password')
            })
            
        # 2. Excel Bulk Upload with Default Password
        elif form_type == 'excel_student':
            default_pass = request.form.get('default_password', '123456')
            file = request.files.get('excel_file')
            if file and file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                try:
                    df = pd.read_excel(filepath)
                    for _, row in df.iterrows():
                        students_list.append({
                            "id": len(students_list) + 1,
                            "fullname": str(row.get('Full Name', 'N/A')),
                            "username": str(row.get('Username', 'N/A')),
                            "id_no": str(row.get('ID No', 'N/A')),
                            "password": str(row.get('Password', default_pass))
                        })
                except Exception as e:
                    print(f"Excel error: {e}")

        # 3. Upload Materials & Assignments with Deadline
        elif form_type == 'material':
            deadline_str = request.form.get('deadline') # format: YYYY-MM-DDTHH:MM
            materials_list.append({
                "title": request.form.get('title'),
                "youtube": request.form.get('youtube'),
                "deadline": deadline_str
            })

        # 4. Host Exam
        elif form_type == 'exam':
            exams_list.append({
                "title": request.form.get('exam_title'),
                "password": request.form.get('exam_password'),
                "duration": request.form.get('duration'),
                "passing_score": request.form.get('passing_score'),
                "grade_view": request.form.get('grade_view') == 'on',
                "screen_timeout": request.form.get('screen_timeout') == 'on'
            })
            
        # 5. Teacher Chat Reply
        elif form_type == 'send_chat':
            message = request.form.get('message')
            receiver = request.form.get('receiver')
            if message:
                chats_list.append({
                    "sender": session.get('user'),
                    "receiver": receiver,
                    "message": message,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
            
        return redirect(url_for('teacher_dashboard'))
        
    return render_template('teacher_dashboard.html', students=students_list, exams=exams_list, materials=materials_list, submissions=submissions_list, cheating_reports=cheating_reports, chats=chats_list)

@app.route('/teacher/delete-student/<int:student_id>')
def delete_student_route(student_id):
    global students_list
    students_list = [s for s in students_list if s['id'] != student_id]
    return redirect(url_for('teacher_dashboard'))

@app.route('/student', methods=['GET', 'POST'])
def student_dashboard():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        action_type = request.form.get('action_type')
        
        # Student submitting assignment with Deadline Validation
        if action_type == 'submit_assignment':
            material_title = request.form.get('material_title')
            selected_material = next((m for m in materials_list if m['title'] == material_title), None)
            
            is_expired = False
            if selected_material and selected_material.get('deadline'):
                try:
                    deadline_dt = datetime.strptime(selected_material['deadline'], '%Y-%m-%dT%H:%M')
                    if datetime.now() > deadline_dt:
                        is_expired = True
                except Exception:
                    pass

            if is_expired:
                flash('የአሳይመንት ማብቂያ ጊዜ (Deadline) አልፏል! ማስተካከል አይቻልም፣ ተዘግቷል።', 'danger')
            else:
                sub_file = request.files.get('assignment_file')
                if sub_file:
                    submissions_list.append({
                        "student": session.get('user'),
                        "filename": sub_file.filename,
                        "assignment_title": material_title
                    })
                    flash('አሳይመንቱ በተሳካ ሁኔታ ተልኳል!', 'success')

        # Student Chat Message
        elif action_type == 'send_chat':
            message = request.form.get('message')
            receiver = request.form.get('receiver', 'Abebe Kebede')
            if message:
                chats_list.append({
                    "sender": session.get('user'),
                    "receiver": receiver,
                    "message": message,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
            
    return render_template('student_dashboard.html', exams=exams_list, materials=materials_list, chats=chats_list)

@app.route('/change-password', methods=['POST'])
def change_password():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    username = session.get('username')
    
    for student in students_list:
        if student['username'] == username:
            if student['password'] == current_pass:
                student['password'] = new_pass
                flash('ይለፍ ቃል በተሳካ ሁኔታ ተቀይሯል!', 'success')
            else:
                flash('የአሁኑ ይለፍ ቃል ትክክል አይደለም!', 'danger')
            break
            
    return redirect(url_for('student_dashboard'))

@app.route('/submit-exam', methods=['POST'])
def submit_exam():
    if session.get('role') == 'student':
        student_name = session.get('user', 'Unknown Student')
        cheating_reports.append({
            "student": student_name,
            "reason": "ተማሪው ፈተናውን አጠናቆ ወይም አስረክቧል።"
        })
        flash('ፈተናው በተሳካ ሁኔታ ተልኳል!', 'success')
    return redirect(url_for('student_dashboard'))

@app.route('/auto-submit-exam', methods=['POST'])
def auto_submit_exam():
    if session.get('role') == 'student':
        student_name = session.get('user', 'Unknown Student')
        cheating_reports.append({
            "student": student_name,
            "reason": "ስክሪን በመቀነስ ወይም ሌላ አፕ በመክፈት ፈተናውን ለማጭበርበር ሙከራ ተደርጓል።"
        })
    return "Submitted", 200

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)