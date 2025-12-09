import os

ENV_FILE = ".env"


MODES = {
    "1": {
        "name": "SAFE",
        "description": "Sangat hati-hati, jarang entry. Cocok buat test / akun kecil.",
        "TIMEFRAME_MINUTES": 15,
        "TECH_CONF_THRESHOLD": 0.35,
        "DRY_RUN": "true",
        "USE_SENTIMENT": "true",
    },
    "2": {
        "name": "BALANCED",
        "description": "Seimbang, nggak terlalu takut, nggak terlalu barbar.",
        "TIMEFRAME_MINUTES": 15,
        "TECH_CONF_THRESHOLD": 0.25,
        "DRY_RUN": "true",
        "USE_SENTIMENT": "true",
    },
    "3": {
        "name": "AGGRESSIVE",
        "description": "Lebih sering entry, cocok buat backtest / uji nyali.",
        "TIMEFRAME_MINUTES": 15,
        "TECH_CONF_THRESHOLD": 0.15,
        "DRY_RUN": "true",
        "USE_SENTIMENT": "false",
    },
    "4": {
        "name": "SCALPING_M5",
        "description": "Timeframe 5 menit, buat scalping. Lebih noise.",
        "TIMEFRAME_MINUTES": 5,
        "TECH_CONF_THRESHOLD": 0.20,
        "DRY_RUN": "true",
        "USE_SENTIMENT": "false",
    },
}


def load_env_lines():
    if not os.path.exists(ENV_FILE):
        print(f"[!] {ENV_FILE} tidak ditemukan.")
        return []
    with open(ENV_FILE, "r", encoding="utf-8") as f:
        return f.readlines()


def save_env_lines(lines):
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)


def set_env_var(lines, key, value):
    key_eq = key + "="
    replaced = False
    new_lines = []
    for line in lines:
        if line.strip().startswith(key_eq):
            new_lines.append(f"{key}={value}\n")
            replaced = True
        else:
            new_lines.append(line)
    if not replaced:
        new_lines.append(f"{key}={value}\n")
    return new_lines


def apply_mode(mode_key):
    mode = MODES[mode_key]
    print(f"\n[*] Menerapkan mode: {mode['name']} - {mode['description']}\n")

    lines = load_env_lines()
    if not lines:
        return

    lines = set_env_var(lines, "TRADING_MODE", mode["name"])
    lines = set_env_var(lines, "TIMEFRAME_MINUTES", str(mode["TIMEFRAME_MINUTES"]))
    lines = set_env_var(lines, "TECH_CONF_THRESHOLD", str(mode["TECH_CONF_THRESHOLD"]))
    lines = set_env_var(lines, "DRY_RUN", mode["DRY_RUN"])
    lines = set_env_var(lines, "USE_SENTIMENT", mode["USE_SENTIMENT"])

    save_env_lines(lines)
    print("[✓] .env berhasil di-update.")
    print(f"    TRADING_MODE={mode['name']}")
    print(f"    TIMEFRAME_MINUTES={mode['TIMEFRAME_MINUTES']}")
    print(f"    TECH_CONF_THRESHOLD={mode['TECH_CONF_THRESHOLD']}")
    print(f"    DRY_RUN={mode['DRY_RUN']}")
    print(f"    USE_SENTIMENT={mode['USE_SENTIMENT']}")
    print("\nSekarang jalanin bot dengan:")
    print("  python -m core.main_loop\n")


def main():
    print("===== AI TRADING MODE DASHBOARD =====\n")
    for k, v in MODES.items():
        print(f"[{k}] {v['name']}  →  {v['description']}")
    print("\n[0] Keluar\n")

    choice = input("Pilih mode (angka): ").strip()

    if choice == "0" or choice == "":
        print("Keluar tanpa perubahan.")
        return

    if choice not in MODES:
        print("Pilihan tidak valid.")
        return

    apply_mode(choice)


if __name__ == "__main__":
    main()
