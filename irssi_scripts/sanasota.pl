# Script for word wars (called sanasota in Finnish) (can be edited to be any
# kind of simple timer).

# Doesn’t work properly yet.

use strict;
use warnings;
use Irssi;

use vars qw($VERSION %IRSSI);
$VERSION = "0.4";
%IRSSI = (
  authors     => 'Veini Lehkonen',
  contact     => 'lehkonev@gmail.com',
  name        => 'sanasota',
  description => 'Simple timer that can be used in specific channels.',
  license     => 'Public Domain',
  url         => '',
  changed     => '2015'
);

use Irssi::Irc;

# The command will only be accepted from these channels.
our @kanavat => ("nanowrimo", "finnnano");
# This is the command that will trigger the timer.
our $sanasota => "!sanasota";
# This is the default time (minutes).
our $perusaika => 10;
# This determines how many timers can be active at one time.
our $montako_sanasotaa_max => 5;
our $montako_sanasotaa = 0;

sub lopeta_sanasota
{
	my ($palvelin, $viesti) = @_;
	$palvelin->command("$viesti sanasota loppui!");
	$montako_sanasotaa--;
}

sub kampaa_sanasota
{
	my ($palvelin, $viesti, $nick, $osoite, $kanava) = @_;
	my ($kasky, $aika, $yksikko) = split(' ', $viesti, 3);
	my $vastaus = "msg " . $kanava . " " . $nick . ": ";
	my $aikayksikko = 1;
	
	# If the word was the correct command defined in $sanasota
	# and the channel is inside @kanavat
	# and the time is a number...
	if ( ($kasky ~= $sanasota) and
	     ($kanava ~~ @kanavat) )
	{
		# If there are too many timers, new one won’t be made.
		if ( $montako_sanasotaa > $montako_sanasotaa_max )
		{
			$palvelin->command( $vastaus . "Liian monta sanasotaa käynnissä.");
		}
		else		
		{
			if ( !defined $aika )
			{
				$aika = 10;
			}
			
			if ( (Scalar::Util::looks_like_number($aika)) and
			     ($aika < 120.1) and
			     ($aika > 0.1) )
			{
				$vastaus .= $aika . ":n ";
				
				# Let’s check if the caller wanted seconds. If not, assume minutes.
				if ($yksikko == "s")
				{
					$vastaus .= "sekunnin";
				}
				else
				{
					$aikayksikko = 60;
					$vastaus .= "minuutin";
				}
				
				$palvelin->command("$vastaus sanasota alkaa nyt!");
				my @parametri = ($palvelin, $vastaus);
				Irssi::timeout_add_once($aikayksikko * $aika * 1000, \&lopeta_sanasota, @parametri);
				$montako_sanasotaa++;
			}
			else
			{
				$palvelin->command($vastaus . "Ei pysty, annettu aika on kummallinen.");
			}
		}
	}
}

Irssi::signal_add ("message public", "kampaa_sanasota");
#Irssi::signal_add ("message private", "kampaa_sanasota");


#timeout_add_once $msecs, $func, $data
#Call $func once after $msecs milliseconds (1000 = 1 second) with parameter $data. $msecs must be at least 10 or an error is signaled via croak.

# # Esim.:
  # sub event_privmsg {
    # # $data = "nick/#channel :text"
    # my ($server, $data, $nick, $address) = @_;
    # my ($target, $text) = split(/ :/, $data, 2);

    # Irssi::signal_stop() if ($text =~ /free.*porn/ || $nick =~ /idiot/);
  # }

# Irssi::signal_add("event privmsg", "event_privmsg")
