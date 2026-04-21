#pragma once

// RP2040 Bootloader configuration

#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET // Activates the double-tap behavior
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 200U // Timeout window in ms in which the double tap can occur.
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_LED GP17 // Specify a optional status led by GPIO number which blinks when entering the bootloader


/* USB Device descriptor parameter */
#define USE_SERIAL
#define MASTER_RIGHT

#define UNICODE_KEY_MAC KC_LEFT_ALT
#define UNICODE_KEY_WINC KC_RIGHT_ALT
#define UNICODE_SELECTED_MODES UNICODE_MODE_MACOS, UNICODE_MODE_WINCOMPOSE
#define UNICODE_CYCLE_PERSIST true
#define UNICODE_TYPE_DELAY 10

//OLED support
#define OLED_DRIVER_ENABLE
#define OLED_DISPLAY_128X32
