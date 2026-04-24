import hashlib, json, csv, os, webbrowser
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__, template_folder='../')

SPECIAL_CHARACTERS = set("!@#$%^&*()-_=+[]{}|:;'<>.,?/~`")
@app.route('/')
def home():
    return render_template('account_pages/login.html')
def password_ok(password: str) -> bool:

    if len(password) < 12:
        return False

    if not any(c.islower() for c in password):
        return False

    if not any(c.isupper() for c in password):
        return False

    if not any(c.isdigit() for c in password):
        return False

    if not any(c in SPECIAL_CHARACTERS for c in password):
        return False

    return True


def dictify(items):
    if type(items) is list:
        dictified = []
        
        for item in items:
            
            if type(item) is dict or type(item) is list:
                item = dictify(item)
            elif hasattr(item,'__dict__'):
                classtype = type(item).__name__
                item = item.__dict__
                item['classtype'] = classtype
            dictified.append(item)
        return dictified
    elif type(items) is dict:
        dictified = {}
        for itemkey in items.keys():
            item = items[itemkey]
            if type(item) is dict or type(item) is list:
                item = dictify(item)
            elif hasattr(item,'__dict__'):
                classtype = type(item).__name__
                item = item.__dict__
                item['classtype'] = classtype
            dictified[itemkey] = item
        return dictified

def undictify(items):
    if type(items) is list:
        undictified = []
        for item in items:
            if type(item) is dict or type(item) is list:
                item = undictify(item)
            try:
                item['classtype']
                obj = True
            except:
                obj = False
            if obj:
                try:
                    classtype = globals()[item['classtype']]
                    item.pop('classtype')
                    itemobj = classtype()
                    for key in item.keys():
                        value = item[key]
                        setattr(itemobj,key,value)
                    item = itemobj
                except:
                    return "error"
            undictified.append(item)
    elif type(items) is dict:
        undictified = {}
        for itemkey in items.keys():
            item = items[itemkey]
            if type(item) is dict or type(item) is list:
                item = undictify(item)
            try:
                item['classtype']
                obj = True
            except:
                obj = False
            if obj:
                try:
                    classtype = globals()[item['classtype']]
                    item.pop('classtype')
                    itemobj = classtype()
                    for key in item.keys():
                        value = item[key]
                        setattr(itemobj,key,value)
                    item = itemobj
                except:
                    return "error"
            undictified[itemkey] = item
    return undictified

def json_dump(file_path,items):
    if not type(items) is dict:
        return False
    try:
        with open(file_path,'r'):
            pass
    except FileNotFoundError:
        create_json(file_path)
    except Exception:
        return False
    items = dictify(items)
    with open(file_path,'w') as file:
        json.dump(items, file)
    return True

def create_json(file_path):
    try:
        with open(file_path,'w') as file:
            file.write('{}')
    except:
        return "error"

def json_pull(file_path):
    try:
        with open(file_path,'r'):
            pass
    except:
        return False
    with open(file_path,'r') as file:
        data = json.load(file)
        data = undictify(data)
    return data


def hash_pw(item: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(item.encode("utf-8"))
    return sha256.hexdigest()


def exists(location, search):
    try:
        with open(location, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if row and row[0] == search:
                    return True
    except:
        return False
    return False

def add_user(username: str, hashed: str) -> None:
    users = json_pull('../docs/user.json')
    users[username] = hashed
    json_dump('../docs/user.json',users)

@app.route('/dashboard')
def dashboard():
    user = request.args.get('user')  # Optional: Pass user data if needed
    return render_template('dashboard/dashboard.html')

@app.route('/incorrect_login')
def incorrect_login():
    return render_template('account_pages/incorrect_login.html')

@app.route('/account_not_option')
def account_not_option():
    return render_template('account_pages/account_not_option.html')


@app.route("/signup", methods=["POST"])
def create_account():
    if request.method == "POST":
        users = json_pull('../docs/accounts.json')
        if not users:
            users = {}
        name = request.form.get('username')
        pw = request.form.get('pw')
        if name in users:
            return render_template('account_pages/account_not_option.html')
        if password_ok(pw)==True:
            add_user(name, hash_pw(pw))
            return redirect(url_for('dashboard/dashboard'))
        
        return render_template('account_pages/password_struggle.html')
    return render_template("signup.html")

@app.route("/login", methods=["POST"])
def login():
    users = json_pull('../docs/accounts.json')
    if not users:
        users = {}
    username = request.form.get('username')
    pw = request.form.get('pw')
    hashed = hash_pw(pw)

    if username in users and users[username] == hashed:
        return render_template('dashboard/dashboard.html')

    return render_template('account_pages/incorrect_login.html')
   


if __name__ == "__main__":
    app.run(debug=True)