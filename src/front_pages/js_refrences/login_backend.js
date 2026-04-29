const SPECIAL_CHARACTERS = new Set("!@#$%^&*()-_=+[]{}|:;'<>.,?/~`".split(''));

function password_ok(password) {
    if (password.length < 12) return false;
    if (![...password].some(c => c === c.toLowerCase() && c !== c.toUpperCase())) return false;
    if (![...password].some(c => c === c.toUpperCase() && c !== c.toLowerCase())) return false;
    if (![...password].some(c => /\d/.test(c))) return false;
    if (![...password].some(c => SPECIAL_CHARACTERS.has(c))) return false;
    return true;
}

async function hash_pw(item) {
    const encoder = new TextEncoder();
    const data = encoder.encode(item);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function json_pull(key) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : {};
    } catch {
        return {};
    }
}

function json_dump(key, items) {
    try {
        localStorage.setItem(key, JSON.stringify(items));
        return true;
    } catch {
        return false;
    }
}

function add_user(username, hashed) {
    let users = json_pull('accounts');
    users[username] = hashed;
    json_dump('accounts', users);
}

async function create_account(username, password) {
    if (!password_ok(password)) {
        return "Password does not meet requirements.";
    }
    if (username in json_pull('accounts')) {
        return "Username already exists.";
    }
    const hashed = await hash_pw(password);
    add_user(username, hashed);
    return username;
}

async function login(username, password) {
    let users = json_pull('accounts');
    if (!users) users = {};
    const hashed = await hash_pw(password);
    if (username in users && users[username] === hashed) {
        return true;
    }
    return false;
}