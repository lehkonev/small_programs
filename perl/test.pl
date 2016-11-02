use strict;
use warnings;

use Data::Dumper;

#use constant C_EMPTY => (); # This stays uninitialised forever.
use constant C => ("qwe", "rty", "uio");
our @global_list = (1, 2, 3, 6, 0);


sub testsub {	
	#------------------------------------------------------------------
	# Silly testing:
	# my $tekstil = "daa";
	# my $tekstip = "dii doo duu";

	# my $yks = "";
	# my $kaks = "";
	# my $kolm = "";
	# my $yksi = "";
	# my $kaksi = "";
	# my $kolme = "";

	# my ($yks, $kaks, $kolm) = split(' ', $tekstil, 3);
	# my ($yksi, $kaksi, $kolme) = split(' ', $tekstip, 3);

	# print "Lyhyempi teksti, eka: '", $yks, "', toka: '", $kaks, "', kolmas: '", $kolm, "'.\n";
	# print "Pitempi teksti, eka: '", $yksi, "', toka: '", $kaksi, "', kolmas: '", $kolme, "'.\n";

	# if (defined $kaks) {
		# print "Kylla siella jotain on.\n";
	# }
	# else {
		# print "Noyp.\n";
	# }

	
	
	#------------------------------------------------------------------
	# Print an array, separated by spaces:
	# my @listing = ("asd", "fgh");
	# my @empty_list = ();
	# print "@listing" . "\n";

	#------------------------------------------------------------------
	# Print the lengths of arrays:
	# print("Empty constant list: " . scalar(C_EMPTY) . "\n");
	# print("Constant list: " . scalar(C) . "\n");
	# print("List: " . scalar(@listing) . "\n");
	# print("Empty list: " . scalar(@empty_list) . "\n");
	# print("Global list: " . scalar(@global_list) . "\n");

	#------------------------------------------------------------------
	# ~~ is ”smartmatch”, experimental, doesn’t seem to be working
	# if ("rty" ~~ C) 
	# {
		# print "Found\n";
	# }
	# else
	# {
		# print "Not found\n";
	# }

	#------------------------------------------------------------------
	# Foreach test + finding out the index.
	# my $i = 0;

	# foreach (C)
	# {
		# print $_;

		# if (not("rty" eq $_))
		# {
			# print ": not Found at $i\n";
			# last; # exit loop)
		# }
		# else
		# {
			# print ":  found\n";
		# }
		# $i++;

	# }

	#------------------------------------------------------------------
	# Alternative for foreach, nicer than above but can’t find out index?
	# if (grep {$_ eq "fgh"} @listing)
	# {
		# print "Found in list\n";
	# }

	# if (grep {$_ eq "rty"} C)
	# {
		# print "Found in C\n";
	# }
	
	#------------------------------------------------------------------
	# Concatenation test:
	# my $msg = "First bit";
	# $msg .= (C)[1]; # Indexing a constant array requires brackets!
	# $msg = $msg . ", and second";
	# $msg .= ", and third.\n";
	# print $msg;
	
	#------------------------------------------------------------------
	# Hash test:
	# my %hashy;
	# my $hash_size = scalar(values %hashy);
	# print "Size of hash: $hash_size\n";
	# $hashy{'metre'} = 1;
	# $hashy{'metre'}->{'unit'} = "m";
	# $hashy{'kilometre'} = 1000;
	# $hash_size = scalar(values %hashy);
	# print "Size of hash: $hash_size\n";
	# delete $hashy{'metre'};
	# delete $hashy{'kilometre'};
	# $hash_size = scalar(values %hashy);
	# print "Size of hash: $hash_size\n";
	# print "metre: $hashy{'metre'} $hashy{'metre'}->{'unit'}\n";
	
	# my %hashy;
	# $hashy{'a'}[5] = "pöö";
	# print $hashy{'a'}[5] . "\n";
	# $hashy{'a'} = [1, 2, 3];
	# print($hashy{'a'}[2]);
	# print($hashy{'a'}[0]);
	
	#------------------------------------------------------------------
	# What the heck is this?
	# print(CRAP "boo?");
	
	#------------------------------------------------------------------
	# 
	# my @arraya;
	# $arraya[1] = "pöö";
	# print $arraya[1];
	# print $arraya[0];
}

testsub();
