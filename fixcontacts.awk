BEGIN { FS=","; OFS=","; }
{ 
  # assume first field is name and second is phone number
  split($1,a," "); 
  n=$2;
  gsub("[ ]","",n)
  gsub("[\(]","",n)
  gsub("[\)]","",n)
  gsub("[\-]","",n)
  gsub("[\"]","",n)
  gsub("[\.]","",n)
  if (n !~ /^1/ && length(n)==10) n="+1"n ;
  if (n ~ /^1/ && length(n)==11) n="+"n ;
  print n, a[1]" ji"; 
}
