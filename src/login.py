#WG_CP2 Login
#import helper 
import hashlib

#dictify function
def dictify(items):
    if type(items) is list:
        dictified = []
        #loop through given dictionary or list
        for item in items:
            #if current item is a list or dictionary
            if type(item) is dict or type(item) is list:
                #dictify it (recursion!)
                item = dictify(item)
            #if current item is an instance of one of our classes
            elif hasattr(item,'__dict__'):
                #run __dict__ on it to get it in dictionary form and set a variable to that
                #add a new key to the dictionary "classtype" and set it equal to typeof object
                classtype = type(item).__name__
                item = item.__dict__
                item['classtype'] = classtype
                #replace the object in the dictionary with the __dict__ified object
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
    #return the dictionary

#JSON writer function
def json_dump(file_path,items):
    #if input is not a dictionary:
    if not type(items) is dict:
        #return false
        return False
    #if file path does not exist
    try:
        with open(file_path,'r'):
            pass
    except FileNotFoundError:
        create_json(file_path)
    except Exception:
        #return false
        return False
    #dictify the dictionary
    items = dictify(items)
    #open given file path
    with open(file_path,'w') as file:
        #write dictionary to it
        json.dump(items, file)
    #return true
    return True

def create_json(file_path):
    try:
        with open(file_path,'w') as file:
            file.write('{}')
    except:
        print('Directory does not exist!')

#JSON reader function
def json_pull(file_path):
    #if file path does not exist
    try:
        with open(file_path,'r'):
            pass
    except:
        #return false
        return False
    #open file path
    with open(file_path,'r') as file:
        #grab data as a dictionary
        data = json.load(file)
        #undictify it
        data = undictify(data)
    #return data
    return data


def hash_pw(item: str) -> str:
    sha256 = hashlib.sha256()
    sha256.update(item.encode("utf-8"))
    return sha256.hexdigest()


#A function to check if something exists
def exists(location, search):
    try:
        with open(location, mode="r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                # skip empty lines
                if row and row[0] == search:
                    return True
    except FileNotFoundError:
        print("file does not exist.")
    except Exception:
        # fallback for unexpected errors
        print("error reading file")
    return False

def add_user(username: str, hashed: str) -> None:
    #if this recieves a username that already is stored it will overwrite it with the hashed password provided.
    users = json_pull('documents/user.json')
    users[username] = hashed
    json_dump('documents/user.json',users)

#define a function that allows for the creation of the account using the already exists checker to check for the user name already exists if so make them use a diffrent username
def create_account():
    # clear screen here
    clear_screen()

    while True:
        name =  input("Choose a username: ").strip()

        if not name:
            print("Username cannot be blank.")
            continue

        if exists("documents/user.json",name):
            print("That username is unavailable.")
            continue

        pw =  input("Choose a password (12+ chars, upper, lower, digit, special): ")
        add_user(name, hash_pw(pw))
        print("Account created.")
        return name
    
    #get their password
    
    #hash their password and save its value

#A function that reads the whole json

#define a function that edits the account json adding accounts to the user json
    
    #Open the file in append mode
    
    #Use dictwriter to set the field names their username and their hashed password
    
    #write to the file their name password hashed and goal and progress 

#A function to encrypt saved passwords with the hashlib library using a specific encryption  this is in helper library

def login():
    while True:
        users = json_pull('documents/user.json')
        name =  input("What is your username? ").strip()
        pw =  input("What is your password? ")
        hashed = hash_pw(pw)

        for u in users.keys():

            if u == name and users[u] == hashed:
                print("Login successful.")
                clear_wait_screen()
                clear_screen()
                return name
        print("Invalid username or password.")

#A function that gets their goal and saves it


def goal_get():
    good=False
    while True:
        try:
            goal = float( input(f"What do you want to set your goal too?",wrong=good).strip())
            break
        except:
            good=True
    return [goal, 0]





#A function that takes in their previous progress towards their goal, and then asks how much more money they have added, and updates the progress.
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
    #Do the thing where you add the progress to the json

#A function that logs them out and takes them back to the main menu without them being logged in.
def logout(): 
    return 