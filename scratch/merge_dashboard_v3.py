import re
import subprocess

# 1. Retrieve the original templates/dashboard.html from HEAD
try:
    base_html = subprocess.check_output(["git", "show", "HEAD:templates/dashboard.html"], text=True, encoding="utf-8")
    base_html = base_html.replace("\r\n", "\n")
except Exception as e:
    print("Failed to run git show HEAD:templates/dashboard.html")
    raise e

# 2. Extract JavaScript script block from HEAD
script_match = re.search(r"<script>(.*?)</script>", base_html, re.DOTALL)
if not script_match:
    print("Error: Could not extract JavaScript from HEAD dashboard.")
    exit(1)
js = script_match.group(1).replace("\r\n", "\n")

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

# Theme updates (Tailwind html `.dark` standard class integration)
js = js.replace(
    'const isDark = () => document.body.classList.contains("dark");',
    'const isDark = () => document.documentElement.classList.contains("dark") || document.body.classList.contains("dark");'
)

# Live Entries buffer fix
js = js.replace(
    'let allLiveEntries = [];      // Stores live buffer entries',
    'let allLiveEntries = { entries: [] };      // Stores live buffer entries'
)

js = js.replace(
    'if (!allLogsData && allLiveEntries.length === 0) return;',
    'if (!allLogsData && (!allLiveEntries.entries || allLiveEntries.entries.length === 0)) return;'
)

js = js.replace(
    'const liveEntries = allLiveEntries.entries || [];',
    'const liveEntries = (allLiveEntries && Array.isArray(allLiveEntries.entries)) ? allLiveEntries.entries : [];'
)

js = js.replace(
    """function toggleDark(){
    document.body.classList.toggle("dark");
    localStorage.setItem("dark", document.body.classList.contains("dark"));
    updateChartTheme();
}
if(localStorage.getItem("dark")==="true") document.body.classList.add("dark");""",
    """function toggleDark() {
    const html = document.documentElement;
    const isDark = html.classList.toggle("dark");
    localStorage.setItem("theme", isDark ? "dark" : "light");
    
    // Update toggle icon
    const ball = document.getElementById("themeBall");
    if (ball) ball.innerText = isDark ? "🌙" : "☀️";

    updateChartTheme();
}

// Initialize theme
(function initTheme() {
    const html = document.documentElement;
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme === "light") {
        html.classList.remove("dark");
        const ball = document.getElementById("themeBall");
        if (ball) ball.innerText = "☀️";
    } else {
        html.classList.add("dark");
        const ball = document.getElementById("themeBall");
        if (ball) ball.innerText = "🌙";
    }
})();"""
)

# loadDevices() dynamic title updater
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

# changeDevice() dynamic header updater
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

# Polling Calculations segment updates
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

# Alert layout segment updates
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

# Motor state polling class assignments for manual/auto buttons in Tailwind
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
        btnOff.className = "py-3 bg-outline-variant/20 text-outline rounded-lg text-xs font-bold uppercase tracking-wider transition-all hover:bg-outline-wider hover:bg-outline-variant/30";
        btnAuto.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface";
        const btnManualMode = document.getElementById("btnManualMode");
        if (btnManualMode) {
            btnManualMode.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface";
        }

        if (motor.MOTOR_MODE === 1) {
            // MANUAL MODE
            if (btnManualMode) {
                btnManualMode.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all bg-[#282a2d] text-[#9ccaff] font-bold shadow-sm";
            }
            if (motor.MOTOR_MANUAL_STATUS === 1) {
                status.innerText = "Active - Running (Manual)";
                status.className = "text-xs text-secondary font-semibold mt-1";
                btnOn.className = "py-3 bg-secondary text-on-secondary rounded-lg text-xs font-bold uppercase tracking-wider transition-all shadow-md";
            } else {
                status.innerText = "Stopped (Manual)";
                status.className = "text-xs text-outline font-semibold mt-1";
                btnOff.className = "py-3 bg-tertiary-container text-white rounded-lg text-xs font-bold uppercase tracking-wider transition-all shadow-md";
            }
        } else {
            // AUTO MODE — read status from calc data
            btnAuto.className = "py-2.5 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all bg-[#282a2d] text-[#9ccaff] font-bold shadow-sm";
            try {
                const calc = await (await fetch("/api/calculated/?mac=" + activeDeviceMac)).json();
                if (calc.MOTOR_STATUS === 1) {
                    status.innerText = "Active - Running (Auto)";
                    status.className = "text-xs text-secondary font-semibold mt-1";
                } else {
                    status.innerText = "Stopped (Auto)";
                    status.className = "text-xs text-outline font-semibold mt-1";
                }
            } catch(e) {
                status.innerText = "Active - Auto Mode";
                status.className = "text-xs text-outline font-semibold mt-1";
            }
        }"""

js = js.replace(motor_state_poll_old, motor_state_poll_new)

# Chart filters active states updates
chart_filters_old = """function switchTimeRange(btn) {
    document.querySelectorAll(".time-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    currentHours = parseInt(btn.dataset.hours);
    renderChartsFromCache(); // Re-filter and render without re-fetching
}"""

chart_filters_new = """function switchTimeRange(btn) {
    document.querySelectorAll(".time-btn").forEach(b => {
        b.className = "time-btn px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline hover:text-on-surface";
    });
    btn.className = "time-btn active px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-[#282a2d] text-[#9ccaff] font-bold shadow-sm";
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
        btn.className = "filter-btn px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline opacity-40";
    } else {
        const activeColors = [
            "filter-btn active px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-primary-container/20 text-[#9ccaff]",
            "filter-btn active px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-amber-500/10 text-amber-500",
            "filter-btn active px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all bg-purple-500/10 text-purple-500"
        ];
        btn.className = activeColors[index];
    }
    chartMain.update();
}"""

js = js.replace(toggle_dataset_old, toggle_dataset_new)

# Add custom modal open/close actions & tabs setup to JavaScript
modal_tab_funcs = """
function openModal() {
    document.getElementById("addDeviceModal").classList.add("active");
    switchTabModal('ble');
}

function closeModal() {
    document.getElementById("addDeviceModal").classList.remove("active");
    if (bleDevice && bleDevice.gatt.connected) {
        bleDevice.gatt.disconnect();
    }
    document.getElementById("blePairedContainer").style.display = "none";
    document.getElementById("bleCredentialsForm").style.display = "none";
    document.getElementById("bleStatus").innerText = "";
    document.getElementById("claimStatus").innerText = "";
}

function switchTabModal(tab) {
    const bleTab = document.getElementById("tabBle");
    const manualTab = document.getElementById("tabManual");
    const bleBtn = document.getElementById("tabBleBtn");
    const manualBtn = document.getElementById("tabManualBtn");
    
    if (tab === 'ble') {
        bleTab.style.display = "flex";
        manualTab.style.display = "none";
        bleBtn.className = "flex-1 pb-3 text-center border-b-2 border-primary text-primary font-semibold text-sm font-bold uppercase tracking-wider";
        manualBtn.className = "flex-1 pb-3 text-center border-b-2 border-transparent text-outline hover:text-on-surface text-sm font-bold uppercase tracking-wider";
    } else {
        bleTab.style.display = "none";
        manualTab.style.display = "flex";
        manualBtn.className = "flex-1 pb-3 text-center border-b-2 border-primary text-primary font-semibold text-sm font-bold uppercase tracking-wider";
        bleBtn.className = "flex-1 pb-3 text-center border-b-2 border-transparent text-outline hover:text-on-surface text-sm font-bold uppercase tracking-wider";
    }
}
"""

js = js + "\n" + modal_tab_funcs

# 4. Load the user design HTML layout
with open("C:/Users/Patel Taksh/.gemini/antigravity-ide/brain/4da987eb-9dae-4a65-b4c5-ac8289f23d1a/scratch/user_design.html", "r", encoding="utf-8") as f:
    layout = f.read().replace("\r\n", "\n")

# 5. Apply layout tags & injections
layout = "{% load static %}\n" + layout

# Add manifest, Chart.js libraries in head
head_inject = """
    <link rel="manifest" href="{% static 'manifest.json' %}">
    <meta name="theme-color" content="#111316">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation@3/dist/chartjs-plugin-annotation.min.js"></script>
"""
layout = layout.replace("</head>", head_inject + "</head>")

# Add circular gauge styles & pulse active animations to head stylesheet
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
layout = layout.replace("</style>", head_styles + "</style>")

# Replace top navbar titles & dynamic heartbeat timestamp info
top_navbar_old = """<header class="w-full h-16 flex items-center bg-[#0c0e11] px-6 justify-between z-50 shrink-0 border-b border-outline-variant/20">
<div class="flex items-center gap-4">
<span class="text-xl font-bold text-[#9ccaff] tracking-tighter font-headline">Synthetic Aquifer</span>"""

top_navbar_new = """<header class="w-full h-16 flex items-center bg-[#0c0e11] px-6 justify-between z-50 shrink-0 border-b border-outline-variant/20">
<div class="flex items-center gap-4">
<span class="text-xl font-bold text-[#9ccaff] tracking-tighter font-headline">HydroFlow</span>
<span class="text-[11px] text-outline bg-surface-container-high px-2.5 py-1 rounded-md font-mono hidden sm:inline ml-4" id="lastUpdated">Heartbeat: --</span>"""

layout = layout.replace(top_navbar_old, top_navbar_new)

# Add theme toggler and dynamic sensor live indicator dot
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

# Sidebar selector replacement
sidebar_old = """<!-- Device Selection Dropdown -->
<div class="relative w-full group mt-2">
<select class="w-full bg-surface-container border border-outline-variant rounded-lg px-3 py-2 text-on-surface font-headline font-bold text-lg appearance-none cursor-pointer hover:border-primary transition-colors focus:outline-none focus:border-primary">
<option>Aquifer-01</option>
<option>Reservoir-Beta</option>
<option>Tank-Sector-7</option>
</select>
<span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-outline pointer-events-none group-hover:text-primary transition-colors">expand_more</span>
</div>"""

sidebar_new = """<!-- Device Selection Dropdown -->
<div class="relative w-full group mt-2">
<select id="deviceSelector" onchange="changeDevice(this.value)" class="w-full bg-surface-container border border-outline-variant rounded-lg px-3 py-2 text-on-surface font-headline font-bold text-lg appearance-none cursor-pointer hover:border-primary transition-colors focus:outline-none focus:border-primary">
    <!-- Dynamically loaded -->
</select>
<span class="material-symbols-outlined absolute right-3 top-1/2 -translate-y-1/2 text-outline pointer-events-none group-hover:text-primary transition-colors">expand_more</span>
</div>"""

layout = layout.replace(sidebar_old, sidebar_new)

# Add device modal trigger
add_device_old = """<button class="mt-4 w-full py-2 border border-outline-variant hover:border-primary rounded-lg text-primary text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-colors" onclick="document.getElementById('addDeviceModal').classList.add('active')">"""
add_device_new = """<button class="mt-4 w-full py-2 border border-outline-variant hover:border-primary rounded-lg text-primary text-xs font-bold uppercase tracking-wider flex items-center justify-center gap-2 transition-colors" onclick="openModal()">"""
layout = layout.replace(add_device_old, add_device_new)

# Main title details
desc_old = """<p class="text-outline text-sm mt-1">System Node: North-Wing Main Reservoirs</p>"""
desc_new = """<p class="text-outline text-sm mt-1" id="activeDeviceMacDisplay">Select or claim a device to start tracking</p>"""
layout = layout.replace(desc_old, desc_new)

# System status alarms
system_status_old = """<div class="glass-overlay p-4 rounded-xl flex items-center gap-6">
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

system_status_new = """<div class="glass-overlay p-4 rounded-xl flex items-center gap-6 border border-outline-variant/15">
<div class="flex flex-col">
<span class="text-[10px] text-outline font-semibold uppercase tracking-widest">System Alerts</span>
<div class="flex items-center gap-2 mt-1">
<span id="alertBadge" class="status-pill text-xs font-bold uppercase py-0.5 px-2 rounded hidden" style="background: var(--danger); color: white;">CRITICAL</span>
<span id="noAlertText" class="text-secondary font-headline text-sm font-bold uppercase">Normal</span>
</div>
</div>
</div>"""

layout = layout.replace(system_status_old, system_status_new)

# Circular gauge value mapping
gauge_old = """<svg class="w-full h-full -rotate-225" viewbox="0 0 120 120">
<circle class="gauge-track" cx="60" cy="60" fill="none" r="50" stroke-linecap="round" stroke-width="8"></circle>
<circle class="gauge-value" cx="60" cy="60" fill="none" r="50" stroke-dashoffset="0" stroke-linecap="round" stroke-width="8"></circle>
</svg>
<div class="absolute inset-0 flex flex-col items-center justify-center text-center">
<span class="text-6xl font-headline font-bold text-on-surface tracking-tighter">65<span class="text-2xl opacity-50">%</span></span>
<span class="text-[10px] font-bold text-primary uppercase tracking-[0.2em] mt-1">Water Level</span>
</div>"""

gauge_new = """<svg class="w-full h-full -rotate-225" viewbox="0 0 120 120">
<circle class="gauge-track" cx="60" cy="60" fill="none" r="50" stroke-linecap="round" stroke-width="8"></circle>
<circle class="gauge-value" id="gaugeValue" cx="60" cy="60" fill="none" r="50" stroke-dashoffset="0" stroke-linecap="round" stroke-width="8"></circle>
</svg>
<div class="absolute inset-0 flex flex-col items-center justify-center text-center">
<span class="text-5xl font-headline font-bold text-on-surface tracking-tighter" id="percentage">--</span>
<span class="text-[10px] font-bold text-primary uppercase tracking-[0.2em] mt-1">Water Level</span>
</div>"""

layout = layout.replace(gauge_old, gauge_new)

# Current volume capacity
volume_old = """<div class="text-4xl font-headline font-bold text-on-surface">14,250 <span class="text-lg font-normal text-outline">Liters</span></div>"""
volume_new = """<div class="text-4xl font-headline font-bold text-on-surface"><span id="filledVolume">--</span> <span class="text-lg font-normal text-outline">Liters</span></div>"""
layout = layout.replace(volume_old, volume_new)

# Dimensions & offset metrics
metrics_old = """<div class="grid grid-cols-2 gap-4">
<div class="bg-surface-container-high p-4 rounded-xl border border-outline-variant/10">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Tank Height</span>
<div class="text-2xl font-headline font-bold text-on-surface">2.5m</div>
</div>
<div class="bg-surface-container-high p-4 rounded-xl border border-outline-variant/10">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Sensor Offset</span>
<div class="text-2xl font-headline font-bold text-on-surface">12cm</div>
</div>
</div>"""

metrics_new = """<div class="grid grid-cols-2 gap-4">
<div class="bg-surface-container-high p-4 rounded-xl border border-outline-variant/10">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Total Height</span>
<div class="text-2xl font-headline font-bold text-on-surface" id="displayHeight">--</div>
</div>
<div class="bg-surface-container-high p-4 rounded-xl border border-outline-variant/10">
<span class="text-[10px] text-outline font-bold uppercase block mb-1">Sensor Dist</span>
<div class="text-2xl font-headline font-bold text-on-surface" id="distanceVal">--</div>
</div>
</div>"""

layout = layout.replace(metrics_old, metrics_new)

# Replace Motor override block card entirely
motor_block_old = """<!-- Motor Control Panel -->
<div class="md:col-span-4 bg-surface-container rounded-xl p-8 flex flex-col justify-between border border-outline-variant/10 shadow-lg">
<div>
<div class="flex justify-between items-start mb-6">
<h3 class="font-headline font-bold uppercase tracking-tight text-xl">Motor Control</h3>
<span class="material-symbols-outlined text-tertiary">tune</span>
</div>
<div class="flex items-center justify-between bg-surface-container-lowest p-6 rounded-xl mb-6 border border-outline-variant/20">
<div>
<p class="text-sm font-bold text-on-surface uppercase">Pump Status</p>
<p class="text-xs text-secondary font-semibold mt-1">Active - Running</p>
</div>
<div class="w-14 h-8 bg-secondary-container rounded-full relative cursor-pointer shadow-inner transition-colors">
<div class="absolute right-1 top-1 w-6 h-6 bg-surface-bright rounded-full shadow-md transition-transform"></div>
</div>
</div>
<div class="bg-surface-container-high p-4 rounded-xl border border-outline-variant/10 flex gap-4 items-start">
<span class="material-symbols-outlined text-primary-fixed-dim text-xl mt-0.5" style="font-variation-settings: 'FILL' 1;">info</span>
<div>
<span class="text-[10px] font-bold text-primary uppercase block mb-1 tracking-wider">Automation Logic</span>
<p class="text-xs leading-relaxed text-on-surface-variant font-medium">Auto-Off at &gt;90%, Auto-On at &lt;10%</p>
</div>
</div>
</div>
<button class="w-full py-4 mt-8 bg-gradient-to-r from-primary to-primary-container rounded-xl font-headline font-bold uppercase tracking-widest text-on-primary text-sm hover:opacity-90 transition-all flex items-center justify-center gap-2 shadow-md">
<span class="material-symbols-outlined text-xl">power_settings_new</span>
                            Emergency Shutoff
                        </button>
</div>"""

motor_block_new = """<!-- Motor Control Panel -->
<div class="md:col-span-4 bg-surface-container rounded-xl p-8 flex flex-col justify-between border border-outline-variant/10 shadow-lg">
    <div>
        <div class="flex justify-between items-start mb-6">
            <h3 class="font-headline font-bold uppercase tracking-tight text-xl">Motor Control</h3>
            <span class="material-symbols-outlined text-tertiary">tune</span>
        </div>
        
        <div class="bg-surface-container-lowest p-5 rounded-xl mb-6 border border-outline-variant/20">
            <p class="text-sm font-bold text-on-surface uppercase">Pump Status</p>
            <p class="text-xs text-secondary font-semibold mt-1" id="motorStatus">Checking...</p>
        </div>

        <div class="space-y-4">
            <div>
                <p class="text-[10px] text-outline font-bold uppercase mb-2">Control Mode</p>
                <div class="grid grid-cols-2 gap-2 bg-surface-container-lowest p-1 rounded-xl border border-outline-variant/10">
                    <button id="btnAuto" onclick="motorAuto()" class="py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface">Auto</button>
                    <button id="btnManualMode" class="py-2 rounded-lg text-xs font-semibold uppercase tracking-wider transition-all text-outline hover:text-on-surface">Manual</button>
                </div>
            </div>

            <div id="manualControlsBlock" class="space-y-2">
                <p class="text-[10px] text-outline font-bold uppercase mb-2">Manual Override</p>
                <div class="grid grid-cols-2 gap-3">
                    <button id="btnOn" onclick="motorOn()" class="py-2.5 bg-outline-variant/25 text-outline rounded-lg text-xs font-bold uppercase tracking-wider transition-all">START</button>
                    <button id="btnOff" onclick="motorOff()" class="py-2.5 bg-outline-variant/25 text-outline rounded-lg text-xs font-bold uppercase tracking-wider transition-all">STOP</button>
                </div>
            </div>
        </div>
    </div>
    
    <button onclick="motorOff()" class="w-full py-4 mt-8 bg-gradient-to-r from-red-600 to-red-800 rounded-xl font-headline font-bold uppercase tracking-widest text-white text-sm hover:opacity-90 transition-all flex items-center justify-center gap-2 shadow-md">
        <span class="material-symbols-outlined text-xl">power_settings_new</span>
        Emergency Shutoff
    </button>
</div>"""

layout = layout.replace(motor_block_old, motor_block_new)

# Battery Power Node card elements
battery_old = """<div class="flex items-end gap-2 mb-2">
<span class="text-5xl font-headline font-bold text-on-surface tracking-tighter">12.4</span>
<span class="text-xl font-headline text-outline mb-1 font-bold">V</span>
</div>
<p class="text-[10px] text-outline font-bold uppercase tracking-widest mb-8">System Voltage Level</p>
<div class="space-y-4">
<div class="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
<div class="h-full bg-secondary w-[85%] rounded-full shadow-[0_0_10px_rgba(68,221,193,0.5)]"></div>
</div>
<div class="flex justify-between items-center text-[10px] font-bold uppercase text-outline">
<span>Charge State: 85%</span>
<span class="text-secondary">Health: Optimal</span>
</div>
</div>"""

battery_new = """<div class="flex items-end gap-2 mb-2">
<span class="text-5xl font-headline font-bold text-on-surface tracking-tighter" id="batteryVoltageDisplay">--</span>
<span class="text-xl font-headline text-outline mb-1 font-bold">V</span>
</div>
<p class="text-[10px] text-outline font-bold uppercase tracking-widest mb-8">System Voltage Level</p>
<div class="space-y-4">
<div class="w-full h-2 bg-surface-container-high rounded-full overflow-hidden">
<div id="batteryBar" class="h-full bg-secondary w-0 rounded-full shadow-[0_0_10px_rgba(68,221,193,0.5)]"></div>
</div>
<div class="flex justify-between items-center text-[10px] font-bold uppercase text-outline">
<span id="batteryChargeText">Charge State: --%</span>
<span id="batteryHealthText" class="text-secondary">Health: Optimal</span>
</div>
</div>"""

layout = layout.replace(battery_old, battery_new)

# History Trends chart block
history_old = """<!-- History Chart -->
<div class="md:col-span-8 bg-surface-container rounded-xl p-8 flex flex-col border border-outline-variant/10 shadow-lg">
<div class="flex justify-between items-center mb-8">
<div>
<h3 class="font-headline font-bold uppercase tracking-tight text-xl">Usage Trends</h3>
<p class="text-[10px] text-outline font-bold uppercase tracking-widest mt-1">Last 24 Hours Metrics</p>
</div>
<div class="flex gap-2">
<div class="px-3 py-1 bg-surface-container-lowest rounded text-[10px] font-bold text-primary border border-outline-variant/20 uppercase">Flow</div>
<div class="px-3 py-1 bg-surface-container-high rounded text-[10px] font-bold text-outline border border-outline-variant/10 uppercase">Supply</div>
</div>
</div>
<div class="flex-grow flex items-end gap-2 h-40">
<!-- Chart bars -->
<div class="flex-1 bg-primary-container/20 rounded-t-sm hover:bg-primary transition-all cursor-pointer relative group" style="height: 40%;"></div>
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
<div class="flex justify-between mt-4 text-[9px] font-bold text-outline uppercase tracking-widest border-t border-outline-variant/20 pt-4">
<span>00:00</span>
<span>06:00</span>
<span>12:00</span>
<span>18:00</span>
<span>23:59</span>
</div>
</div>"""

history_new = """<!-- Historical Chart -->
<div class="md:col-span-8 bg-surface-container rounded-xl p-8 flex flex-col border border-outline-variant/10 shadow-lg">
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
        <div>
            <h3 class="font-headline font-bold uppercase tracking-tight text-xl">Usage Trends</h3>
            <p class="text-[10px] text-outline font-bold uppercase tracking-widest">Historical Telemetry Logs</p>
        </div>
        <div class="flex flex-wrap gap-4 items-center">
            <div class="flex gap-1.5 bg-surface-container-lowest p-1 rounded-xl border border-outline-variant/10">
                <button id="btnFilterWater" class="filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-[#9ccaff] bg-primary-container/20" data-index="0" onclick="toggleDataset(0, this)">Water</button>
                <button id="btnFilterBattery" class="filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline hover:text-on-surface" data-index="1" onclick="toggleDataset(1, this)">Battery</button>
                <button id="btnFilterMotor" class="filter-btn active px-3 py-1.5 rounded-lg text-[10px] font-bold uppercase tracking-wider transition-all text-outline hover:text-on-surface" data-index="2" onclick="toggleDataset(2, this)">Motor</button>
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

layout = layout.replace(history_old, history_new)

# Config Form Section Replacement
config_form_old = """<form class="space-y-8 max-w-3xl">
<!-- Tank Dimensions -->
<div>
<h3 class="text-primary font-bold uppercase tracking-wider text-sm mb-4 flex items-center gap-2">
<span class="material-symbols-outlined">square_foot</span> Tank Specifications
                            </h3>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Total Height (cm)</label>
<input class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number" value="250"/>
</div>
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Sensor Offset (cm)</label>
<input class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number" value="12"/>
</div>
<div class="md:col-span-2">
<label class="block text-xs font-bold text-outline uppercase mb-2">Max Capacity (Liters)</label>
<input class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number" value="15000"/>
</div>
</div>
</div>
<!-- Automation Thresholds -->
<div class="pt-6 border-t border-outline-variant/20">
<h3 class="text-primary font-bold uppercase tracking-wider text-sm mb-4 flex items-center gap-2">
<span class="material-symbols-outlined">rule</span> Logic Thresholds
                            </h3>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Auto-On Level (%)</label>
<input class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number" value="10"/>
</div>
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Auto-Off Level (%)</label>
<input class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number" value="90"/>
</div>
</div>
</div>
<!-- Power Management -->
<div class="pt-6 border-t border-outline-variant/20">
<h3 class="text-primary font-bold uppercase tracking-wider text-sm mb-4 flex items-center gap-2">
<span class="material-symbols-outlined">battery_saver</span> Power Management
                            </h3>
<div class="flex items-center justify-between p-4 bg-surface-container-lowest border border-outline-variant/50 rounded-lg">
<div>
<p class="font-bold text-sm text-on-surface">Deep Sleep Mode</p>
<p class="text-xs text-outline mt-1">Reduces update frequency to conserve battery</p>
</div>
<label class="relative inline-flex items-center cursor-pointer">
<input checked="" class="sr-only peer" type="checkbox"/>
<div class="w-11 h-6 bg-surface-container-high peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-surface-bright after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container"></div>
</label>
</div>
</div>
<div class="pt-6 border-t border-outline-variant/20 flex justify-end gap-4">
<button class="px-6 py-2 border border-outline-variant rounded-lg text-outline font-bold uppercase text-xs hover:bg-surface-container-high transition-colors" type="button">Discard</button>
<button class="px-6 py-2 bg-primary text-on-primary rounded-lg font-bold uppercase text-xs hover:bg-primary-fixed transition-colors" type="button">Save Configuration</button>
</div>
</form>"""

config_form_new = """<form class="space-y-8 max-w-3xl">
<!-- Tank Dimensions -->
<div>
<h3 class="text-primary font-bold uppercase tracking-wider text-sm mb-4 flex items-center gap-2">
<span class="material-symbols-outlined">square_foot</span> Tank Specifications
</h3>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Total Height (meters)</label>
<input id="totalHeight" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number" step="0.1"/>
</div>
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Total Volume (Liters)</label>
<input id="totalVolume" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number"/>
</div>
</div>
</div>
<!-- Automation Thresholds -->
<div class="pt-6 border-t border-outline-variant/20">
<h3 class="text-primary font-bold uppercase tracking-wider text-sm mb-4 flex items-center gap-2">
<span class="material-symbols-outlined">rule</span> Logic Thresholds
</h3>
<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Auto-On Level (Min %)</label>
<input id="minPercentage" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number"/>
</div>
<div>
<label class="block text-xs font-bold text-outline uppercase mb-2">Auto-Off Level (Max %)</label>
<input id="maxPercentage" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number"/>
</div>
</div>
</div>
<!-- Power Management -->
<div class="pt-6 border-t border-outline-variant/20">
<h3 class="text-primary font-bold uppercase tracking-wider text-sm mb-4 flex items-center gap-2">
<span class="material-symbols-outlined">battery_saver</span> Power Management
</h3>
<div class="flex items-center justify-between p-4 bg-surface-container-lowest border border-outline-variant/50 rounded-lg">
<div>
<p class="font-bold text-sm text-on-surface">Deep Sleep Mode</p>
<p class="text-xs text-outline mt-1">Reduces update frequency to conserve battery</p>
</div>
<label class="relative inline-flex items-center cursor-pointer">
<input id="deepSleepToggle" class="sr-only peer" type="checkbox"/>
<div class="w-11 h-6 bg-surface-container-high peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-surface-bright after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-container"></div>
</label>
</div>
<div class="mt-4">
<label class="block text-xs font-bold text-outline uppercase mb-2">Sleep Interval (seconds)</label>
<input id="sleepInterval" class="w-full bg-surface-container-lowest border border-outline-variant rounded-lg px-4 py-3 text-on-surface focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all" type="number"/>
</div>
</div>

<div class="pt-6 border-t border-outline-variant/20 flex justify-end gap-4">
<button onclick="sendInput()" class="px-6 py-2 bg-primary text-on-primary rounded-lg font-bold uppercase text-xs hover:bg-primary-fixed transition-colors" type="button">Save Configuration</button>
</div>
</form>

<!-- Stored configurations list -->
<div class="bg-surface-container-high p-6 rounded-xl border border-outline-variant/10 mt-8">
  <p class="text-[10px] text-outline font-bold uppercase tracking-widest mb-3">Stored Configurations</p>
  <div class="grid grid-cols-2 md:grid-cols-6 gap-4 text-xs text-outline">
      <div class="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/10">
          <span class="block text-[9px] opacity-75 mb-1">Height</span>
          <span id="storedHeight" class="font-bold text-on-surface">--</span> m
      </div>
      <div class="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/10">
          <span class="block text-[9px] opacity-75 mb-1">Volume</span>
          <span id="storedVolume" class="font-bold text-on-surface">--</span> L
      </div>
      <div class="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/10">
          <span class="block text-[9px] opacity-75 mb-1">Min Level</span>
          <span id="storedMin" class="font-bold text-on-surface">--</span> %
      </div>
      <div class="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/10">
          <span class="block text-[9px] opacity-75 mb-1">Max Level</span>
          <span id="storedMax" class="font-bold text-on-surface">--</span> %
      </div>
      <div class="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/10">
          <span class="block text-[9px] opacity-75 mb-1">Deep Sleep</span>
          <span id="storedDeepSleep" class="font-bold text-on-surface">--</span>
      </div>
      <div class="bg-surface-container-lowest p-3 rounded-lg border border-outline-variant/10">
          <span class="block text-[9px] opacity-75 mb-1">Interval</span>
          <span id="storedSleepInterval" class="font-bold text-on-surface">--</span> s
      </div>
  </div>
</div>"""

layout = layout.replace(config_form_old, config_form_new)

# Operational logs tab contents
logs_tab_old = """<!-- Tab: Logs -->
<div class="tab-content" id="tab-logs">
<div class="bg-surface-container rounded-xl p-8 border border-outline-variant/10 shadow-lg">
<div class="flex justify-between items-center mb-6">
<h2 class="text-2xl font-headline font-bold uppercase">Operational Logs</h2>
<button class="px-4 py-2 border border-outline-variant rounded-lg text-primary text-xs font-bold uppercase tracking-wider flex items-center gap-2 hover:bg-surface-container-high transition-colors">
<span class="material-symbols-outlined text-sm">download</span> Export CSV
                        </button>
</div>
<div class="overflow-x-auto">
<table class="w-full text-left border-collapse">
<thead>
<tr class="border-b border-outline-variant/30 text-[10px] uppercase tracking-widest text-outline">
<th class="py-4 px-4 font-bold">Timestamp</th>
<th class="py-4 px-4 font-bold">Event Type</th>
<th class="py-4 px-4 font-bold">Details</th>
<th class="py-4 px-4 font-bold">Status</th>
</tr>
</thead>
<tbody class="text-sm font-medium">
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-high/50 transition-colors">
<td class="py-4 px-4 text-on-surface-variant">2023-10-27 14:32:01</td>
<td class="py-4 px-4"><span class="px-2 py-1 bg-primary-container/20 text-primary rounded text-xs uppercase font-bold">Pump On</span></td>
<td class="py-4 px-4">Level dropped below 10% threshold</td>
<td class="py-4 px-4"><span class="text-secondary flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">check_circle</span> Success</span></td>
</tr>
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-high/50 transition-colors">
<td class="py-4 px-4 text-on-surface-variant">2023-10-27 10:15:44</td>
<td class="py-4 px-4"><span class="px-2 py-1 bg-surface-container-highest text-outline rounded text-xs uppercase font-bold">Sync</span></td>
<td class="py-4 px-4">Config updated via Dashboard</td>
<td class="py-4 px-4"><span class="text-secondary flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">check_circle</span> Success</span></td>
</tr>
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-high/50 transition-colors">
<td class="py-4 px-4 text-on-surface-variant">2023-10-26 23:45:12</td>
<td class="py-4 px-4"><span class="px-2 py-1 bg-error-container/20 text-error rounded text-xs uppercase font-bold">Network</span></td>
<td class="py-4 px-4">Connection timeout (30s)</td>
<td class="py-4 px-4"><span class="text-error flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">error</span> Failed</span></td>
</tr>
<tr class="border-b border-outline-variant/10 hover:bg-surface-container-high/50 transition-colors">
<td class="py-4 px-4 text-on-surface-variant">2023-10-26 18:22:05</td>
<td class="py-4 px-4"><span class="px-2 py-1 bg-primary-container/20 text-primary rounded text-xs uppercase font-bold">Pump Off</span></td>
<td class="py-4 px-4">Level reached 90% threshold</td>
<td class="py-4 px-4"><span class="text-secondary flex items-center gap-1"><span class="material-symbols-outlined text-[16px]">check_circle</span> Success</span></td>
</tr>
</tbody>
</table>
</div>
<div class="flex justify-between items-center mt-6 text-xs text-outline font-bold uppercase">
<span>Showing 1-4 of 128</span>
<div class="flex gap-2">
<button class="w-8 h-8 rounded border border-outline-variant flex items-center justify-center hover:text-primary hover:border-primary disabled:opacity-50"><span class="material-symbols-outlined text-sm">chevron_left</span></button>
<button class="w-8 h-8 rounded border border-outline-variant flex items-center justify-center hover:text-primary hover:border-primary"><span class="material-symbols-outlined text-sm">chevron_right</span></button>
</div>
</div>
</div>
</div>"""

logs_tab_new = """<!-- Tab: Logs -->
<div class="tab-content" id="tab-logs">
<div class="bg-surface-container rounded-xl p-8 border border-outline-variant/10 shadow-lg">
<div class="flex justify-between items-center mb-6">
<h2 class="text-2xl font-headline font-bold uppercase">Operational Logs</h2>
<button onclick="exportCSV()" class="px-4 py-2 border border-outline-variant rounded-lg text-primary text-xs font-bold uppercase tracking-wider flex items-center gap-2 hover:bg-surface-container-high transition-colors">
<span class="material-symbols-outlined text-sm">download</span> Export CSV
</button>
</div>
<div class="overflow-x-auto">
<table class="w-full text-left border-collapse">
<thead>
<tr class="border-b border-outline-variant/30 text-[10px] uppercase tracking-widest text-outline">
<th class="py-4 px-4 font-bold">Timestamp</th>
<th class="py-4 px-4 font-bold">Water Level</th>
<th class="py-4 px-4 font-bold">Volume</th>
<th class="py-4 px-4 font-bold">Distance</th>
<th class="py-4 px-4 font-bold">Battery</th>
<th class="py-4 px-4 font-bold">Mode</th>
<th class="py-4 px-4 font-bold">Motor Status</th>
</tr>
</thead>
<tbody id="logsBody" class="text-sm font-medium">
<tr><td colspan="7" class="py-8 text-center text-outline italic">Initializing logs...</td></tr>
</tbody>
</table>
</div>
<div class="flex justify-between items-center mt-6 text-xs text-outline font-bold uppercase border-t border-outline-variant/20 pt-4">
<span id="paginationInfo"></span>
<div class="flex gap-2">
<button id="btnPrevPage" onclick="logsPage(-1)" class="w-8 h-8 rounded border border-outline-variant flex items-center justify-center hover:text-primary hover:border-primary disabled:opacity-50"><span class="material-symbols-outlined text-sm">chevron_left</span></button>
<button id="btnNextPage" onclick="logsPage(1)" class="w-8 h-8 rounded border border-outline-variant flex items-center justify-center hover:text-primary hover:border-primary"><span class="material-symbols-outlined text-sm">chevron_right</span></button>
</div>
</div>
</div>
</div>"""

layout = layout.replace(logs_tab_old, logs_tab_new)

# Replace Modals container with dual Bluetooth/Manual claim modal
modals_old = """<!-- Modals -->
<div class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] items-center justify-center p-4" id="addDeviceModal">
<div class="bg-surface-container w-full max-w-md rounded-xl border border-outline-variant/20 shadow-2xl overflow-hidden flex flex-col max-h-full">
<div class="p-6 border-b border-outline-variant/20 flex justify-between items-center bg-[#0c0e11]">
<h3 class="font-headline font-bold text-xl uppercase tracking-tight">Add Device</h3>
<button class="text-outline hover:text-primary transition-colors" onclick="document.getElementById('addDeviceModal').classList.remove('active')">
<span class="material-symbols-outlined">close</span>
</button>
</div>
<div class="p-6 overflow-y-auto">
<!-- Registration Tabs -->
<div class="flex border-b border-outline-variant/30 mb-6">
<button class="pb-2 px-4 text-sm font-bold uppercase tracking-wider text-primary border-b-2 border-primary">Bluetooth</button>
<button class="pb-2 px-4 text-sm font-bold uppercase tracking-wider text-outline hover:text-on-surface">Manual ID</button>
</div>
<div class="text-center py-8">
<div class="w-16 h-16 bg-primary-container/10 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
<span class="material-symbols-outlined text-3xl text-primary">bluetooth_searching</span>
</div>
<p class="font-bold text-on-surface mb-1">Scanning for devices...</p>
<p class="text-xs text-outline">Ensure your device is powered on and within range.</p>
</div>
<div class="space-y-3 mt-4 hidden"> <!-- Hidden mockup of found device -->
<div class="p-4 border border-primary bg-primary-container/5 rounded-lg flex justify-between items-center cursor-pointer">
<div class="flex items-center gap-3">
<span class="material-symbols-outlined text-primary">water_pump</span>
<div>
<p class="font-bold text-sm">HydroNode-X7</p>
<p class="text-[10px] text-outline uppercase tracking-wider">RSSI: -45dBm</p>
</div>
</div>
<span class="material-symbols-outlined text-primary">add_circle</span>
</div>
</div>
</div>
<div class="p-6 border-t border-outline-variant/20 bg-surface-container-lowest">
<button class="w-full py-3 bg-surface-container-high hover:bg-outline-variant/30 rounded-lg text-on-surface font-bold uppercase text-xs tracking-wider transition-colors border border-outline-variant/30">
                    Cancel
                </button>
</div>
</div>
</div>"""

modals_new = """<!-- Modals -->
<div class="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] hidden items-center justify-center p-4" id="addDeviceModal">
<div class="bg-surface-container w-full max-w-md rounded-xl border border-outline-variant/20 shadow-2xl overflow-hidden flex flex-col max-h-full">
<div class="p-6 border-b border-outline-variant/20 flex justify-between items-center bg-[#0c0e11]">
<h3 class="font-headline font-bold text-xl uppercase tracking-tight">Add Device</h3>
<button class="text-outline hover:text-primary transition-colors" onclick="closeModal()">
<span class="material-symbols-outlined">close</span>
</button>
</div>
<div class="p-6 overflow-y-auto">
<!-- Registration Tabs -->
<div class="flex border-b border-outline-variant/30 mb-6">
<button id="tabBleBtn" onclick="switchTabModal('ble')" class="flex-1 pb-3 text-center border-b-2 border-primary text-primary font-semibold text-sm font-bold uppercase tracking-wider">Bluetooth</button>
<button id="tabManualBtn" onclick="switchTabModal('manual')" class="flex-1 pb-3 text-center border-b-2 border-transparent text-outline hover:text-on-surface text-sm font-bold uppercase tracking-wider">Manual ID</button>
</div>

<!-- BLE setup view -->
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
    
    <button id="btnBleScan" onclick="scanBleDevice()" class="w-full py-3 bg-[#0077c1] hover:bg-opacity-95 text-white font-semibold rounded-lg text-sm flex items-center justify-center gap-2 shadow-md">
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

<!-- Manual ID setup view -->
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
<div class="p-6 border-t border-outline-variant/20 bg-surface-container-lowest">
<button onclick="closeModal()" class="w-full py-3 bg-surface-container-high hover:bg-outline-variant/30 rounded-lg text-on-surface font-bold uppercase text-xs tracking-wider transition-colors border border-outline-variant/30">
                    Cancel
                </button>
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

layout = layout.replace(modals_old, modals_new)

# Replace mockup Scripts and insert full recovered dynamic script block
scripts_old = """<!-- Scripts -->
<script>
        function switchTab(tabId) {
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            // Remove active state from nav items (basic implementation)
            document.querySelectorAll('aside li').forEach(el => {
                el.classList.remove('bg-[#0077c1]', 'text-white');
                if(!el.classList.contains('bg-[#0077c1]')){
                    el.classList.add('text-[#e2e2e6]');
                }
            });
            
            // Show selected tab
            document.getElementById('tab-' + tabId).classList.add('active');
            
            // Re-apply active styling to clicked item (simplified for demo)
            const clicked = event.currentTarget;
            clicked.classList.remove('text-[#e2e2e6]', 'hover:bg-[#282a2d]');
            clicked.classList.add('bg-[#0077c1]', 'text-white');
        }
        
        // Close modal when clicking outside
        document.getElementById('addDeviceModal').addEventListener('click', function(e) {
            if (e.target === this) {
                this.classList.remove('active');
            }
        });
    </script>"""

scripts_new = f"""<!-- Scripts -->
<script>
        function switchTab(tabId) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            // Remove active state from nav items
            document.querySelectorAll('aside li').forEach(el => {{
                el.classList.remove('bg-[#0077c1]', 'text-white');
                if(!el.classList.contains('bg-[#0077c1]')){{
                    el.classList.add('text-[#e2e2e6]');
                }}
            }});
            
            // Show selected tab
            document.getElementById('tab-' + tabId).classList.add('active');
            
            // Re-apply active styling to clicked item
            const clicked = event.currentTarget;
            if (clicked) {{
                clicked.classList.remove('text-[#e2e2e6]', 'hover:bg-[#282a2d]');
                clicked.classList.add('bg-[#0077c1]', 'text-white');
            }}
        }}
        
        // Close modal when clicking outside
        document.getElementById('addDeviceModal').addEventListener('click', function(e) {{
            if (e.target === this) {{
                closeModal();
            }}
        }});
</script>
<script>
{js}
</script>"""

layout = layout.replace(scripts_old, scripts_new)

# 8. Write final merged file to templates/dashboard.html
with open("templates/dashboard.html", "w", encoding="utf-8") as f:
    f.write(layout)

print("SUCCESS: Dashboard design fully operationalized with dynamic telemetry logic!")
