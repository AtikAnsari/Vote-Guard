/**
 * =============================================================================
 * VOTE-GUARD — ESP32 Wireless Configuration Template
 * =============================================================================
 * Copy this file to 'config.h' and fill in your actual local Wi-Fi credentials
 * and laptop LAN IP address.
 * 
 * NOTE: 'config.h' is ignored by Git to protect your local credentials.
 */

#ifndef VOTE_GUARD_CONFIG_H
#define VOTE_GUARD_CONFIG_H

// =============================================================================
// 1. LOCAL WI-FI NETWORK CONFIGURATION
// =============================================================================
// Connect both your laptop and the ESP32 to the SAME Wi-Fi network or Mobile Hotspot.
#define WIFI_SSID       "YOUR_WIFI_SSID_HERE"
#define WIFI_PASSWORD   "YOUR_WIFI_PASSWORD_HERE"

// =============================================================================
// 2. FASTAPI BACKEND LAN IPv4 ADDRESS
// =============================================================================
// Replace with your laptop's actual LAN IPv4 address discovered via 'ipconfig'
// IMPORTANT: DO NOT use '127.0.0.1' or 'localhost' (those refer to the ESP32 itself!).
//
// Format: "http://<LAPTOP_LAN_IP>:8000"
// Example: "http://192.168.1.100:8000"
#define BACKEND_BASE_URL "http://192.168.1.100:8000"

// Network connection timeout in milliseconds
#define HTTP_TIMEOUT_MS  5000

#endif // VOTE_GUARD_CONFIG_H
