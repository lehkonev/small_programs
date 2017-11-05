# Script for word wars (called sanasota in Finnish) (can be edited to be any kind of simple timer).
# This scripts works in irssi after it came out of beta, but there are other issues with it. 

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
  changed     => '2015-11-17'
);

use Irssi::Irc;

# The command will only be accepted from these channels.
our @kanavat = ("#nanowrimo", "#finnnano");
# This is the command that will trigger the timer.
our $sanasota = "!sanasota";
# This is the default time (minutes).
our $perusaika = 10;
# This determines how many timers can be active at one time.
our $montako_sanasotaa_max = 5;
our $montako_sanasotaa = 0;
our @palvelimet;
our @viestit;

sub lopeta_sanasota
{

        # Testiprintti, toivottavasti omaan status-ikkunaan.
        #print ( CRAP "Eka on $_[0], toka on $_[1]." );

        #my ($palvelin, $viesti) = split('¤', $_[0], 2);
        #print ( CRAP "Palvelin on $palvelin ja viesti on $viesti." );
        #my Irssi::Server $pal = $palvelin;
        #print ( CRAP "Globaali palvelin on $palv." );
        #$pal->command("$viesti sanasota loppui!");
        my $i = $_[0];
        $palvelimet[$i]->command("$viestit[$i] sanasota loppui!");
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
        if ( ($kasky ~~ $sanasota) and
             ($kanava ~~ @kanavat) )
        {
                # If there are too many timers, new one won’t be made.
                if ( $montako_sanasotaa > $montako_sanasotaa_max )
                {
                        $palvelin->command( $vastaus . "Ei pysty, liian monta sanasotaa käynnissä.");
                }
                else
                {
                        if ( !defined $aika )
                        {
                                $aika = 10;
                        }

                        if ( #(Scalar::Util::looks_like_number($aika)) and
                             ($aika < 120.1) and
                             ($aika > 0.1) )
                        {
                                $vastaus .= $aika . ":n ";

                                # Let’s check if the caller wanted seconds. If not, assume minutes.
                                if ($yksikko ~~ "s")
                                {
                                        $vastaus .= "sekunnin";
                                }
                                else
                                {
                                        $aikayksikko = 60;
                                        $vastaus .= "minuutin";
                                }

                                $palvelin->command("$vastaus sanasota alkaa nyt!");
                                #print ( CRAP "Palvelin on $palvelin ja vastaus on $vastaus." );
# Here is a stupid concatenation because arrays did not work for me.
                                $montako_sanasotaa++;
                                #my $parametri = $palvelin . "¤" . $vastaus;
                                #$palv = $palvelin;
                                $palvelimet[$montako_sanasotaa] = $palvelin;
                                $viestit[$montako_sanasotaa] = $vastaus;
                                my $tagi = Irssi::timeout_add_once($aikayksikko * $aika * 1000, \&lopeta_sanasota, ($montako_sanasotaa));
                                #Irssi::timeout_remove($tagi);
                        }
                        else
                        {
                                $palvelin->command($vastaus . "Ei pysty, annettu aika on kummallinen.");
                        }
                }
        }
}

Irssi::signal_add ("message public", "kampaa_sanasota");
