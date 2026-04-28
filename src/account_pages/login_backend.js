const SPECIAL_CHARACTERS = new Set("!@#$%^&*()-_=+[]{}|:;'<>.,?/~`".split(''));

function password_ok(password) {
    if (password.length < 12) {
        return false;
    }

    if (![...password].some(c => c === c.toLowerCase() && c !== c.toUpperCase())) {
        return false;
    }

    if (![...password].some(c => c === c.toUpperCase() && c !== c.toLowerCase())) {
        return false;
    }

    if (![...password].some(c => /\d/.test(c))) {
        return false;
    }

    if (![...password].some(c => SPECIAL_CHARACTERS.has(c))) {
        return false;
    }

    return true;
}

function dictify(items) {
    if (Array.isArray(items)) {
        const dictified = [];

        for (let item of items) {
            if (typeof item === 'object' && item !== null) {
                if (Array.isArray(item) || (item.constructor === Object)) {
                    item = dictify(item);
                } else if (item.constructor && item.constructor.name) {
                    let newItem = {...item};
                    newItem.classtype = item.constructor.name;
                    item = newItem;
                }
            }
            dictified.push(item);
        }
        return dictified;
    } else if (typeof items === 'object' && items !== null) {
        const dictified = {};
        for (const itemkey in items) {
            if (Object.prototype.hasOwnProperty.call(items, itemkey)) {
                let item = items[itemkey];
                if (typeof item === 'object' && item !== null) {
                    if (Array.isArray(item) || (item.constructor === Object)) {
                        item = dictify(item);
                    } else if (item.constructor && item.constructor.name) {
                        let newItem = {...item};
                        newItem.classtype = item.constructor.name;
                        item = newItem;
                    }
                }
                dictified[itemkey] = item;
            }
        }
        return dictified;
    }
}

const fs = require('fs');

function undictify(items) {
    if (Array.isArray(items)) {
        let undictified = [];
        for (let item of items) {
            if (typeof item === 'object' && item !== null) {
                item = undictify(item);
            }
            let obj = false;
            try {
                obj = item.hasOwnProperty('classtype');
            } catch {
                obj = false;
            }
            if (obj) {
                try {
                    let classtype = globalThis[item['classtype']];
                    if (typeof classtype !== 'function') throw new Error();
                    delete item['classtype'];
                    let itemobj = new classtype();
                    for (let key in item) {
                        if (item.hasOwnProperty(key)) {
                            itemobj[key] = item[key];
                        }
                    }
                    item = itemobj;
                } catch {
                    return "error";
                }
            }
            undictified.push(item);
        }
        return undictified;
    } else if (typeof items === 'object' && items !== null) {
        let undictified = {};
        for (let itemkey in items) {
            if (items.hasOwnProperty(itemkey)) {
                let item = items[itemkey];
                if (typeof item === 'object' && item !== null) {
                    item = undictify(item);
                }
                let obj = false;
                try {
                    obj = item.hasOwnProperty('classtype');
                } catch {
                    obj = false;
                }
                if (obj) {
                    try {
                        let classtype = globalThis[item['classtype']];
                        if (typeof classtype !== 'function') throw new Error();
                        delete item['classtype'];
                        let itemobj = new classtype();
                        for (let key in item) {
                            if (item.hasOwnProperty(key)) {
                                itemobj[key] = item[key];
                            }
                        }
                        item = itemobj;
                    } catch {
                        return "error";
                    }
                }
                undictified[itemkey] = item;
            }
        }
        return undictified;
    }
    return items;
}

function json_dump(file_path, items) {
    if (typeof items !== 'object' || items === null || Array.isArray(items)) {
        return false;
    }
    try {
        fs.accessSync(file_path, fs.constants.R_OK);
    } catch (err) {
        if (err.code === 'ENOENT') {
            create_json(file_path);
        } else {
            return false;
        }
    }
    // Assuming dictify is defined elsewhere or identity function
    if (typeof dictify === 'function') {
        items = dictify(items);
    }
    try {
        fs.writeFileSync(file_path, JSON.stringify(items));
    } catch {
        return false;
    }
    return true;
}

function create_json(file_path) {
    try {
        fs.writeFileSync(file_path, '{}');
    } catch {
        return "error";
    }
}

function json_pull(file_path) {
    try {
        fs.accessSync(file_path, fs.constants.R_OK);
    } catch {
        return false;
    }
    try {
        let data = JSON.parse(fs.readFileSync(file_path, 'utf8'));
        data = undictify(data);
        return data;
    } catch {
        return false;
    }
}


function hash_pw(item) {
    sha256 = hashlib.sha256()
    sha256.update(item.encode("utf-8"))
    return sha256.hexdigest()
}

function exists(location, search) {
    try {
        const data = fs.readFileSync(location, 'utf8');
        const lines = data.split('\n');
        for (let line of lines) {
            const row = line.split(',');
            if (row && (row[0] === search)) {
                return true;
            }
        }
    } catch {
        return false;
    }
    return false;
}

function add_user(username, hashed) {
    let users = json_pull('../docs/user.json');
    users[username] = hashed;
    json_dump('../docs/user.json', users);
}

function create_account() {
    document.getElementById('createID').addEventListener('click'); 
    // 1. Get values from the input boxes
    const name = document.getElementById('username').value;
    const pword = document.getElementById('pw').value;
    let users = json_pull('../docs/accounts.json');
    if (!users) {
        users = {}
    }
    let ok = password_ok(pw);
    if (!ok) {
        return "Password does not meet requirements.";
    }
    add_user(name, hash_pw(pw));
    return name;
}

function login() {
    document.getElementById('loginID').addEventListener('click');
    // 1. Get values from the input boxes
    const name = document.getElementById('username').value;
    const pw = document.getElementById('pw').value;
    let users = json_pull('../docs/accounts.json');
    if (!users) {
        users = {}
    }
    let hashed = hash_pw(pw)
    if (username in users && (users[name] == hashed)) {
        return true;
    }
    return false;
}
