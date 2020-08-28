/* Copyright 2020 Duckle
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
#include QMK_KEYBOARD_H
#include "analog.h"
#include "qmk_midi.h"

uint8_t midi2vol = 0x3E;

// Defines names for use in layer keycodes and the keymap

#define _MEDIA 0
#define _LIGHTS 1
#define _VOLUME 2
#define _DISCORD 3
#define _EDIT 4
#define _NAV 5
#define _RESET 6
#define _TOOGLE 7
/*
enum layer_names {
    
    _MEDIA,
    _LIGHTS,
    _VOLUME,
    _DISCORD,
    _EDIT,
    _NAV,
    _RESET,
    _TOOGLE
};
*/

// Defines the keycodes used by our macros in process_record_user
enum custom_keycodes {
    DEFAULT = SAFE_RANGE,
    SPOTIFY,DISCORD,CHROME 
};


const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    /* Base */
    [_MEDIA] = LAYOUT(
        MO(_TOOGLE),
        KC_MPLY, KC_MNXT,  KC_COPY,
        KC_MUTE,  KC_MPRV, KC_PASTE, KC_ENTER
    ),
    [_LIGHTS] = LAYOUT(
        MO(_TOOGLE),
        RGB_TOG, RGB_MOD, RGB_VAI,
        BL_TOGG, BL_STEP, BL_BRTG, KC_LSFT
    )
    ,
    [_VOLUME] = LAYOUT(
        MO(_TOOGLE),
        SPOTIFY, DISCORD, CHROME,
        KC_NO, KC_NO, KC_NO, DEFAULT
    )
    ,
    [_DISCORD] = LAYOUT(
        MO(_TOOGLE),
        KC_VOLD, KC_VOLU, KC_F24,
        KC_MRWD, KC_MFFD, KC_F23, KC_MPLY
    )
    ,
    [_EDIT] = LAYOUT(
        MO(_TOOGLE),
        KC_MENU, KC_CUT, KC_COPY,
        KC_FIND, KC_UNDO, KC_PASTE, KC_MPLY
    )
    ,
    [_NAV] = LAYOUT(
        MO(_TOOGLE),
        KC_SPC, KC_UP, KC_BSPACE,
        KC_RIGHT, KC_DOWN, KC_LEFT, KC_ENTER      
    )
    ,
    [_RESET] = LAYOUT(
        MO(_TOOGLE),
        KC_NO, KC_NO, KC_NO,
        KC_NO, KC_NO, KC_NO, RESET 
    ),
    [_TOOGLE] = LAYOUT(
        MO(_TOOGLE),
        TO(_MEDIA),    TO(_LIGHTS),    TO(_VOLUME),
        TO(_DISCORD),    TO(_EDIT),    TO(_NAV),    TO(_RESET)
    )
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    switch (keycode) {
        case DEFAULT:
            if (record->event.pressed) {
                // when keycode QMKBEST is pressed
                midi2vol= 0x3E;
            } else {
                // when keycode QMKBEST is released
            }
            break;
        case SPOTIFY:
            if (record->event.pressed) {
                // when keycode SPOTIFY is pressed
                midi2vol= 0x3F;
            } else {
                
                // when keycode SPOTIFY is released
            }
            break;
        case DISCORD:
            if (record->event.pressed) {
                // when keycode SPOTIFY is pressed
                midi2vol= 0x40;
            } else {
                
                // when keycode SPOTIFY is released
            }
            break;
        case CHROME:
            if (record->event.pressed) {
                // when keycode SPOTIFY is pressed
                midi2vol= 0x41;
            } else {
                
                // when keycode SPOTIFY is released
            }
            break;
    }
    return true;
}

uint8_t divisor = 0;


void slider(void) {
    if (divisor++) { // only run the slider function 1/256 times it's called
        return;
    }

    midi_send_cc(&midi_device, 2, midi2vol, 0x7F - (analogReadPin(SLIDER_PIN) >> 3));
}

void matrix_scan_user(void) {
    slider();
}
