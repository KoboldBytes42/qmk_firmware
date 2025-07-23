 /* Copyright 2020 Josef Adamcik
  * Modification for VIA support and RGB underglow by Jens Bonk-Wiltfang
  * 
  * This program is free software: you can redistribute it and/or modify 
  * it under the terms of the GNU General Public License as published by 
  * the Free Software Foundation, either version 2 of the License, or 
  * (at your option) any later version. 
  * 
  * This program is distributed in the hope that it will be useful, 
  * but WITHOUT ANY WARRANTY; without even the implied warranty of 
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
  * GNU General Public License for more details. 
  * 
  * You should have received a copy of the GNU General Public License 
  * along with this program.  If not, see <http://www.gnu.org/licenses/>. 
  */ 

//Sets up what the OLED screens display.

#include "oled_driver.h"

#ifdef OLED_DRIVER_ENABLE

static void render_logo(void) {
    static const char PROGMEM raw_logo[] = {
        0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,224,224,224,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,128,224,224,224,  0,  0,  0,  0,  0,  0,  0,224,224,224,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,192,224,240,248,240,240,248,248,240,224,128,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
        0,  0,  0,  0,192,192,199,199,199,199,199,199,199,199,199,255,255,255,199,199,199,199,199,199,199,199,199,199,192,128,  0,  0,  0,  0,  0,255,255,255,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 12, 28, 62,248,240,192,  0,  0,  0,  0,  0,  0,  0,192,224,240,252,255, 15,  3,192,199,199,199,199,199,199,199,255,255,255,199,199,199,199,199,199,192,192,  0,  0,  0,  0,  0,  0,  0,128,192,216,252,252,252,252,252,248,248,227,207,159, 63,127, 31,127, 63,159,231,241,248,252,252,252,252,252,252,216,128,  0,  0,  0, 
        0,  0,  0,  0,  1,129,225,249,125, 25,  1,129,249,255,127,  1,  1,  1,  1,255,255,  1,  1,  9, 61,253,241,193,  1,  1,  0,  0,  0,  0,  0, 15,255,255,224,  0,  0,  0,128,248,248,112,  0,  0,  0,  0,  0,  0,  0,  3, 31,255,252,224,  0,  0,  0,  7,  7,  3,245,255,255,  0,  0, 56, 56,184,248,184, 56, 56, 56, 56, 24, 56, 24,254,254,254, 56, 56, 56,  0,  0,  0,  0,  0,  0,  0,  0,  0,  3,  7, 15, 15,143,207,239,239,231,247,246,209,192,230, 15,230,192,241,246,247,231,239,239,207,143, 15,  7,  7,  3,  0,  0,  0, 
        0,  0,  0,  2,  7,  7,227,241,112,120, 62, 31, 15,  3,224,224,224,224,224,255,127,  0,  0,  0,  0,  0,  7, 15, 15,  4,  0,  0,  0,  0,  0,  0,  0,  3, 15, 15, 14, 14, 15,  7,  3,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  3,  1,  1,  0,  0,  0,  0,  0,  0,255,255,255,  0,  0,  0,  0,  0,  1,  3, 15,110,236,224,224,224,224,255,127, 63,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 14, 31, 15, 47,127,127,127,127, 63, 31, 15,  0, 31, 63,127,127,127,127,127, 31, 31, 31,  0,  0,  0,  0,  0,  0,  0,
    };
    oled_write_raw_P(raw_logo, sizeof(raw_logo));
}


static void print_status_narrow(void) {
    // Print current mode
    oled_write_P(PSTR("\n\n"), false);

    switch (get_highest_layer(layer_state)) {
        case 0:
            oled_write_ln_P(PSTR("Qwrt"), false);
            break;
        case 1:
            oled_write_ln_P(PSTR("Mod"), false);
            break;
        default:
            oled_write_P(PSTR("Mod\n"), false);
            break;
    }
    oled_write_P(PSTR("\n\n"), false);
    // Print current layer
    oled_write_ln_P(PSTR("LAYER"), false);
    switch (get_highest_layer(layer_state)) {
        case 0:
            oled_write_P(PSTR("Base\n"), false);
            break;       
        case 1:
            oled_write_P(PSTR("Lower"), false);
            break;
        case 2:
            oled_write_P(PSTR("Raise"), false);
            break;
        default:
            oled_write_ln_P(PSTR("Undef"), false);
    }
    oled_write_P(PSTR("\n\n"), false);
    led_t led_usb_state = host_keyboard_led_state();
    oled_write_ln_P(PSTR("CPSLK"), led_usb_state.caps_lock);

    oled_write_P(PSTR("\n"), false);
    switch(unicode_config.input_mode) {
        case UNICODE_MODE_MACOS:
            oled_write_ln_P(PSTR("MacOS"), false);
            break;
        case UNICODE_MODE_WINCOMPOSE:
            oled_write_ln_P(PSTR("WinC"), false);
            break;
        default:
            oled_write_ln_P(PSTR("Undef"), false);
    }

} 

oled_rotation_t oled_init_user(oled_rotation_t rotation) {
    if (is_keyboard_master()) {
        return OLED_ROTATION_270;
    }
    return rotation;
}

bool oled_task_user(void) {
    if (is_keyboard_master()) {
        print_status_narrow();
        //oled_write_ln(PSTR("OLED Active!"), false);
        return false;
    } else {
        render_logo();
        return false;
    }
}

#endif