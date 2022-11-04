from flask import Flask, render_template,request
import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=fbd88901-ebdb-4a4f-a32e-9822b9fb237b.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32731;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=brd83146;PWD=86sieylZYORbSY3i",'','')

app = Flask(__name__) 
 
@app.route('/') 

def index():  
    return render_template('index.html') 

@app.route('/home', methods=['POST','GET']) 

def home():  
    
    name = request.form['uname']
    password = request.form['password']
    sql = "SELECT * FROM user WHERE username=? and password=?"
    stmt = ibm_db.prepare(conn,sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.bind_param(stmt,2,password)
    ibm_db.execute(stmt)

    account = ibm_db.fetch_assoc(stmt)

    if account:
        #app.logger.info(account)
        return render_template('home.html' ,x=account)
    else:
        msg="No userfound"
        return render_template('/index.html', msg = msg) 

@app.route("/register",)

def register():
    return render_template('register.html')  

# API calls
@app.route("/reg", methods=['POST'])

def reg():

        uname = request.form['uname']
        name = request.form['name']
        password = request.form['password']
        email = request.form['email']
        sql = "insert into user (username,password,name,email) values (?,?,?,?)"
        stmt = ibm_db.prepare(conn,sql)
        ibm_db.bind_param(stmt,1,uname)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.bind_param(stmt,3,name)
        ibm_db.bind_param(stmt,4,email)
        
        ibm_db.execute(stmt)

        if(stmt):
            return render_template("index.html")
        else:
            return render_template("resister.html")
            
if __name__ =='__main__':  
    app.run(debug = True)  