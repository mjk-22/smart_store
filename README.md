# **Smart Store

## **Overview**

The Smart Store IoT System is a Raspberry Pi–based application that combines real-time fridge monitoring, fan automation, product and inventory management, customer accounts, self-checkout, and reporting tools. The system uses ESP32 microcontrollers, MQTT communication, and a Django web application to provide a complete smart store prototype.

This README explains how to install, configure, and run the full system.

---

# **1. Requirements**

## **Hardware**

* Raspberry Pi 400 (or any Raspberry Pi running Raspberry Pi OS)
* Two ESP32 microcontrollers
* Two DHT11 sensors
* L293D motor driver
* 5V cooling fans
* Blue LED, red LED, and a buzzer
* Breadboard, jumper wires
* 2.4 GHz Wi-Fi network

## **Software**

* Python 3.11+
* Django 5.2.6
* Mosquitto MQTT broker
* Arduino IDE
* Python libraries: `paho-mqtt`, `RPi.GPIO`, `imaplib`, `smtplib`, `email`

---

# **2. Installation Instructions**

## **2.1 Setup Raspberry Pi Environment**

### **Step 1 - Update system**

```bash
sudo apt update && sudo apt upgrade -y
```

### **Step 2 - Install Python tools**

```bash
sudo apt install python3-pip python3-venv -y
```

### **Step 3 - Create virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

### **Step 4 - Install Django and required libraries**

```bash
pip install "Django==5.2.7"
pip install paho-mqtt
pip install RPi.GPIO
```

---

## **2.2 Install and Configure Mosquitto MQTT Broker**

```bash
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl enable mosquitto
```

Test the broker:

```bash
mosquitto_sub -t test &
mosquitto_pub -t test -m "hello"
```

---

## **2.3 Clone the Smart Store Project**

```bash
git clone <your repository URL>
cd smart_store
```

---

# **3. Django Setup**

### **Step 1 - Apply migrations**

```bash
python manage.py migrate
```

### **Step 2 - Create admin user**

```bash
python manage.py createsuperuser
```

### **Step 3 - Run Django server**

```bash
python manage.py runserver 0.0.0.0:8000
```

The site will be available at:

```
http://<raspberry_pi_ip>:8000
```

---

# **4. ESP32 Installation and Setup**

### **Step 1 - Install Arduino IDE**

### **Step 2 - Install ESP32 board support**

* Open Arduino IDE
* Go to **Tools -> Board -> Boards Manager**
* Search **ESP32**, install package

### **Step 3 - Install required Arduino libraries**

* DHT sensor library
* PubSubClient
* ArduinoJson

### **Step 4 - Flash ESP32 code**

Update these variables in your `.ino` file:

```cpp
const char* ssid = "YourNetwork";
const char* password = "YourPassword";
const char* mqtt_server = "RaspberryPi_IP";
```

Upload to each ESP32:

* One using topic `"frig1"`
* One using topic `"frig2"`

---

# **5. Background Services (Run on Raspberry Pi)**

Open a terminal and activate virtual environment:

```bash
cd smart_store
source venv/bin/activate
```

### **5.1 MQTT → Database Listener**

```bash
python mqtt_to_db.py
```

### **5.2 Fan Control Service**

```bash
python fan_control.py
```

### **5.3 Email Alert Sender**

(This script is called automatically by `mqtt_to_db.py` when temperature goes above threshold.)

### **5.4 Email Reply Watcher**

```bash
python email_reply_watcher.py
```

### **5.5 Fan Status Sync**

```bash
python fan_status_to_db.py
```

---

# **6. Wiring Summary**

### **ESP32 + DHT11**

* VCC → 3.3V
* GND → GND
* Signal → GPIO 4

### **Raspberry Pi + L293D + Fan**

* GPIO 18 -> L293D IN1 (Fridge 1 fan)
* GPIO 23 -> L293D IN2 (Fridge 2 fan)
* Fan power -> L293D OUT
* External 5V -> L293D motor VCC
* GND shared with Raspberry Pi

### **LED + Buzzer**

* Blue LED → GPIO 17
* Red LED → GPIO 27
* Buzzer → GPIO 22

---

# **7. Usage Instructions**

## **7.1 Access the Dashboard**

Open:

```
http://<raspberry_pi_ip>:8000/dashboard
```

View:

* Live gauges
* Temperature & humidity
* Last update time
* Fan status
* Threshold update form

## **7.2 Update Thresholds**

* Enter new temperature/humidity values
* Submit the form

## **7.3 Email Alerts**

* System sends alert when temperature exceeds threshold
* User replies “YES FID:<id>” to turn fan ON

## **7.4 Product & Inventory Management**

* Access Django admin or custom pages
* Add products, edit prices, manage stock

## **7.5 Self Checkout**

* Scan UPC/EPC codes
* Items appear in cart
* Checkout generates a receipt
* Email receipt is sent automatically

## **7.6 Reports**

* View sales report
* View inventory levels
* View customer activity

---

# **8. Troubleshooting**

### **ESP32 not connecting**

* Make sure Wi-Fi is **2.4 GHz** (ESP32 does NOT support 5 GHz if using hotspot).
* Check the Raspberry Pi IP address:

  ```bash
  hostname -I
  ```

### **MQTT messages not showing**

* Use:

  ```bash
  mosquitto_sub -t frig1
  ```

### **Fan not spinning**

* Check L293D wiring
* Confirm GPIO pin numbers in `fan_pins.json`
* Make sure `fan_control.py` is running

### **Scripts failing**

* Ensure the virtual environment is active:

  ```bash
  source venv/bin/activate
  ```

---

