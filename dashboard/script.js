/* =========================================================
   ECOGRID — COMPLETE APPLICATION SCRIPT
   Flask API + Dashboard + Three.js Digital Twin
   ========================================================= */

"use strict";

/* =========================================================
   1. CONFIGURATION
   ========================================================= */

const CONFIG = {
    API_BASE: "http://127.0.0.1:5000",
    API_ENDPOINT: "/api/dashboard-data",
    REFRESH_INTERVAL: 30000,

    TOTAL_METERS: 125,

    ORIGINAL_PEAK: 163.169,
    OPTIMIZED_PEAK: 130.5352,
    PEAK_REDUCTION: 20
};

const state = {
    dashboardData: null,
    charts: {},
    refreshTimer: null,
    sceneMode: "society",
    selectedObject: null,
    three: null,
    animationFrame: null,
    initialized: false
};


/* =========================================================
   2. DOM HELPERS
   ========================================================= */

const $ = (id) => document.getElementById(id);

function setText(id, value) {
    const element = $(id);
    if (element) element.textContent = value;
}

function formatNumber(value, decimals = 2) {
    const number = Number(value);

    if (!Number.isFinite(number)) return "--";

    return number.toLocaleString("en-IN", {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

function setDotStatus(element, status) {
    if (!element) return;

    element.classList.remove("offline", "warning");

    if (status === "offline") {
        element.classList.add("offline");
    } else if (status === "warning") {
        element.classList.add("warning");
    }
}


/* =========================================================
   3. INTRODUCTION SCREEN
   ========================================================= */

function initializeIntro() {
    const enterButton = $("enterPlatformBtn");

    if (!enterButton) return;

    enterButton.addEventListener("click", () => {
        document.body.classList.add("intro-dismissed");

        setTimeout(() => {
            resizeDigitalTwin();

            if (state.three) {
                state.three.controls?.update();
            }
        }, 950);
    });
}


/* =========================================================
   4. API CONNECTION
   ========================================================= */

function setApiStatus(connected, message = "") {
    const statusDot = $("apiStatusDot");

    setDotStatus(statusDot, connected ? "online" : "offline");

    setText(
        "apiStatus",
        message || (connected ? "API Connected" : "API Disconnected")
    );

    setText(
        "connectionStatus",
        connected ? "Connected" : "Disconnected"
    );

    setText(
        "monitoringStatus",
        connected ? "Receiving Data" : "Unavailable"
    );

    setText(
        "systemStatus",
        connected ? "OPERATIONAL" : "API OFFLINE"
    );

    const systemDot = document.querySelector(
        ".system-status-item .status-dot"
    );

    setDotStatus(systemDot, connected ? "online" : "offline");
}

async function fetchDashboardData() {
    const url = `${CONFIG.API_BASE}${CONFIG.API_ENDPOINT}`;

    try {
        const response = await fetch(url, {
            method: "GET",
            headers: {
                "Accept": "application/json"
            },
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error(`API returned HTTP ${response.status}`);
        }

        const data = await response.json();

        if (
            !data ||
            typeof data !== "object" ||
            Array.isArray(data)
        ) {
            throw new Error("Invalid dashboard API response");
        }

        if (
            data.status &&
            String(data.status).toLowerCase() !== "success"
        ) {
            throw new Error(`API status: ${data.status}`);
        }

        state.dashboardData = data;

        setApiStatus(true);
        updateDashboard(data);

        return data;

    } catch (error) {
        console.error("EcoGrid API connection error:", error);

        setApiStatus(false, "API Connection Error");

        return null;
    }
}


/* =========================================================
   5. DASHBOARD KPI UPDATES
   ========================================================= */

function updateDashboard(data) {
    const totalEnergy = Number(data.total_energy_kwh);
    const peakEnergy = Number(data.peak_hourly_energy_kwh);

    if (Number.isFinite(totalEnergy)) {
        setText("totalEnergy", formatNumber(totalEnergy, 2));

        setText(
            "optimizationTotalEnergy",
            `${formatNumber(totalEnergy, 3)} kWh`
        );
    }

    if (Number.isFinite(peakEnergy)) {
        setText("peakDemand", formatNumber(peakEnergy, 2));
        setText("peakEnergy", `${formatNumber(peakEnergy, 2)} kWh`);
    }

    const activeSensors = Number(data.active_sensors);

    if (Number.isFinite(activeSensors)) {
        setText("activeSensors", activeSensors);
        setText("sensorCount", `/ ${CONFIG.TOTAL_METERS}`);
    }

    setText("peakReduction", CONFIG.PEAK_REDUCTION);
    setText("originalPeak", formatNumber(CONFIG.ORIGINAL_PEAK, 3));
    setText("optimizedPeak", formatNumber(CONFIG.OPTIMIZED_PEAK, 3));
    setText("optimizationReduction", CONFIG.PEAK_REDUCTION);

    updateEnergyCharts(data);
    updateSensorTable(data.sensors);

    applyEnergyDataToDigitalTwin(data);

    if (Array.isArray(data.hourly_energy)) {
        updatePeakHour(data.hourly_energy, data.hourly_labels);
    }

    updateSystemStatus(data);
}


/* =========================================================
   6. SYSTEM STATUS
   ========================================================= */

function updateSystemStatus(data) {
    const hasEnergyData =
        Array.isArray(data.hourly_energy) &&
        data.hourly_energy.length > 0;

    const hasSensorData =
        Array.isArray(data.sensors) &&
        data.sensors.length > 0;

    setText(
        "monitoringStatus",
        hasEnergyData ? "Active" : "No Data"
    );

    setText(
        "twinStatus",
        state.three ? "Ready" : "Initializing"
    );

    const status = $("systemStatus");

    if (status) {
        status.textContent =
            hasEnergyData && hasSensorData
                ? "OPERATIONAL"
                : "PARTIAL DATA";

        status.style.color =
            hasEnergyData && hasSensorData
                ? "var(--emerald)"
                : "var(--warning)";
    }
}


/* =========================================================
   7. PEAK HOUR CALCULATION
   ========================================================= */

function updatePeakHour(values, labels) {
    if (!Array.isArray(values) || values.length === 0) return;

    const numbers = values.map(Number);

    const validValues = numbers
        .map((value, index) => ({ value, index }))
        .filter(item => Number.isFinite(item.value));

    if (validValues.length === 0) return;

    const peak = validValues.reduce((highest, current) =>
        current.value > highest.value ? current : highest
    );

    const peakLabel =
        Array.isArray(labels) && labels[peak.index] !== undefined
            ? labels[peak.index]
            : `${String(peak.index).padStart(2, "0")}:00`;

    setText("peakHour", peakLabel);
}


/* =========================================================
   8. ENERGY CHARTS
   ========================================================= */

function updateEnergyCharts(data) {
    if (!Array.isArray(data.hourly_energy)) return;

    const values = data.hourly_energy.map(value => {
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    });

    const labels =
        Array.isArray(data.hourly_labels) &&
        data.hourly_labels.length === values.length
            ? data.hourly_labels
            : values.map((_, index) =>
                `${String(index).padStart(2, "0")}:00`
            );

    createOrUpdateChart(
        "energyChart",
        labels,
        values,
        "Hourly energy",
        "line"
    );

    createOrUpdateChart(
        "forecastChart",
        labels,
        values,
        "Observed hourly energy",
        "bar"
    );
}

function createOrUpdateChart(
    canvasId,
    labels,
    values,
    datasetLabel,
    chartType
) {
    const canvas = $(canvasId);

    if (!canvas || typeof Chart === "undefined") {
        console.warn(`Chart.js or canvas missing: ${canvasId}`);
        return;
    }

    const context = canvas.getContext("2d");

    if (state.charts[canvasId]) {
        const chart = state.charts[canvasId];

        chart.data.labels = labels;
        chart.data.datasets[0].data = values;
        chart.update("none");

        return;
    }

    const isLine = chartType === "line";

    state.charts[canvasId] = new Chart(context, {
        type: chartType,

        data: {
            labels,

            datasets: [{
                label: datasetLabel,
                data: values,

                borderColor: "#35d68b",
                backgroundColor: isLine
                    ? "rgba(53, 214, 139, 0.10)"
                    : "rgba(53, 214, 139, 0.55)",

                borderWidth: isLine ? 2.5 : 1,
                pointRadius: isLine ? 2.5 : 0,
                pointHoverRadius: 5,

                fill: isLine,
                tension: 0.35,

                borderRadius: isLine ? 0 : 4,

                maxBarThickness: 24,
                spanGaps: false
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            interaction: {
                intersect: false,
                mode: "index"
            },

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    backgroundColor: "#10251a",
                    borderColor: "rgba(53,214,139,0.3)",
                    borderWidth: 1,
                    titleColor: "#ffffff",
                    bodyColor: "#cde2d4",

                    callbacks: {
                        label: (context) =>
                            `${context.dataset.label}: ${formatNumber(
                                context.parsed.y,
                                2
                            )} kWh`
                    }
                }
            },

            scales: {
                x: {
                    grid: {
                        display: false
                    },

                    ticks: {
                        color: "#82958a",
                        maxTicksLimit: 12,
                        font: {
                            family: "Inter",
                            size: 9
                        }
                    },

                    border: {
                        color: "rgba(156,220,180,0.12)"
                    }
                },

                y: {
                    beginAtZero: true,

                    title: {
                        display: true,
                        text: "Energy (kWh)",
                        color: "#82958a",
                        font: {
                            family: "Inter",
                            size: 10
                        }
                    },

                    grid: {
                        color: "rgba(156,220,180,0.08)"
                    },

                    ticks: {
                        color: "#82958a",
                        font: {
                            family: "Inter",
                            size: 9
                        }
                    },

                    border: {
                        display: false
                    }
                }
            }
        }
    });
}


/* =========================================================
   9. SENSOR TABLE
   ========================================================= */

function normalizeKey(key) {
    return String(key).toLowerCase().replace(/[^a-z0-9]/g, "");
}

function getSensorValue(sensor, possibleKeys, fallback = null) {
    if (!sensor || typeof sensor !== "object") return fallback;

    const availableKeys = Object.keys(sensor);

    for (const possibleKey of possibleKeys) {
        const normalizedPossibleKey = normalizeKey(possibleKey);

        const matchingKey = availableKeys.find(
            key => normalizeKey(key) === normalizedPossibleKey
        );

        if (matchingKey !== undefined) {
            const value = sensor[matchingKey];

            if (
                value !== undefined &&
                value !== null &&
                value !== ""
            ) {
                return value;
            }
        }
    }

    return fallback;
}

function getSensorEnergy(sensor) {
    const value = getSensorValue(
        sensor,
        [
            "energy_kWh",
            "energy_kwh",
            "energy",
            "consumption_kwh",
            "reading",
            "value"
        ],
        null
    );

    if (value === null) return null;

    const number = Number(value);

    return Number.isFinite(number) ? number : null;
}

function updateSensorTable(sensors) {
    const tbody = $("sensorTableBody");

    if (!tbody) return;

    if (!Array.isArray(sensors) || sensors.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="5">No sensor records returned by the API.</td>
            </tr>
        `;
        return;
    }

    tbody.replaceChildren();

    sensors.forEach((sensor, index) => {
        const row = document.createElement("tr");

        const sensorId = getSensorValue(
            sensor,
            ["sensor_id", "id", "meter_id"],
            `Sensor ${index + 1}`
        );

        const location = getSensorValue(
            sensor,
            ["location", "building", "building_id", "area", "zone"],
            "Not specified"
        );

        const type = getSensorValue(
            sensor,
            ["type", "sensor_type", "meter_type"],
            "Energy meter"
        );

        const energy = getSensorEnergy(sensor);

        const sensorStatus = getSensorValue(
            sensor,
            ["status", "state"],
            "Available"
        );

        const cells = [
            sensorId,
            location,
            type,
            energy === null
                ? "--"
                : `${formatNumber(energy, 2)} kWh`,
            sensorStatus
        ];

        cells.forEach((value, cellIndex) => {
            const cell = document.createElement("td");
            cell.textContent = String(value);
            row.appendChild(cell);

            if (cellIndex === 4) {
                const normalized = String(value).toLowerCase();

                if (
                    normalized.includes("offline") ||
                    normalized.includes("error")
                ) {
                    cell.style.color = "var(--danger)";
                } else {
                    cell.style.color = "var(--emerald)";
                }
            }
        });

        tbody.appendChild(row);
    });
}


/* =========================================================
   10. BUILDING-WISE ENERGY MAPPING
   ========================================================= */

function normalizeBuildingId(value) {
    if (value === null || value === undefined) return null;

    const text = String(value).toUpperCase();

    const patterns = [
        /\bBUILDING[\s_-]*([1-5])\b/,
        /\bBLOCK[\s_-]*([1-5])\b/,
        /\bTOWER[\s_-]*([1-5])\b/,
        /\bBLDG[\s_-]*([1-5])\b/,
        /\bB[\s_-]*([1-5])\b/
    ];

    for (const pattern of patterns) {
        const match = text.match(pattern);

        if (match) {
            return `B${match[1]}`;
        }
    }

    return null;
}

function getBuildingMetrics(sensors, buildingId) {
    const records = sensors.filter(sensor => {
        const buildingValue = getSensorValue(
            sensor,
            [
                "building",
                "building_id",
                "building_name",
                "block",
                "tower"
            ],
            null
        );

        return normalizeBuildingId(buildingValue) === buildingId;
    });

    if (records.length === 0) return null;

    const voltageValues = [];
    const powerValues = [];
    const energyValues = [];
    const currentValues = [];

    records.forEach(sensor => {
        const voltage = Number(
            getSensorValue(sensor, ["voltage_V", "voltage"], NaN)
        );

        const power = Number(
            getSensorValue(sensor, ["power_W", "power"], NaN)
        );

        const energy = Number(
            getSensorValue(sensor, ["energy_kWh", "energy_kwh", "energy"], NaN)
        );

        const current = Number(
            getSensorValue(sensor, ["current_A", "current"], NaN)
        );

        if (Number.isFinite(voltage)) voltageValues.push(voltage);
        if (Number.isFinite(power)) powerValues.push(power);
        if (Number.isFinite(energy)) energyValues.push(energy);
        if (Number.isFinite(current)) currentValues.push(current);
    });

    const sum = values =>
        values.reduce((total, value) => total + value, 0);

    const average = values =>
        values.length
            ? sum(values) / values.length
            : null;

    const totalPowerW = sum(powerValues);
    const totalEnergy = sum(energyValues);

    return {
        buildingId,
        sensorCount: records.length,

        voltage: average(voltageValues),
        powerW: totalPowerW,
        powerKW: totalPowerW / 1000,

        energy: totalEnergy,
        totalEnergy,

        current: sum(currentValues),

        status: "Operational",
        dataStatus: "Live"
    };
}

function applyEnergyDataToDigitalTwin(data) {
    if (!state.three || !state.three.world || !data) return;

    const sensors = Array.isArray(data.sensors)
        ? data.sensors
        : [];

    const buildingMetrics = {};

    for (let index = 1; index <= 5; index++) {
        const buildingId = `B${index}`;

        buildingMetrics[buildingId] = getBuildingMetrics(
            sensors,
            buildingId
        );
    }

    state.three.world.traverse(object => {
        const buildingId = object.userData?.buildingId;

        if (!buildingId) return;

        const metrics = buildingMetrics[buildingId];

        object.userData.metrics = metrics;
        object.userData.energyScope = "building";

        if (metrics) {
            object.userData.energy = metrics.totalEnergy;
            object.userData.status = "Operational";
        } else {
            object.userData.energy = null;
            object.userData.status = "No Sensor Data";
        }
    });

    if (state.selectedObject) {
        showSelectedObject(state.selectedObject);
    }
}


/* =========================================================
   11. NAVIGATION
   ========================================================= */

function initializeNavigation() {
    const links = document.querySelectorAll(
        ".sidebar-nav a[data-section]"
    );

    links.forEach(link => {
        link.addEventListener("click", event => {
            event.preventDefault();

            const sectionId = link.dataset.section;
            const target = $(sectionId);

            if (!target) return;

            links.forEach(item => item.classList.remove("active"));
            link.classList.add("active");

            target.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

            setTimeout(resizeDigitalTwin, 350);
        });
    });
}


/* =========================================================
   12. THREE.JS DIGITAL TWIN
   ========================================================= */

function initializeDigitalTwin() {
    const canvas = $("society3DCanvas");

    if (!canvas) return;

    if (typeof THREE === "undefined") {
        showTwinError("Three.js failed to load.");
        return;
    }

    const scene = new THREE.Scene();

    scene.background = new THREE.Color("#07130d");
    scene.fog = new THREE.Fog("#07130d", 35, 90);

    const camera = new THREE.PerspectiveCamera(
        42,
        1,
        0.1,
        150
    );

    camera.position.set(19, 16, 23);

    const renderer = new THREE.WebGLRenderer({
        canvas,
        antialias: true,
        alpha: false,
        powerPreference: "low-power"
    });

    renderer.setPixelRatio(
        Math.min(window.devicePixelRatio || 1, 1.5)
    );

    renderer.outputEncoding = THREE.sRGBEncoding;
    renderer.shadowMap.enabled = false;

    const controls = typeof THREE.OrbitControls !== "undefined"
        ? new THREE.OrbitControls(camera, renderer.domElement)
        : null;

    if (controls) {
        controls.enableDamping = true;
        controls.dampingFactor = 0.06;

        controls.enablePan = true;
        controls.enableZoom = true;
        controls.enableRotate = true;

        controls.minDistance = 10;
        controls.maxDistance = 55;

        controls.maxPolarAngle = Math.PI / 2.05;

        controls.target.set(0, 1.5, 0);
    }

    scene.add(new THREE.AmbientLight(0xffffff, 0.8));

    const mainLight = new THREE.DirectionalLight(
        0xd6ffe5,
        1.15
    );

    mainLight.position.set(12, 25, 12);
    scene.add(mainLight);

    const greenLight = new THREE.PointLight(
        0x35d68b,
        0.8,
        45
    );

    greenLight.position.set(-12, 9, -8);
    scene.add(greenLight);

    const world = new THREE.Group();
    scene.add(world);

    state.three = {
        scene,
        camera,
        renderer,
        controls,
        world,
        raycaster: new THREE.Raycaster(),
        pointer: new THREE.Vector2(),
        interactiveObjects: [],
        resizeObserver: null,
        lastWidth: 0,
        lastHeight: 0
    };

    createSocietyScene();
    initializeTwinInteraction();
    initializeTwinButtons();
    resizeDigitalTwin();

    const loading = $("twinLoading");
    if (loading) loading.classList.add("hidden");

    animateDigitalTwin();
}


/* =========================================================
   13. 3D MATERIALS & OBJECT HELPERS
   ========================================================= */

function material(color, roughness = 0.8, metalness = 0.05) {
    return new THREE.MeshStandardMaterial({
        color,
        roughness,
        metalness
    });
}

function addBox(
    parent,
    name,
    x,
    y,
    z,
    width,
    height,
    depth,
    color,
    options = {}
) {
    const geometry = new THREE.BoxGeometry(
        width,
        height,
        depth
    );

    const mesh = new THREE.Mesh(
        geometry,
        material(
            color,
            options.roughness ?? 0.8,
            options.metalness ?? 0.05
        )
    );

    mesh.position.set(
        x,
        y + height / 2,
        z
    );

    mesh.userData = {
        name,
        description: options.description || name,
        energy: options.energy ?? null,
        energyScope: null,
        buildingId: options.buildingId || null,
        metrics: null,
        status: options.status || "Operational",
        selectable: options.selectable !== false,
        category: options.category || "Infrastructure"
    };

    parent.add(mesh);

    if (mesh.userData.selectable) {
        state.three.interactiveObjects.push(mesh);
    }

    return mesh;
}

function addLine(parent, points, color, opacity = 0.4) {
    const geometry = new THREE.BufferGeometry().setFromPoints(
        points.map(point =>
            new THREE.Vector3(point[0], point[1], point[2])
        )
    );

    const line = new THREE.Line(
        geometry,
        new THREE.LineBasicMaterial({
            color,
            transparent: true,
            opacity
        })
    );

    parent.add(line);

    return line;
}


/* =========================================================
   14. EXISTING SOCIETY SCENE
   ========================================================= */

function createSocietyScene() {
    clearTwinScene();

    const world = state.three.world;

    createGround(world);
    createRoads(world);
    createResidentialBuildings(world);
    createSocietyInfrastructure(world);
    createLandscape(world);

    state.sceneMode = "society";

    if (state.dashboardData) {
        applyEnergyDataToDigitalTwin(state.dashboardData);
    }

    updateSceneButtons();
    resetTwinCamera();
}

function createGround(parent) {
    const ground = new THREE.Mesh(
        new THREE.PlaneGeometry(48, 42),
        material("#14261b")
    );

    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -0.12;
    parent.add(ground);

    const grid = new THREE.GridHelper(
        48,
        24,
        0x28583a,
        0x183523
    );

    grid.position.y = -0.08;
    grid.material.transparent = true;
    grid.material.opacity = 0.28;

    parent.add(grid);
}

function createRoads(parent) {
    addBox(
        parent,
        "Main Internal Road",
        0,
        -0.06,
        0,
        5,
        0.12,
        39,
        "#26332b",
        { selectable: false }
    );

    addBox(
        parent,
        "Cross Society Road",
        0,
        -0.055,
        0,
        43,
        0.11,
        4,
        "#26332b",
        { selectable: false }
    );

    addLine(
        parent,
        [[-1.2, 0.015, -19], [-1.2, 0.015, 19]],
        "#b9c6a7",
        0.35
    );

    addLine(
        parent,
        [[1.2, 0.015, -19], [1.2, 0.015, 19]],
        "#b9c6a7",
        0.35
    );
}

function createResidentialBuildings(parent) {
    const buildingPositions = [
        { x: -12, z: -12, name: "Building B1" },
        { x: 12, z: -12, name: "Building B2" },
        { x: -12, z: 12, name: "Building B3" },
        { x: 12, z: 12, name: "Building B4" },
        { x: 0, z: 0, name: "Building B5" }
    ];

    buildingPositions.forEach((position, index) => {
        const group = new THREE.Group();

        group.position.set(position.x, 0, position.z);

        parent.add(group);

        const buildingName = position.name;
        const buildingId = `B${index + 1}`;

        addBox(
            group,
            buildingName,
            0,
            0,
            0,
            6,
            8,
            5,
            index % 2 === 0 ? "#879b8c" : "#758d7d",
            {
                category: "Residential Building",
                description:
                    `${buildingName}: four-floor residential block with 20 flats and common-area energy meters.`,
                buildingId,
                energy: null,
                status: "Monitored"
            }
        );

        for (let floor = 1; floor <= 4; floor++) {
            const y = floor * 1.8;

            addBox(
                group,
                `${buildingName} floor detail`,
                0,
                y,
                2.52,
                6.05,
                0.07,
                0.08,
                "#d2ddd2",
                { selectable: false }
            );

            for (let windowIndex = 0; windowIndex < 3; windowIndex++) {
                addBox(
                    group,
                    `${buildingName} window`,
                    -1.9 + windowIndex * 1.9,
                    y - 1.35,
                    2.57,
                    0.95,
                    0.85,
                    0.05,
                    "#1a4033",
                    { selectable: false }
                );

                addBox(
                    group,
                    `${buildingName} balcony`,
                    -1.9 + windowIndex * 1.9,
                    y - 1.55,
                    2.9,
                    1.15,
                    0.12,
                    0.7,
                    "#a4b7a8",
                    { selectable: false }
                );
            }

            for (let side = -1; side <= 1; side += 2) {
                for (let windowIndex = 0; windowIndex < 2; windowIndex++) {
                    addBox(
                        group,
                        `${buildingName} side window`,
                        side * 3.04,
                        y - 1.3,
                        -1.1 + windowIndex * 2.2,
                        0.05,
                        0.8,
                        0.95,
                        "#1a4033",
                        { selectable: false }
                    );
                }
            }
        }

        addBox(
            group,
            `${buildingName} roof`,
            0,
            8.05,
            0,
            6.2,
            0.15,
            5.2,
            "#52685a",
            { selectable: false }
        );

        addBox(
            group,
            `${buildingName} service core`,
            1.85,
            8.2,
            -1.25,
            1.3,
            1.4,
            1.3,
            "#405b49",
            {
                category: "Common Area",
                description: `${buildingName} rooftop service core.`,
                buildingId,
                selectable: true
            }
        );

        const label = createTextSprite(buildingName);
        label.position.set(0, 10.2, 0);
        label.scale.set(3.8, 0.85, 1);
        group.add(label);
    });
}


/* =========================================================
   15. SOCIETY INFRASTRUCTURE
   ========================================================= */

function createSocietyInfrastructure(parent) {
    addBox(
        parent,
        "Water Pump Station",
        -18,
        0,
        2,
        3,
        1.5,
        2.5,
        "#587e69",
        {
            category: "Common Utility",
            description: "Common-area water pumping infrastructure.",
            energy: null,
            status: "Operational"
        }
    );

    addBox(
        parent,
        "Backup Generator",
        18,
        0,
        -3,
        3.3,
        1.5,
        2,
        "#6a776d",
        {
            category: "Backup Infrastructure",
            description: "Standby backup generator for power interruptions.",
            status: "Standby"
        }
    );

    addBox(
        parent,
        "Security Monitoring",
        -18,
        0,
        -7,
        1.3,
        2.5,
        1.3,
        "#435f4d",
        {
            category: "Common Utility",
            description: "Society security and CCTV monitoring point.",
            status: "Operational"
        }
    );

    addBox(
        parent,
        "Society Entrance Gate",
        0,
        0,
        19,
        7,
        2.3,
        0.25,
        "#71887a",
        {
            category: "Society Infrastructure",
            description: "Main residential community entrance."
        }
    );

    addBox(
        parent,
        "Entrance Gate Pillar",
        -3.6,
        0,
        19,
        0.5,
        3.1,
        0.5,
        "#9cad9e",
        { selectable: false }
    );

    addBox(
        parent,
        "Entrance Gate Pillar",
        3.6,
        0,
        19,
        0.5,
        3.1,
        0.5,
        "#9cad9e",
        { selectable: false }
    );
}


/* =========================================================
   16. LANDSCAPING
   ========================================================= */

function createLandscape(parent) {
    const treePositions = [
        [-19, -17],
        [-19, 15],
        [19, -17],
        [19, 15],
        [-7, -19],
        [7, -19],
        [-7, 19],
        [7, 19],
        [-19, 0],
        [19, 7]
    ];

    treePositions.forEach((position, index) => {
        createTree(parent, position[0], position[1], index);
    });
}

function createTree(parent, x, z, index) {
    const trunk = new THREE.Mesh(
        new THREE.CylinderGeometry(0.12, 0.17, 1.3, 6),
        material("#70543a")
    );

    trunk.position.set(x, 0.65, z);
    parent.add(trunk);

    const leaves = new THREE.Mesh(
        new THREE.IcosahedronGeometry(0.85, 1),
        material(index % 2 === 0 ? "#276342" : "#34774d")
    );

    leaves.position.set(x, 1.7, z);
    parent.add(leaves);
}

function createTextSprite(text) {
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 128;

    const context = canvas.getContext("2d");

    context.fillStyle = "rgba(5,18,11,0.88)";
    context.fillRect(0, 0, 512, 128);

    context.strokeStyle = "#35d68b";
    context.lineWidth = 4;
    context.strokeRect(3, 3, 506, 122);

    context.fillStyle = "#ffffff";
    context.font = "bold 48px Inter, Arial";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(text, 256, 65);

    const texture = new THREE.CanvasTexture(canvas);

    const sprite = new THREE.Sprite(
        new THREE.SpriteMaterial({
            map: texture,
            transparent: true,
            depthWrite: false
        })
    );

    return sprite;
}


/* =========================================================
   17. PROPOSED ENERGY INTEGRATION SCENE
   ========================================================= */

function createProposedScene() {
    clearTwinScene();

    const world = state.three.world;

    createGround(world);

    addBox(
        world,
        "Energy Integration Platform",
        0,
        0,
        0,
        29,
        0.35,
        19,
        "#183b27",
        {
            category: "Energy System",
            description: "Proposed integrated energy infrastructure."
        }
    );

    addEnergyUnit(
        world,
        "Utility Grid",
        -10,
        0.2,
        -5,
        "#627d6b",
        "Existing electricity supply connection."
    );

    addEnergyUnit(
        world,
        "PV Inverter",
        -3,
        0.2,
        -5,
        "#267b55",
        "Proposed solar photovoltaic inverter."
    );

    addEnergyUnit(
        world,
        "Battery Storage",
        5,
        0.2,
        -5,
        "#397b58",
        "Proposed battery energy storage system."
    );

    addEnergyUnit(
        world,
        "EV Charger",
        11,
        0.2,
        1,
        "#337b8a",
        "Proposed electric vehicle charging infrastructure."
    );

    addEnergyUnit(
        world,
        "Base Heat Pump",
        -7,
        0.2,
        5,
        "#467e83",
        "Proposed heat pump integration."
    );

    createSolarArray(world, -3, 0.5, 5);

    addEnergyUnit(
        world,
        "Total Load",
        3,
        0.2,
        5,
        "#a17d3d",
        "Aggregate community energy demand."
    );

    const connections = [
        [[-10, 2, -5], [-3, 2, -5]],
        [[-3, 2, -5], [5, 2, -5]],
        [[5, 2, -5], [11, 2, 1]],
        [[-3, 2, -5], [-7, 2, 5]],
        [[5, 2, -5], [3, 2, 5]],
        [[-3, 2, -5], [-3, 2, 5]]
    ];

    connections.forEach(points => {
        addLine(world, points, "#45d995", 0.8);
    });

    const title = createTextSprite("PROPOSED ENERGY INTEGRATION");
    title.position.set(0, 5, -9);
    title.scale.set(9, 2.2, 1);
    world.add(title);

    state.sceneMode = "proposed";

    updateSceneButtons();
    resetTwinCamera();
}

function addEnergyUnit(
    parent,
    name,
    x,
    y,
    z,
    color,
    description
) {
    const unit = addBox(
        parent,
        name,
        x,
        y,
        z,
        3.2,
        2.4,
        2.5,
        color,
        {
            category: "Proposed Integration",
            description,
            status: "Proposed / Simulated"
        }
    );

    addBox(
        parent,
        `${name} top panel`,
        x,
        y + 2.4,
        z,
        2.6,
        0.12,
        2,
        "#a4c6ae",
        { selectable: false }
    );

    return unit;
}

function createSolarArray(parent, x, y, z) {
    for (let row = 0; row < 2; row++) {
        for (let column = 0; column < 3; column++) {
            const panel = new THREE.Mesh(
                new THREE.BoxGeometry(1.7, 0.12, 1.4),
                material("#174c61", 0.35, 0.4)
            );

            panel.position.set(
                x + column * 1.9,
                y + 1.8,
                z + row * 1.7
            );

            panel.rotation.x = -0.12;
            parent.add(panel);

            const frame = new THREE.Mesh(
                new THREE.BoxGeometry(1.85, 0.08, 1.55),
                material("#a6b5a9", 0.45, 0.3)
            );

            frame.position.copy(panel.position);
            frame.position.y -= 0.08;
            frame.rotation.x = -0.12;
            parent.add(frame);
        }
    }

    const label = createTextSprite("PV SOLAR ARRAY");
    label.position.set(x + 1.9, 4, z + 1);
    label.scale.set(4, 1, 1);
    parent.add(label);
}


/* =========================================================
   18. SCENE MANAGEMENT
   ========================================================= */

function clearTwinScene() {
    const world = state.three.world;

    world.traverse(object => {
        if (object.geometry) {
            object.geometry.dispose();
        }

        if (object.material) {
            const materials = Array.isArray(object.material)
                ? object.material
                : [object.material];

            materials.forEach(item => {
                if (item.map) item.map.dispose();
                item.dispose();
            });
        }
    });

    while (world.children.length > 0) {
        world.remove(world.children[0]);
    }

    state.three.interactiveObjects = [];
    state.selectedObject = null;

    showSelectedObject(null);
}

function updateSceneButtons() {
    const societyButton = $("societySceneBtn");
    const proposedButton = $("proposedSceneBtn");

    if (!societyButton || !proposedButton) return;

    societyButton.classList.toggle(
        "active",
        state.sceneMode === "society"
    );

    proposedButton.classList.toggle(
        "active",
        state.sceneMode === "proposed"
    );
}

function initializeTwinButtons() {
    const societyButton = $("societySceneBtn");
    const proposedButton = $("proposedSceneBtn");
    const resetButton = $("reset3DView");

    if (societyButton) {
        societyButton.addEventListener("click", () => {
            if (state.sceneMode !== "society") {
                createSocietyScene();
            }
        });
    }

    if (proposedButton) {
        proposedButton.addEventListener("click", () => {
            if (state.sceneMode !== "proposed") {
                createProposedScene();
            }
        });
    }

    if (resetButton) {
        resetButton.addEventListener("click", resetTwinCamera);
    }
}


/* =========================================================
   19. CAMERA CONTROLS
   ========================================================= */

function resetTwinCamera() {
    if (!state.three) return;

    const { camera, controls } = state.three;

    if (state.sceneMode === "proposed") {
        camera.position.set(22, 18, 25);

        if (controls) {
            controls.target.set(0, 1.5, 0);
        }
    } else {
        camera.position.set(19, 16, 23);

        if (controls) {
            controls.target.set(0, 2, 0);
        }
    }

    camera.lookAt(0, 1.5, 0);

    if (controls) controls.update();
}

function resizeDigitalTwin() {
    if (!state.three) return;

    const canvas = state.three.renderer.domElement;
    const parent = canvas.parentElement;

    if (!parent) return;

    const width = parent.clientWidth;
    const height = parent.clientHeight;

    if (!width || !height) return;

    if (
        state.three.lastWidth === width &&
        state.three.lastHeight === height
    ) {
        return;
    }

    state.three.lastWidth = width;
    state.three.lastHeight = height;

    state.three.camera.aspect = width / height;
    state.three.camera.updateProjectionMatrix();

    state.three.renderer.setSize(width, height, false);
}


/* =========================================================
   20. 3D OBJECT SELECTION & BUILDING DETAILS
   ========================================================= */

function initializeTwinInteraction() {
    const canvas = $("society3DCanvas");

    if (!canvas || !state.three) return;

    canvas.addEventListener("pointerdown", event => {
        if (event.button !== 0) return;

        const rect = canvas.getBoundingClientRect();

        state.three.pointer.x =
            ((event.clientX - rect.left) / rect.width) * 2 - 1;

        state.three.pointer.y =
            -((event.clientY - rect.top) / rect.height) * 2 + 1;

        state.three.raycaster.setFromCamera(
            state.three.pointer,
            state.three.camera
        );

        const intersections = state.three.raycaster.intersectObjects(
            state.three.interactiveObjects,
            false
        );

        if (intersections.length > 0) {
            const selected = intersections[0].object;

            state.selectedObject = selected;
            showSelectedObject(selected);
        }
    });
}


/* Create a building metrics display without requiring HTML edits */

function createTwinMetricsContainer() {
    let container = $("twinObjectMetrics");

    if (container) return container;

    const energyElement = $("twinObjectEnergy");

    if (!energyElement || !energyElement.parentElement) {
        return null;
    }

    container = document.createElement("div");
    container.id = "twinObjectMetrics";

    container.style.display = "grid";
    container.style.gridTemplateColumns =
        "repeat(2, minmax(0, 1fr))";
    container.style.gap = "12px";
    container.style.marginTop = "14px";
    container.style.width = "100%";

    energyElement.parentElement.insertAdjacentElement(
        "afterend",
        container
    );

    return container;
}

function renderBuildingMetrics(metrics) {
    const container = createTwinMetricsContainer();

    if (!container) return;

    container.replaceChildren();

    const items = [
        {
            label: "Average Voltage",
            value: metrics.voltage,
            unit: "V"
        },
        {
            label: "Total Power",
            value: metrics.powerKW,
            unit: "kW"
        },
        {
            label: "Energy Reading",
            value: metrics.energy,
            unit: "kWh"
        },
        {
            label: "Total Energy",
            value: metrics.totalEnergy,
            unit: "kWh"
        },
        {
            label: "Total Current",
            value: metrics.current,
            unit: "A"
        },
        {
            label: "Connected Sensors",
            value: metrics.sensorCount,
            unit: ""
        }
    ];

    items.forEach(item => {
        const card = document.createElement("div");

        card.style.padding = "12px";
        card.style.borderRadius = "10px";
        card.style.background = "rgba(53,214,139,0.07)";
        card.style.border = "1px solid rgba(53,214,139,0.15)";
        card.style.minWidth = "0";

        const heading = document.createElement("div");

        heading.textContent = item.label;
        heading.style.fontSize = "11px";
        heading.style.opacity = "0.7";
        heading.style.marginBottom = "6px";

        const reading = document.createElement("strong");

        reading.style.fontSize = "16px";
        reading.style.color = "#35d68b";

        reading.textContent =
            item.value === null || !Number.isFinite(Number(item.value))
                ? "--"
                : `${formatNumber(item.value, 2)} ${item.unit}`.trim();

        card.appendChild(heading);
        card.appendChild(reading);

        container.appendChild(card);
    });
}

function clearBuildingMetrics() {
    const container = $("twinObjectMetrics");

    if (container) {
        container.replaceChildren();
    }
}

function showSelectedObject(object) {
    if (!object) {
        setText("twinObjectName", "Select an object");
        setText("twinObjectType", "Explore the community model");

        setText(
            "twinObjectDescription",
            "Select buildings and energy infrastructure to explore their role in the ecosystem."
        );

        setText("twinObjectEnergy", "--");
        setText("twinObjectStatus", "--");

        clearBuildingMetrics();

        return;
    }

    const info = object.userData || {};

    setText("twinObjectName", info.name || "Selected Component");
    setText("twinObjectType", info.category || "Infrastructure");

    setText(
        "twinObjectDescription",
        info.description || "Energy infrastructure component."
    );

    /* BUILDING DETAILS */

    if (info.buildingId) {
        const metrics = info.metrics;

        if (metrics) {
            setText(
                "twinObjectEnergy",
                `${formatNumber(metrics.totalEnergy, 3)} kWh`
            );

            setText(
                "twinObjectStatus",
                "Operational · Live"
            );

            renderBuildingMetrics(metrics);

        } else {
            setText("twinObjectEnergy", "Not available");

            setText(
                "twinObjectStatus",
                "No Sensor Data"
            );

            clearBuildingMetrics();
        }

        return;
    }

    /* OTHER INFRASTRUCTURE COMPONENTS */

    clearBuildingMetrics();

    const energy =
        info.energy !== null && info.energy !== undefined
            ? Number(info.energy)
            : null;

    setText(
        "twinObjectEnergy",
        energy !== null && Number.isFinite(energy)
            ? `${formatNumber(energy, 2)} kWh`
            : "Not available"
    );

    setText(
        "twinObjectStatus",
        info.status || "Operational"
    );
}


/* =========================================================
   21. 3D ANIMATION LOOP
   ========================================================= */

function animateDigitalTwin() {
    if (!state.three) return;

    state.animationFrame = requestAnimationFrame(
        animateDigitalTwin
    );

    if (state.three.controls) {
        state.three.controls.update();
    }

    state.three.renderer.render(
        state.three.scene,
        state.three.camera
    );
}


/* =========================================================
   22. 3D ERROR HANDLING
   ========================================================= */

function showTwinError(message) {
    const loading = $("twinLoading");

    if (loading) {
        loading.textContent = message;
        loading.classList.remove("hidden");
    }

    setText("twinStatus", "Unavailable");

    console.error(message);
}


/* =========================================================
   23. DATE & TIME
   ========================================================= */

function updateDate() {
    const element = $("currentDate");

    if (!element) return;

    const now = new Date();

    element.textContent = now.toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    }).toUpperCase();
}


/* =========================================================
   24. APPLICATION INITIALIZATION
   ========================================================= */

async function initializeEcoGrid() {
    if (state.initialized) return;

    state.initialized = true;

    console.log("EcoGrid initializing...");

    initializeIntro();
    initializeNavigation();
    updateDate();

    try {
        initializeDigitalTwin();
    } catch (error) {
        console.error("3D initialization failed:", error);
        showTwinError("3D environment could not initialize.");
    }

    await fetchDashboardData();

    state.refreshTimer = setInterval(() => {
        fetchDashboardData();
    }, CONFIG.REFRESH_INTERVAL);

    window.addEventListener("resize", resizeDigitalTwin);

    setText("twinStatus", state.three ? "Ready" : "Unavailable");

    console.log("EcoGrid initialization complete.");
}


/* =========================================================
   25. START APPLICATION
   ========================================================= */

if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeEcoGrid,
        { once: true }
    );
} else {
    initializeEcoGrid();
}


/* =========================================================
   END OF ECOGRID APPLICATION SCRIPT
   ========================================================= */