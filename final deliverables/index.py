from glob import escape
from flask import Flask, render_template, session, request, redirect, url_for
import ibm_db
from datetime import date
from datetime import datetime

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=brd83146;PWD=86sieylZYORbSY3i",'','')

app = Flask(__name__)
app.secret_key = 'name'
# url routing

@app.route('/')
def index():
    if 'name' in session:
        return redirect('home')
    else:
        return render_template('index.html',m="")

@app.route('/login', methods=['POST','GET'])
def log():
    uname = request.form['username']
    password = request.form['password']
    account = login(uname,password)
    if account:
        return redirect(url_for('home'))
    else: 
        return render_template('index.html',m="* Invalid Credintials")

@app.route('/addacc')
def addacc():
    return render_template('addacc.html')

@app.route('/home')
def home():
    if 'name' in session:
        addinc()
        sql = "select expense from expenses where username=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,session['name'])
        ibm_db.execute(stmt)
        expense = ibm_db.fetch_assoc(stmt)
        expense = expense['EXPENSE']
        session['expense'] = expense
        if 'income' in session: 
            return render_template('home.html',tra=transactions())
        else:
            return redirect('addacc')
    else:
        return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html',msg="") 

@app.route('/credit')
def credit():
    if 'name' in session:
        return render_template('credit.html')
    else:
        return redirect(url_for('index'))

@app.route('/debit')
def debit():
    if 'name' in session:
        return render_template('debit.html')
    else:
        return redirect(url_for('index'))

@app.route('/changepass')
def changepass():
    if 'name' in session:
        return render_template('changepass.html')
    else:
        return redirect(url_for('index'))

@app.route('/transactions')
def transactionsfull():
    if 'name' in session:
        transs = tran()
        return render_template('transactions.html',tra =transs )
    else:
        return redirect(url_for('index'))

# API call
#login
def login(name,password):
    sql = "SELECT * FROM users WHERE username=? and password=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.bind_param(stmt,2,password)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    if account:
        session['name'] = name
        return account
    else:
        return 0

#logout
@app.route('/logout')
def logout():
    session.pop('name',None)
    session.pop('income',None)
    return redirect(url_for('index'))


# new user registration
@app.route('/newuser', methods=['post','GET'])
def reg():
    uname = request.form['uname']
    name = request.form['name']
    password = request.form['password']
    email = request.form['email']
    sql = "select * from users where username=?"
    stmt  = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,uname)
    ibm_db.execute(stmt)
    user = ibm_db.fetch_assoc(stmt)
    if user:
        return render_template('/register.html',msg="* Username exists")
    
    sql = "select * from users where email=?"
    stmt  = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    user = ibm_db.fetch_assoc(stmt)
    if user:
        return render_template('/register.html', msg="* Email exists")
        
    sql = "insert into users (username,password,name,email) values (?,?,?,?)"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,uname)
    ibm_db.bind_param(stmt,2,password)
    ibm_db.bind_param(stmt,3,name)
    ibm_db.bind_param(stmt,4,email)
    ibm_db.execute(stmt)
    return redirect(url_for('index'))
  
# checking for new user  
def addinc():
    sql1= "SELECT * FROM income WHERE username=?"
    stmt = ibm_db.prepare(conn,sql1)
    ibm_db.bind_param(stmt,1,session.get('name'))
    ibm_db.execute(stmt)
    inc = ibm_db.fetch_assoc(stmt)
    if inc:
        session['income'] = inc['BALANCE']
    else:
        return redirect(url_for('addacc'))

# inserting income and balance for new user
@app.route('/addincome', methods=['POST'] )
def addin():
    income = request.form['income']
    name = request.form['uname']
    balance = request.form['balance']
    sql = "insert into income (username,income,balance) values (?,?,?)"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.bind_param(stmt,2,income)
    ibm_db.bind_param(stmt,3,balance)
    ibm_db.execute(stmt)
    session['income'] = balance

    #adding expense data
    sql = "insert into expenses (username,expense) values (?,'0')"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.execute(stmt)
    return redirect(url_for('home'))

#addding credit 
@app.route('/addcredit', methods=['POST','GET'])
def addcredit():
    amount = request.form['amount']
    reason = request.form['reason']
    sql = "insert into transactions (username,reason,amount,type,date,time) values (?,?,?,'credit',?,?)"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['name'])
    ibm_db.bind_param(stmt,3,amount)
    ibm_db.bind_param(stmt,2,reason)
    ibm_db.bind_param(stmt,4,date.today())
    tt = datetime.now()
    time = tt.strftime("%H:%M:%S")
    ibm_db.bind_param(stmt,5,time)
    ibm_db.execute(stmt)
    #updating balance after credit
    acc = int(amount)
    new_var = session['income']
    balance =  int(new_var) + acc
    sql = "update INCOME set BALANCE=? where USERNAME=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,balance)
    ibm_db.bind_param(stmt,2,session['name'])
    ibm_db.execute(stmt)
    
    return redirect(url_for('credit'))

#changing password
@app.route('/change', methods=['POST','GET'])
def chanpass():
    oldpass = request.form['oldpass']
    newpass = request.form['newpass']
    sql = "select password from users where username=?" 
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['name'])
    ibm_db.execute(stmt)
    password = ibm_db.fetch_assoc(stmt)
    password = password['PASSWORD']
    if (password == oldpass):
        sql = "update users set password=? where username=?"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,newpass)
        ibm_db.bind_param(stmt,2,session['name'])
        ibm_db.execute(stmt)
        return redirect(url_for('home'))
    else:
        return render_template('changepass.html',msg = "old password does not match")

#adding debit 
@app.route('/adddebit', methods=['POST','GET'])
def adddebit():
    amount = request.form['amount']
    reason = request.form['reason']
    sql = "insert into TRANSACTIONS (username,reason,amount,type,date,time) values (?,?,?,'debit',?,?)"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['name'])
    ibm_db.bind_param(stmt,3,amount)
    ibm_db.bind_param(stmt,2,reason)
    ibm_db.bind_param(stmt,4,date.today())
    tt = datetime.now()
    time = tt.strftime("%H:%M:%S")
    ibm_db.bind_param(stmt,5,time)
    ibm_db.execute(stmt)

    #updating balance after debit
    acc = int(amount)
    new_var = session['income']
    balance =  int(new_var) - acc
    sql = "update INCOME set BALANCE=? where USERNAME=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,balance)
    ibm_db.bind_param(stmt,2,session['name'])
    ibm_db.execute(stmt)
    session['income'] = balance
     

    # updating debit amount
    sql = "select expense from expenses where username=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,session['name'])
    ibm_db.execute(stmt)
    expense = ibm_db.fetch_assoc(stmt)
    expense = expense['EXPENSE']
    expense = expense + acc
    sql = "update expenses set expense=? where username=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,expense)
    ibm_db.bind_param(stmt,2,session['name'])
    ibm_db.execute(stmt)
    session['expense']=expense
    return redirect(url_for('debit'))   

# transaction details
def transactions():
    t=[]
    sql= f"select * from TRANSACTIONS where username='{escape(session['name'])}'"
    stmt=ibm_db.exec_immediate(conn,sql)
    trans = ibm_db.fetch_assoc(stmt)
    a=1
    while trans != False and a<6:
        t.append(trans)
        trans = ibm_db.fetch_assoc(stmt)
        a +=1
    return t

def tran():
    t=[]
    sql= f"select * from TRANSACTIONS where username='{escape(session['name'])}'"
    stmt=ibm_db.exec_immediate(conn,sql)
    trans = ibm_db.fetch_assoc(stmt)
    while trans != False:
        t.append(trans)
        trans = ibm_db.fetch_assoc(stmt)
    return t

if __name__ == '__main__':
    app.run(debug=True,use_reloader=True)