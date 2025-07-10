#pragma once


//#include "quantum.h"

/* USB Device descriptor parameter */
#define USE_SERIAL
#define MASTER_RIGHT

/* key matrix size */
// Rows are doubled-up
//#define MATRIX_ROWS 10
//#define MATRIX_COLS 6

//enable LEDs
//#define RGBLIGHT_SPLIT
#define WS2812_DI_PIN D3  //done in .json
//#define RGBLIGHT_LED_COUNT 74
//#define RGBLED_SPLIT {37,37}

//OLED support
#define OLED_DRIVER_ENABLE
#define OLED_DISPLAY_128X32
//#define SPLIT_OLED_ENABLE. //done in .json

// wiring of each half
#define MATRIX_ROW_PINS { C6, D7, E6, B4, B5 }
#define MATRIX_COL_PINS_RIGHT { B6, B2, B3, B1, F7, F6 }
#define MATRIX_ROW_PINS_RIGHT { C6, D7, E6, B4, B5 }
#define MATRIX_COL_PINS { F6, F7, B1, B3, B2, B6 }


/* encoder support 
#define ENCODER_A_PINS { F5 }
#define ENCODER_B_PINS { F4 }
#define ENCODER_A_PINS_RIGHT { F4 }
#define ENCODER_B_PINS_RIGHT { F5 }
#define ENCODER_RESOLUTION 2 */

/*
#define LAYOUT(L00, L01, L02, L03, L04, L05,           R00, R01, R02, R03, R04, R05,  \
               L10, L11, L12, L13, L14, L15,           R10, R11, R12, R13, R14, R15,  \
               L20, L21, L22, L23, L24, L25,           R20, R21, R22, R23, R24, R25,  \
               L30, L31, L32, L33, L34, L35, L40, R40, R30, R31, R32, R33, R34, R35, \
               L41, L42, L43, L44, L45, R41, R42, R43, R44, R45  \
    ) \
    { \
        { L00, L01, L02, L03, L04, L05 }, \
        { L10, L11, L12, L13, L14, L15 }, \
        { L20, L21, L22, L23, L24, L25 }, \
        { L30, L31, L32, L33, L34, L35 }, \
        { L40, L41, L42, L43, L44, L45 }, \
        { R05, R04, R03, R02, R01, R00 }, \
        { R15, R14, R13, R12, R11, R10 }, \
        { R25, R24, R23, R22, R21, R20 }, \
        { R35, R34, R33, R32, R31, R30 }, \
        { R45, R44, R43, R42, R41, R40 } \
    }*/


    