# usage: awk -f fixcontacts.awk phonepos=2 namesuffix="ji" kirtan.csv
#
# phonepos argument tells the column position of Whatsapp phone no in the csv file
# namesuffix is the string to be appended to the name
#
BEGIN { FS=","; OFS=","; }
{ 
  #
  # assume first field is name and second is phone number
  #
  if (phonepos==1) {
    n=$1; split($2,a," "); 
  } else if (phonepos==2) {
    n=$2; split($1,a," "); 
  }

  #
  # clean the phone number of special variables
  #
  gsub("[ ]","",n);
  gsub("[\(]","",n);
  gsub("[\)]","",n);
  gsub("[\-]","",n);
  gsub("[\"]","",n);
  gsub("[\.]","",n);
  # if the US country code is not there in the beginning then add it
  if (n !~ /^1/ && length(n)==10) n="+1"n ;
  # if the US country code is  there in the beginning but there is no + then add it
  if (n ~ /^1/ && length(n)==11) n="+"n ;
  
  firstname=a[1];
  gsub("[\"]","",firstname);

  print n, firstname" "namesuffix; 
}
