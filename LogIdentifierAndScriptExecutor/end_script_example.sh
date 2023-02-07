echo "Executing User defined bash script after capturing target statement"

b=2
c=3
a=$(($b+$c))
d=$((2*$a))

echo $d

echo "Executed user defined bash script"