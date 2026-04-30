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

  // Kobold Samurai!

#include QMK_KEYBOARD_H
#include "oled.c"
//#include "encoder.c"

/* simple combo mechanism
const uint16_t PROGMEM combo_ae[] = {KC_A, KC_E, COMBO_END};
const uint16_t PROGMEM combo_ue[] = {KC_U, KC_E, COMBO_END};
const uint16_t PROGMEM combo_oe[] = {KC_O, KC_E, COMBO_END};
combo_t key_combos[] = {
    COMBO(combo_ae, RALT(KC_Q)),  // for ä
    COMBO(combo_ue, RALT(KC_Y)), // for ü
    COMBO(combo_oe, RALT(KC_P)), // for ü
};
*/

//advanced combo mechanism
enum combo_events {
  UML_AE,
  UML_UE,
  UML_OE,
};

const uint16_t PROGMEM combo_ae[] = {KC_A, KC_E, COMBO_END};
const uint16_t PROGMEM combo_ue[] = {KC_U, KC_E, COMBO_END};
const uint16_t PROGMEM combo_oe[] = {KC_O, KC_E, COMBO_END};

combo_t key_combos[] = {
  [UML_AE] = COMBO_ACTION(combo_ae),
  [UML_UE] = COMBO_ACTION(combo_ue),
  [UML_OE] = COMBO_ACTION(combo_oe),
};
/* COMBO_ACTION(x) is same as COMBO(x, KC_NO) */

void process_combo_event(uint16_t combo_index, bool pressed) {
  switch(combo_index) {
    case UML_AE:
      if (pressed) {
        if (unicode_config.input_mode == UNICODE_MODE_MACOS) {
          tap_code16(UC(0x00FC));
        }
        else {
          tap_code16(RALT(KC_Q));
        }
      }
      break;
    case UML_UE:
      if (pressed) {
        tap_code16(RALT(KC_Y));
      }
      break;
    case UML_OE:
      if (pressed) {
        tap_code16(RALT(KC_P));
      }
      break;
  }
}
//Default keymap. This can be changed in Via. Use oled.c and encoder.c to change beavior that Via cannot change.

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
/*
 * QWERTY
 * ,-----------------------------------------.                    ,-----------------------------------------.
 * | ESC  |   1  |   2  |   3  |   4  |   5  |                    |   6  |   7  |   8  |   9  |   0  |  -   |
 * |------+------+------+------+------+------|                    |------+------+------+------+------+------|
 * | Tab  |   Q  |   W  |   E  |   R  |   T  |                    |   Y  |   U  |   I  |   O  |   P  | Bspc |
 * |------+------+------+------+------+------|                    |------+------+------+------+------+------|
 * |   \  |   A  |   S  |   D  |   F  |   G  |-------.    ,-------|   H  |   J  |   K  |   L  |   ;  |  '   |
 * |------+------+------+------+------+------|       |    |       |------+------+------+------+------+------|
 * |LShift|   Z  |   X  |   C  |   V  |   B  |-------|    |-------|   N  |   M  |   ,  |   .  |   /  |  =   |
 * `-----------------------------------------/       /     \      \-----------------------------------------'
 *            | LCTR | LAlt | LGUI |LOWER | /Enter  /       \Space \  |RAISE | RGUI | RAlt | RCTR |
 *            |      |      |      |      |/       /         \      \ |      |      |      |      |
 *            `----------------------------------'           '------''---------------------------'
 */

[0] = LAYOUT(
  KC_ESC,   KC_1,   KC_2,    KC_3,    KC_4,    KC_5,                     KC_6,    KC_7,    KC_8,    KC_9,    KC_0,  KC_MINUS,
  KC_TAB,   KC_Q,   KC_W,    KC_E,    KC_R,    KC_T,                     KC_Y,    KC_U,    KC_I,    KC_O,    KC_P,  KC_BSPC,
  KC_BSLS,  KC_A,   KC_S,    KC_D,    KC_F,    KC_G,                     KC_H,    KC_J,    KC_K,    KC_L, KC_SCLN,  KC_QUOT,
  KC_LSFT,  KC_Z,   KC_X,    KC_C,    KC_V,    KC_B, _______,     _______,KC_N,    KC_M, KC_COMM,  KC_DOT, KC_SLSH,  KC_EQL,
                 KC_LCTL,KC_LALT,KC_LGUI, MO(1), KC_ENT,            KC_SPC,  MO(2), KC_RGUI, KC_RALT, KC_RCTL
),

/* LOWER
 * ,-----------------------------------------.                    ,-----------------------------------------.
 * |      |  F1  |  F2  |  F3  |  F4  |  F5  |                    |  F6  |  F7  |  F8  |  F9  | F10  | F11  |
 * |------+------+------+------+------+------|                    |------+------+------+------+------+------|
 * |  `\~ | nxt  |      |      |      |      |                    |   \  |  UE  |      |  OE  |     |  F12  |
 * |------+------+------+------+------+------|                    |------+------+------+------+------+------|
 * |      |  AE  |   @  |   #  |   $  |   %  |-------.    ,-------|   ~  |   &  |   (  |   )  |   *  |   |  |
 * |------+------+------+------+------+------|       |    |       |------+------+------+------+------+------|
 * |      |  =   |  -   |  +   |   {  |   }  |-------|    |-------|      | `\~  |   [  |   ]  |   ~  |   \  |
 * `-----------------------------------------/       /     \      \-----------------------------------------'
 *            | LCTR | LAlt | LGUI |LOWER | /Enter  /       \Space \  |RAISE | LGUI | RAlt | RCTR |
 *            |      |      |      |      |/       /         \      \ |      |      |      |      |
 *            `----------------------------------'           '------''---------------------------'
 */
[1] = LAYOUT(
  UC_NEXT, KC_F1,      KC_F2,   KC_F3,   KC_F4,   KC_F5,                          KC_F6,    KC_F7,      KC_F8,   KC_F9,      KC_F10,  KC_F11,
  KC_GRV,  UC_NEXT,    _______, _______, _______, _______,                        KC_BSLS,  UC(0x00FC), _______, UC(0x00F6), _______, KC_F12,
  _______, UC(0x00E4), KC_AT,   KC_HASH, KC_DLR,  KC_PERC,                        KC_TILD,  KC_AMPR,    KC_LPRN, KC_RPRN,    KC_ASTR, KC_PIPE,
  _______, KC_EQL,     KC_MINS, KC_PLUS, KC_LCBR, KC_RCBR, _______,      _______, _______,  KC_GRV,     KC_LBRC, KC_RBRC,    KC_TILD, KC_BSLS,
                       _______, _______, _______, _______, _______,      _______, _______, _______,     _______, _______
),
/* RAISE
 * ,----------------------------------------.                    ,-----------------------------------------.
 * |      |      |      |      |      |      |                    | ValU |ModPre|ModNxt|      | SpdU | OnOff|
 * |------+------+------+------+------+------|                    |------+------+------+------+------+------|
 * |      | Ins  | Pscr | Menu |      |      |                    | ValD | PagD |  Up  | PagU | SpdD | Del  |
 * |------+------+------+------+------+------|                    |------+------+------+------+------+------|
 * |      |      |      |      |      | Caps |-------.    ,-------| SatU | Left | Down | Right| HueU | Bspc |
 * |------+------+------+------+------+------|       |    |       |------+------+------+------+------+------|
 * |      | Undo |  Cut | Copy | Paste|      |-------|    |-------| SatD |      |      |      | HueD |RShift|
 * `-----------------------------------------/       /     \      \-----------------------------------------'
 *            | LCTR | LAlt | LGUI |LOWER | /Enter  /       \Space \  |RAISE | RGUI | RAlt | RCTR |
 *            |      |      |      |      |/       /         \      \ |      |      |      |      |
 *            `----------------------------------'           '------''---------------------------'
 */
[2] = LAYOUT(
  _______, _______, _______, _______, _______, _______,                          RM_VALU, RM_PREV, RM_NEXT, _______,  RM_SPDU, RM_TOGG,
  _______, KC_INS,  KC_PSCR, KC_APP,  _______, _______,                          RM_VALD, KC_PGDN, KC_UP,   KC_PGUP,  RM_SPDD, KC_DEL,
  _______, _______, _______, _______, _______, KC_CAPS,                          RM_SATU, KC_LEFT, KC_DOWN, KC_RGHT,  RM_HUEU, KC_BSPC,
  _______, KC_UNDO, KC_CUT, KC_COPY, KC_PASTE, _______,  _______,       _______, RM_SATD, _______, _______, _______,  RM_HUED, KC_RSFT,
                     _______, _______, _______, _______, _______,       _______, _______, _______, _______, _______
)
};
