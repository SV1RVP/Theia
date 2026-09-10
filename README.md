<p align="center">
  <img src="logo/Theia%20Dark.png" alt="Project Theia Logo" width="170">
</p>

# Project Theia (Θεία) - Real-Time Radiation Monitoring & Multi-Cloud Proxy

[![License: AGPL v3](https://img.shields.io/badge/Code_License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.html)
[![Data License: CC BY-NC-SA 4.0](https://img.shields.io/badge/Data_License-CC_BY--NC--SA_4.0-orange.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask-black.svg)](https://flask.palletsprojects.com/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-SV1RVP%2FTheia-brightgreen.svg)](https://github.com/SV1RVP/Theia)

[🇬🇧 English](#-english) • [🇬🇷 Ελληνικά](#-ελληνικά)

---

## 🇬🇧 English

### 🌌 The Myth of Titaness Theia & The Project's Name

> *"Theia (Θεία), the shining Titaness of clear sight and celestial light, who endowed gold and silver with their wondrous luster, and gave to mortal eyes the divine power of vision..."*  
> — *Hesiod, Theogony*

In ancient Greek mythology, **Theia (Θεία)**—whose name literally signifies *"divine"*, *"goddess"*, or *"sight"*—was one of the primordial Titans, the daughter of Uranus (the Sky) and Gaia (the Earth). Revered as the goddess of vision, light, and the shimmering heavens, she gave mortal eyes the capacity to perceive light and behold the grandeur of the physical world. She was also the mother of the celestial triad: **Helios (the Sun)**, **Selene (the Moon)**, and **Eos (the Dawn)**—the celestial bodies whose rays illuminate our planet.

#### Why Project Theia?
Ionizing radiation and cosmic rays constantly permeate our atmosphere and terrestrial surroundings. Yet, despite their immense physical power and biological significance, they are completely invisible, odorless, and silent to the human senses.

Just as the Titaness Theia endowed humanity with the gift of physical sight, **Project Theia bestows upon us the digital vision to perceive that which is otherwise unseen.** By intercepting, recording, and visualizing the radioactive pulses of your detector in real time, Project Theia illuminates the invisible universe of ionizing radiation, transforming silent environmental waves into clear, actionable knowledge.

---

### 📌 Overview
**Project Theia** is a lightweight, secure local proxy server, scientific telemetry logger, and state-of-the-art Web Dashboard designed for WiFi-enabled Geiger-Müller radiation monitors (such as the GQ GMC-300, GMC-500+, GMC-600+, or custom ESP32/ESP8266 radiation detectors).

The server intercepts telemetry emitted by radiation monitors over your local network (LAN), persists the readings in local SQLite and CSV formats, renders an ultra-clean live dashboard, and asynchronously pushes measurements to global citizen-science platforms (**GMCMap.com**, **Radmon.org**, **Safecast.org**, and **OpenSenseMap.org**) without adding any latency to the detector.

---

### ⚙️ Complete Key Features

1. **Real-Time Radiation Telemetry**:
   - Live instantaneous CPM (Counts Per Minute), ACPM (Average CPM), and calculated Dose Rate ($\mu\text{Sv/h}$).
   - **24-Hour Accumulated Dose ($\mu\text{Sv}$)**: Utilizes trapezoidal numerical integration over 24-hour readings to calculate the true accumulated exposure dose in microSieverts ($\mu\text{Sv}$), eliminating confusing lifetime raw pulse counters.
   - 3 analog-style dial gauges and an Environmental Radiation Spectrum indicator (Safe, Elevated, Warning, Danger).

2. **Refined, Distraction-Free Web Dashboard**:
   - Modern glassmorphism UI with subtle micro-animations and responsive layout.
   - Clean top navigation bar with a centralized **Live Status Pill** (`NORMAL (SAFE)`, `ELEVATED`, `DANGER`, `OFFLINE`).
   - High-DPI unclipped logo emblem.
   - **One-Click Bilingual Switching**: Instant toggle between **English** and **Ελληνικά** with browser persistence.
   - **Adaptive Dark & Light Themes**: Seamless palette switching matched to the Theia emblems.

3. **High-Resolution Historical Analytics**:
   - 24-hour trend area chart powered by ApexCharts.
   - Quick timeframe selectors (1h, 6h, 12h, 24h).
   - Dual-axis mode (pulses CPM alongside dose rate $\mu\text{Sv/h}$) and single-metric focus.
   - Live statistics ribbon (24h Average CPM, Peak Maximum $\mu\text{Sv/h}$, Data Points count).
   - One-click **CSV Data Export** with timestamps, CPM, and $\mu\text{Sv/h}$.

4. **Multi-Target Asynchronous Cloud Forwarder**:
   - Background worker queue that forwards readings to global networks without blocking local response time:
     - **GMCMap.com** (Global radiation map)
     - **Radmon.org** (Open community monitoring)
     - **Safecast.org** (CC0 open data)
     - **OpenSenseMap.org** (Citizen Science - CC BY-SA)
   - Individual retry logic with configurable backoff.

5. **Security & Local Data Privacy**:
   - **IP Whitelisting**: Restricts ingestion to private LAN subnets or explicit IP/CIDR masks in `config/app.json`.
   - **Token Authentication**: Accepts `X-Theia-Token` header or `?token=...` parameter.
   - **Automated Retention Purge**: Keeps SQLite database size manageable on micro-servers like Raspberry Pi.

6. **Automated One-Click Updates**:
   - Dedicated updater scripts (`update-windows.bat`, `update-linux.sh`) pulling directly from the official GitHub repository [https://github.com/SV1RVP/Theia](https://github.com/SV1RVP/Theia).
   - Built-in update check API (`/api/system/check-update`).

---

### 📁 Modular Configuration & Local Storage (`config/`)

All system settings, platform credentials, and local historical databases are cleanly organized inside the `config/` directory:

| File | Target Platform / Purpose | Key Settings / Role |
|:---|:---|:---|
| `config/app.json` | Project Theia Core Server | `port`, `retention_days`, `ingest_auth_token`, `allowed_device_ips`, retry limits |
| `config/gmcmap.json` | GMCMap.com (GQ Electronics) | `enabled`, `user_account_id`, `geiger_counter_id` |
| `config/radmon.json` | Radmon.org Community Network | `enabled`, `username`, `password` |
| `config/safecast.json` | Safecast.org Global Open Data | `enabled`, `api_key`, `device_id`, `latitude`, `longitude` |
| `config/opensensemap.json` | OpenSenseMap.org Citizen Science | `enabled`, `sensebox_id`, `sensor_id` |
| `config/radiation_data.db` | Local SQLite Database | Telemetry history, timestamps, CPM and dose logs |
| `config/radiation_log.csv` | Measurement Log (CSV) | Continuous tabular raw radiation data |

*Note: All files inside `config/` are strictly preserved and never overwritten during system updates.*

---

### 🚀 Installation & Quick Start

#### 🪟 Windows Setup
1. **Clone or Download:**
   ```cmd
   git clone https://github.com/SV1RVP/Theia.git
   cd Theia
   ```
2. **Run Installer:**
   Double-click `install-windows.bat` (checks Python 3.9+, creates `.venv`, installs requirements, and prepares `config/`).
3. **Configure Settings (Optional):**
   Open `config/` and edit `app.json` or the platform JSON files (`gmcmap.json`, etc.) with your favorite editor.
4. **Start Server:**
   Double-click `start-windows.bat` (or run `.venv\Scripts\python.exe main.py`).
5. Open [http://localhost:80](http://localhost:80) in your web browser.

#### 🐧 Linux / Raspberry Pi Setup
1. **Clone:**
   ```bash
   git clone https://github.com/SV1RVP/Theia.git
   cd Theia
   ```
2. **Install:**
   ```bash
   chmod +x install-linux.sh update-linux.sh
   ./install-linux.sh
   ```
3. **Configure Settings (Optional):**
   ```bash
   nano config/app.json
   nano config/gmcmap.json
   ```
4. **Start in Production (Gunicorn):**
   ```bash
   sudo .venv/bin/gunicorn --bind 0.0.0.0:80 main:app
   ```

---

### 🔄 Updating Project Theia

Project Theia can be updated directly from the official [GitHub Repository](https://github.com/SV1RVP/Theia) using either method:

1. **One-Click Update via Web Dashboard (Recommended)**:
   - Click the **`🔄 Update`** button in the top navigation bar.
   - Project Theia checks for the latest GitHub commit.
   - Click **"Update Now"**: the server downloads only the system code, **strictly preserves the `config/` folder**, upgrades dependencies, and automatically restarts the service.

2. **Command Line / Scripts**:
   - **Windows**: Double-click `update-windows.bat`
   - **Linux / Raspberry Pi**: Run `./update-linux.sh`

---

### ⚙️ Geiger Counter Configuration

In your Geiger counter's WiFi settings (e.g. GMC-500+):
- **Server:** Your server's local LAN IP (e.g. `192.168.1.50`)
- **Port:** `80`
- **URL Path:** `/log2.asp`

---

### 📡 API Endpoints

- **Data Ingestion:** `GET /log2.asp?CPM=...&ACPM=...&uSV=...&dose=...`
- **Live Readings & 24h History:** `GET /api/data`
- **System Version:** `GET /api/system/version`
- **Check for Updates:** `GET /api/system/check-update`

---

### 👤 Author & Licensing

- **Creator:** Alexandros - Ermis Tsourapas (SV1RVP)
- **Project Code License:** [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html)
- **Radiation Data License:** [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

---
---

## 🇬🇷 Ελληνικά

### 🌌 Ο Μύθος της Τιτανίδας Θείας & Το Όνομα του Project

> *"Η Θεία δε γέννησε τον μέγα Ήλιο και τη λαμπρή Σελήνη, και την Ηώ που φέγγει σε όλους τους θνητούς πάνω στη γη και στους αθάνατους θεούς που κατέχουν τον πλατύ ουρανό..."*  
> — *Ησίοδος, Θεογονία*

Στην αρχαία ελληνική μυθολογία, η **Θεία**—κόρη του Ουρανού και της Γαίας—ήταν μία από τις δώδεκα πρωταρχικές Τιτανίδες. Ήταν η θεότητα του φωτός, της ουράνιας λάμψης και της **όρασης**, εκείνη που χάρισε στα μάτια των θνητών τη δύναμη να βλέπουν το φως και να κατανοούν τον ορατό κόσμο. Παράλληλα, ήταν η μητέρα των ουράνιων σωμάτων που λούζουν τη Γη με φως: του **Ηλίου**, της **Σελήνης** και της **Ηούς (της Αυγής)**.

#### Γιατί Project Theia;
Η ιοντίζουσα ακτινοβολία και οι κοσμικές ακτίνες διαπερνούν συνεχώς το περιβάλλον μας. Ωστόσο, παρόλη τη φυσική και βιολογική τους σημασία, παραμένουν παντελώς αόρατες, άοσμες και ανεπαίσθητες στις ανθρώπινες αισθήσεις.

Όπως η Τιτανίδα Θεία δώρισε στους ανθρώπους το φως και την όραση, έτσι και το **Project Theia χαρίζει στα μάτια μας την «όραση» να αντιλαμβανόμαστε το αόρατο.** Υποδέχεται, καταγράφει και αναλύει σε πραγματικό χρόνο τις καταγραφές του μετρητή ραδιενέργειας, μετατρέποντας τα αόρατα ενεργειακά κύματα σε καθαρή, κατανοητή και ζωντανή πληροφόρηση.

---

### 📌 Επισκόπηση
Το **Project Theia** είναι ένας ελαφρύς, ασφαλής τοπικός διακομιστής (proxy server), καταγραφέας ραδιενέργειας και σύγχρονος πίνακας ελέγχου (Web Dashboard) για μετρητές Geiger-Müller με υποστήριξη WiFi (όπως τα GMC-300, GMC-500+, GMC-600+ ή ιδιοκατασκευές ESP32/ESP8266).

Το σύστημα λαμβάνει τις μετρήσεις του ανιχνευτή μέσω του τοπικού δικτύου (LAN), τις αποθηκεύει σε βάση SQLite και αρχείο CSV, τις προβάλλει σε έναν καλαίσθητο πίνακα ελέγχου στο browser και τις προωθεί ασύγχρονα σε παγκόσμια δίκτυα επιτήρησης (**GMCMap.com**, **Radmon.org**, **Safecast.org**, **OpenSenseMap.org**) χωρίς να καθυστερεί τον ανιχνευτή.

---

### ⚙️ Όλες οι Δυνατότητες του Συστήματος

1. **Τηλεμετρία Ραδιενέργειας σε Πραγματικό Χρόνο**:
   - Ζωντανές ενδείξεις τρέχουσας ροής παλμών **CPM**, μέσου όρου **ACPM** και ρυθμού δόσης σε **$\mu\text{Sv/h}$**.
   - **24-ωρη Συσσωρευμένη Δόση ($\mu\text{Sv}$)**: Υπολογισμός πραγματικής συσσωρευμένης δόσης με τραπεζοειδή αριθμητική ολοκλήρωση των μετρήσεων του τελευταίου 24ώρου, αντικαθιστώντας τους παραπλανητικούς μετρητές παλμών με πραγματική βιολογική έκθεση σε $\mu\text{Sv}$.
   - 3 αναλογικά όργανα με βελόνες και μπάρα φάσματος ακτινοβολίας περιβάλλοντος (Φυσιολογικό, Αυξημένο, Προσοχή, Κίνδυνος).

2. **Κομψός, Μινιμαλιστικός Πίνακας Ελέγχου**:
   - Σύγχρονη σχεδίαση glassmorphism με ομαλά micro-animations.
   - Συμπαγής γραμμή πλοήγησης με **Κεντρικό Badge Κατάστασης** (`NORMAL (SAFE)`, `ELEVATED`, `DANGER`, `OFFLINE`).
   - Μεγάλο, καθαρό εικονίδιο χωρίς κομμένες γωνίες.
   - **Άμεση Εναλλαγή Γλώσσας**: Πλήρης υποστήριξη **Ελληνικών** και **Αγγλικών** με αποθήκευση της προτίμησης.
   - **Σκοτεινό (Dark) & Φωτεινό (Light) Θέμα**: Προσαρμογή στα επίσημα χρώματα των λογοτύπων Theia Dark & White.

3. **Ιστορική Ανάλυση & Γραφήματα Υψηλής Ανάλυσης**:
   - 24-ωρο διαδραστικό διάγραμμα περιοχής (ApexCharts).
   - Επιλογέας χρονικού εύρους (1Ω, 6Ω, 12Ω, 24Ω).
   - Προβολή διπλού άξονα (ταυτόχρονα CPM και $\mu\text{Sv/h}$) ή μεμονωμένης μέτρησης.
   - Λωρίδα γρήγορων στατιστικών (Μέσος όρος 24Ω, Κορυφή $\mu\text{Sv/h}$, Σύνολο καταγραφών).
   - Άμεση **Εξαγωγή σε αρχείο CSV** για στατιστική ανάλυση σε Excel/Python.

4. **Ασύγχρονη Πολυ-Δικτυακή Προώθηση (Multi-Cloud Forwarder)**:
   - Εσωτερική ουρά και worker thread για προώθηση στο παρασκήνιο:
     - **GMCMap.com** (Παγκόσμιος χάρτης)
     - **Radmon.org** (Ανοικτό δίκτυο κοινότητας)
     - **Safecast.org** (Παγκόσμια ανοιχτά δεδομένα - CC0)
     - **OpenSenseMap.org** (Citizen Science - CC BY-SA)

5. **Ασφάλεια & Τοπική Ιδιωτικότητα**:
   - **Φιλτράρισμα IP**: Επιτρέπει μετρήσεις μόνο από το τοπικό LAN ή συγκεκριμένες IP (`config/app.json`).
   - **Έλεγχος Token**: Προαιρετική πιστοποίηση μέσω header `X-Theia-Token` ή παραμέτρου `?token=...`.
   - **Αυτόματη Εκκαθάριση**: Αυτόματη διαγραφή παλιών μετρήσεων για εξοικονόμηση χώρου σε Raspberry Pi.

6. **Αυτόματη Ενημέρωση με Ένα Κλικ**:
   - Έτοιμα scripts ενημέρωσης (`update-windows.bat`, `update-linux.sh`) που αντλούν αυτόματα τις αλλαγές από το επίσημο repository: [https://github.com/SV1RVP/Theia](https://github.com/SV1RVP/Theia).

---

### 📁 Αρθρωτή Διαμόρφωση & Τοπικά Δεδομένα (`config/`)

Όλες οι ρυθμίσεις του συστήματος, οι εξωτερικές πλατφόρμες και τα ιστορικά δεδομένα είναι συγκεντρωμένα στον φάκελο `config/`:

| Αρχείο | Σκοπός / Πλατφόρμα | Βασικές Παράμετροι / Ρόλος |
|:---|:---|:---|
| `config/app.json` | Κεντρικός Διακομιστής Theia | `port`, `retention_days`, `ingest_auth_token`, `allowed_device_ips`, όρια επαναπροσπάθειας |
| `config/gmcmap.json` | GMCMap.com (GQ Electronics) | `enabled`, `user_account_id`, `geiger_counter_id` |
| `config/radmon.json` | Radmon.org Ανοικτή Κοινότητα | `enabled`, `username`, `password` |
| `config/safecast.json` | Safecast.org Ανοικτά Δεδομένα | `enabled`, `api_key`, `device_id`, `latitude`, `longitude` |
| `config/opensensemap.json` | OpenSenseMap.org Citizen Science | `enabled`, `sensebox_id`, `sensor_id` |
| `config/radiation_data.db` | Τοπική Βάση SQLite | Ιστορικό μετρήσεων, χρονοσφραγίδες, CPM και δόσεις |
| `config/radiation_log.csv` | Αρχείο Καταγραφής CSV | Συνεχής καταγραφή ακατέργαστων μετρήσεων |

*Σημείωση: Όλα τα αρχεία μέσα στον φάκελο `config/` προστατεύονται απόλυτα και ΔΕΝ αντικαθίστανται ποτέ κατά τις ενημερώσεις.*

---

### 🚀 Εγκατάσταση & Εκκίνηση

#### 🪟 Σε Windows
1. **Λήψη / Clone:**
   ```cmd
   git clone https://github.com/SV1RVP/Theia.git
   cd Theia
   ```
2. **Εγκατάσταση:**
   Κάντε διπλό κλικ στο `install-windows.bat` (ελέγχει την Python, φτιάχνει το `.venv`, εγκαθιστά τις βιβλιοθήκες και προετοιμάζει τον φάκελο `config/`).
3. **Ρύθμιση Παραμέτρων (Προαιρετικά):**
   Ανοίξτε τον φάκελο `config/` και συμπληρώστε το `app.json` ή τα αρχεία των υπηρεσιών (`gmcmap.json` κ.λπ.) με έναν κειμενογράφο.
4. **Εκκίνηση:**
   Κάντε διπλό κλικ στο `start-windows.bat` (ή εκτελέστε `.venv\Scripts\python.exe main.py`).
5. Ανοίξτε τη διεύθυνση [http://localhost:80](http://localhost:80) στον περιηγητή σας.

#### 🐧 Σε Linux / Raspberry Pi
1. **Λήψη:**
   ```bash
   git clone https://github.com/SV1RVP/Theia.git
   cd Theia
   ```
2. **Εγκατάσταση:**
   ```bash
   chmod +x install-linux.sh update-linux.sh
   ./install-linux.sh
   ```
3. **Ρύθμιση Παραμέτρων (Προαιρετικά):**
   ```bash
   nano config/app.json
   nano config/gmcmap.json
   ```
4. **Εκκίνηση με Gunicorn:**
   ```bash
   sudo .venv/bin/gunicorn --bind 0.0.0.0:80 main:app
   ```

---

### 🔄 Ενημέρωση (Update) του Project Theia

Μπορείτε να αναβαθμίσετε το Project Theia στην τελευταία έκδοση από το [GitHub](https://github.com/SV1RVP/Theia) με δύο τρόπους:

1. **Απευθείας από το Web Dashboard με 1 Κλικ (Συνιστάται)**:
   - Πατάτε το κουμπί **`🔄 Update`** στην επάνω γραμμή πλοήγησης.
   - Ελέγχεται αυτόματα το τελευταίο commit στο GitHub.
   - Πατάτε **"Ενημέρωση Τώρα"**: Το σύστημα κατεβάζει μόνο τα νέα αρχεία συστήματος, **προστατεύει 100% τον φάκελο `config/`**, αναβαθμίζει τις βιβλιοθήκες και επανεκκινεί αυτόματα την υπηρεσία (service restart).

2. **Μέσω Εντολών / Scripts**:
   - **Σε Windows**: Κάντε διπλό κλικ στο `update-windows.bat`
   - **Σε Linux / Raspberry Pi**: Εκτελέστε `./update-linux.sh`

---

### ⚙️ Ρύθμιση του Μετρητή Geiger

Στις ρυθμίσεις WiFi του μετρητή σας (π.χ. GMC-500+):
- **Server:** Η τοπική IP του υπολογιστή/Raspberry Pi (π.χ. `192.168.1.50`)
- **Port:** `80`
- **URL Path:** `/log2.asp`

---

### 📡 API Endpoints

- **Υποδοχή Μετρήσεων:** `GET /log2.asp?CPM=...&ACPM=...&uSV=...&dose=...`
- **Δεδομένα & Ιστορικό 24Ω:** `GET /api/data`
- **Έκδοση Συστήματος:** `GET /api/system/version`
- **Έλεγχος Ενημερώσεων:** `GET /api/system/check-update`

---

### 👤 Δημιουργός & Άδειες Χρήσης

- **Δημιουργός:** Alexandros - Ermis Tsourapas (SV1RVP)
- **Άδεια Project / Κώδικα:** [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html)
- **Άδεια Δεδομένων:** [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
