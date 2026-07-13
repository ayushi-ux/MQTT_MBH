import re
import subprocess

# 1. Retrieve the original templates/dashboard.html from HEAD
try:
    base_html = subprocess.check_output(["git", "show", "HEAD:templates/dashboard.html"], text=True, encoding="utf-8")
except Exception as e:
    print("Failed to run git show HEAD:templates/dashboard.html")
    raise e

# 2. Extract JavaScript script block from HEAD
script_match = re.search(r"<script>(.*?)</script>", base_html, re.DOTALL)
if not script_match:
    print("Error: Could not extract JavaScript from HEAD dashboard.")
    exit(1)
js = script_match.group(1)

# 3. Apply Min/Max and Deep Sleep JavaScript changes to base JS
ble_inputs_old = """    const height = document.getElementById("bleTotalHeight").value;
    const volume = document.getElementById("bleTotalVolume").value;
    
    // Read final MAC and Serial from the hidden inputs"""

ble_inputs_new = """    const height = document.getElementById("bleTotalHeight").value;
    const volume = document.getElementById("bleTotalVolume").value;
    const minPct = document.getElementById("bleMinPercentage").value;
    const maxPct = document.getElementById("bleMaxPercentage").value;
    const deepSleep = document.getElementById("bleDeepSleep").value;
    const sleepInterval = document.getElementById("bleSleepInterval").value;
    
    // Read final MAC and Serial from the hidden inputs"""

js = js.replace(ble_inputs_old, ble_inputs_new)

ble_register_old = """        const response = await fetch("/api/register-device/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mac_address: finalMac,
                serial_number: finalSerial,
                device_name: name,
                total_height: +height,
                total_volume: +volume
            })
        });"""

ble_register_new = """        const response = await fetch("/api/register-device/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mac_address: finalMac,
                serial_number: finalSerial,
                device_name: name,
                total_height: +height,
                total_volume: +volume,
                min_percentage: +minPct,
                max_percentage: +maxPct,
                deep_sleep: +deepSleep,
                sleep_interval: +sleepInterval
            })
        });"""

js = js.replace(ble_register_old, ble_register_new)

manual_claim_old = """async function submitManualClaim() {
    const statusEl = document.getElementById("claimStatus");
    const name = document.getElementById("claimDeviceName").value;
    const mac = document.getElementById("claimMacAddress").value;
    const serial = document.getElementById("claimSerialNumber").value;
    const height = document.getElementById("claimTotalHeight").value;
    const volume = document.getElementById("claimTotalVolume").value;
    
    if (!name || !mac || !height || !volume) {
        statusEl.innerText = "Device Name, MAC, Height, and Volume are required.";
        statusEl.style.color = "var(--warning)";
        return;
    }
    
    statusEl.innerText = "Registering device...";
    statusEl.style.color = "var(--primary)";
    
    try {
        const response = await fetch("/api/register-device/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mac_address: mac,
                serial_number: serial,
                device_name: name,
                total_height: +height,
                total_volume: +volume
            })
        });"""

manual_claim_new = """async function submitManualClaim() {
    const statusEl = document.getElementById("claimStatus");
    const name = document.getElementById("claimDeviceName").value;
    const mac = document.getElementById("claimMacAddress").value;
    const serial = document.getElementById("claimSerialNumber").value;
    const height = document.getElementById("claimTotalHeight").value;
    const volume = document.getElementById("claimTotalVolume").value;
    const minPct = document.getElementById("claimMinPercentage").value;
    const maxPct = document.getElementById("claimMaxPercentage").value;
    const deepSleep = document.getElementById("claimDeepSleep").checked ? 1 : 0;
    const sleepInterval = document.getElementById("claimSleepInterval").value;
    
    if (!name || !mac || !height || !volume || !minPct || !maxPct || !sleepInterval) {
        statusEl.innerText = "All fields (including Deep Sleep Interval) are required.";
        statusEl.style.color = "var(--warning)";
        return;
    }
    
    statusEl.innerText = "Registering device...";
    statusEl.style.color = "var(--primary)";
    
    try {
        const response = await fetch("/api/register-device/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                mac_address: mac,
                serial_number: serial,
                device_name: name,
                total_height: +height,
                total_volume: +volume,
                min_percentage: +minPct,
                max_percentage: +maxPct,
                deep_sleep: +deepSleep,
                sleep_interval: +sleepInterval
            })
        });"""

js = js.replace(manual_claim_old, manual_claim_new)

trigger_refresh_old = """function triggerDeviceRefresh() {
    fetchHistory();
    fetchLiveHistory();
    fetchLogs(1);
    
    document.getElementById("storedHeight").innerText = "--";
    document.getElementById("storedVolume").innerText = "--";
}"""

trigger_refresh_new = """function triggerDeviceRefresh() {
    fetchHistory();
    fetchLiveHistory();
    fetchLogs(1);
    
    document.getElementById("storedHeight").innerText = "--";
    document.getElementById("storedVolume").innerText = "--";
    document.getElementById("storedMin").innerText = "--";
    document.getElementById("storedMax").innerText = "--";
    document.getElementById("storedDeepSleep").innerText = "--";
    document.getElementById("storedSleepInterval").innerText = "--";
}"""

js = js.replace(trigger_refresh_old, trigger_refresh_new)

send_input_old = """function sendInput(){
    const h = document.getElementById("totalHeight").value;
    const v = document.getElementById("totalVolume").value;
    if (!h || !v) return;

    fetch("/api/send-input/",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            total_height: +h,
            total_volume: +v,
            mac_address: activeDeviceMac
        })
    });

    // Show immediately
    document.getElementById("storedHeight").innerText = h;
    document.getElementById("storedVolume").innerText = v;
}"""

send_input_new = """function sendInput(){
    const h = document.getElementById("totalHeight").value;
    const v = document.getElementById("totalVolume").value;
    const minPct = document.getElementById("minPercentage").value;
    const maxPct = document.getElementById("maxPercentage").value;
    const deepSleep = document.getElementById("deepSleepToggle").checked ? 1 : 0;
    const sleepInterval = document.getElementById("sleepInterval").value;
    if (!h || !v || !minPct || !maxPct || !sleepInterval) return;

    fetch("/api/send-input/",{
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body:JSON.stringify({
            total_height: +h,
            total_volume: +v,
            min_percentage: +minPct,
            max_percentage: +maxPct,
            deep_sleep: +deepSleep,
            sleep_interval: +sleepInterval,
            mac_address: activeDeviceMac
        })
    });

    // Show immediately
    document.getElementById("storedHeight").innerText = h;
    document.getElementById("storedVolume").innerText = v;
    document.getElementById("storedMin").innerText = minPct;
    document.getElementById("storedMax").innerText = maxPct;
    document.getElementById("storedDeepSleep").innerText = deepSleep === 1 ? "Enabled" : "Disabled";
    document.getElementById("storedSleepInterval").innerText = sleepInterval;
}"""

js = js.replace(send_input_old, send_input_new)

input_poll_old = """    /* ---------- INPUT ---------- */
    try {
        const input = await (await fetch("/api/input/?mac=" + activeDeviceMac)).json();
        const th = input.total_height;
        const tv = input.total_volume;

        if (th !== undefined && tv !== undefined) {
            document.getElementById("storedHeight").innerText = th;
            document.getElementById("storedVolume").innerText = tv;
        }
    } catch(e) { console.warn("input poll error", e); }"""

input_poll_new = """    /* ---------- INPUT ---------- */
    try {
        const input = await (await fetch("/api/input/?mac=" + activeDeviceMac)).json();
        const th = input.total_height;
        const tv = input.total_volume;
        const minPct = input.min_percentage;
        const maxPct = input.max_percentage;
        const deepSleep = input.deep_sleep;
        const sleepInterval = input.sleep_interval;

        if (th !== undefined && tv !== undefined) {
            document.getElementById("storedHeight").innerText = th;
            document.getElementById("storedVolume").innerText = tv;
        }
        if (minPct !== undefined && maxPct !== undefined) {
            document.getElementById("storedMin").innerText = minPct;
            document.getElementById("storedMax").innerText = maxPct;
        }
        if (deepSleep !== undefined && sleepInterval !== undefined) {
            document.getElementById("storedDeepSleep").innerText = deepSleep === 1 ? "Enabled" : "Disabled";
            document.getElementById("storedSleepInterval").innerText = sleepInterval;
        }
    } catch(e) { console.warn("input poll error", e); }"""

js = js.replace(input_poll_old, input_poll_new)

js = js.replace(
    'const isDark = () => document.body.classList.contains("dark");',
    'const isDark = () => document.documentElement.classList.contains("dark") || document.body.classList.contains("dark");'
)

js = js.replace(
    """function toggleDark() {
    const body = document.body;
    const isDark = body.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    
    // Update toggle icon
    const ball = document.getElementById("themeBall");
    if (ball) ball.innerText = isDark ? "🌙" : "☀️";

    updateChartTheme();
}""",
    """function toggleDark() {
    const html = document.documentElement;
    const isDark = html.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    
    // Update toggle icon
    const ball = document.getElementById("themeBall");
    if (ball) ball.innerText = isDark ? "🌙" : "☀️";

    updateChartTheme();
}"""
)

js = js.replace(
    """// Initialize theme
(function initTheme() {
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark");
        const ball = document.getElementById("themeBall");
        if (ball) ball.innerText = "🌙";
    }
})();""",
    """// Initialize theme
(function initTheme() {
    if (localStorage.getItem("theme") !== "light") {
        document.documentElement.classList.add("dark");
        const ball = document.getElementById("themeBall");
        if (ball) ball.innerText = "🌙";
    } else {
        document.documentElement.classList.remove("dark");
        const ball = document.getElementById("themeBall");
        if (ball) ball.innerText = "☀️";
    }
})();"""
)

# Tweak loadDevices() to update dynamic header titles
js = js.replace(
    """        select.value = activeDeviceMac;
        localStorage.setItem("active_device_mac", activeDeviceMac);
        
        triggerDeviceRefresh();""",
    """        select.value = activeDeviceMac;
        localStorage.setItem("active_device_mac", activeDeviceMac);
        
        // Update header display info
        const activeDev = data.devices.find(d => d.mac_address === activeDeviceMac);
        if (activeDev) {
            document.getElementById("activeDeviceNameDisplay").innerText = activeDev.device_name;
            document.getElementById("activeDeviceMacDisplay").innerText = "MAC: " + activeDev.mac_address + " | Serial: " + activeDev.serial_number;
        }
        
        triggerDeviceRefresh();"""
)

# Tweak changeDevice() to update dynamic header titles
js = js.replace(
    """function changeDevice(mac) {
    activeDeviceMac = mac;
    localStorage.setItem("active_device_mac", mac);
    triggerDeviceRefresh();
}""",
    """function changeDevice(mac) {
    activeDeviceMac = mac;
    localStorage.setItem("active_device_mac", mac);
    
    // Update header display info
    fetch("/api/list-devices/").then(res => res.json()).then(data => {
        const activeDev = data.devices.find(d => d.mac_address === mac);
        if (activeDev) {
            document.getElementById("activeDeviceNameDisplay").innerText = activeDev.device_name;
            document.getElementById("activeDeviceMacDisplay").innerText = "MAC: " + activeDev.mac_address + " | Serial: " + activeDev.serial_number;
        }
    }).catch(e => console.warn(e));
    
    triggerDeviceRefresh();
}"""
)

calculated_poll_old = """            updateVal("percentage", pct + " %");
            updateVal("filledVolume", calc.FILLED_WATER_IN_VOLUME);
            updateVal("distanceVal", calc.DISTANCE + " m");
            updateVal("batteryVoltage", calc.BATTERY_VOLTAGE + " V");

            // Tank animation
            const waterFill = document.getElementById("waterFill");
            const waterText = document.getElementById("waterText");
            const tankElement = document.getElementById("tankElement");
            
            if (waterFill) waterFill.style.height = pct + "%";
            if (waterText) waterText.innerText = pct + "%";
            
            // Toggle Motor-Sync Animations (Bubbles & Stream)
            if (tankElement) {
                tankElement.classList.toggle('motor-on', calc.MOTOR_STATUS === 1);
            }

            const status = document.getElementById("motorStatus");
            if (status) {
                status.classList.toggle('pulse-active', calc.MOTOR_STATUS === 1);
            }"""

calculated_poll_new = """            updateVal("percentage", pct + "%");
            updateVal("filledVolume", calc.FILLED_WATER_IN_VOLUME.toLocaleString());
            updateVal("distanceVal", calc.DISTANCE + "m");
            
            // Update circular SVG gauge stroke-dasharray (max 270 degrees)
            const gaugeValue = document.getElementById("gaugeValue");
            if (gaugeValue) {
                const dashVal = (pct / 100) * 270;
                gaugeValue.style.strokeDasharray = `${dashVal} 360`;
            }
            
            // Display height in telemetry details
            const displayHeight = document.getElementById("displayHeight");
            if (displayHeight) displayHeight.innerText = calc.TOTAL_HEIGHT + "m";
            
            // Update battery voltage & charge percent display
            if (calc.BATTERY_VOLTAGE !== undefined) {
                const volt = Number(calc.BATTERY_VOLTAGE);
                document.getElementById("batteryVoltageDisplay").innerText = volt.toFixed(2);
                
                const batPct = Math.max(0, Math.min(100, Math.round(((volt - 3.2) / 1.0) * 100)));
                const batteryBar = document.getElementById("batteryBar");
                if (batteryBar) batteryBar.style.width = batPct + "%";
                
                const batteryChargeText = document.getElementById("batteryChargeText");
                if (batteryChargeText) batteryChargeText.innerText = "Charge State: " + batPct + "%";
                
                const batteryHealthText = document.getElementById("batteryHealthText");
                if (batteryHealthText) {
                    if (volt < 3.3) {
                        batteryHealthText.innerText = "CRITICALLY LOW";
                        batteryHealthText.className = "text-red-500 font-bold";
                    } else if (volt < 3.5) {
                        batteryHealthText.innerText = "LOW POWER";
                        batteryHealthText.className = "text-amber-500 font-bold";
                    } else {
                        batteryHealthText.innerText = "Health: Optimal";
                        batteryHealthText.className = "text-secondary font-bold";
                    }
                }
            }

            const status = document.getElementById("motorStatus");"""

js = js.replace(calculated_poll_old, calculated_poll_new)

alerts_old = """            /* ---------- ALERTS ---------- */
            const badge = document.getElementById("alertBadge");
            if (pct <= 10) {
                badge.style.display = "inline-block";
                badge.innerText = "CRITICAL LOW";
                badge.style.background = "var(--danger)";
                badge.style.color = "white";
                badge.style.animation = "alertFlash 1s infinite";
            }
            else if (pct >= 95) {
                badge.style.display = "inline-block";
                badge.innerText = "TANK FULL";
                badge.style.background = "var(--success)";
                badge.style.color = "white";
                badge.style.animation = "none";
            }
            else {
                badge.style.display = "none";
            }"""

alerts_new = """            /* ---------- ALERTS ---------- */
            const badge = document.getElementById("alertBadge");
            const noAlertText = document.getElementById("noAlertText");
            if (pct <= 10) {
                badge.style.display = "inline-block";
                badge.innerText = "CRITICAL LOW";
                badge.className = "status-pill text-xs font-bold uppercase py-0.5 px-2 rounded bg-error text-on-error-container pulse-active";
                if (noAlertText) noAlertText.style.display = "none";
            }
            else if (pct >= 95) {
                badge.style.display = "inline-block";
                badge.innerText = "TANK FULL";
                badge.className = "status-pill text-xs font-bold uppercase py-0.5 px-2 rounded bg-secondary text-on-secondary-container";
                if (noAlertText) noAlertText.style.display = "none";
            }
            else {
                badge.style.display = "none";
                if (noAlertText) noAlertText.style.display = "inline";
            }"""

js = js.replace(alerts_old, alerts_new)

motor_state_poll_old = """        if (motor.MOTOR_MODE === 1) {
            // MANUAL MODE
            if (motor.MOTOR_MANUAL_STATUS === 1) {
                status.innerText = "⚡ MOTOR ON (MANUAL)";
                status.className = "motor-status motor-on";
                btnOn.classList.add("active");
            } else {
                status.innerText = "⛔ MOTOR OFF (MANUAL)";
                status.className = "motor-status motor-off";
                btnOff.classList.add("active");
            }
        } else {
            // AUTO MODE — read status from calc data
            try {
                const calc = await (await fetch("/api/calculated/?mac=" + activeDeviceMac)).json();
                if (calc.MOTOR_STATUS === 1) {
                    status.innerText = "⚡ MOTOR ON (AUTO)";
                    status.className = "motor-status motor-on";
                } else {
                    status.innerText = "⛔ MOTOR OFF (AUTO)";
                    status.className = "motor-status motor-off";
                }
            } catch(e) {
                status.innerText = "AUTO MODE";
                status.className = "motor-status motor-auto";
            }
            btnAuto.classList.add("active");
        }"""

motor_state_poll_new = """        // Reset button active styles in Tailwind
        btnOn.className = "py-3 bg-outline-variant/20 text-outline rounded-lg text-xs font-bold uppercase tracking-wider transition-all hover:bg-outline-variant/30";
        btnOff.className = "py-3 bg-outline-variant/20 text-outline rounded-lg text-xs font-bold uppercase tracking-wider transition-all hover:bg-outline-variant/30";
        btnAuto.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface";
        const btnManualMode = document.getElementById("btnManualMode");
        btnManualMode.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface";

        if (motor.MOTOR_MODE === 1) {
            // MANUAL MODE
            btnManualMode.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all bg-[#282a2d] text-[#9ccaff] font-bold shadow-sm";
            if (motor.MOTOR_MANUAL_STATUS === 1) {
                status.innerText = "Active - Running (Manual)";
                status.className = "font-headline font-bold text-lg text-secondary";
                btnOn.className = "py-3 bg-secondary text-on-secondary rounded-lg text-xs font-bold uppercase tracking-wider transition-all shadow-md";
            } else {
                status.innerText = "Stopped (Manual)";
                status.className = "font-headline font-bold text-lg text-outline";
                btnOff.className = "py-3 bg-tertiary-container text-white rounded-lg text-xs font-bold uppercase tracking-wider transition-all shadow-md";
            }
        } else {
            // AUTO MODE — read status from calc data
            btnAuto.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all bg-[#282a2d] text-[#9ccaff] font-bold shadow-sm";
            try {
                const calc = await (await fetch("/api/calculated/?mac=" + activeDeviceMac)).json();
                if (calc.MOTOR_STATUS === 1) {
                    status.innerText = "Active - Running (Auto)";
                    status.className = "font-headline font-bold text-lg text-secondary";
                } else {
                    status.innerText = "Stopped (Auto)";
                    status.className = "font-headline font-bold text-lg text-outline";
                }
            } catch(e) {
                status.innerText = "Active - Auto Mode";
                status.className = "font-headline font-bold text-lg text-outline";
            }
        }"""

js = js.replace(motor_state_poll_old, motor_state_poll_new)

chart_filters_old = """function switchTimeRange(btn) {
    document.querySelectorAll(".time-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentHours = parseInt(btn.dataset.hours);
    renderChartsFromCache(); // Re-filter and render without re-fetching
}"""

chart_filters_new = """function switchTimeRange(btn) {
    document.querySelectorAll(".time-btn").forEach(b => {
        b.className = "time-btn px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline hover:text-on-surface";
    });
    btn.className = "time-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-[#282a2d] text-[#9ccaff] font-bold shadow-sm";
    currentHours = parseInt(btn.dataset.hours);
    renderChartsFromCache(); // Re-filter and render without re-fetching
}"""

js = js.replace(chart_filters_old, chart_filters_new)

toggle_dataset_old = """function toggleDataset(index, btn) {
    const meta = chartMain.getDatasetMeta(index);
    meta.hidden = meta.hidden === null ? !chartMain.data.datasets[index].hidden : null;
    
    if (meta.hidden) {
        btn.classList.remove("active");
        btn.style.opacity = "0.4";
        btn.style.background = "transparent";
    } else {
        btn.classList.add("active");
        btn.style.opacity = "1";
        // Restore background based on index
        const colors = ["rgba(59,130,246,0.1)", "rgba(245,158,11,0.1)", "rgba(139,92,246,0.1)"];
        btn.style.background = colors[index];
    }
    chartMain.update();
}"""

toggle_dataset_new = """function toggleDataset(index, btn) {
    const meta = chartMain.getDatasetMeta(index);
    meta.hidden = meta.hidden === null ? !chartMain.data.datasets[index].hidden : null;
    
    if (meta.hidden) {
        btn.className = "filter-btn px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline opacity-40";
    } else {
        const activeColors = [
            "filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-primary-container/20 text-[#9ccaff]",
            "filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-amber-500/10 text-amber-500",
            "filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-purple-500/10 text-purple-500"
        ];
        btn.className = activeColors[index];
    }
    chartMain.update();
}"""

js = js.replace(toggle_dataset_old, toggle_dataset_new)

# 5. Read stitch_screen.html
with open("stitch_screen.html", "r", encoding="utf-8") as f:
    layout = f.read()

# 6. Declare layout injections
head_inject = """
    <link rel="manifest" href="{% static 'manifest.json' %}">
    <meta name="theme-color" content="#111316">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3/dist/chartjs-plugin-annotation.min.js"></script>
"""

head_styles = """
        .gauge-track {
            stroke: #1e2023;
            stroke-dasharray: 270 360;
        }
        .gauge-value {
            stroke: #9ccaff;
            stroke-dasharray: 0 360;
            transition: stroke-dasharray 0.5s ease-in-out;
        }
        .pulse-active {
            animation: pulse-light 1.5s infinite;
        }
        @keyframes pulse-light {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }
"""

extra_bento_cards = """
    <!-- Card 5: System Configuration Card -->
    <div class="md:col-span-4 bg-surface-container rounded-xl p-8 flex flex-col justify-between border border-outline-variant/10">
        <div>
            <div class="flex justify-between items-start mb-6">
                <h3 class="font-headline font-bold uppercase tracking-tight text-xl">System Config</h3>
                <span class="material-symbols-outlined text-primary">tune</span>
            </div>
            <div class="space-y-3">
                <div class="flex flex-col gap-1">
                    <label class="font-bold text-[10px] text-outline uppercase">Tank Height (meters)</label>
                    <input id="totalHeight" type="number" placeholder="e.g. 3.0" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-3 text-sm text-on-surface focus:outline-none focus:border-primary">
                </div>
                <div class="flex flex-col gap-1">
                    <label class="font-bold text-[10px] text-outline uppercase">Tank Volume (Liters)</label>
                    <input id="totalVolume" type="number" placeholder="e.g. 5000" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-3 text-sm text-on-surface focus:outline-none focus:border-primary">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div class="flex flex-col gap-1">
                        <label class="font-bold text-[10px] text-outline uppercase">Min Level (%)</label>
                        <input id="minPercentage" type="number" placeholder="e.g. 20" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-3 text-sm text-on-surface focus:outline-none focus:border-primary">
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="font-bold text-[10px] text-outline uppercase">Max Level (%)</label>
                        <input id="maxPercentage" type="number" placeholder="e.g. 90" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-3 text-sm text-on-surface focus:outline-none focus:border-primary">
                    </div>
                </div>
                
                <div class="flex items-center justify-between p-3 bg-[#111316] border border-outline-variant rounded-lg text-xs mt-2">
                    <label for="deepSleepToggle" class="font-semibold text-outline cursor-pointer select-none">Enable Deep Sleep</label>
                    <input id="deepSleepToggle" type="checkbox" class="rounded border-outline-variant bg-[#111316] text-primary focus:ring-primary w-4 h-4 cursor-pointer">
                </div>
                
                <div class="flex flex-col gap-1">
                    <label class="font-bold text-[10px] text-outline uppercase">Sleep Interval (seconds)</label>
                    <input id="sleepInterval" type="number" placeholder="e.g. 300" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-3 text-sm text-on-surface focus:outline-none focus:border-primary">
                </div>
            </div>
        </div>
        <button class="w-full py-4 mt-6 bg-gradient-to-r from-primary to-primary-container rounded-xl font-headline font-bold uppercase tracking-widest text-on-primary text-sm hover:opacity-90 transition-all flex items-center justify-center gap-2 shadow-md" onclick="sendInput()">
            <span class="material-symbols-outlined text-lg">save</span> Update Sensor
        </button>
    </div>

    <!-- Card 5b: Stored display variables overlay -->
    <div class="bg-surface-container rounded-xl p-6 md:col-span-8 border border-outline-variant/10 flex flex-col justify-center">
        <p class="text-[10px] text-outline font-bold uppercase tracking-widest mb-3">Stored Configurations</p>
        <div class="grid grid-cols-2 sm:grid-cols-6 gap-4 text-xs text-outline">
            <div class="bg-surface-container-high p-3 rounded-lg">
                <span class="block text-[9px] opacity-75 mb-1">Height</span>
                <span id="storedHeight" class="font-bold text-on-surface">--</span> m
            </div>
            <div class="bg-surface-container-high p-3 rounded-lg">
                <span class="block text-[9px] opacity-75 mb-1">Volume</span>
                <span id="storedVolume" class="font-bold text-on-surface">--</span> L
            </div>
            <div class="bg-surface-container-high p-3 rounded-lg">
                <span class="block text-[9px] opacity-75 mb-1">Min Level</span>
                <span id="storedMin" class="font-bold text-on-surface">--</span> %
            </div>
            <div class="bg-surface-container-high p-3 rounded-lg">
                <span class="block text-[9px] opacity-75 mb-1">Max Level</span>
                <span id="storedMax" class="font-bold text-on-surface">--</span> %
            </div>
            <div class="bg-surface-container-high p-3 rounded-lg">
                <span class="block text-[9px] opacity-75 mb-1">Deep Sleep</span>
                <span id="storedDeepSleep" class="font-bold text-on-surface">--</span>
            </div>
            <div class="bg-surface-container-high p-3 rounded-lg">
                <span class="block text-[9px] opacity-75 mb-1">Interval</span>
                <span id="storedSleepInterval" class="font-bold text-on-surface">--</span> s
            </div>
        </div>
    </div>

    <!-- Card 6: Log Table Card -->
    <div class="col-span-full bg-surface-container rounded-xl p-8 flex flex-col justify-between mt-6 border border-outline-variant/10">
        <div class="flex justify-between items-center mb-6">
            <div>
                <h3 class="font-headline font-bold uppercase tracking-tight text-xl">Operational Logs</h3>
                <p class="text-[10px] text-outline font-bold uppercase tracking-widest">Historical State Transitions</p>
            </div>
            <button class="py-2.5 px-4 bg-surface-container-high border border-outline-variant hover:bg-outline-variant/30 text-on-surface font-bold text-xs uppercase tracking-wider rounded-lg flex items-center gap-2 transition-all shadow-sm" onclick="exportCSV()">
                <span class="material-symbols-outlined text-sm">download</span> Export CSV
            </button>
        </div>

        <div class="overflow-x-auto rounded-xl border border-outline-variant bg-surface-container-lowest">
            <table class="w-full text-left border-collapse text-xs">
                <thead>
                    <tr class="bg-surface-container-high border-b border-outline-variant text-[10px] text-outline font-bold uppercase tracking-wider">
                        <th class="p-4">Timestamp</th>
                        <th class="p-4">Water Level</th>
                        <th class="p-4">Volume</th>
                        <th class="p-4">Distance</th>
                        <th class="p-4">Battery</th>
                        <th class="p-4">Mode</th>
                        <th class="p-4">Motor Status</th>
                    </tr>
                </thead>
                <tbody id="logsBody" class="divide-y divide-outline-variant/10">
                    <tr>
                        <td colspan="7" class="p-8 text-center text-outline italic">Initializing logs...</td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="flex justify-between items-center mt-6 pt-4 border-t border-outline-variant/10">
            <div class="flex gap-2">
                <button id="btnPrevPage" class="px-4 py-2 border border-outline-variant text-outline hover:text-on-surface hover:bg-surface-container-high disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all" onclick="logsPage(-1)">PREV</button>
                <button id="btnNextPage" class="px-4 py-2 border border-outline-variant text-outline hover:text-on-surface hover:bg-surface-container-high disabled:opacity-40 disabled:cursor-not-allowed rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all" onclick="logsPage(1)">NEXT</button>
            </div>
            <span id="paginationInfo" class="text-xs text-outline font-medium"></span>
        </div>
    </div>
"""

modal_html = """
    <!-- Add Device Modal Overlay -->
    <div id="addDeviceModal" class="fixed inset-0 bg-slate-900/80 backdrop-blur-sm z-50 hidden items-center justify-center p-4">
        <div class="bg-surface-container border border-outline-variant max-w-md w-full rounded-2xl p-6 shadow-2xl relative">
            <button onclick="closeModal()" class="absolute top-4 right-4 text-outline hover:text-on-surface">
                <span class="material-symbols-outlined">close</span>
            </button>
            <h3 class="font-headline font-bold text-lg text-on-surface mb-4">Add Tank Device</h3>
            
            <!-- Tabs -->
            <div class="flex border-b border-outline-variant/30 mb-4 text-sm font-medium">
                <button id="tabBleBtn" onclick="switchTab('ble')" class="flex-1 pb-3 text-center border-b-2 border-primary text-primary font-semibold">
                    Bluetooth Setup
                </button>
                <button id="tabManualBtn" onclick="switchTab('manual')" class="flex-1 pb-3 text-center border-b-2 border-transparent text-outline hover:text-on-surface">
                    Manual Claim
                </button>
            </div>
            
            <!-- BLE Tab Content -->
            <div id="tabBle" class="space-y-4 flex flex-col">
                <p class="text-xs text-outline leading-relaxed">Configure Wi-Fi settings for a nearby sensor device via Web Bluetooth.</p>
                
                <div class="flex items-center gap-2 text-xs text-outline">
                    <input type="checkbox" id="bleScanAll" class="rounded border-outline-variant bg-[#111316] text-primary focus:ring-primary w-4 h-4 cursor-pointer">
                    <label for="bleScanAll" class="cursor-pointer select-none">Show all nearby Bluetooth devices (skip name filter)</label>
                </div>
                
                <details class="text-xs text-outline cursor-pointer select-none">
                    <summary class="font-semibold text-primary">Advanced BLE UUID Settings</summary>
                    <div class="mt-2 p-3 bg-[#111316] border border-outline-variant rounded-lg space-y-2">
                        <div class="flex flex-col gap-1 cursor-default">
                            <label class="font-bold text-[10px] text-outline">Service UUID:</label>
                            <input id="bleServiceUuidInput" type="text" value="12345678-1234-1234-1234-123456789abc" class="w-full bg-[#1e2023] border border-outline-variant rounded p-1.5 text-[10px] font-mono text-on-surface">
                        </div>
                        <div class="flex flex-col gap-1 cursor-default">
                            <label class="font-bold text-[10px] text-outline">Characteristic UUID:</label>
                            <input id="bleCharUuidInput" type="text" value="87654321-4321-4321-4321-cba987654321" class="w-full bg-[#1e2023] border border-outline-variant rounded p-1.5 text-[10px] font-mono text-on-surface">
                        </div>
                    </div>
                </details>
                
                <button id="btnBleScan" onclick="scanBleDevice()" class="w-full py-3 bg-[#0077c1] hover:bg-opacity-95 text-white font-semibold rounded-lg text-sm flex items-center justify-center gap-2">
                    <span class="material-symbols-outlined text-lg">bluetooth_searching</span> Scan Nearby Device
                </button>
                
                <div id="blePairedContainer" class="hidden justify-between items-center p-3 bg-[#111316] border border-outline-variant rounded-lg text-xs">
                    <span class="font-semibold text-outline">Paired:</span>
                    <span id="pairedDeviceName" class="font-bold text-secondary">--</span>
                </div>
                
                <!-- BLE credentials form -->
                <div id="bleCredentialsForm" class="hidden flex-col gap-3">
                    <input id="bleMacAddress" type="hidden" value="">
                    <input id="bleSerialNumber" type="hidden" value="SN-UNKNOWN">
                    <input id="bleDeviceName" type="hidden" value="Water Tank">
                    <input id="bleTotalHeight" type="hidden" value="3.0">
                    <input id="bleTotalVolume" type="hidden" value="1000.0">
                    <input id="bleMinPercentage" type="hidden" value="20.0">
                    <input id="bleMaxPercentage" type="hidden" value="90.0">
                    <input id="bleDeepSleep" type="hidden" value="0">
                    <input id="bleSleepInterval" type="hidden" value="300">
                    
                    <div class="text-xs font-bold text-outline mt-2">Enter Wi-Fi Credentials for Sensor:</div>
                    <input id="bleWifiSsid" type="text" placeholder="WiFi Network Name (SSID)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <input id="bleWifiPass" type="password" placeholder="WiFi Password" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <button id="btnBleConfigure" onclick="configureBleDevice()" class="w-full py-3 bg-secondary hover:bg-opacity-95 text-on-secondary font-bold rounded-lg text-sm">
                        ⚙️ Configure Device
                    </button>
                </div>
                <div id="bleStatus" class="text-xs text-center text-outline font-semibold"></div>
            </div>
            
            <!-- Manual Tab Content -->
            <div id="tabManual" class="hidden space-y-4 flex flex-col">
                <p class="text-xs text-outline leading-relaxed">Claim a sensor that is already connected to WiFi and broadcasting telemetry.</p>
                <div class="space-y-3">
                    <input id="claimDeviceName" type="text" placeholder="Device Name (e.g. Roof Tank)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <input id="claimMacAddress" type="text" placeholder="MAC Address (e.g. EC:E3:34:1B:BB:08)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <input id="claimSerialNumber" type="text" placeholder="Serial Number (e.g. SN-123456)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <input id="claimTotalHeight" type="number" step="0.1" placeholder="Tank Height (meters)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <input id="claimTotalVolume" type="number" step="10" placeholder="Tank Volume (Liters)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <input id="claimMinPercentage" type="number" value="20" placeholder="Min Level (%)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <input id="claimMaxPercentage" type="number" value="90" placeholder="Max Level (%)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <div class="flex items-center justify-between p-2.5 bg-[#111316] border border-outline-variant rounded-lg text-xs">
                        <label for="claimDeepSleep" class="font-semibold text-outline cursor-pointer select-none">Enable Deep Sleep</label>
                        <input id="claimDeepSleep" type="checkbox" class="rounded border-outline-variant bg-[#111316] text-primary focus:ring-primary w-4 h-4 cursor-pointer">
                    </div>
                    <input id="claimSleepInterval" type="number" value="300" placeholder="Sleep Interval (sec)" class="w-full bg-[#111316] border border-outline-variant rounded-lg p-2.5 text-sm text-on-surface">
                    <button id="btnClaimSubmit" onclick="submitManualClaim()" class="w-full py-3 bg-[#0077c1] hover:bg-opacity-95 text-white font-bold rounded-lg text-sm">
                        💾 Register Device
                    </button>
                </div>
                <div id="claimStatus" class="text-xs text-center text-outline font-semibold"></div>
            </div>
        </div>
    </div>

    <!-- Alert Buzzers -->
    <audio id="buzzerLow" loop>
        <source src="https://actions.google.com/sounds/v1/alarms/beep_short.ogg" type="audio/ogg">
    </audio>
    <audio id="buzzerFull">
        <source src="https://actions.google.com/sounds/v1/cartoon/clang_and_wobble.ogg" type="audio/ogg">
    </audio>
"""

mobile_nav_old = """<!-- Bottom Navigation (Mobile Only) -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 bg-[#111316] h-16 flex items-center justify-around z-50 px-6 border-t border-outline-variant/10">
<div class="flex flex-col items-center gap-1 text-[#9ccaff] font-bold">
<span class="material-symbols-outlined">dashboard</span>
<span class="text-[10px] uppercase">Home</span>
</div>
<div class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70">
<span class="material-symbols-outlined">monitoring</span>
<span class="text-[10px] uppercase">Data</span>
</div>
<div class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70">
<span class="material-symbols-outlined">settings</span>
<span class="text-[10px] uppercase">Config</span>
</div>
</nav>"""

mobile_nav_new = """<!-- Bottom Navigation (Mobile Only) -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 bg-[#111316] h-16 flex items-center justify-around z-50 px-6 border-t border-outline-variant/10">
    <div class="flex flex-col items-center gap-1 text-[#9ccaff] font-bold cursor-pointer">
        <span class="material-symbols-outlined">dashboard</span>
        <span class="text-[10px] uppercase font-headline">Home</span>
    </div>
    <div onclick="openModal()" class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70 cursor-pointer hover:opacity-100">
        <span class="material-symbols-outlined">add_circle</span>
        <span class="text-[10px] uppercase font-headline">Add</span>
    </div>
    <div onclick="toggleDark()" class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70 cursor-pointer hover:opacity-100">
        <span class="material-symbols-outlined">settings</span>
        <span class="text-[10px] uppercase font-headline">Config</span>
    </div>
</nav>"""

# 7. Apply layout customizations
layout = "{% load static %}\n" + layout

# Inject manifest, Chart.js libraries
layout = layout.replace("</head>", head_inject + "</head>")

# Add circular gauge variables & alert animations to styles
layout = layout.replace("</style>", head_styles + "</style>")

# Replace top header text & insert heartbeat placeholder
top_navbar_old = """<header class="w-full h-16 flex items-center bg-[#111316] dark:bg-slate-950 px-6 justify-between z-50 fixed top-0">
<div class="flex items-center gap-4">
<span class="text-xl font-bold text-[#9ccaff] tracking-tighter font-headline">Synthetic Aquifer</span>"""

top_navbar_new = """<header class="w-full h-16 flex items-center bg-[#111316] dark:bg-[#0c0e11] px-6 justify-between z-50 fixed top-0 border-b border-outline-variant/10">
<div class="flex items-center gap-4">
<span class="text-xl font-bold text-[#9ccaff] tracking-tighter font-headline">HydroFlow</span>
<span class="text-[11px] text-outline bg-surface-container-high px-2.5 py-1 rounded-md font-mono hidden sm:inline" id="lastUpdated">Last Heartbeat: Waiting for data...</span>"""

layout = layout.replace(top_navbar_old, top_navbar_new)

# Replace top navbar status indicators with dynamic sensor indicator and theme toggler
status_old = """<div class="flex items-center gap-4">
<span class="material-symbols-outlined text-[#9ccaff] cursor-pointer active:opacity-80">notifications</span>
<span class="material-symbols-outlined text-[#9ccaff] cursor-pointer active:opacity-80">water_drop</span>"""

status_new = """<div class="flex items-center gap-4">
<div id="sensorPill" class="flex items-center gap-2 bg-[#1e2023] px-3 py-1 rounded-full text-xs font-semibold text-outline-variant">
    <div id="sensorDot" class="w-2.5 h-2.5 rounded-full bg-outline"></div>
    <span id="sensorLabel">Waiting for sensor...</span>
</div>
<button onclick="toggleDark()" class="w-8 h-8 rounded-full bg-surface-container flex items-center justify-center border border-outline-variant/15 hover:bg-outline-variant/30 transition-all text-sm" id="themeBall">🌙</button>"""

layout = layout.replace(status_old, status_new)

# Replace Left Sidebar content to inject active dropdown selector and config button
sidebar_old = """<aside class="hidden lg:flex flex-col h-screen w-64 fixed left-0 top-0 bg-[#1a1c1f] dark:bg-slate-900 py-8 z-40">
<div class="px-6 mb-12 flex flex-col gap-1">
<div class="w-12 h-12 bg-surface-container-high rounded-xl mb-4 flex items-center justify-center">
<span class="material-symbols-outlined text-primary text-3xl">waves</span>
</div>
<h2 class="text-on-surface font-headline font-bold text-lg">Aquifer-01</h2>
<p class="text-secondary text-[10px] font-semibold uppercase tracking-widest">Active Flow</p>
</div>"""

sidebar_new = """<aside class="hidden lg:flex flex-col h-screen w-64 fixed left-0 top-0 bg-[#1a1c1f] dark:bg-slate-900 py-8 z-40 border-r border-outline-variant/10">
<div class="px-6 mb-6 flex flex-col gap-1 mt-16">
<div class="w-12 h-12 bg-surface-container-high rounded-xl mb-4 flex items-center justify-center">
<span class="material-symbols-outlined text-primary text-3xl">waves</span>
</div>
<h2 class="text-on-surface font-headline font-bold text-lg">HydroFlow Node</h2>
<p class="text-secondary text-[10px] font-semibold uppercase tracking-widest">Active Tank</p>
</div>

<!-- Device Selection Dropdown -->
<div class="px-6 mb-4">
    <label for="deviceSelector" class="text-outline text-[10px] font-bold uppercase tracking-widest block mb-2">Select Active Tank</label>
    <select id="deviceSelector" onchange="changeDevice(this.value)" class="w-full bg-[#111316] border border-outline-variant rounded-lg text-sm text-on-surface py-2.5 px-3 focus:outline-none focus:border-primary cursor-pointer">
        <!-- Options populated dynamically -->
    </select>
</div>

<!-- Add Device Button -->
<div class="px-6 mb-6">
    <button onclick="openModal()" class="w-full py-3 bg-[#0077c1] hover:bg-opacity-95 text-white rounded-lg font-headline uppercase text-xs font-bold tracking-wider transition-all flex items-center justify-center gap-2 shadow-md">
        <span class="material-symbols-outlined text-sm">add</span> Add Tank Device
    </button>
</div>"""

layout = layout.replace(sidebar_old, sidebar_new)

# Simplify sidebar navigation items
nav_old = """<ul class="space-y-1">
<li class="bg-[#0077c1] text-white rounded-r-full mr-4 px-6 py-3 flex items-center gap-4 cursor-pointer transition-all">
<span class="material-symbols-outlined">dashboard</span>
<span class="font-headline uppercase text-xs font-semibold">Overview</span>
</li>
<li class="text-[#e2e2e6] hover:text-[#9ccaff] hover:bg-[#282a2d] px-6 py-3 flex items-center gap-4 cursor-pointer transition-all">
<span class="material-symbols-outlined">monitoring</span>
<span class="font-headline uppercase text-xs font-semibold">Analytics</span>
</li>
<li class="text-[#e2e2e6] hover:text-[#9ccaff] hover:bg-[#282a2d] px-6 py-3 flex items-center gap-4 cursor-pointer transition-all">
<span class="material-symbols-outlined">settings</span>
<span class="font-headline uppercase text-xs font-semibold">Settings</span>
</li>
</ul>"""

nav_new = """<ul class="space-y-1">
<li class="bg-[#0077c1]/10 text-primary border-r-4 border-primary px-6 py-3 flex items-center gap-4 cursor-pointer transition-all">
<span class="material-symbols-outlined">dashboard</span>
<span class="font-headline uppercase text-xs font-bold tracking-wider">Overview</span>
</li>
</ul>"""

layout = layout.replace(nav_old, nav_new)

# Update page titles and alerts in header
header_old = """<div>
<h1 class="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase">HydroFlow Dashboard</h1>
<p class="text-outline text-sm mt-1">System Node: North-Wing Main Reservoirs</p>
</div>
<div class="glass-overlay p-4 rounded-xl flex items-center gap-6">
<div class="flex flex-col">
<span class="text-[10px] text-outline font-semibold uppercase tracking-widest">System Status</span>
<div class="flex items-center gap-2">
<div class="w-2 h-2 rounded-full bg-secondary animate-pulse"></div>
<span class="text-secondary font-headline text-sm font-bold uppercase">Optimal</span>
</div>
</div>
<div class="w-px h-8 bg-outline-variant/30"></div>
<div class="flex flex-col">
<span class="text-[10px] text-outline font-semibold uppercase tracking-widest">Network</span>
<span class="text-on-surface font-headline text-sm font-bold uppercase">98 ms</span>
</div>
</div>"""

header_new = """<div>
<h1 class="text-4xl font-headline font-bold tracking-tight text-on-surface uppercase" id="activeDeviceNameDisplay">HydroFlow Dashboard</h1>
<p class="text-outline text-sm mt-1" id="activeDeviceMacDisplay">Select or claim a device to start tracking</p>
</div>
<div class="glass-overlay p-4 rounded-xl flex items-center gap-6 border border-outline-variant/15">
<div class="flex flex-col">
<span class="text-[10px] text-outline font-semibold uppercase tracking-widest">System Alerts</span>
<div class="flex items-center gap-2 mt-1">
<span id="alertBadge" class="status-pill text-xs font-bold uppercase py-0.5 px-2 rounded hidden" style="background: var(--danger); color: white;">CRITICAL</span>
<span id="noAlertText" class="text-secondary font-headline text-sm font-bold uppercase">Normal</span>
</div>
</div>
</div>"""

layout = layout.replace(header_old, header_new)

# Replace SVG circular gauge and tank metadata panel
gauge_old = """<div class="relative w-64 h-64 flex items-center justify-center">
<svg class="w-full h-full -rotate-225" viewbox="0 0 120 120">
<circle class="gauge-track" cx="60" cy="60" fill="none" r="50" stroke-linecap="round" stroke-width="8"></circle>
<circle class="gauge-value" cx="60" cy="60" fill="none" r="50" stroke-dashoffset="0" stroke-linecap="round" stroke-width="8"></circle>
</svg>
<div class="absolute inset-0 flex flex-col items-center justify-center text-center">
<span class="text-6xl font-headline font-bold text-on-surface tracking-tighter">65<span class="text-2xl opacity-50">%</span></span>
<span class="text-[10px] font-bold text-primary uppercase tracking-[0.2em] mt-1">Water Level</span>
</div>
</div>
<!-- Tank Info Details -->
<div class="flex-grow space-y-8 max-w-xs w-full">
<div class="bg-surface-container-lowest p-5 rounded-lg border-l-2 border-primary">
<div class="flex justify-between items-center mb-1">
<span class="text-[10px] text-outline font-bold uppercase">Current Volume</span>
<span class="material-symbols-outlined text-primary text-lg">opacity</span>
</div>
<div class="text-3xl font-headline font-bold text-on-surface">14,250 <span class="text-sm font-normal text-outline">Liters</span></div>
</div>
<div class="grid grid-cols-2 gap-4">
<div class="bg-surface-container-high p-4 rounded-lg">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Tank Height</span>
<div class="text-xl font-headline font-bold text-on-surface">2.5m</div>
</div>
<div class="bg-surface-container-high p-4 rounded-lg">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Sensor Offset</span>
<div class="text-xl font-headline font-bold text-on-surface">12cm</div>
</div>
</div>
</div>"""

gauge_new = """<div class="relative w-64 h-64 flex items-center justify-center">
<svg class="w-full h-full -rotate-225" viewbox="0 0 120 120">
<circle class="gauge-track" cx="60" cy="60" fill="none" r="50" stroke-linecap="round" stroke-width="8"></circle>
<circle class="gauge-value" id="gaugeValue" cx="60" cy="60" fill="none" r="50" stroke-dashoffset="0" stroke-linecap="round" stroke-width="8"></circle>
</svg>
<div class="absolute inset-0 flex flex-col items-center justify-center text-center">
<span class="text-5xl font-headline font-bold text-on-surface tracking-tighter" id="percentage">--</span>
<span class="text-[10px] font-bold text-primary uppercase tracking-[0.2em] mt-1">Water Level</span>
</div>
</div>
<!-- Tank Info Details -->
<div class="flex-grow space-y-4 max-w-xs w-full">
<div class="bg-surface-container-lowest p-5 rounded-lg border-l-2 border-primary">
<div class="flex justify-between items-center mb-1">
<span class="text-[10px] text-outline font-bold uppercase">Current Volume</span>
<span class="material-symbols-outlined text-primary text-lg">opacity</span>
</div>
<div class="text-3xl font-headline font-bold text-on-surface"><span id="filledVolume">--</span> <span class="text-sm font-normal text-outline">Liters</span></div>
</div>
<div class="grid grid-cols-2 gap-4">
<div class="bg-surface-container-high p-4 rounded-lg">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Sensor Dist</span>
<div class="text-xl font-headline font-bold text-on-surface" id="distanceVal">--</div>
</div>
<div class="bg-surface-container-high p-4 rounded-lg">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Total Height</span>
<div class="text-xl font-headline font-bold text-on-surface" id="displayHeight">--</div>
</div>
</div>
</div>"""

layout = layout.replace(gauge_old, gauge_new)

# Replace Motor override block
motor_old = """<!-- Motor Control Panel -->
<div class="md:col-span-4 bg-surface-container rounded-xl p-8 flex flex-col justify-between">
<div>
<div class="flex justify-between items-start mb-6">
<h3 class="font-headline font-bold uppercase tracking-tight text-xl">Motor Control</h3>
<span class="material-symbols-outlined text-tertiary">settings_input_component</span>
</div>
<div class="flex items-center justify-between bg-surface-container-lowest p-6 rounded-xl mb-6">
<div>
<p class="text-sm font-bold text-on-surface uppercase">Pump Status</p>
<p class="text-xs text-secondary font-semibold">Active - Running</p>
</div>
<!-- Toggle Switch -->
<div class="w-14 h-8 bg-secondary-container rounded-full relative cursor-pointer shadow-inner">
<div class="absolute right-1 top-1 w-6 h-6 bg-surface-bright rounded-full shadow-md"></div>
</div>
</div>
<div class="space-y-4">
<div class="flex items-center gap-3 p-3 bg-surface-container-high rounded-lg">
<span class="material-symbols-outlined text-primary-fixed-dim text-xl" style="font-variation-settings: 'FILL' 1;">info</span>
<p class="text-[11px] leading-tight text-on-surface-variant font-medium">
<span class="text-primary font-bold uppercase block mb-1">Automation Logic</span>
                                Auto-Off at >90%, Auto-On at <10%
                            </p>
</div>
</div>
</div>
<button class="w-full py-4 mt-8 bg-gradient-to-r from-primary to-primary-container rounded-xl font-headline font-bold uppercase tracking-widest text-on-primary text-sm hover:opacity-90 transition-all flex items-center justify-center gap-2">
<span class="material-symbols-outlined text-xl">power_settings_new</span>
                    Emergency Shutoff
                </button>
</div>"""

motor_new = """<!-- Motor Control Panel -->
<div class="md:col-span-4 bg-surface-container rounded-xl p-8 flex flex-col justify-between border border-outline-variant/10">
    <div>
        <div class="flex justify-between items-start mb-6">
            <h3 class="font-headline font-bold uppercase tracking-tight text-xl">Motor Control</h3>
            <span class="material-symbols-outlined text-tertiary">settings_input_component</span>
        </div>
        
        <div class="bg-surface-container-lowest p-5 rounded-xl mb-6">
            <p class="text-[10px] text-outline font-bold uppercase block mb-2">Pump Status</p>
            <div id="motorStatus" class="font-headline font-bold text-lg text-outline">Checking...</div>
        </div>

        <div class="space-y-4">
            <div>
                <p class="text-[10px] text-outline font-bold uppercase mb-2">Control Mode</p>
                <div class="grid grid-cols-2 gap-2 bg-surface-container-lowest p-1 rounded-xl">
                    <button id="btnAuto" onclick="motorAuto()" class="py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface">Auto Mode</button>
                    <button id="btnManualMode" class="py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface">Manual</button>
                </div>
            </div>

            <div id="manualControlsBlock" class="space-y-2">
                <p class="text-[10px] text-outline font-bold uppercase mb-2">Manual Override</p>
                <div class="grid grid-cols-2 gap-3">
                    <button id="btnOn" onclick="motorOn()" class="py-3 bg-outline-variant/20 text-outline rounded-lg text-xs font-bold uppercase tracking-wider transition-all">START</button>
                    <button id="btnOff" onclick="motorOff()" class="py-3 bg-outline-variant/20 text-outline rounded-lg text-xs font-bold uppercase tracking-wider transition-all">STOP</button>
                </div>
            </div>
        </div>
    </div>
    
    <button onclick="motorOff()" class="w-full py-4 mt-8 bg-gradient-to-r from-red-600 to-red-800 rounded-xl font-headline font-bold uppercase tracking-widest text-white text-sm hover:opacity-90 transition-all flex items-center justify-center gap-2 shadow-md">
        <span class="material-symbols-outlined text-xl">power_settings_new</span>
        Emergency Shutoff
    </button>
</div>"""

layout = layout.replace(motor_old, motor_new)

# Replace Power Node
power_old = """<!-- Battery Health Section -->
<div class="md:col-span-4 bg-surface-container rounded-xl p-8 overflow-hidden group">
<div class="flex justify-between items-center mb-8">
<h3 class="font-headline font-bold uppercase tracking-tight text-xl">Power Node</h3>
<span class="material-symbols-outlined text-secondary" style="font-variation-settings: 'FILL' 1;">battery_charging_80</span>
</div>
<div class="flex items-end gap-2 mb-2">
<span class="text-5xl font-headline font-bold text-on-surface">12.4</span>
<span class="text-xl font-headline text-outline mb-1 font-bold">V</span>
</div>
<p class="text-[10px] text-outline font-bold uppercase tracking-widest mb-8">System Voltage Level</p>
<div class="space-y-6">
<div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
<div class="h-full bg-secondary w-[85%] rounded-full"></div>
</div>
<div class="flex justify-between items-center text-[10px] font-bold uppercase text-outline">
<span>Charge State: 85%</span>
<span class="text-secondary">Health: Optimal</span>
</div>
</div>
</div>"""

power_new = """<!-- Power Node -->
<div class="md:col-span-4 bg-surface-container rounded-xl p-8 overflow-hidden border border-outline-variant/10">
    <div class="flex justify-between items-center mb-8">
        <h3 class="font-headline font-bold uppercase tracking-tight text-xl">Power Node</h3>
        <span class="material-symbols-outlined text-secondary" style="font-variation-settings: 'FILL' 1;">battery_charging_80</span>
    </div>
    <div class="flex items-end gap-2 mb-2">
        <span class="text-5xl font-headline font-bold text-on-surface" id="batteryVoltageDisplay">--</span>
        <span class="text-xl font-headline text-outline mb-1 font-bold">V</span>
    </div>
    <p class="text-[10px] text-outline font-bold uppercase tracking-widest mb-8">System Voltage Level</p>
    <div class="space-y-6">
        <div class="w-full h-1.5 bg-surface-container-high rounded-full overflow-hidden">
            <div id="batteryBar" class="h-full bg-secondary w-0 transition-all duration-500 rounded-full"></div>
        </div>
        <div class="flex justify-between items-center text-[10px] font-bold uppercase text-outline">
            <span id="batteryChargeText">Charge State: --%</span>
            <span id="batteryHealthText" class="text-secondary">Health: Optimal</span>
        </div>
    </div>
</div>"""

layout = layout.replace(power_old, power_new)

# Replace History trends chart area
chart_old = """<!-- History Chart -->
<div class="md:col-span-8 bg-surface-container rounded-xl p-8 flex flex-col">
<div class="flex justify-between items-center mb-8">
<div>
<h3 class="font-headline font-bold uppercase tracking-tight text-xl">Usage Trends</h3>
<p class="text-[10px] text-outline font-bold uppercase tracking-widest">Last 24 Hours Metrics</p>
</div>
<div class="flex gap-2">
<div class="px-3 py-1 bg-surface-container-lowest rounded text-[10px] font-bold text-primary uppercase">Flow</div>
<div class="px-3 py-1 bg-surface-container-high rounded text-[10px] font-bold text-outline uppercase">Supply</div>
</div>
</div>
<!-- Fake Chart Area -->
<div class="flex-grow flex items-end gap-2 h-40">
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 40%;">
<div class="absolute -top-8 left-1/2 -translate-x-1/2 glass-overlay px-2 py-1 rounded text-[10px] opacity-0 group-hover:opacity-100 transition-opacity">12L</div>
</div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 60%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 45%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 70%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 30%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 85%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 50%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 40%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 95%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 60%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 40%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 30%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 55%;"></div>
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 65%;"></div>
</div>
<div class="flex justify-between mt-4 text-[9px] font-bold text-outline uppercase tracking-widest">
<span>00:00</span>
<span>06:00</span>
<span>12:00</span>
<span>18:00</span>
<span>23:59</span>
</div>
</div>"""

chart_new = """<!-- Historical Chart -->
<div class="md:col-span-8 bg-surface-container rounded-xl p-8 flex flex-col justify-between border border-outline-variant/10">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
            <h3 class="font-headline font-bold uppercase tracking-tight text-xl">Usage Trends</h3>
            <p class="text-[10px] text-outline font-bold uppercase tracking-widest">Historical Telemetry Logs</p>
        </div>
        <div class="flex flex-wrap gap-4 items-center">
            <div class="flex gap-1.5 bg-surface-container-lowest p-1 rounded-xl">
                <button id="btnFilterWater" class="filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-[#9ccaff] bg-primary-container/20" data-index="0" onclick="toggleDataset(0, this)">Water</button>
                <button id="btnFilterBattery" class="filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-amber-500 bg-amber-500/10" data-index="1" onclick="toggleDataset(1, this)">Battery</button>
                <button id="btnFilterMotor" class="filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-purple-500 bg-purple-500/10" data-index="2" onclick="toggleDataset(2, this)">Motor</button>
            </div>
            <div class="flex gap-1 bg-[#111316] p-1 rounded-xl">
                <button id="btnTime1H" class="time-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-[#282a2d] text-[#9ccaff] font-bold shadow-sm" data-hours="1" onclick="switchTimeRange(this)">1H</button>
                <button id="btnTime6H" class="time-btn px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline hover:text-on-surface" data-hours="6" onclick="switchTimeRange(this)">6H</button>
                <button id="btnTime24H" class="time-btn px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline hover:text-on-surface" data-hours="24" onclick="switchTimeRange(this)">24H</button>
            </div>
        </div>
    </div>
    
    <div class="w-full relative h-[280px] min-h-[280px]">
        <canvas id="chartMain"></canvas>
    </div>
</div>"""

# Replace history chart area
layout = layout.replace(chart_old, chart_new)

bento_grid_end = '</div>\n</main>'

# Inject extra bento widgets (Config Card, Spans, Logs table)
layout = layout.replace(bento_grid_end, extra_bento_cards + "\n" + bento_grid_end)

# Inject Mobile Nav elements
mobile_nav_old = """<!-- Bottom Navigation (Mobile Only) -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 bg-[#111316] h-16 flex items-center justify-around z-50 px-6 border-t border-outline-variant/10">
<div class="flex flex-col items-center gap-1 text-[#9ccaff] font-bold">
<span class="material-symbols-outlined">dashboard</span>
<span class="text-[10px] uppercase">Home</span>
</div>
<div class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70">
<span class="material-symbols-outlined">monitoring</span>
<span class="text-[10px] uppercase">Data</span>
</div>
<div class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70">
<span class="material-symbols-outlined">settings</span>
<span class="text-[10px] uppercase">Config</span>
</div>
</nav>"""

mobile_nav_new = """<!-- Bottom Navigation (Mobile Only) -->
<nav class="md:hidden fixed bottom-0 left-0 right-0 bg-[#111316] h-16 flex items-center justify-around z-50 px-6 border-t border-outline-variant/10">
    <div class="flex flex-col items-center gap-1 text-[#9ccaff] font-bold cursor-pointer">
        <span class="material-symbols-outlined">dashboard</span>
        <span class="text-[10px] uppercase font-headline">Home</span>
    </div>
    <div onclick="openModal()" class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70 cursor-pointer hover:opacity-100">
        <span class="material-symbols-outlined">add_circle</span>
        <span class="text-[10px] uppercase font-headline">Add</span>
    </div>
    <div onclick="toggleDark()" class="flex flex-col items-center gap-1 text-[#e2e2e6] opacity-70 cursor-pointer hover:opacity-100">
        <span class="material-symbols-outlined">settings</span>
        <span class="text-[10px] uppercase font-headline">Config</span>
    </div>
</nav>"""

layout = layout.replace(mobile_nav_old, mobile_nav_new)

# Inject BLE setup modulators, overlay panels, audio alerts, and the full recovered dynamic Javascript block before closing body tag
layout = layout.replace("</body>", f"{modal_html}\n<script>\n{js}\n</script>\n</body>")

# Overwrite templates/dashboard.html
with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(layout)

print("SUCCESS: Full dashboard design overhaul and Javascript recovery completed successfully!")
