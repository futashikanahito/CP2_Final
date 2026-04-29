const SPECIAL_CHARACTERS = new Set("!@#$%^&*()-_=+[]{}|:;'<>.,?/~`".split(''));

function password_ok(password) {
    if (password.length < 8) return false;
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
        return JSON.parse(localStorage.getItem(key)) || {};
    } catch { return {}; }
}

function json_dump(key, items) {
    try {
        localStorage.setItem(key, JSON.stringify(items));
        return true;
    } catch { return false; }
}

async function create_account(username, pw) {
    if (!password_ok(pw)) return "Password does not meet requirements.";
    let users = json_pull('accounts');
    if (username in users) return "Username already exists.";
    users[username] = await hash_pw(pw);
    json_dump('accounts', users);
    return username;
}

async function login(username, pw) {
    let users = json_pull('accounts');
    const hashed = await hash_pw(pw);
    return (username in users) && (users[username] === hashed);
}