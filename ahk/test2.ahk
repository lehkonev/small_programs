;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;2345678901234567890123456789012345678901234567890123456789012345678901234567890

#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

;! AutoHotkey_L

; fi:   67830795
; jp:   68224017
; enus: 67699721
; fi20: -255785973 (on olevinaan fi18)
; fi18: -254868469
; fi19: -254802933
; fi05: -255850487

; fi05: -255851509 (suomi)
; fi18: -254868469
; fi19: -254802933
; fi20: -255785973 (on olevinaan fi18)
; fi21: -255720437
; fi21: -255719415 (jos se on EN_gb-näppiksessä)

MsgBox Started test2!

a::
	en := DllCall("LoadKeyboardLayout", "Str", "00000409", "Int", 1)
	fi := DllCall("LoadKeyboardLayout", "Str", "0000040B", "Int", 1)
	fi18 := DllCall("LoadKeyboardLayout", "Str", "a001040b", "Int", 1)
	fi19 := DllCall("LoadKeyboardLayout", "Str", "abcdef01", "Int", 1)
	fi20 := DllCall("LoadKeyboardLayout", "Str", "00009998", "Int", 1)
	w := DllCall("GetForegroundWindow")
	pid := DllCall("GetWindowThreadProcessId", "UInt", w, "Ptr", 0)
	lang := DllCall("GetKeyboardLayout", "UInt", pid)
	test := "okokoko"
	testi := DllCall("CurrentInputMethodLanguageTag", "Str", test)
	testii := DllCall("GetKeyboardLayout")

	if (lang = en) {
		MsgBox Englantia (US) (%lang%). %testi% %testii%
	}
	else if (lang = 67830795) {
		MsgBox Suomea (%lang%). %testi% %testii%
	}
	else if (lang = -255720437) {
		MsgBox Suomea (%lang%) 21. %testi% %testii%
	}
	else {
		MsgBox Jotain muuta (%lang%). %testi% %testii%
	}

return

; Array test: nope.
;b::
;	 size := DllCall("GetKeyboardLayoutList", "Int", 0, "Ptr", 0)
;	 VarSetCapacity(myarray, 4*size)
;	 point := 0
;	 list := DllCall("GetKeyboardLayoutList", "Int", size, "Ptr", myarray)
;	 Msgbox koko ""%size%"" , osoitin ""%myarray%"" , lista ""%list%""
;return

is_right_keyboard() {
	MsgBox Is right keyboard?
	
	wanted := DllCall("LoadKeyboardLayout", "Str", "00000409", "Int", 1)
	w := DllCall("GetForegroundWindow")
	pid := DllCall("GetWindowThreadProcessId", "UInt", w, "Ptr", 0)
	lang := DllCall("GetKeyboardLayout", "UInt", pid)

	if (lang = wanted) {
		return 1
	}

	return 0
}

#If is_right_keyboard()
c::MsgBox Yes!

;wanted := DllCall("LoadKeyboardLayout", "Str", "abcdef01", "Int", 1)
#If

; $ prevents AHK from calling this infinitely.
;$d::
;	Sleep 2000
;	funct()
;	Send d
;return
;
;$>+Ctrl::
;	Send {RShift down}{Ctrl down}{RShift up}{Ctrl up}
;	Sleep 100
;	funct()
;return
;
;funct() {
;	MsgBox Hi!
;	return
;}

; You can make a hotkey that calls a function, like this:
;a::MyFunction()

; Send unicode:
;a::Send {U+03B1}
