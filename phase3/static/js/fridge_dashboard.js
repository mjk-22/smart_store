// static/js/fridge_dashboard.js

const MAX_TEMP = 40;   // Scale 0–40 °C
const MAX_HUM  = 100;  // Scale 0–100 %

function drawGauge(canvas, value, max, threshold) {
    const ctx = canvas.getContext("2d");
    const w = canvas.width;
    const h = canvas.height;

    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h * 0.95;
    const r  = Math.min(w, h * 2) * 0.45;

    const start = Math.PI;
    const end   = 2 * Math.PI;

    // Background arc
    ctx.beginPath();
    ctx.arc(cx, cy, r, start, end);
    ctx.lineWidth = 16;
    ctx.strokeStyle = "rgba(148,163,184,0.3)";
    ctx.stroke();

    const safeThreshold = (typeof threshold === "number") ? threshold : null;
    const isOver = safeThreshold !== null && value > safeThreshold;
    const arcColor = isOver ? "#ef4444" : "#22c55e";   // red if over thr, else green

    const ratio = Math.max(0, Math.min(1, value / max));
    const valAngle = start + (end - start) * ratio;

    // Foreground arc
    ctx.beginPath();
    ctx.arc(cx, cy, r, start, valAngle);
    ctx.lineWidth = 16;
    ctx.strokeStyle = arcColor;
    ctx.stroke();

    // Threshold marker (small tick)
    if (safeThreshold !== null) {
        const thrRatio = Math.max(0, Math.min(1, safeThreshold / max));
        const thrAngle = start + (end - start) * thrRatio;

        const outer = r + 4;
        const inner = r - 10;

        ctx.beginPath();
        ctx.moveTo(
            cx + outer * Math.cos(thrAngle),
            cy + outer * Math.sin(thrAngle)
        );
        ctx.lineTo(
            cx + inner * Math.cos(thrAngle),
            cy + inner * Math.sin(thrAngle)
        );
        ctx.lineWidth = 3;
        ctx.strokeStyle = "#eab308";  // yellow tick
        ctx.stroke();
    }

    // Needle (value marker)
    const needleLen = r * 0.7;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.lineTo(
        cx + needleLen * Math.cos(valAngle),
        cy + needleLen * Math.sin(valAngle)
    );
    ctx.lineWidth = 3;
    ctx.strokeStyle = "#e5e7eb";
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, 5, 0, 2 * Math.PI);
    ctx.fillStyle = "#e5e7eb";
    ctx.fill();
}

function updateFromData(fridge) {
    const id = fridge.id;

    const tempValSpan = document.getElementById(`tempVal-${id}`);
    const humValSpan  = document.getElementById(`humVal-${id}`);
    const updatedSpan = document.querySelector(`[data-updated="${id}"]`);
    const fanPill     = document.querySelector(`[data-fan="${id}"]`);

    const temp = (typeof fridge.temperature === "number") ? fridge.temperature : null;
    const hum  = (typeof fridge.humidity === "number") ? fridge.humidity : null;

    const tThr = (typeof fridge.temp_threshold === "number") ? fridge.temp_threshold : null;
    const hThr = (typeof fridge.humidity_threshold === "number") ? fridge.humidity_threshold : null;

    if (tempValSpan) {
        tempValSpan.textContent = temp !== null ? temp.toFixed(1) : "--";
    }
    if (humValSpan) {
        humValSpan.textContent = hum !== null ? hum.toFixed(1) : "--";
    }
    if (updatedSpan && fridge.updated_at) {
        updatedSpan.textContent = fridge.updated_at;
    }

    // Fan pill text + colour
    if (fanPill) {
        const on = !!fridge.fan_on;
        fanPill.textContent = `Fan: ${on ? "ON" : "OFF"} (auto)`;
        fanPill.classList.toggle("pill-on", on);
        fanPill.classList.toggle("pill-off", !on);
    }

    const tempCanvas = document.getElementById(`tempGauge-${id}`);
    const humCanvas  = document.getElementById(`humGauge-${id}`);

    if (tempCanvas && temp !== null) {
        drawGauge(tempCanvas, temp, MAX_TEMP, tThr);
    }
    if (humCanvas && hum !== null) {
        drawGauge(humCanvas, hum, MAX_HUM, hThr);
    }
}

function refreshGauges() {
    const container = document.querySelector(".fridge-dashboard");
    if (!container) return;

    const url = container.dataset.latestUrl;
    fetch(url)
        .then(r => r.json())
        .then(data => {
            if (!data.fridges) return;
            data.fridges.forEach(updateFromData);
        })
        .catch(err => console.error("fridge refresh failed", err));
}

document.addEventListener("DOMContentLoaded", () => {
    refreshGauges();
    setInterval(refreshGauges, 3000);
});