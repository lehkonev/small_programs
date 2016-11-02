# Public Timer
# Creator: Veini Lehkonen, lehkonev@gmail.com
# Version: 0.2
# Date: 2016-10-31
# ----------------------------------------------------------------------------
# Environment used to create and test:
# ...
# Windows 10 Home 64-bit
##############################################################################
# A simple timer script. Features:
# * The one running the script is able to use the timer command.
# * The script can be adjusted to accept commands from other people as well
#   (from everyone in specific channels, defined in @CHANNELS, and from
#   specific servers, defined in @SERVERS).
# * The format of the timer command is “COMMAND_WORD TIME [UNIT]”, where
#   COMMAND_WORD is one of the words defined in CMD_WORD, for example “!timer”,
#   TIME is an integer or real number, for example 5.5, and UNIT is optional;
#   it can be either “s” (seconds) or something else (defaults to minutes).
# * The maximum number of running timers can be adjusted (TIMERS_MAX).
# * The maximum and minimum time value of the timer can be adjusted (TIME_MAX,
#   TIME_MIN).
#------------------------------------------------------------------------------

use strict;
use warnings;
use Irssi;

use vars qw($VERSION %IRSSI);
$VERSION = "0.2";
%IRSSI = (
  authors     => 'Veini Lehkonen',
  contact     => 'lehkonev@gmail.com',
  name        => 'public_timer',
  description => '.',
  license     => 'Public Domain',
  url         => '',
  changed     => '2016-10-31' # It’s NANOWRIMO TIME!
);

use Irssi::Irc;

# Constants:
use constant TIMERS_MAX => 20;
use constant TIME_MAX => 180.0;
use constant TIME_MIN => 1.0;
# The timer commands: commands that will start the timer or show the help
# message.
use constant CMD_WORD => (
	"!sanasota", 
	"!ajastin", 
	"!wordwar", 
	"!timer"
	);
# For the following, the order of the values is important, since the
# language/wording will be chosen according to the order.
use constant MSG_START => (
	"sanasota alkoi!",
	"ajastus alkoi!", 
	"word war started!", 
	"timer started!"
	);
use constant MSG_END => (
	"sanasota loppui!",
	"ajastus loppui!", 
	"wordwar ended!", 
	"timer ended!"
	);
use constant MSG_TIMES_M => (
	" minuutin ",
	" minuutin ",
	" minute ",
	" minute "
	);
use constant MSG_TIMES_S => (
	" sekunnin ",
	" sekunnin ",
	" second ",
	" second "
	);
use constant MSG_TIMES_SUFFIX => (
	":n",
	":n",
	"",
	""
	);
use constant MSG_MAX_TIMERS => (
	"Virhe: liian monta sanasotaa käynnissä.",
	"Virhe: liian monta ajastusta käynnissä.",
	"Error: too many ongoing word wars.",
	"Error: too many running timers."
	);
use constant MSG_HELP => (
	"!sanasota: ohje: Kirjoita ”!sanasota 10” " .
	"aloittaaksesi 10 minuutin sanasodan. " .
	"Hyväksyttävät yksiköt: minuutti (m) ja sekunti (s). " .
	"Hyväksyttävät aika-arvot: " . TIME_MIN . "–" . TIME_MAX . ". " .
	"Sanasotien maksimimäärä: " . TIMERS_MAX . ".",
	"!ajastin: ohje: Kirjoita ”!ajastin 10” " .
	"aloittaaksesi 10 minuutin ajastuksen. " .
	"Hyväksyttävät yksiköt: minuutti (m) ja sekunti (s). " .
	"Hyväksyttävät aika-arvot: " . TIME_MIN . "–" . TIME_MAX . ". " .
	"Ajastuksien maksimimäärä: " . TIMERS_MAX . ".",
	"!wordwar: guide: Type “!wordwar 10” " .
	"to start a 10 minute word war. " .
	"Accepted units: minute (m) and second (s). " .
	"Accepted time values: " . TIME_MIN . "–" . TIME_MAX . ". " .
	"Maximum number of word wars: " . TIMERS_MAX . ".",
	"!timer: guide: Type “!timer 10” " .
	"to start a 10 minute timer. " .
	"Accepted units: minute (m) and second (s). " .
	"Accepted time values: " . TIME_MIN . "–" . TIME_MAX . ". " .
	"Maximum number of timers: " . TIMERS_MAX . "."
	);

# The following constants are not literal constants for two reasons:
# 1) They can be empty, and constants do not seem to work when empty.
# 2) In case the script is ever modified so that these lists can be edited at
#    runtime. For example, the user could type a command like
#    “!timer add channel #nameofchannel” to add the channel to the list of
#    channels from where the timer command is accepted.

# The channels and servers from where the timer command is accepted.
# (Empty: accepted from everywhere.)
# Format: ("#channel1", "#channel2", "#channel3", "#channel4")
our @CHANNELS = ();
our @SERVERS = ();
# The command will always be accepted from self.

# Global:
our %timers;

#------------------------------------------------------------------------------
# Subroutine: checker_own – runs when a message from self is sent.
# It separates the values to nicely understandable parts and passes them
# to the check_timer subroutine.
# Parameters: @_
sub checker_own {
	my ($server, $msg, $nick, $address, $target) = @_;
	check_timer($server, $msg, $nick, $nick);
}

#------------------------------------------------------------------------------
# Subroutine: checker_public – runs when a message from someone else is
# received. It checks whether the message came from an approved server and
# channel and separates the values to nicely understandable parts and passes
# them to the check_timer subroutine.
sub checker_public {
	my ($server, $msg, $nick, $address, $target) = @_;
	
	# Checking whether the server was right:
	if (not((scalar(@SERVERS) == 0) or
	        (grep {$_ eq $server} @SERVERS))) {
		return 0;
	}
	
	# Checking whether the channel was right:
	if (not((scalar(@CHANNELS) == 0) or
	        (grep {$_ eq $target} @CHANNELS))) {
		return 0;
	}
	
	check_timer($server, $msg, $nick, $target);
}

#------------------------------------------------------------------------------
# Subroutine: check_timer – checks whether the message’s first word is the
# timer command. Parameters:
# $server: the server where the command came from.
# $msg: the message that may contain the timer command.
# $nick: the nick that sent the message.
# $target: the channel where the message was sent.
sub check_timer {
	my ($server, $msg, $nick, $target) = @_;
	# The first word should be the timer command.
	my ($cmd, $cmd_rest) = split(' ', $msg, 2);
	
	# Command (the index needs to be taken down for language purposes):
	my $language_index = 0;
	my $found = 0;
	foreach (CMD_WORD) {
		if ($_ eq $cmd) {
			$found = 1;
			last;
		}
		$language_index++;
	}
	
	if (not($found)) {
		return 0;
	}
	
	# The command was found in a correct context.
	#print("Server: '$server', Nick: '$nick', Target: '$target', index: '$language_index', command: '$cmd_rest'\n");
	run_timer($server, $nick, $target, $language_index, $cmd_rest)	;
}

#------------------------------------------------------------------------------
# Subroutine: run_timer – constructs a proper message in response to the
# timer command.
sub run_timer {
	my ($server, $nick, $target, $language_index, $cmd) = @_;
	
	# After the timer command word, there should be a time and possibly a unit.
	my $time;
	my $unit;
	if (defined $cmd) {
		($time, $unit) = split(' ', $cmd, 2);
	}
	my $return_msg = "msg " . $target . " ";

	# If the time is not recognisable and within limits, send the help message.
	if (not((defined $time) and
	        (Scalar::Util::looks_like_number($time)) and
	        ($time <= TIME_MAX) and
	        ($time >= TIME_MIN))) {
		$server->command($return_msg . (MSG_HELP)[$language_index]);
		return 0;
	}
	
	# If there are too many timers, new ones will not be made.
	my $number_of_timers = scalar(values %timers);
	if ($number_of_timers >= TIMERS_MAX) {
		$server->command($return_msg . (MSG_MAX_TIMERS)[$language_index]);
		return 0;
	}
	
	# Figure out if a proper time unit was given (minute and second accepted).
	# Default to minute.
	my $time_multiplier = 60;
	my $time_unit = (MSG_TIMES_M)[$language_index];
	if ((defined $unit) and ($unit eq "s")) {
		$time_multiplier = 1;
		$time_unit = (MSG_TIMES_S)[$language_index];
	}
	else {
		$unit = "m";
	}
	
	# Since the time will be in milliseconds, any decimals are not important.
	# Truncating the possible decimals to get an integer is just fine.
	my $time_ms = int($time_multiplier * $time * 1000);

	# Construct the timer start message.
	$return_msg .= $nick . ": " . 
	               $time . (MSG_TIMES_SUFFIX)[$language_index] .
	               $time_unit;								 

	# Construct the timer name.
	my $timer_name = "$nick $time $unit $number_of_timers";
	while (1) {
		if (exists($timers{$timer_name})) {
			# It should not be possible to get here, but better be sure.
			$number_of_timers++;
			$timer_name = "N$nick T$time U$unit #$number_of_timers";
		}
		else {
			last;
		}
	}
	
	$server->command($return_msg . (MSG_START)[$language_index]);
	$timers{$timer_name}[0] = $server;
	$timers{$timer_name}[1] = $return_msg . (MSG_END)[$language_index];
	$timers{$timer_name}[2] =
		Irssi::timeout_add_once($time_ms, \&end_timer, $timer_name);
}

#------------------------------------------------------------------------------
# Subroutine: end_timer – sends a proper message when the timer is ending and
# removes the timer.
sub end_timer {
	my ($timer_name) = @_;
	my $number_of_timers = -1;
	if (exists($timers{$timer_name})) {
		($timers{$timer_name}[0])->command($timers{$timer_name}[1]);
		# Is this needed for timeout_add_once?
		Irssi::timeout_remove($timers{$timer_name}[2]);
		delete($timers{$timer_name});
		# $number_of_timers = scalar(values %timers);
		# print("
# Timer $timer_name deleted and there are $number_of_timers timers.
# ");
	}
	
	# This should never happen.
	else {
		$number_of_timers = scalar(values %timers);
		print("
Timer $timer_name does not exist and there are $number_of_timers timers.
");
		# (Note: the above prints to the irssi status screen.)
	}
}

Irssi::signal_add_last("message own_public", "checker_own"); # msg by self
Irssi::signal_add_last("message public", "checker_public"); # msg by another
