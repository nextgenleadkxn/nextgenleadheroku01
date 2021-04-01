import psycopg2
from flask import Flask, request, render_template
from flask_restful import Api
from sqlalchemy import Column, String, Integer, Date, BOOLEAN #data types in python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from collections import OrderedDict

app = Flask(__name__, template_folder='templates')
api = Api(app)

Base = declarative_base()
database_url = "postgres://vkhablomrjnmnm:d9ed7e9f184d6c50baecfb232f1b7f48d106d70ce7b0f2121ad113e56a4ad030@ec2-52-45-73-150.compute-1.amazonaws.com:5432/d2ccvk1nmv202o"

# disable sqlalchemy pool using NullPool as by default Postgres has its own pool
engine = create_engine(database_url, echo=True, poolclass=NullPool)

conn = engine.connect()

Session = sessionmaker(bind=engine)
session = Session()
print("session -> {}".format(session))


class PersonalInfo(Base):
    __tablename__ = 'personalinfo'
    EmpId = Column("empid", String, primary_key=True)
    Name = Column("name", String)
    Age = Column("age", Integer)
    MaritalStatus = Column("maritalstatus", String)
    DOB = Column("dob", Date)


class FinancialInfo(Base):
    __tablename__ = 'financialinfo'
    EmpId = Column("empid", String, primary_key=True)
    Salary = Column("salary", Integer)
    BankName = Column("bankname", String)
    BankAccountNumber = Column("bankaccountnumber", Integer)
    PanCard = Column("pancard", String)
    IFSCCode = Column("ifsccode", String)


class Department(Base):
    __tablename__ = 'department'
    EmpId = Column("empid", String, primary_key=True)
    DepartmentName = Column("departmentname", String)
    SubDepartmentName = Column("subdepartmentname", String)


class EmployeeView(Base):
    __tablename__ = 'employee'
    emp_id = Column("empid", String, primary_key=True)
    name = Column("name", String)
    age = Column("age", Integer)
    marital_status = Column("maritalstatus", String)
    dob = Column("dob", Date)
    salary = Column("salary", Integer)
    bank_name = Column("bankname", String)
    bank_account_number = Column("bankaccountnumber", Integer)
    pan_card = Column("pancard", String)
    ifsccode = Column("ifsccode", String)
    department_name = Column("departmentname", String)
    sub_department_name = Column("subdepartmentname", String)


class User(Base):
    __tablename__ = 'login'
    username = Column("username", String, primary_key=True)
    password = Column("password", )


@app.route('/', methods=['GET'])
def home():
    Empid = request.args.get("empid")
    result = session.query(PersonalInfo, FinancialInfo, Department).filter(PersonalInfo.EmpId == Empid).all()
    result = [item.__dict__ for item in result[0]]
    for item in result:
        item.pop('_sa_instance_state')
    return str("result")


@app.route('/view', methods=['GET'])
def view():
    Emp_id = request.args.get("empid")
    result = session.query(EmployeeView).filter(EmployeeView.emp_id == Emp_id).all()
    result = [item.__dict__ for item in result]
    print("result: {}".format(result))
    for item in result:
        item.pop('_sa_instance_state')
    return str(result)


# view table helps in reduce in response time.
# with view table we can get data from different table into 1 table
@app.route('/view1', methods=['GET'])
def view1():
    Emp_id = request.args.get("empid")
    result = session.query(EmployeeView).filter(EmployeeView.emp_id == Emp_id).all()
    result = [item.__dict__ for item in result]
    result1 = OrderedDict(result[0])
    print(result1)
    print("result: {}".format(result))
    del result1['_sa_instance_state']
    return str(result1)


@app.route('/viewall', methods=['GET'])
def viewall():
    Emp_id = request.args.get("empid")
    result = session.query(EmployeeView).order_by(EmployeeView.dob.desc()).all()
    result = [item.__dict__ for item in result]
    for item in result:
        item.pop('_sa_instance_state')
    return str(result)


# order by dict keys for one nested dict in list
@app.route('/viewall1', methods=['GET'])
def viewall1():
    Emp_id = request.args.get("empid")
    result = session.query(EmployeeView).all()
    result = [item.__dict__ for item in result]
    for item in result:
        item.pop('_sa_instance_state')
    for n in result.count(dict):
        result = dict(sorted(result[n].items()))
    return str(result)


@app.route('/signup', methods=['GET'])
def signup():
    return render_template('index.html')


@app.route('/signup', methods=['POST'])
def getvalues():
    if request.form['password'] == request.form['confirm password']:
        record = User(username=request.form['username'], password=request.form['password'])
        session.add_all([record])
        session.commit()
        session.close()
        return ("signup successful")
    elif request.form['password'] != request.form['confirm password']:
        return ("password and confirm password didn't match")


@app.route('/login', methods=['GET'])
def login1():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if session.query(User).filter(User.username == username and User.password == password):
        return str("login successful")
    else:
        return ("invalid username/ password")


if __name__ == "__main__":
    app.run(debug=True)
