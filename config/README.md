# Project Theia - Configuration Files / Αρχεία Ρυθμίσεων

This directory contains individual JSON configuration files for Project Theia and all supported platforms.
Σε αυτόν τον φάκελο βρίσκονται τα ξεχωριστά αρχεία ρυθμίσεων JSON για το Project Theia και τις υποστηριζόμενες πλατφόρμες.

---

## 📁 Files Overview / Επισκόπηση Αρχείων

### 1. `app.json` (Project & Server Settings / Ρυθμίσεις Συστήματος)
- **`port`**: Listening port (default `80`, or `5000` / `8080`). / Θύρα ακρόασης.
- **`retention_days`**: Database retention limit in days (`0` for unlimited). / Ημέρες διατήρησης στη βάση.
- **`ingest_auth_token`**: Optional secret token for `/log2.asp`. / Μυστικό token ασφαλείας.
- **`allowed_device_ips`**: Allowed IP/CIDR list for LAN access. / Επιτρεπόμενες IP/υποδίκτυα.
- **`max_upload_retries`**: Upload retry attempts on connection error. / Επαναπροσπάθειες αποστολής.
- **`upload_retry_delay_seconds`**: Delay between upload retries. / Χρόνος αναμονής επανάληψης.

### 2. `gmcmap.json` (GMCMap.com)
- **`enabled`**: `true` or `false`
- **`user_account_id`**: Your User Account ID from GMCMap.com
- **`geiger_counter_id`**: Your Geiger Counter ID from GMCMap.com

### 3. `radmon.json` (Radmon.org)
- **`enabled`**: `true` or `false`
- **`username`**: Your Radmon.org username
- **`password`**: Your Radmon.org data submission password

### 4. `safecast.json` (Safecast.org)
- **`enabled`**: `true` or `false`
- **`api_key`**: Your Safecast API key
- **`device_id`**: Safecast device ID
- **`latitude`** & **`longitude`**: Sensor coordinates (e.g. `37.9838`, `23.7275`)

### 5. `opensensemap.json` (OpenSenseMap.org)
- **`enabled`**: `true` or `false`
- **`sensebox_id`**: Your senseBox ID
- **`sensor_id`**: Radiation sensor ID on OpenSenseMap

### 6. Local Storage & Logs / Τοπική Βάση & Αρχεία Καταγραφής
- **`radiation_data.db`**: SQLite database storing telemetry history. / Βάση δεδομένων ιστορικού.
- **`radiation_log.csv`**: Text log in CSV format. / Αρχείο συνεχούς καταγραφής CSV.

---
*Note: Any platform setting left empty or disabled (`enabled: false`) is safely ignored. Everything inside `config/` is strictly preserved and NEVER overwritten during system updates.*  
*Σημείωση: Όλες οι ρυθμίσεις και τα δεδομένα στον φάκελο `config/` προστατεύονται και ΔΕΝ αντικαθίστανται ποτέ κατά τις ενημερώσεις συστήματος.*
