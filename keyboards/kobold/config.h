#pragma once


//#include "quantum.h"

/* USB Device descriptor parameter */
#define USE_SERIAL
#define MASTER_RIGHT

#define UNICODE_KEY_MAC KC_LEFT_ALT
#define UNICODE_KEY_WINC KC_RIGHT_ALT
#define UNICODE_SELECTED_MODES UNICODE_MODE_MACOS, UNICODE_MODE_WINCOMPOSE
#define UNICODE_CYCLE_PERSIST true
#define UNICODE_TYPE_DELAY 10


//#define SPLIT_TRANSPORT_MIRROR
//#define ENABLE_RGB_MATRIX_SOLID_REACTIVE

/* key matrix size              -> done in .json */
// Rows are doubled-up
//#define MATRIX_ROWS 10
//#define MATRIX_COLS 6. 

//enable LEDs.                  //done in .json
//#define RGBLIGHT_LED_COUNT 74
//#define RGBLIGHT_SPLIT
//#define WS2812_DI_PIN D3  
//#define RGBLED_SPLIT {37,37}

//OLED support
#define OLED_DRIVER_ENABLE
#define OLED_DISPLAY_128X32
//#define SPLIT_OLED_ENABLE.    kukn//done in .json

// wiring of each half
//#define MATRIX_ROW_PINS { C6, D7, E6, B4, B5 }
//#define MATRIX_COL_PINS_RIGHT { B6, B2, B3, B1, F7, F6 }
//#define MATRIX_ROW_PINS_RIGHT { C6, D7, E6, B4, B5 }
//#define MATRIX_COL_PINS { F6, F7, B1, B3, B2, B6 }

/* encoder support 
#define ENCODER_A_PINS { F5 }
#define ENCODER_B_PINS { F4 }
#define ENCODER_A_PINS_RIGHT { F4 }
#define ENCODER_B_PINS_RIGHT { F5 }
#define ENCODER_RESOLUTION 2 */

