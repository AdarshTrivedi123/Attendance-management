from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re

app = Flask(__name__)
app.secret_key = "ftygf"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'attendance'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/student', methods=['GET', 'POST'])
def student():
    msg = ''
    cur = mysql.connection.cursor()
    if request.method == 'POST' and 'nm' in request.form and 'cl' in request.form and 'adm' in request.form and 'mail' in request.form and 'pwd' in request.form:
        msg = ''
        nm = request.form['nm']
        cl = request.form['cl']
        admno = request.form['adm']
        mail = request.form['mail']
        pwd = request.form['pwd']
        cur.execute("select* from students where admno=%s", (admno, ))
        mysql.connection.commit()
        acc = cur.fetchone()
        if acc:
            msg = 'Account already exists'
        elif not re.match("^[0-9/_-]*$", admno):
            msg = 'Invalid Admission Number'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', mail):
            msg = 'Invalid E-mail'
        elif not len(pwd) >= 6:
            msg = 'Password must be atleast 6 character long'
        else:
            msg = 'Registered Succesfully'
            cur.execute("insert into students value(%s,%s,%s,%s,%s)",
                        (nm, cl, admno, mail, pwd))
            mysql.connection.commit()
            cur.close()

    return render_template("reg.html", msg=msg)


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        adm = request.form['adm']
        pswd = request.form['pwd']
        cur.execute("select* from students where admno=%s", (adm, ))
        mysql.connection.commit()
        adm_data = cur.fetchall()
        if adm_data:
            cur.execute(
                "select* from students where admno=%s and pwd=%s", (adm, pswd, ))
            mysql.connection.commit()
            check = cur.fetchall()
            if check:
                return redirect(url_for('student_attendance', admno=adm))
            else:
                msg = 'wrong password'
        else:
            msg = 'No such admmission number exists'

    return render_template("login.html", msg=msg)


@app.route('/student_attendance/<admno>')
def student_attendance(admno):
    cur = mysql.connection.cursor()
    cur.execute("select name from students where admno=%s", (admno, ))
    mysql.connection.commit()
    name = cur.fetchone()
    cur = mysql.connection.cursor()
    cur.execute("select date,present,absent from data where admno=%s", (admno, ))
    mysql.connection.commit()
    attendance_data = cur.fetchall()
    return render_template("display.html", data=attendance_data, name=name)


@app.route('/teacher', methods=['GET', 'POST'])
def teacher():
    msg = ''
    cur = mysql.connection.cursor()
    if request.method == 'POST' and 'nm' in request.form and 'tid' in request.form and 'eid' in request.form and 'pwd' in request.form:
        msg = ''
        nm = request.form['nm']
        tid = request.form['tid']
        mail = request.form['eid']
        pwd = request.form['pwd']
        cur.execute("select* from teachers where tid=%s", (tid, ))
        mysql.connection.commit()
        acc = cur.fetchone()
        if acc:
            msg = 'Account already exists'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', mail):
            msg = 'Invalid E-mail'
        elif not len(pwd) >= 6:
            msg = 'Password must be atleast 6 character long'
        else:
            msg = 'Registered Succesfully'
            cur.execute("insert into teachers value(%s,%s,%s,%s)",
                        (tid, nm, mail, pwd))
            mysql.connection.commit()
            cur.close()

    return render_template("regt.html", msg=msg)


@app.route('/logint', methods=['GET', 'POST'])
def logint():
    msg = ''
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        eid = request.form['eid']
        pwd = request.form['pwd']
        cur.execute("select* from teachers where tid=%s", (eid, ))
        mysql.connection.commit()
        tdata = cur.fetchall()
        if tdata:
            cur.execute(
                "select* from teachers where tid=%s and password=%s", (eid, pwd, ))
            mysql.connection.commit()
            check = cur.fetchall()
            if check:
                return redirect(url_for('teacher_attendance'))
            else:
                msg = 'wrong password'
        else:
            msg = 'wrong Employee ID'

    return render_template("logint.html", msg=msg)


# @app.route('/teacher_attendance')
# def teacher_attendance():
#     return render_template("att.html")

@app.route('/teacher_attendance', methods=['GET', 'POST'])
def teacher_attendance():

    if request.method == 'POST' and 'cl' in request.form and 'dt_f' in request.form:

        cl = request.form['cl']
        dt_dummy = request.form['dt_f']
        dt = dt_dummy.replace("-", "")
        choice = request.form['choice']
        # dt_dummy = dt[0:2] + "-" + dt[2:4] + "-" + dt[4:]
        # '-'.join([dt[:2], dt[2:4], dt[4:]])
        if choice == "make":
            cur = mysql.connection.cursor()
            cur.execute(
                "select data.admno from students inner join data on data.admno=students.admno and students.class=%s and  data.date=%s", (cl, dt_dummy, ))
            data_check = cur.fetchall()
            if data_check:
                msg = "Attendance already marked for this date, you can only view attendance"
                return render_template("att.html", msg=msg)

            else:
                cur.execute(
                    "select name, admno from students where class=%s", (cl, ))
                data = cur.fetchall()
                session['data'] = data
                return render_template("list.html", data=data, dt=dt, dt_dummy=dt_dummy)

        else:
            cur = mysql.connection.cursor()
            cur.execute("select students.name,data.admno,data.present from students inner join data on students.admno=data.admno and students.class=%s and data.date=%s", (cl, dt_dummy, ))
            data = cur.fetchall()
            return render_template("view.html", data=data, cl=cl, dt_dummy=dt_dummy)
    msg = ""
    return render_template("att.html", msg=msg)


@app.route('/padata/<int:admno>/<int:dt>', methods=['GET', 'POST'])
def padata(admno, dt):
    if request.method == 'POST' and request.form.get('pa') == 'present':
        return redirect(url_for('present', admno=admno, dt=dt))
    else:
        return redirect(url_for('absent', admno=admno, dt=dt))


@app.route('/present/<admno>/<dt>')
def present(admno, dt):
    cur = mysql.connection.cursor()
    dt_dummy = dt[0:4] + "-" + dt[4:6] + "-" + dt[6:]
    cur.execute("insert into data value(%s,%s,%s,%s)",
                (admno, dt_dummy, "Yes", "No"))
    mysql.connection.commit()
    data = session.get("data")
    return render_template("list.html", data=data, dt=dt, dt_dummy=dt_dummy, ad_done=admno)
    # return redirect(request.referrer)
    # return redirect(url_for('view_list'))


@app.route('/absent/<int:admno>/<dt>')
def absent(admno, dt):
    cur = mysql.connection.cursor()
    dt_dummy = dt[0:4] + "-" + dt[4:6] + "-" + dt[6:]
    cur.execute("insert into data value(%s,%s,%s,%s)",
                (admno, dt_dummy, "No", "Yes"))
    mysql.connection.commit()
    data = session.get("data")
    return render_template("list.html", data=data, dt=dt, dt_dummy=dt_dummy)


app.run(debug=True)
