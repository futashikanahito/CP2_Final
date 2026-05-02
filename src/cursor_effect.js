const canvas = document.getElementById("waveCanvas");
const ctx = canvas.getContext("2d");

let width, height;
let cols, rows;
let spacing = 20;

let range = 8;
let distribution = 6;
let intensity = 2;
let maximum = 25;

let grid = [];

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;

    cols = Math.floor(width / spacing) + 2;
    rows = Math.floor(height / spacing);

    grid = [];

    for (let i = 0; i < cols * rows; i++) {
        grid[i] = 0;
    }
}

window.addEventListener("resize", resize);
resize();

function disturb(mouseX, mouseY) {
    let col = Math.floor(mouseX / spacing);
    let row = Math.floor(mouseY / spacing);

    for (let dx = -range; dx <= range; dx++) {
        for (let dy = -range; dy <= range; dy++) {
            let nx = col + dx;
            let ny = row + dy;

            if (nx >= 0 && nx < cols && ny >= 0 && ny < rows) {
                let index = nx + ny * cols;

                let dist = Math.sqrt(dx * dx + dy * dy);
                let influence = Math.max(0, 1 - dist / distribution);

                grid[index] += influence * intensity;
                grid[index] = Math.min(grid[index], maximum);
            }
        }
    }
}

window.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    disturb(x, y);
});

function update() {
    for (let i = 0; i < grid.length; i++) {
        grid[i] *= 0.92;

        if (grid[i] < 0.01) {
            grid[i] = 0;
        }
    }
}

function draw() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < grid.length; i++) {
        let value = grid[i];

        if (value <= 0.01) continue;

        let gx = i % cols;
        let gy = Math.floor(i / cols);

        let x = gx * spacing;
        let y = gy * spacing;

        let radius = value;
        let t = (gx / cols + (rows - gy) / rows) / 2;

        const blue = { r: 100, g: 55, b: 200 };
        const green = { r: 0, g: 200, b: 100 };

        function lighten(color, amount) {
            return {
                r: Math.floor(color.r + (255 - color.r) * amount),
                g: Math.floor(color.g + (255 - color.g) * amount),
                b: Math.floor(color.b + (255 - color.b) * amount)
            };
        }

        const lightBlue = lighten(blue, 0.6);
        const lightGreen = lighten(green, 0.6);

        let r = Math.floor(lightBlue.r * (1 - t) + lightGreen.r * t);
        let g = Math.floor(lightBlue.g * (1 - t) + lightGreen.g * t);
        let b = Math.floor(lightBlue.b * (1 - t) + lightGreen.b * t);

        ctx.beginPath();
        ctx.arc(x, y, radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(${r}, ${g}, ${b}, ${0.35 + value * 0.05})`;
        ctx.fill();
    }
}

window.addEventListener('message', (event) => {
    const { type, value } = event.data;

    switch (type) {
        case 'ce-range':
            range = value;
            break;
        case 'ce-distribution':
            distribution = value;
            break;
        case 'ce-intensity':
            intensity = value;
            break;
        case 'ce-maximum':
            maximum = value;
            break;
    }
});

function animate() {
    update();
    draw();
    requestAnimationFrame(animate);
}



animate();