#pragma once

/* USB Device descriptor parameter */
#define MASTER_RIGHT

/* key matrix size */
// Rows are doubled-up
#define MATRIX_ROWS 10
#define MATRIX_COLS 6

// wiring of each half
#define MATRIX_ROW_PINS { C6, D7, E6, B4, B5 }
#define MATRIX_COL_PINS { B6, B2, B3, B1, F7, F6 }
#define MATRIX_ROW_PINS_RIGHT { C6, D7, E6, B4, B5 }
#define MATRIX_COL_PINS_RIGHT { F6, F7, B1, B3, B2, B6 }


/* encoder support */
#define ENCODER_A_PINS { F5 }
#define ENCODER_B_PINS { F4 }
#define EENCODER_A_PINS_RIGHT { F4 }
#define ENCODERS_PAD_B_RIGHT { F5 }
#define ENCODER_RESOLUTION 2


/* communication between sides */

//#define NO_ACTION_MACRO
//#define NO_ACTION_FUNCTION

