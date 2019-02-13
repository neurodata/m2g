#!/bin/bash

if [ $# -lt 1 ] ; then
 echo "Usage: `basename $0` <eddy current ecclog file>"
 exit 1;
fi

logfile=$1;
basenm=`basename $logfile .ecclog`;

nums=`grep -n 'Final' $logfile | sed 's/:.*//'`;

rm -f ec_disp.txt 2>/dev/null
rm -f ec_rot.txt 2>/dev/null
rm -f ec_trans.txt 2>/dev/null
rm -f grot_ts.txt 2>/dev/null

touch grot_ts.txt
touch grot.mat

firsttime=yes;
m=1;
for n in $nums ; do
	echo "Volume $m"
	n1=`echo $n + 1 | bc` ;
	n2=`echo $n + 5 | bc` ;
	sed -n  "$n1,${n2}p" $logfile > grot.mat ;
	if [ $firsttime = yes ] ; then firsttime=no; cp grot.mat grot.refmat ; cp grot.mat grot.oldmat ; fi
	absval=`$FSLDIR/bin/rmsdiff grot.mat grot.refmat $basenm`;
	relval=`$FSLDIR/bin/rmsdiff grot.mat grot.oldmat $basenm`;
	cp grot.mat grot.oldmat
	echo $absval $relval >> ec_disp.txt ;
	$FSLDIR/bin/avscale --allparams grot.mat $basenm | grep 'Rotation Angles' | sed 's/.* = //' >> ec_rot.txt ;
	$FSLDIR/bin/avscale --allparams grot.mat $basenm | grep 'Translations' | sed 's/.* = //' >> ec_trans.txt ;
	m=`echo $m + 1 | bc`;
done

echo "absolute" > grot_labels.txt
echo "relative" >> grot_labels.txt

$FSLDIR/bin/fsl_tsplot -i ec_disp.txt -t 'Eddy Current estimated mean displacement (mm)' -l grot_labels.txt -o ec_disp.png

echo "x" > grot_labels.txt
echo "y" >> grot_labels.txt
echo "z" >> grot_labels.txt

$FSLDIR/bin/fsl_tsplot -i ec_rot.txt -t 'Eddy Current estimated rotations (radians)' -l grot_labels.txt -o ec_rot.png
$FSLDIR/bin/fsl_tsplot -i ec_trans.txt -t 'Eddy Current estimated translations (mm)' -l grot_labels.txt -o ec_trans.png

# clean up temp files
/bin/rm grot_labels.txt grot.oldmat grot.refmat grot.mat 2>/dev/null

#Translation Regressor
for i in `ls ./ec_trans.txt`;
do
	prefix=`echo $i | awk 'BEGIN{FS="_ec_trans"}{print $1}'`
	count=`cat $i| wc |awk '{ print $1}'`
	#Translation for x
	x_total=`cat $i |tr -d - |awk '{s+=$1} END {print s}'`
	x_average=`echo "scale=4; $x_total / $count" | bc`
	#Translation for y
	y_total=`cat $i |tr -d - |awk '{s+=$2} END {print s}'`
	y_average=`echo "scale=4; $y_total / $count" | bc`
	#Translation for z
	z_total=`cat $i |tr -d - |awk '{s+=$3} END {print s}'`
	z_average=`echo "scale=4; $z_total / $count" | bc`
	#euclidian distance
	euclidian=$(echo "scale=4;sqrt(($x_average*$x_average)+($y_average*$y_average)+($z_average*$z_average))" | bc)

echo "Translation ${euclidian}" >> movement_data.txt
done

#Rotation Regressor
for i in `ls ./ec_rot.txt`;
do
	prefix=`echo $i | awk 'BEGIN{FS="_ec_rot"}{print $1}'`
	count=`cat $i| wc |awk '{ print $1}'`
	#Translation for x
	x_total=`cat $i |tr -d - |awk '{s+=$1} END {print s}'`
	x_average=`echo "scale=4; $x_total / $count" | bc`
	#Translation for y
	y_total=`cat $i |tr -d - |awk '{s+=$2} END {print s}'`
	y_average=`echo "scale=4; $y_total / $count" | bc`
	#Translation for z
	z_total=`cat $i |tr -d - |awk '{s+=$3} END {print s}'`
	z_average=`echo "scale=4; $z_total / $count" | bc`
	#euclidian distance
	euclidian=$(echo "scale=4;sqrt(($x_average*$x_average)+($y_average*$y_average)+($z_average*$z_average))" | bc)

echo "Rotation ${euclidian}" >> movement_data.txt
done

#Displacement
for i in `ls ./ec_disp.txt`;
do
	prefix=`echo $i | awk 'BEGIN{FS="_ec_disp"}{print $1}'`
	count=`cat $i| wc |awk '{ print $1}'`
	#Translation for x
	x_total=`cat $i |tr -d - |awk '{s+=$1} END {print s}'`
	x_average=`echo "scale=4; $x_total / $count" | bc`
	#Translation for y
	y_total=`cat $i |tr -d - |awk '{s+=$2} END {print s}'`
	y_average=`echo "scale=4; $y_total / $count" | bc`
	#Translation for z
	z_total=`cat $i |tr -d - |awk '{s+=$3} END {print s}'`
	z_average=`echo "scale=4; $z_total / $count" | bc`
	#euclidian distance
	euclidian=$(echo "scale=4;sqrt(($x_average*$x_average)+($y_average*$y_average)+($z_average*$z_average))" | bc)

echo "Displacement ${euclidian}" >> movement_data.txt
done

rm MOTION_OUTLIERS.txt 2>/dev/null
touch MOTION_OUTLIERS.txt

##CHECK TRANSLATION THRESHOLDS
# Total volumes
tot_vols=`cat ec_trans.txt | wc -l`

#check number of lines that x values are greater than 2 mm or less than -2 mm translated
p_trans=`awk '$3>2 || $2>2 || $1>2' ec_trans.txt | wc -l`
n_trans=`awk '$3<-2 || $2<-2 || $1<-2' ec_trans.txt | wc -l`

Total_translines=`expr $p_trans + $n_trans`

perc_trans=$(echo "scale=4;(($Total_translines/$tot_vols))*100" | bc | awk '{print int($1+0.5)}')

if [ $perc_trans -gt 10 ]; then
	echo -e "\e[41mPARTICIPANT UNUSABLE DUE TO MOTION. "$perc_trans"% TRANSLATION EXCEEDS RECOMMENDED THRESHOLD OF 2MM\e[0m" >> MOTION_OUTLIERS.txt
else
	echo -e "\e[42mTRANSLATION OF VOLUMES DUE TO MOTION LOOKS ACCEPTABLE. "$perc_trans"% Translation.\e[0m" >> MOTION_OUTLIERS.txt
fi

##CHECK ROTATION THRESHOLDS
# Total volumes
tot_vols=`cat ec_rot.txt | wc -l`

#check number of lines that x values are greater than 2 mm or less than -2 mm translated
p_rot=`awk '$3>.2 || $2>.2 || $1>.2' ec_rot.txt | wc -l`
n_rot=`awk '$3<-.2 || $2<-.2 || $1<-.2' ec_rot.txt | wc -l`

Total_rot=`expr $p_rot + $n_rot`

perc_rot=$(echo "scale=4;(($Total_rot/$tot_vols))*100" | bc | awk '{print int($1+0.5)}')

if [ "$perc_rot" -gt 10 ];
then
	echo -e "\e[41mPARTICIPANT UNUSABLE DUE TO MOTION. "$perc_rot"% Rotation EXCEEDS RECOMMENDED THRESHOLD OF .2 Degrees\e[0m" >> MOTION_OUTLIERS.txt
else
	echo -e "\e[42mROTATION OF VOLUMES DUE TO MOTION LOOKS ACCEPTABLE. "$perc_rot"% Rotation.\e[0m" >> MOTION_OUTLIERS.txt
fi

cat MOTION_OUTLIERS.txt
