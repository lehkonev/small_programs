#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

;! AutoHotkey_L


; All the keys:

;SC1::{Esc}
;SC03B::{F1}
;SC03C::{F2}
;SC03D::{F3}
;SC03E::{F4}
;SC03F::{F5}
;SC40::{F6}
;SC41::{F7}
;SC42::{F8}
;SC43::{F9}
;SC44::{F10}
;SC57::{F11}
;SC58::{F12}
;SC137::
;SC152::{Ins}
;SC153::{Del}
SC29::!
SC2::1
SC3::2
SC4::3
SC5::4
SC6::5
SC7::6
SC8::7
SC9::8
SC00A::9
SC00B::0
SC00C::+
SC00D::!
SC07D::!
;SC00E::{BS}
;SC00F::{Tab}
SC10::q
SC11::w
SC12::e
SC13::r
SC14::t
SC15::y
SC16::u
SC17::i
SC18::o
SC19::p
SC01A::å
SC01B::!
;SC01C::{Enter}
;SC03A::{CapsLock}
SC01E::a
SC01F::s
SC20::d
SC21::f
SC22::g
SC23::h
SC24::j
SC25::k
SC26::l
SC27::ö
SC28::ä
SC02B::’
;SC02A::{LShift}
SC02C::z
SC02D::x
SC02E::c
SC02F::v
SC30::b
SC31::n
SC32::m
SC33::,
SC34::.
SC35::-
SC73::!
;SC136::{RShift}
;SC01D::{LControl}
;SC15B::{LWIN}
;SC38::{Lalt}
SC07B::!
SC39::space
SC79::!
;SC11D::{rcontrol}
;SC14B::{Left}
;SC148::{Up}
;SC150::{Down}
;SC14D::{Right}


;deadkeys := {a: "½", b: "¾", c: "¿"} ; ... etc
;>!-::
; Input, key, L1, {delete}{esc}{home}{end} ; ... etc
; Send % deadkeys[key]
;return

; katakana/hiragana
SC70::!