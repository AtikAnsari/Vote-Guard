/*
  =============================================================================
  VOTE-GUARD — ESP32 Wireless Standalone Firmware (Wi-Fi + RC522 + Actuators)
  =============================================================================

  HARDWARE PIN MAPPING (ESP32 DevKit V1 30-Pin):
  -----------------------------------------------------------------------------
  
  
  RC522 RFID MODULE (SPI):
    - 3.3V -> ESP32 3V3 (STRICTLY 3.3V! Never connect to 5V/VIN)
    - GND  -> ESP32 Common GND
    - RST  -> GPIO 4
    - MISO -> GPIO 19
    - MOSI -> GPIO 23
    - SCK  -> GPIO 18
    - SDA (SS) -> GPIO 5

  OPERATIONAL INDICATORS & ACTUATORS (Active HIGH):
    - GREEN LED  -> GPIO 25 (Anode [+] -> 220Ω resistor -> GPIO 25 | Cathode [-] -> GND)
    - YELLOW LED -> GPIO 26 (Anode [+] -> 220Ω resistor -> GPIO 26 | Cathode [-] -> GND)
    - RED LED    -> GPIO 27 (Anode [+] -> 220Ω resistor -> GPIO 27 | Cathode [-] -> GND)
    - BUZZER     -> GPIO 32 (Signal/Positive [+] -> GPIO 32 | Negative [-] -> GND)

  COMMUNICATION MODES:
    1. Primary Wireless Mode : Wi-Fi HTTP POST direct to FastAPI backend LAN IPv4.
    2. Diagnostic Serial Mode: USB Serial console (115200 baud) for live diagnostics.
  =============================================================================
*/

#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
// =============================================================================
// WI-FI & BACKEND CONFIGURATION
// =============================================================================
// If config.h exists in the sketch folder, it will be loaded.
// Otherwise, the embedded fallback settings below are used directly.
#if __has_include("config.h")
  #include "config.h"
#else
  // Wi-Fi Access Point Credentials (Connect laptop and ESP32 to the same network)
  #define WIFI_SSID         "YOUR_WIFI_SSID"
  #define WIFI_PASSWORD     "YOUR_WIFI_PASSWORD"

  // Laptop LAN IPv4 Address (Discovered via 'ipconfig' - DO NOT use 127.0.0.1!)
  #define BACKEND_BASE_URL  "http://192.168.1.100:8000"

  // HTTP connection timeout in milliseconds
  #define HTTP_TIMEOUT_MS   5000
#endif

// PIN DEFINITIONS (Exact Hardware Wiring Confirmed)
#define PIN_RC522_SS      5     // SDA / Chip Select
#define PIN_RC522_RST     4     // RC522 Reset
#define PIN_RC522_SCK     18    // SPI Clock
#define PIN_RC522_MISO    19    // SPI MISO
#define PIN_RC522_MOSI    23    // SPI MOSI

#define PIN_LED_GREEN     25    // Green Status LED  -> GPIO 25
#define PIN_LED_YELLOW    26    // Yellow Status LED -> GPIO 26
#define PIN_LED_RED       27    // Red Status LED    -> GPIO 27
#define PIN_BUZZER        32    // Active Buzzer     -> GPIO 32

// Reader Instance
MFRC522 rfid(PIN_RC522_SS, PIN_RC522_RST);

// Scan Debounce Tracker: Prevents re-scanning while holding tag on reader (4 seconds)
unsigned long lastScanTime = 0;
String lastScannedUID = "";
const unsigned long SCAN_DEBOUNCE_MS = 4000;


// =============================================================================
// ACTUATOR & FEEDBACK ROUTINES
// =============================================================================

void beep(int durationMs) {
  digitalWrite(PIN_BUZZER, HIGH);
  delay(durationMs);
  digitalWrite(PIN_BUZZER, LOW);
}

void clearIndicators() {
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_YELLOW, LOW);
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_BUZZER, LOW);
}

// 1. Success: Green LED visible blink pattern + confirmation tone
void handleVoteAccepted() {
  clearIndicators();
  Serial.println("[ACTUATOR] >>> ACTION: GREEN LED BLINK (Vote Accepted)");

  // 3 distinct, visible green blinks with confirmation tone
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED_GREEN, HIGH);
    if (i == 0) beep(150);
    delay(220);
    digitalWrite(PIN_LED_GREEN, LOW);
    delay(120);
  }
  clearIndicators();
}

// 2. Warning: Yellow LED visible blink pattern + 3 alert chirps
void handleUnregistered() {
  clearIndicators();
  Serial.println("[ACTUATOR] >>> ACTION: YELLOW LED BLINK (Unregistered Card)");

  // 3 distinct yellow blinks with alert chirps
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED_YELLOW, HIGH);
    beep(80);
    delay(140);
    digitalWrite(PIN_LED_YELLOW, LOW);
    delay(100);
  }
  clearIndicators();
}

// 3. Duplicate Rejection: Red LED rapid strobe + 3 prominent alarm buzzes
void handleDuplicate() {
  clearIndicators();
  Serial.println("[ACTUATOR] >>> ACTION: RED LED STROBE (Duplicate Vote Blocked)");

  // 3 alarm buzzes with red strobe
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED_RED, HIGH);
    digitalWrite(PIN_BUZZER, HIGH);
    delay(160);
    digitalWrite(PIN_LED_RED, LOW);
    digitalWrite(PIN_BUZZER, LOW);
    delay(90);
  }
  // Extra visible red strobe flashes
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED_RED, HIGH);
    delay(100);
    digitalWrite(PIN_LED_RED, LOW);
    delay(80);
  }
  clearIndicators();
}

// 4. Network or Server Error: Red + Yellow warning, NEVER Green!
void handleNetworkOrServerError(const String &reason) {
  clearIndicators();
  Serial.print("[ACTUATOR] >>> ACTION: ERROR INDICATION (");
  Serial.print(reason);
  Serial.println(") - NEVER GREEN");

  // Alternating Red & Yellow flashes with warning buzzes
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_LED_RED, HIGH);
    digitalWrite(PIN_LED_YELLOW, HIGH);
    beep(100);
    delay(150);
    digitalWrite(PIN_LED_RED, LOW);
    digitalWrite(PIN_LED_YELLOW, LOW);
    delay(100);
  }
  clearIndicators();
}

// Hardware Boot Self-Test
void hardwareSelfTest() {
  Serial.println("\n[SELF-TEST] Testing Hardware Actuators...");
  clearIndicators();

  Serial.println("  [1/4] Green LED (GPIO 25)");
  digitalWrite(PIN_LED_GREEN, HIGH);
  delay(350);
  digitalWrite(PIN_LED_GREEN, LOW);
  delay(150);

  Serial.println("  [2/4] Yellow LED (GPIO 26)");
  digitalWrite(PIN_LED_YELLOW, HIGH);
  delay(350);
  digitalWrite(PIN_LED_YELLOW, LOW);
  delay(150);

  Serial.println("  [3/4] Red LED (GPIO 27)");
  digitalWrite(PIN_LED_RED, HIGH);
  delay(350);
  digitalWrite(PIN_LED_RED, LOW);
  delay(150);

  Serial.println("  [4/4] Active Buzzer (GPIO 32)");
  beep(80);

  clearIndicators();
  Serial.println("[SELF-TEST] Peripheral verification complete.\n");
}


// =============================================================================
// WI-FI CONNECTION MANAGEMENT
// =============================================================================

void connectToWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.println("=================================================");
  Serial.print("[WIFI] Connecting to SSID: '");
  Serial.print(WIFI_SSID);
  Serial.println("'");

  // Reset Wi-Fi state cleanly
  WiFi.disconnect(true);
  delay(200);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  unsigned long startAttemptTime = millis();
  // Wait up to 15 seconds for connection on primary SSID
  while (WiFi.status() != WL_CONNECTED && millis() - startAttemptTime < 15000) {
    delay(400);
    Serial.print(".");
  }
  Serial.println();

  // If not connected, automatically try with/without a trailing space
  if (WiFi.status() != WL_CONNECTED) {
    String altSSID = String(WIFI_SSID);
    if (!altSSID.endsWith(" ")) {
      altSSID += " ";
    } else {
      altSSID.trim();
    }
    Serial.print("[WIFI] Primary timed out. Trying matching SSID: '");
    Serial.print(altSSID);
    Serial.println("'");

    WiFi.disconnect(true);
    delay(200);
    WiFi.begin(altSSID.c_str(), WIFI_PASSWORD);
    unsigned long altAttempt = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - altAttempt < 15000) {
      delay(400);
      Serial.print(".");
    }
    Serial.println();
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("[WIFI] Successfully Connected!");
    Serial.print("  - Assigned ESP32 IP : ");
    Serial.println(WiFi.localIP());
    Serial.print("  - Subnet Mask       : ");
    Serial.println(WiFi.subnetMask());
    Serial.print("  - Gateway IP        : ");
    Serial.println(WiFi.gatewayIP());
    Serial.print("  - Wi-Fi Signal RSSI : ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    Serial.print("  - Target Backend    : ");
    Serial.println(BACKEND_BASE_URL);
    Serial.println("=================================================");
  } else {
    Serial.print("[WIFI-WARNING] Connection failed. Status code: ");
    int st = WiFi.status();
    Serial.println(st);
    if (st == 1) { // WL_NO_SSID_AVAIL
      Serial.println("  -> Reason: SSID NOT FOUND! Check if your Wi-Fi name has a trailing space (e.g. 'Launchpad ')");
    } else if (st == 4) { // WL_CONNECT_FAILED
      Serial.println("  -> Reason: PASSWORD REJECTED! Check your Wi-Fi password.");
    } else if (st == 6) { // WL_DISCONNECTED
      Serial.println("  -> Reason: Handshake timeout. Ensure 2.4 GHz band is enabled.");
    }
    Serial.println("  ESP32 will retry connection automatically.");
    Serial.println("=================================================");
    handleNetworkOrServerError("Wi-Fi Not Connected");
  }
}


// =============================================================================
// WIRELESS VERIFICATION VIA FASTAPI BACKEND
// =============================================================================

// Lightweight helper to extract JSON string fields without heavy library dependencies
String extractJsonField(const String &json, const String &fieldName) {
  String searchKey = "\"" + fieldName + "\"";
  int keyIndex = json.indexOf(searchKey);
  if (keyIndex == -1) return "";

  int colonIndex = json.indexOf(":", keyIndex + searchKey.length());
  if (colonIndex == -1) return "";

  int valStart = json.indexOf("\"", colonIndex);
  if (valStart == -1) return "";

  int valEnd = json.indexOf("\"", valStart + 1);
  if (valEnd == -1) return "";

  return json.substring(valStart + 1, valEnd);
}

void verifyVoteOverWiFi(const String &rfidUID) {
  // 1. Verify Wi-Fi connectivity
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("[HTTP-ERROR] Wi-Fi offline. Reconnecting...");
    connectToWiFi();
    if (WiFi.status() != WL_CONNECTED) {
      handleNetworkOrServerError("Wi-Fi Offline");
      return;
    }
  }

  // 2. Prepare HTTP request
  HTTPClient http;
  String targetEndpoint = String(BACKEND_BASE_URL) + "/api/vote/verify-and-record";
  String payload = "{\"rfid_uid\":\"" + rfidUID + "\"}";

  Serial.println("-------------------------------------------------");
  Serial.print("[HTTP-TX] Target Endpoint : ");
  Serial.println(targetEndpoint);
  Serial.print("[HTTP-TX] Payload         : ");
  Serial.println(payload);

  http.begin(targetEndpoint);
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(HTTP_TIMEOUT_MS);

  // 3. Transmit POST
  unsigned long reqStartTime = millis();
  int httpResponseCode = http.POST(payload);
  unsigned long reqDuration = millis() - reqStartTime;

  Serial.print("[HTTP-RX] Status Code     : ");
  Serial.print(httpResponseCode);
  Serial.print(" (");
  Serial.print(reqDuration);
  Serial.println(" ms)");

  // 4. Handle Network / Server Failure
  if (httpResponseCode <= 0) {
    Serial.print("[HTTP-ERROR] Connection Failed: ");
    Serial.println(http.errorToString(httpResponseCode));
    http.end();
    handleNetworkOrServerError("HTTP Connection Failed");
    return;
  }

  String responseBody = http.getString();
  Serial.print("[HTTP-RX] Raw Response    : ");
  Serial.println(responseBody);
  http.end();

  // 5. Parse authoritative response fields
  String status = extractJsonField(responseBody, "status");
  String ledDirective = extractJsonField(responseBody, "hardware_led");
  String voterName = extractJsonField(responseBody, "voter_name");
  String message = extractJsonField(responseBody, "message");

  status.toUpperCase();
  ledDirective.toUpperCase();

  Serial.print("[PARSER] Parsed Status    : ");
  Serial.println(status);
  Serial.print("[PARSER] Hardware LED     : ");
  Serial.println(ledDirective);
  if (voterName.length() > 0) {
    Serial.print("[PARSER] Voter Name       : ");
    Serial.println(voterName);
  }

  // 6. Actuate Indicators based strictly on Authoritative Backend Result
  if (status == "ACCEPTED" || status == "VOTE_ACCEPTED" || ledDirective == "GREEN") {
    handleVoteAccepted();
  }
  else if (status == "ALREADY_VOTED" || status == "DUPLICATE" || ledDirective == "RED") {
    handleDuplicate();
  }
  else if (status == "UNREGISTERED" || ledDirective == "YELLOW") {
    handleUnregistered();
  }
  else {
    // Unknown status, INACTIVE, or malformed response: NEVER GREEN
    Serial.println("[PARSER-WARNING] Unrecognized status. Actuating safety rejection.");
    handleNetworkOrServerError("Unrecognized Backend Status");
  }

  Serial.println("-------------------------------------------------");
}


// =============================================================================
// SETUP
// =============================================================================

void setup() {
  Serial.begin(115200);
  delay(500);

  // 1. Initialize GPIO Pins
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  clearIndicators();

  // 2. Initialize SPI Bus and RC522 Reader
  SPI.begin();
  rfid.PCD_Init();
  delay(50);

  // 3. Startup Banner
  Serial.println("\n=================================================");
  Serial.println("       VOTE-GUARD ESP32 WIRELESS CONTROLLER      ");
  Serial.println("=================================================");
  Serial.println("Hardware Pin Assignments (CONFIRMED):");
  Serial.println("  - GREEN LED  : GPIO 25");
  Serial.println("  - YELLOW LED : GPIO 26");
  Serial.println("  - RED LED    : GPIO 27");
  Serial.println("  - BUZZER     : GPIO 32");
  Serial.println("  - RC522 SPI  : SS=5, RST=4, SCK=18, MISO=19, MOSI=23");
  Serial.println("=================================================");

  // 4. Hardware Self-Test (Green -> Yellow -> Red -> Beep)
  hardwareSelfTest();

  // 5. Connect to Wi-Fi Network
  connectToWiFi();

  Serial.println("[VOTE-GUARD] Online & Ready. Tap RFID Tag on Reader...\n");
}


// =============================================================================
// MAIN LOOP
// =============================================================================

void loop() {
  // 1. Process Optional USB Serial Directives (Backwards Compatibility & Debugging)
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    while (Serial.available() > 0 && (Serial.peek() == '\n' || Serial.peek() == '\r' || Serial.peek() == ' ')) {
      Serial.read();
    }
    if (cmd == 'V' || cmd == 'v' || cmd == 'G') {
      handleVoteAccepted();
    } else if (cmd == 'D' || cmd == 'd' || cmd == 'R') {
      handleDuplicate();
    } else if (cmd == 'U' || cmd == 'u' || cmd == 'Y') {
      handleUnregistered();
    } else if (cmd == 'T' || cmd == 't') {
      hardwareSelfTest();
    }
  }

  // 2. Detect RFID Card Presence
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  // 3. Read Card Serial Data
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  // 4. Format Hex UID String (e.g. "71411605")
  String uidString = "";
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      uidString += "0";
    }
    uidString += String(rfid.uid.uidByte[i], HEX);
  }
  uidString.toUpperCase();

  // 5. Debounce Check: Prevent instant repeated scans of the same held card
  unsigned long now = millis();
  if (uidString != lastScannedUID || (now - lastScanTime > SCAN_DEBOUNCE_MS)) {
    lastScannedUID = uidString;
    lastScanTime = now;

    // Instant physical contact acknowledgment chirp (20ms)
    beep(20);

    Serial.println("\n[RFID-SCAN] =====================================");
    Serial.print("[RFID-SCAN] Scanned Card UID: ");
    Serial.println(uidString);

    // 6. Send to Backend over Wi-Fi
    verifyVoteOverWiFi(uidString);
  }

  // 7. Halt Card and Release Crypto State
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
