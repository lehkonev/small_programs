use strict;

my $tekstil = "daa";
my $tekstip = "dii doo duu";

# my $yks = "";
# my $kaks = "";
# my $kolm = "";
# my $yksi = "";
# my $kaksi = "";
# my $kolme = "";

my ($yks, $kaks, $kolm) = split(' ', $tekstil, 3);
my ($yksi, $kaksi, $kolme) = split(' ', $tekstip, 3);

print "Lyhyempi teksti, eka: '", $yks, "', toka: '", $kaks, "', kolmas: '", $kolm, "'.\n";
print "Pitempi teksti, eka: '", $yksi, "', toka: '", $kaksi, "', kolmas: '", $kolme, "'.\n";

if ( defined $kaks )
{
	print "Kylla siella jotain on.\n";
}
else
{
	print "Noyp.\n";
}
