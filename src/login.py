import hashlib, json,csv

SPECIAL_CHARACTERS = set("!@#$%^&*()-_=+[]{}|:;'<>.,?/~`")

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
                except KeyError:
                    print(f'The class {item['classtype']} is not imported into helper.py! Import it at the top of helper.py to make loading work properly!')
                except Exception as e:
                    print(f'Unknown error when loading object! {e}')
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
                except KeyError:
                    print(f'The class {item['classtype']} is not imported into helper.py! Import it at the top of helper.py to make loading work properly!')
                except Exception as e:
                    print(f'Unknown error when loading object! {e}')
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
        print('Directory does not exist!')

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
    except FileNotFoundError:
        print("file does not exist.")
    except Exception:
        print("error reading file")
    return False

def add_user(username: str, hashed: str) -> None:
    users = json_pull('documents/user.json')
    users[username] = hashed
    json_dump('documents/user.json',users)

def create_account(name,pw):
        ok = password_ok(pw)
        add_user(name, hash_pw(pw))
        print("Account created.")
        return name
    
def login():
    while True:
        users = json_pull('documents/user.json')
        name =  input("What is your username? ").strip()
        pw =  input("What is your password? ")
        hashed = hash_pw(pw)

        for u in users.keys():

            if u == name and users[u] == hashed:
                print("Login successful.")
                return name
        print("Invalid username or password.")


def goal_get():
    good=False
    while True:
        try:
            goal = float( input(f"What do you want to set your goal too?",wrong=good).strip())
            break
        except:
            good=True
    return [goal, 0]


def new_goal_progress(goal):
    good=False
    while True:
        try:
            progress = float( input(f"What progress have you made towards your goal?",wrong=good).strip())
            break
        except:
            good=True
    new_progress = progress + goal[1]
    return [goal[0], new_progress]
