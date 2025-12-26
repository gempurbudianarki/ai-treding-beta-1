// static/js/dashboard.js

document.addEventListener("DOMContentLoaded", () => {
    console.log("[dashboard] JS loaded");

    const navItems = document.querySelectorAll(".nav-item");
    const views = document.querySelectorAll(".view");

    const toggleTrading = document.getElementById("toggle-trading");
    const modeSelect = document.getElementById("mode-select");

    const badgeMode = document.getElementById("badge-mode");
    const badgeDryrun = document.getElementById("badge-dryrun");
    const sidebarUpdated = document.getElementById("sidebar-updated");

    // --- helper safe-get untuk nested obj ---
    const get = (obj, path, fallback = null) => {
        try {
            return path.split(".").reduce((o, k) => (o && k in o ? o[k] : undefined), obj) ?? fallback;
        } catch {
            return fallback;
        }
    };

    // ================= NAV SWITCH =================
    navItems.forEach(btn => {
        btn.addEventListener("click", () => {
            const view = btn.dataset.view;
            navItems.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            views.forEach(v => {
                if (v.id === `view-${view}`) {
                    v.classList.add("active");
                } else {
                    v.classList.remove("active");
                }
            });
        });
    });

    // ================= FETCH STATUS =================
    async function fetchStatus() {
        try {
            const res = await fetch("/api/status");
            if (!res.ok) {
                console.warn("status.json not ready yet");
                return;
            }
            const data = await res.json();
            updateUIFromStatus(data);
        } catch (err) {
            console.error("Error fetch status:", err);
        }
    }

    function updateUIFromStatus(data) {
        if (!data || typeof data !== "object") return;

        const symbol = data.symbol || "-";
        const tf = data.timeframe_minutes ?? data.timeframe ?? 0;
        const dryRun = !!data.dry_run;
        const mode = (data.mode || "SAFE").toUpperCase();
        const tradingEnabled = data.trading_enabled !== false; // default true if kosong

        // Badge mode + dryrun
        if (badgeMode) {
            badgeMode.textContent = `MODE: ${mode}`;
        }
        if (badgeDryrun) {
            badgeDryrun.textContent = `DRY RUN: ${dryRun ? "ON" : "OFF"}`;
        }

        // Sidebar updated time (pakai timestamp kalau ada)
        if (sidebarUpdated) {
            const ts = data.timestamp || "-";
            sidebarUpdated.textContent = `Updated: ${ts}`;
        }

        // Sync toggle + dropdown
        if (toggleTrading) {
            toggleTrading.checked = tradingEnabled;
        }
        if (modeSelect) {
            modeSelect.value = mode;
        }

        // Update card yang sudah di-render server kalau mau dipaksa live:
        const accountCard = document.querySelector(".card .card-value");
        if (accountCard) {
            accountCard.textContent = symbol;
        }

        // Technical card
        const techCard = document.querySelectorAll(".card .card-label");
        // cari card yg labelnya "Technical Bias" & "Sentiment"
        techCard.forEach(labelEl => {
            const text = labelEl.textContent.trim().toLowerCase();
            const parent = labelEl.parentElement;
            if (!parent) return;

            if (text === "technical bias") {
                const valEl = parent.querySelector(".card-value");
                const mutedEl = parent.querySelector(".muted");
                if (valEl) {
                    const dir = get(data, "technical.direction", "-");
                    valEl.textContent = String(dir || "-").toUpperCase();
                }
                if (mutedEl) {
                    const conf = get(data, "technical.confidence", 0);
                    mutedEl.textContent = `Confidence: ${conf.toFixed(2)}`;
                }
            }

            if (text === "sentiment") {
                const valEl = parent.querySelector(".card-value");
                const mutedEl = parent.querySelector(".muted");
                if (valEl) {
                    const sent = get(data, "sentiment.sentiment", "-");
                    valEl.textContent = sent && sent !== "-" ? String(sent).charAt(0).toUpperCase() + String(sent).slice(1) : "-";
                }
                if (mutedEl) {
                    const conf = get(data, "sentiment.confidence", 0);
                    mutedEl.textContent = `Confidence: ${conf.toFixed(2)}`;
                }
            }

            if (text === "last loop") {
                const valEl = parent.querySelector(".card-value");
                if (valEl) {
                    valEl.textContent = data.timestamp || "-";
                }
            }
        });
    }

    // ================== TOGGLE TRADING ==================
    if (toggleTrading) {
        toggleTrading.addEventListener("change", async () => {
            const enabled = toggleTrading.checked;
            try {
                const res = await fetch("/api/toggle", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ trading_enabled: enabled })
                });
                const data = await res.json();
                console.log("toggle response:", data);
            } catch (err) {
                console.error("toggle error:", err);
            }
        });
    }

    // ================== SET MODE ==================
    if (modeSelect) {
        modeSelect.addEventListener("change", async () => {
            const mode = modeSelect.value;
            try {
                const res = await fetch("/api/set_mode", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ mode })
                });
                const data = await res.json();
                console.log("mode response:", data);

                if (badgeMode) {
                    badgeMode.textContent = `MODE: ${mode.toUpperCase()}`;
                }
            } catch (err) {
                console.error("set_mode error:", err);
            }
        });
    }

    // ================== SIGNALS (opsional; kalau lo nanti bikin tabel) ==================
    async function fetchSignals() {
        const tableBody = document.getElementById("signals-table-body");
        const snap = document.getElementById("signals-snapshot");

        if (!tableBody && !snap) return;

        try {
            const res = await fetch("/api/signals");
            if (!res.ok) return;
            const signals = await res.json();

            if (tableBody) {
                tableBody.innerHTML = "";
                signals.slice().reverse().forEach(sig => {
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td>${sig.time || "-"}</td>
                        <td>${sig.symbol || "-"}</td>
                        <td>${sig.action || "-"}</td>
                        <td>${sig.reason || "-"}</td>
                    `;
                    tableBody.appendChild(tr);
                });
            }

            if (snap) {
                snap.innerHTML = "";
                signals.slice(-5).reverse().forEach(sig => {
                    const div = document.createElement("div");
                    div.className = "headline-item";
                    div.textContent = `${sig.time || ""} • ${sig.action || ""} • ${sig.reason || ""}`;
                    snap.appendChild(div);
                });
            }

        } catch (err) {
            console.error("fetchSignals error:", err);
        }
    }

    // ================== PNL (opsional; kalau nanti lo pakai chart.js / dll) ==================
    async function fetchPnl() {
        // placeholder kalau lo mau pakai canvas #daily-pnl-chart
        // sementara nggak di-implement biar nggak nambah lib
    }

    // ================== LOOPING ==================
    fetchStatus();
    fetchSignals();

    setInterval(() => {
        fetchStatus();
        fetchSignals();
    }, 60000); // 60 detik
});
