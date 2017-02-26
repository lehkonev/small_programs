; AHK_startup
; Creator: Veini Lehkonen, lehkonev@gmail.com
; Version: 0.9
; Date: 2017-02-09
;-----------------------------------------------------------------------------
; Environment used to create and test:
; AutoHotkey v1.1.24.05
; Windows 10 Home 64-bit
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; This script is supposed to be run when the system starts, to allow making more use of my laptop’s keyboard. Essentially it adds functionality to five keys that do not do anything if the laptop’s input language is not Japanese (three conversion keys and two keys not found in other keyboards). This script also assumes a certain self-made keyboard layout. The keyboard layout does not function properly, which is why some dead keys are defined here as well.

#NoEnv
#KeyHistory 0
#EscapeChar `
SendMode Input
SetWorkingDir %A_ScriptDir%

;-----------------------------------------------------------------------------
; Constants

; Switch to turn the script on in all keyboards (1). This will mess up inputting Japanese, because the conversion keys will not work. Therefore the default is 0, which will enable the script only for the wanted_keyboard below. 
global always_on := 0

; The first two uppercase letters tell which language setting the keyboard can be found in. The letters after the underscore tell the name of the self-made keyboard.
; The numbers seem random. If it were a keyboard that came with the official language pack, it probably would have some connection to LOCALEID in the keyboard file.
global wanted_keyboards := {"FI_fi21": -255720437, "EN_fi21": -255719415, "EN_fi22": -255784951, "EN_fiD01": -255653879, "EN_fi23": -255391735, "EN_fiD02": -255457271}
global current_keyboard := -1

; Dead keys to enable some special characters. The other dead keys are implemented by the keyboard layout itself, but for some inexplicable reason, one of them does not work, so here they are.
; The underscore is needed because keys that have only digits are not recognised otherwise. It is added to the key in the calling function.
; For some inexplicable reason, letters a–z and A–Z seem to be treated the same (“ö” and “Ö” and “ä” and “Ä” are not treated the same). Therefore, accessing the list {"a_": "å", "d_": "ð", "A_": "Å", "D_": "Ð"} with either “A_” or “a_” returns the value for key “A_” (which is “Å”). If the uppercase letters were listed first, it would return a lowercase letter, so apparently the value that is closer to the end of the list is returned.
; Because the associative list does not seem to distinguish between uppercase and lowercase letters for a–z, two separate lists are needed.
dead_keys := {"1_": "¡", "2_": "„", "3_": "‚", "4_": "‹", "5_": "›", "-_": "­", "=_": "€", ",_": "—", "/_": "¿", "a_": "å", "d_": "ð", "e_": "ə", "i_": "ı", "k_": "ĸ", "m_": "¤", "n_": "ŋ", "o_": "ø", "p_": "£", "s_": "ß", "t_": "þ", "y_": "¥", "z_": "ʒ", "ö_": "œ", "ä_": "æ"}
dead_keys_upper := {"A_": "Å", "D_": "Ð", "E_": "Ə", "N_": "Ŋ", "O_": "Ø", "T_": "Þ", "Z_": "Ʒ", "Ä_": "Æ", "Ö_": "Œ"}
;dead_keys := {"1": "¡", "2": "„", "3": "‚", "4": "‹", "5": "›", "-": "­", "=": "€", ",": "—", "/": "¿", "a": "å", "d": "ð", "e": "ə", "i": "ı", "k": "ĸ", "m": "¤", "n": "ŋ", "o": "ø", "p": "£", "s": "ß", "t": "þ", "y": "¥", "z": "ʒ", "ö": "œ", "ä": "æ", "A": "Å", "D": "Ð", "E": "Ə", "N": "Ŋ", "O": "Ø", "T": "Þ", "Z": "Ʒ", "Ä": "Æ", "Ö": "Œ"}

;-----------------------------------------------------------------------------
; Function definitions

;not functional yet
z_is_right_keyboard() {
  ; Declaring these globals as globals because that is how things are done.
  global wanted_keyboards
	global current_keyboard
	
	;detect_keyboard()
	window := DllCall("GetForegroundWindow")
	pid := DllCall("GetWindowThreadProcessId", "UInt", window, "Ptr", 0)
	current_keyboard := DllCall("GetKeyboardLayout", "UInt", pid)
	if (current_keyboard = wanted_keyboards) {
		return 1
	}
	return 0
}

;not functional yet
z_detect_keyboard() {
  global current_keyboard
	
	window := DllCall("GetForegroundWindow")
	pid := DllCall("GetWindowThreadProcessId", "UInt", window, "Ptr", 0)
	current_keyboard := DllCall("GetKeyboardLayout", "UInt", pid)
	return
}

; The above functions are supposed to be used so that the keyboard is detected only when the user presses Ctrl+Shift (to change the input method and therefore keyboard layout) or Alt+Shift (to change what collection of keyboard layouts is available). That way the keyboard would not need to be detected every single time a character is typed.
; The above does present a problem: what if the user changes the layout via the language bar, using the mouse? Perhaps the detection has to occur always, then.

; is_right_keyboard: checks whether the current keyboard layout is the one where the hotkeys should work.
; - Return value: bool; 1 if the hotkeys should work, 0 if they should not.
is_right_keyboard() {
  global always_on
	
  if always_on {
	  return 1
	}
	
	else {
    global wanted_keyboards
		global current_keyboard
		
		window := DllCall("GetForegroundWindow")
		pid := DllCall("GetWindowThreadProcessId", "UInt", window, "Ptr", 0)
		current_keyboard := DllCall("GetKeyboardLayout", "UInt", pid)

		for name, keyboard in wanted_keyboards {
		  if (current_keyboard = keyboard) {
			  return 1
		  }
		}
		

		return 0
	}
	return 0
}

;-----------------------------------------------------------------------------
; Functional code

#If is_right_keyboard()

; Keeping Capslock accessible:
+!^Capslock::Capslock

; This causes the above mapping to work.
!^Capslock::Capslock

; These two cause the above mapping to work; otherwise the above only turns Capslock on.
!Capslock::Capslock 
^Capslock::Capslock

; Remap Caps Lock (https://autohotkey.com/docs/misc/Remap.htm):
; Because both remappings allow additional modifier keys to be held down, the more specific +Capslock::Capslock remapping must be placed first for it to work.
+Capslock::…
Capslock::_

; Remap special Japanese keys on Dell, with Shift.
+SC07D::| ; Left of Backspace.
+SC073::return ; Left of Right Shift. ; Empty! Unassigned!
+SC07B::‘ ; Between Alt and Space.
+SC079::° ; Right of Space.
+SC070::« ; Left of Right Control.

; Same as above but without Shift.
SC07D::+ ; Left of Backspace.
SC073::; ; Left of Right Shift.
SC07B::“ ; Between Alt and Space.
SC079::” ; Right of Space.
SC070::» ; Left of Right Control.

; Dead key, to the left of Backspace.
<!<^SC07D::
	; The second to last keys ({delete}–{enter}) terminate the execution of the dead key -> "Endkey:" terminate. The last comma-separated set (spaces not allowed, unless they are a part of the string) is a list of matches -> "Match". However, they do not work if they are keys generated by an AHK script (or just this script, not sure). They are ignored regardless of the I option (ignore AHK-produced input).
  Input key, B C I L1, {delete}{esc}{backspace}{enter}, –,|,s,S
		
  if (ErrorLevel = "Timeout") { ; This should not happen because the restriction is not set.
    return
  }
	
	; This has to be commented out because for some inexplicable reason it always catches.
;  else if (ErrorLevel = "Max") {
;	  Send You somehow managed to send more than one key: "%key%".
;    return
;  }
	
  else if (ErrorLevel = "NewInput") {
    ;Send The input was interrupted with %ErrorLevel% and you entered "%key%".
    return
  }
	
  else if InStr(ErrorLevel, "EndKey:") {
    ;Send You entered "%key%" and terminated the input with %ErrorLevel%.
    return
  }
	
  else if (ErrorLevel = "Match") {
    ;Send A match was found for "%key%".
    return
  }
	
  else {
		key_str = %key%_ ; The underscore is needed or digits are not recognised.
		
		; Because the associative list does not seem to distinguish between uppercase and lowercase letters for a–z, two separate lists are needed.
		if (GetKeyState("Shift")) {
			;u := "u"
      ;Send % key_str dead_keys_upper[key_str] u
      Send % dead_keys_upper[key_str]
			
    }
		else {
      ;Send % key_str dead_keys[key_str]
			Send % dead_keys[key_str]
		}
    return
	}
return ; Just in case.

#If