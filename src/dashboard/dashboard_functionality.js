let zIndex = 1;
let activeDrag = null;
let activeResize = null;

function shieldIframes() {
    document.querySelectorAll('.window iframe').forEach(f => {
        f.style.pointerEvents = 'none';
    });
}

function unshieldIframes() {
    document.querySelectorAll('.window iframe').forEach(f => {
        f.style.pointerEvents = 'auto';
    });
}

document.addEventListener('mousemove', (e) => {
    if (activeDrag) {
        const {win, offsetX, offsetY} = activeDrag;
        win.style.left = (e.clientX - offsetX) + 'px';
        win.style.top = (e.clientY - offsetY) + 'px';
    }
    if (activeResize) {
        resizeWindow(e, activeResize);
    }
});

document.addEventListener('mouseup', () => {
    activeDrag = null;
    activeResize = null;
    unshieldIframes();
});

function createWindow(name, path) {
    const win = document.createElement('div');
    win.className = 'window';
    win.style.top = '50px';
    win.style.left = '50px';
    win.style.zIndex = zIndex++;

    win.innerHTML = `
        <div class="titlebar">
            <div>${name}</div>.
            <div class="buttons">
                <div class="btn min"></div>
                <div class="btn max"></div>
                <div class="btn close"></div>
            </div>
        </div>
        <div class="content">
            <iframe src="${path}" style="width:100%;height:100%;border:none;"></iframe>
        </div>
        <div class="resizer right"></div>
        <div class="resizer bottom"></div>
        <div class="resizer left"></div>
        <div class="resizer top"></div>
        <div class="resizer br-corner"></div>
        <div class="resizer bl-corner"></div>
        <div class="resizer tr-corner"></div>
        <div class="resizer tl-corner"></div>
    `;

    document.getElementById('desktop').appendChild(win);

    const titlebar = win.querySelector('.titlebar');
    titlebar.addEventListener('mousedown', (e) => {
        win.style.zIndex = zIndex++;
        shieldIframes();
        activeDrag = {win, offsetX: e.clientX - win.offsetLeft, offsetY: e.clientY - win.offsetTop};
    });

    win.querySelector('.close').onclick = () => win.remove();
    win.querySelector('.min').onclick = () => win.style.display = 'none';
    win.querySelector('.max').onclick = () => {
        win.style.width = '100vw';
        win.style.height = 'calc(100vh - 40px)';
        win.style.top = '0';
        win.style.left = '0';
    };

    function initResize(dir, e) {
        e.preventDefault();
        win.style.zIndex = zIndex++;
        shieldIframes();
        activeResize = {win, dir, startX: e.clientX, startY: e.clientY, startW: parseInt(getComputedStyle(win).width), startH: parseInt(getComputedStyle(win).height), startLeft: win.offsetLeft, startTop: win.offsetTop};
    }

    win.querySelector('.resizer.right').addEventListener('mousedown', (e) => initResize('right',  e));
    win.querySelector('.resizer.bottom').addEventListener('mousedown', (e) => initResize('bottom', e));
    win.querySelector('.resizer.left').addEventListener('mousedown', (e) => initResize('left',   e));
    win.querySelector('.resizer.top').addEventListener('mousedown', (e) => initResize('top',    e));
    win.querySelector('.resizer.br-corner').addEventListener('mousedown', (e) => initResize('br',     e));
    win.querySelector('.resizer.bl-corner').addEventListener('mousedown', (e) => initResize('bl',     e));
    win.querySelector('.resizer.tr-corner').addEventListener('mousedown', (e) => initResize('tr',     e));
    win.querySelector('.resizer.tl-corner').addEventListener('mousedown', (e) => initResize('tl',     e));
}

function resizeWindow(e, {win, dir, startX, startY, startW, startH, startLeft, startTop }) {
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;

    if (dir === 'right') {win.style.width = Math.max(200, startW + dx) + 'px'}
    if (dir === 'bottom') {win.style.height = Math.max(150, startH + dy) + 'px'}
    if (dir === 'left') {win.style.width = Math.max(200, startW - dx) + 'px'; win.style.left = (startLeft + dx) + 'px'}
    if (dir === 'top') {win.style.height = Math.max(150, startH - dy) + 'px'; win.style.top = (startTop  + dy) + 'px'}
    if (dir === 'br') {win.style.width = Math.max(200, startW + dx) + 'px'; win.style.height = Math.max(150, startH + dy) + 'px'}
    if (dir === 'bl') {win.style.width = Math.max(200, startW - dx) + 'px'; win.style.left = (startLeft + dx) + 'px'; win.style.height = Math.max(150, startH + dy) + 'px'}
    if (dir === 'tr') {win.style.width = Math.max(200, startW + dx) + 'px'; win.style.height = Math.max(150, startH - dy) + 'px'; win.style.top = (startTop + dy) + 'px'}
    if (dir === 'tl') {win.style.width = Math.max(200, startW - dx) + 'px'; win.style.left = (startLeft + dx) + 'px'; win.style.height = Math.max(150, startH - dy) + 'px'; win.style.top = (startTop + dy) + 'px'}
}

function createCalendar() {
    const calendarUrl = "https://calendar.google.com/calendar/embed?wkst=1&ctz=America%2FDenver&showPrint=0&src=dHJ1ZWVnZ2xlc3RvbkBnbWFpbC5jb20&src=Y2xhc3Nyb29tMTA4Mzg5MzM4NDY0MDYzNjc0Nzk3QGdyb3VwLmNhbGVuZGFyLmdvb2dsZS5jb20&src=YTdmMmU1NjkzMWYzYjAxNDAzNTY4MTYyNTc1OGMyOTVlYmJhM2NjZTRmMWRmYmMwNTQwNDE1OTQyZTllNmYxZkBncm91cC5jYWxlbmRhci5nb29nbGUuY29t&src=ZW4udXNhI2hvbGlkYXlAZ3JvdXAudi5jYWxlbmRhci5nb29nbGUuY29t&color=%23039be5&color=%237cb342&color=%237cb342&color=%230b8043";

    createWindow('My Calendar', calendarUrl);
}

function createSettings() {
    const win = document.createElement('div');
    win.className = 'window';
    win.style.width = '95vw';
    win.style.height = '80vw';
    win.style.top = '50%';
    win.style.left = '50%';
    win.style.transform = 'translate(-50%, -50%)';
    win.style.zIndex = zIndex++;

    win.innerHTML = `
        <div class="content">
            <iframe src="../dashboard_content/settings.html" style="width:100%;height:100%;border:none;"></iframe>
        </div>
    `;

    document.getElementById('desktop').appendChild(win);

    function handleMessage(e) {
        if (e.data?.type === 'close-settings') {
            win.remove();
            window.removeEventListener('message', handleMessage); // cleanup
        }
    }

    window.addEventListener('message', handleMessage);
}

window.addEventListener('message', (e) => {
    const { type, value } = e.data ?? {};

    if (type === 'set-theme') {
        const isLight = value === 'light';
        document.body.classList.toggle('dashboard-light', isLight);
    }

    if (type === 'set-bg-color') {
        document.body.style.background = value;
    }

    if (type === 'set-brightness') {
        document.body.style.filter = `brightness(${value}%)`;
    }

    if (type === 'reset-bg') {
        document.body.style.background = '';
    }
});