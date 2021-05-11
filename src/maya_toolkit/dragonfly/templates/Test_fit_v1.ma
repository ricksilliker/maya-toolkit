//Maya ASCII 2018ff07 scene
//Name: Test_fit_v5.ma
//Last modified: Wed, Apr 10, 2019 04:29:14 PM
//Codeset: 1252
file -rdi 1 -ns "model" -rfn "modelRN" -op "v=0;" -typ "mayaAscii" "D:/dev/gemini/SourceArt/Characters/CharacterTest/Rigs/Work/Test//model/Test_model_v1.ma";
file -r -ns "model" -dr 1 -rfn "modelRN" -op "v=0;" -typ "mayaAscii" "D:/dev/gemini/SourceArt/Characters/CharacterTest/Rigs/Work/Test//model/Test_model_v1.ma";
requires maya "2018ff07";
requires "stereoCamera" "10.0";
currentUnit -l centimeter -a degree -t ntsc;
fileInfo "application" "maya";
fileInfo "product" "Maya 2018";
fileInfo "version" "2018";
fileInfo "cutIdentifier" "201711281015-8e846c9074";
fileInfo "osv" "Microsoft Windows 8 Business Edition, 64-bit  (Build 9200)\n";
createNode transform -n "FitSkeleton";
	rename -uid "3C55B6C7-49AD-A182-B578-FE9BE002BBB8";
	addAttr -ci true -sn "visCylinders" -ln "visCylinders" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "visBoxes" -ln "visBoxes" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "visBones" -ln "visBones" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "lockCenterJoints" -ln "lockCenterJoints" -dv 1 -min 0 -max 
		1 -at "bool";
	addAttr -ci true -sn "visGap" -ln "visGap" -dv 0.75 -min 0 -max 1 -at "double";
	addAttr -ci true -k true -sn "visGeo" -ln "visGeo" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "visGeoType" -ln "visGeoType" -min 0 -max 3 -en "cylinders:boxes:spheres:bones" 
		-at "enum";
	addAttr -ci true -sn "visSpheres" -ln "visSpheres" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "visPoleVector" -ln "visPoleVector" -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "visJointOrient" -ln "visJointOrient" -min 0 -max 1 
		-at "bool";
	addAttr -ci true -k true -sn "visJointAxis" -ln "visJointAxis" -min 0 -max 1 -at "bool";
	addAttr -ci true -sn "preRebuildScript" -ln "preRebuildScript" -dt "string";
	addAttr -ci true -sn "postRebuildScript" -ln "postRebuildScript" -dt "string";
	addAttr -r false -s false -ci true -m -im false -sn "drivingSystem" -ln "drivingSystem" 
		-at "message";
	addAttr -ci true -m -sn "drivingSystem_Fingers_R" -ln "drivingSystem_Fingers_R" 
		-dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -m -sn "drivingSystem_Fingers_L" -ln "drivingSystem_Fingers_L" 
		-dv 1 -min 0 -max 1 -at "bool";
	setAttr -l on ".v";
	setAttr ".ove" yes;
	setAttr -l on -k off ".tx";
	setAttr -l on -k off ".ty";
	setAttr -l on -k off ".tz";
	setAttr -l on -k off ".rx";
	setAttr -l on -k off ".ry";
	setAttr -l on -k off ".rz";
	setAttr ".visCylinders" yes;
	setAttr ".visGap" 1;
	setAttr -s 36 ".drivingSystem";
	setAttr -s 18 ".drivingSystem_Fingers_R";
	setAttr -s 18 ".drivingSystem_Fingers_R";
	setAttr -s 18 ".drivingSystem_Fingers_L";
	setAttr -s 18 ".drivingSystem_Fingers_L";
createNode nurbsCurve -n "FitSkeletonShape" -p "FitSkeleton";
	rename -uid "8D7E3B9A-4E08-4511-80DC-9B8994F1D986";
	setAttr -k off ".v";
	setAttr ".ove" yes;
	setAttr ".ovc" 29;
	setAttr ".cc" -type "nurbsCurve" 
		3 8 2 no 3
		13 -2 -1 0 1 2 3 4 5 6 7 8 9 10
		11
		12.240173377699845 7.4949445740043694e-16 -12.240173377699826
		-1.97488903135085e-15 1.0599452265791625e-15 -17.310219196541201
		-12.240173377699833 7.4949445740043734e-16 -12.240173377699833
		-17.310219196541201 3.0714560892679934e-31 -5.0160684556665005e-15
		-12.240173377699836 -7.4949445740043704e-16 12.240173377699829
		-5.2159068722043027e-15 -1.0599452265791627e-15 17.310219196541205
		12.240173377699826 -7.4949445740043734e-16 12.240173377699833
		17.310219196541201 -5.6929864886735388e-31 9.2973524981034812e-15
		12.240173377699845 7.4949445740043694e-16 -12.240173377699826
		-1.97488903135085e-15 1.0599452265791625e-15 -17.310219196541201
		-12.240173377699833 7.4949445740043734e-16 -12.240173377699833
		;
createNode joint -n "Root" -p "FitSkeleton";
	rename -uid "65FAB061-4223-D5FE-A4D5-75839A05F642";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "centerBtwFeet" -ln "centerBtwFeet" -dv 1 -min 0 -max 
		1 -at "bool";
	addAttr -ci true -k true -sn "inbetweenJoints" -ln "inbetweenJoints" -dv 2 -min 
		0 -max 10 -at "long";
	addAttr -ci true -k true -sn "freeOrient" -ln "freeOrient" -dv 1 -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 1.0262204333175599e-15 50.375000000000021 2.7880966962955112e-05 ;
	setAttr -l on ".tx";
	setAttr ".r" -type "double3" 6.3611093629270217e-15 3.1805546814635174e-14 -4.7708320221952761e-14 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 89.999999999999986 0 89.999999999999986 ;
	setAttr ".dl" yes;
	setAttr ".typ" 1;
	setAttr ".otp" -type "string" "Mid";
	setAttr -k on ".fat" 8.8514488900366448;
	setAttr -k on ".fatY" 0.64999999999999991;
	setAttr -k on ".fatZ";
	setAttr -k on ".inbetweenJoints" 0;
createNode joint -n "Spine1" -p "Root";
	rename -uid "46956B90-4D29-4B0E-C64F-CEA6CC841F08";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.477376426915626 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "inbetweenJoints" -ln "inbetweenJoints" -dv 2 -min 
		0 -max 10 -at "long";
	setAttr ".t" -type "double3" 5.8712599695809331e-05 -2.7880966968856119e-05 -5.9010081861647148e-15 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".typ" 1;
	setAttr -k on ".fat" 8.8514488900366448;
	setAttr -k on ".fatY" 0.65;
	setAttr -k on ".fatZ";
	setAttr -k on ".inbetweenJoints" 0;
createNode joint -n "Spine2" -p "Spine1";
	rename -uid "8E56E4F1-4608-E616-A347-B083E795C1D7";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.477376426915626 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "inbetweenJoints" -ln "inbetweenJoints" -dv 2 -min 
		0 -max 10 -at "long";
	setAttr ".t" -type "double3" 7.293139599645734 3.6082248300317666e-16 -5.1850404394045783e-15 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".typ" 1;
	setAttr -k on ".fat" 8.8514488900366448;
	setAttr -k on ".fatY" 0.65;
	setAttr -k on ".inbetweenJoints" 0;
createNode joint -n "Spine3" -p "Spine2";
	rename -uid "FE718D81-4141-34D6-4D1F-EC8DD2F08C2D";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1.477376426915626 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "inbetweenJoints" -ln "inbetweenJoints" -dv 2 -min 
		0 -max 10 -at "long";
	setAttr ".t" -type "double3" 3.6174600636228291 3.5064002792120134e-16 -5.1579815579618208e-15 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 2.8249000307521015e-30 4.4726550208080702e-15 ;
	setAttr ".typ" 1;
	setAttr -k on ".fat" 8.8514488900366448;
	setAttr -k on ".fatY" 0.65;
	setAttr -k on ".inbetweenJoints" 0;
createNode joint -n "Chest" -p "Spine3";
	rename -uid "CCD84068-4DCB-4061-D313-5888560F8432";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "freeOrient" -ln "freeOrient" -dv 1 -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 6.1345978392350347 4.19751160184303e-14 7.3800522470863778e-15 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" 1.7260588825846559e-14 -2.2551385917940818e-13 1.9083328088781066e-14 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -1.6588611857701156e-16 1.6481844864000559e-16 -0.74229611813807039 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "Chest";
	setAttr -k on ".fat" 8.8514488900366448;
	setAttr -k on ".fatY" 0.64999999999999991;
	setAttr -k on ".fatZ";
createNode joint -n "Scapula" -p "Chest";
	rename -uid "3AAB6DAD-4370-1F39-C22F-489544484B38";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.65 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 4.7058995826738226 -0.80794403451436303 -1.6352441222125997 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 38.842183020579839 80.247256168881407 42.33554186947611 ;
	setAttr ".otp" -type "string" "PropA1";
	setAttr -k on ".fat" 3.3843775167787173;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Shoulder" -p "Scapula";
	rename -uid "69BF24DC-4EC1-6B30-D365-D280A42B2D2D";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "twistJoints" -ln "twistJoints" -dv 2 -min 0 -max 10 
		-at "long";
	addAttr -ci true -k true -sn "bendyJoints" -ln "bendyJoints" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 4.8713115118142074 8.8817841970012523e-16 0 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -2.6115468817738678e-14 8.2988312129135355 -9.1506851688212265 ;
	setAttr ".pa" -type "double3" -4.1293130717023516e-07 0 0 ;
	setAttr ".dl" yes;
	setAttr ".typ" 10;
	setAttr -k on ".fat" 3.3843775167787173;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Elbow" -p "Shoulder";
	rename -uid "669A79A3-4C28-C24D-D7EC-B1BA754BF9EB";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "twistJoints" -ln "twistJoints" -dv 2 -min 0 -max 10 
		-at "long";
	addAttr -ci true -k true -sn "bendyJoints" -ln "bendyJoints" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 16.396299349487428 -0.0092558865007914999 -0.0021997085828836579 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -5.1684013573782151e-15 -1.3666445896913547e-16 4.829290626460141 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "22";
	setAttr -k on ".fat" 2.3430305885391109;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Wrist" -p "Elbow";
	rename -uid "09CD3300-4974-FB65-F5B6-BABAB456860E";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "freeOrient" -ln "freeOrient" -dv 1 -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 13.465194796525831 0.09147652649164538 0.0022006214256413349 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.5841237403368404 -0.10639693200210369 -0.98779569411650781 ;
	setAttr ".dl" yes;
	setAttr ".typ" 12;
	setAttr -k on ".fat" 0.88514488900366384;
	setAttr -k on ".fatY" 2.3100000000000005;
	setAttr -k on ".fatZ";
createNode joint -n "MiddleFinger1" -p "Wrist";
	rename -uid "E272554A-4CE6-979A-F7E5-17A7A6C062FA";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 5.0414003881031135 0.17206310110628431 0.51114053177097674 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.786819765717233 2.628165005958309 -0.83415935074787695 ;
	setAttr ".pa" -type "double3" -2.490303168013669e-17 3.8068719241856406 -4.0949047407001542 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "21";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "MiddleFinger2" -p "MiddleFinger1";
	rename -uid "5857EB9E-4B99-DB0B-F150-529587E5B0BE";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.9096180337497302 -5.773159728050814e-15 -2.9842794901924208e-13 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.0016089467944019834 -0.57528121283282108 -0.011166219201679638 ;
	setAttr ".pa" -type "double3" 0 0 2.5199999009299203 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "20";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "MiddleFinger3" -p "MiddleFinger2";
	rename -uid "074B5F3D-4E12-AD3F-6FF2-31B644DC87DE";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.7800786408907072 -3.7747582837255322e-15 1.4210854715202004e-13 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.82353990199076932 12.460351000636459 0.42404629689927081 ;
	setAttr ".pa" -type "double3" 0 0 3.6712939054552742 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "19";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "MiddleFinger4" -p "MiddleFinger3";
	rename -uid "EE3644E4-4869-4850-E340-9EBACA064BB5";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.11999999999999991 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.3570158478737788 -4.4408920985006262e-16 -4.2632564145606011e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -9.3945031954113177e-15 -1.1607065407886847 -0.18155029906273373 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "18";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "ThumbFinger1" -p "Wrist";
	rename -uid "847F4324-4797-799D-10EB-C5A063817BDE";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.1273613282665522 1.4899549521501601 -0.076160740043064834 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -56.891805499787289 15.355000172902614 33.284981999939028 ;
	setAttr ".pa" -type "double3" -34.462082586865911 -8.7285733235282201 -1.7903981777634761 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "4";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "ThumbFinger2" -p "ThumbFinger1";
	rename -uid "7C36D16C-48C5-218A-4689-4B8C8269B92D";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.7561155185542212 -1.1368683772161603e-13 -1.7763568394002505e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -2.7167775435534578 13.148996957926951 -8.7283111651375727 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "3";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "ThumbFinger3" -p "ThumbFinger2";
	rename -uid "20775B32-4314-57E8-19AD-3D9E29CA526F";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 2.1300533483648287 8.5265128291212022e-14 3.907985046680551e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -4.218728457181423 16.030459170885816 -6.2362287747816092 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "2";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "ThumbFinger4" -p "ThumbFinger3";
	rename -uid "BCAE25F8-4776-CF20-75D7-BBBDCF1C5239";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.11999999999999991 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.3922899379143203 0 -3.5527136788005009e-15 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 -2.3766289632854027 -2.2458878892116996 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "1";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "IndexFinger1" -p "Wrist";
	rename -uid "734B6A6C-455F-3A63-EE71-B0B0485882F8";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 4.9940725702650042 1.4705252457033002 0.42708191552915764 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.86596435513329806 2.5751882784955948 1.9796584406144879 ;
	setAttr ".pa" -type "double3" 0.065532877363568762 20.527688987272207 -2.5422327562497964 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "8";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "IndexFinger2" -p "IndexFinger1";
	rename -uid "F00FD7F8-4A86-EEE6-58F4-B9B17B24F919";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.8958459870956688 -3.1086244689504383e-15 9.9475983006414026e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.089227135094746529 1.3526299957600048 0.03285723294409762 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "7";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "IndexFinger3" -p "IndexFinger2";
	rename -uid "AF143C46-41E6-4B6E-612F-BE8FE3052CFC";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.7018676030744118 -2.6645352591003757e-15 1.4210854715202004e-13 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -2.0318494547103891 2.0445772399183455 -0.4421515087877913 ;
	setAttr ".pa" -type "double3" 0 0 5.7600000490223469 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "6";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "IndexFinger4" -p "IndexFinger3";
	rename -uid "CC172B7E-43A0-1ABB-3E34-B09500091158";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.11999999999999991 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.206572157857039 2.6645352591003757e-15 -1.4210854715202004e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -7.1819163909797065e-15 4.8455818306589196 0.77466227044400993 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "5";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Cup" -p "Wrist";
	rename -uid "5613728D-4F44-6203-8874-0780C82A9C7F";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.0527322386344835 -0.53378469589215127 0.080510004876288122 ;
	setAttr ".r" -type "double3" 1.6151254241821488e-15 -4.81093692594468e-13 -3.4691612882098432e-13 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.070384563939273809 -5.021294631704917 0.80410382342427889 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "17";
	setAttr -k on ".fat" 0.62480815694376313;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "PinkyFinger1" -p "Cup";
	rename -uid "FDD99309-46CB-8A29-6827-F8AF4A7B48C2";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 3.7071185602069079 -1.801943932892708 -0.51426848136063086 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -4.101179108637643 9.0814234814350723 -3.5241087211710878 ;
	setAttr ".pa" -type "double3" -0.21586850671656455 -15.856897343794616 -7.9762775885025459 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "12";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "PinkyFinger2" -p "PinkyFinger1";
	rename -uid "21C1B16B-4C72-23E9-5E37-E68B3404ACB9";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.6217384760383737 -3.5527136788005009e-15 1.4210854715202004e-13 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.27569141151243326 1.8974817288736447 -0.59989087772802452 ;
	setAttr ".pa" -type "double3" 0 0 0.71999997359174039 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "11";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "PinkyFinger3" -p "PinkyFinger2";
	rename -uid "4E818891-44A9-3932-15E1-DE993202F26B";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.3075790527134572 2.6645352591003757e-15 9.9475983006414026e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 2.2723505682222913 7.8159216996053402 0.8805766958540393 ;
	setAttr ".pa" -type "double3" 0 0 5.7599997887354624 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "10";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "PinkyFinger4" -p "PinkyFinger3";
	rename -uid "EBC91BBF-4F06-6929-2389-6B82CA21374F";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.11999999999999991 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 0.98936702360622419 -2.6645352591003757e-15 -4.2632564145606011e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.1331715562890586e-14 -0.75718689842663212 -0.38414609643250081 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "9";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "RingFinger1" -p "Cup";
	rename -uid "DCA8BC09-4164-2A2C-6BD0-92B1C108FE72";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 4.020766381390942 -0.64970454286571178 -0.079831321118334131 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -1.4043036735462024 10.49900459244248 -2.6971919819548726 ;
	setAttr ".pa" -type "double3" -0.07133019936876682 -2.835223641928581 -1.4417652325251511 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "16";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "RingFinger2" -p "RingFinger1";
	rename -uid "1227AF54-4620-E767-E97C-FEACCF4A2051";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.6314301111866527 -2.6645352591003757e-15 -4.2632564145606011e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -0.28341319068608212 -0.23215132997587004 -0.0059797259624334133 ;
	setAttr ".pa" -type "double3" 0 0 -2.1600000310934706 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "15";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "RingFinger3" -p "RingFinger2";
	rename -uid "11E1D099-42F3-4D48-AA45-9F8A5DC4AFC7";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.4936784227923567 1.3322676295501878e-15 7.1054273576010019e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0.68782922334351959 4.4479727739972423 1.3685032453412018 ;
	setAttr ".pa" -type "double3" 0 0 4.3200001190538568 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "14";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "RingFinger4" -p "RingFinger3";
	rename -uid "13CF6DF6-4469-4835-3E3C-F9B90F5F4830";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.11999999999999991 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.2327202080026254 -1.3322676295501878e-15 -1.4210854715202004e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -1.9091647786347582e-14 1.6915524387540488 -1.1942976994865442 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "13";
	setAttr -k on ".fat" 0.62480815694376268;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Neck" -p "Chest";
	rename -uid "66346B9D-4D5B-986F-5307-23BE08D78060";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "inbetweenJoints" -ln "inbetweenJoints" -dv 2 -min 
		0 -max 10 -at "long";
	addAttr -ci true -k true -sn "unTwister" -ln "unTwister" -dv 1 -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 6.7440400309615143 -1.2281937265599259 3.4232327315268892e-14 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -3.7584967318768006e-17 -1.3354349759807613e-14 6.2314965278806564 ;
	setAttr ".pa" -type "double3" -1.7940447748746266e-16 6.8425179703803005e-15 0 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "0";
	setAttr -k on ".fat" 1.6661550851833684;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
	setAttr -k on ".inbetweenJoints" 1;
createNode joint -n "Head" -p "Neck";
	rename -uid "E2742812-443B-A2A1-5329-C083CC94B78F";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "global" -ln "global" -min 0 -max 10 -at "long";
	setAttr ".t" -type "double3" 8.2435811169478779 -0.039637314043909404 1.2076509120155104e-14 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -5.4891994589471507 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "1";
	setAttr -k on ".fat" 1.6661550851833684;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Eye" -p "Head";
	rename -uid "E01A0452-4779-0B61-15F0-3F9347EBEB40";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "aim" -ln "aim" -dv 1 -min 0 -max 1 -at "bool";
	addAttr -ci true -k true -sn "noFlip" -ln "noFlip" -dv 1 -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" 4.6079861498927954 7.1984790173145523 -1.7529048523159143 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 2.8249000307521015e-30 -1.4124500153760508e-30 89.999999999999986 ;
	setAttr ".pa" -type "double3" 8.9959671327899885e-14 -89.999999999998849 0 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "Eye";
	setAttr -k on ".fat" 1.0413469282396051;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "EyeEnd" -p "Eye";
	rename -uid "33820E71-44E0-9235-0EDE-0FA7CD514BE0";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.19999999999999996 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 0.88967558705765271 -4.2632564145606011e-14 5.3290705182007514e-15 ;
	setAttr ".r" -type "double3" 15.943578395557601 -0.25535337936060021 0.054080155178905319 ;
	setAttr ".ro" 1;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 5.7055094273191919e-15 -2.5444437451708134e-14 1.1131941385122302e-14 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "24";
	setAttr -k on ".fat" 1.0413469282396051;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Jaw" -p "Head";
	rename -uid "82CB12A9-403E-EAE4-47F7-239959CB5B9E";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 1.2109006650584604 1.1786011110827828 -3.1078430592159913e-15 ;
	setAttr -l on ".tz";
	setAttr ".r" -type "double3" 9.5674180608276428e-15 5.1268157251392607e-15 5.0888874903416268e-14 ;
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 123.62966882150303 ;
	setAttr ".otp" -type "string" "31";
	setAttr ".radi" 0.5;
	setAttr -k on ".fat" 1.0413469282396051;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "JawEnd" -p "Jaw";
	rename -uid "F2C80A78-4901-3005-7DDA-5BBDE47CDA19";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.19999999999999996 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 7.3575215744868885 1.4210854715202004e-14 -6.5834966600843265e-16 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.6269323370872225e-14 -3.5471046450181591e-15 0 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "25";
	setAttr -k on ".fat" 1.0413469282396051;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "HeadEnd" -p "Head";
	rename -uid "84C24364-4F88-5819-13DA-C6B747834E9D";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 13.217962659234914 1.1546319456101628e-14 3.5065151025226053e-15 ;
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 0 0 -1.5902773407317584e-15 ;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "23";
	setAttr -k on ".fat" 1.8223571244193091;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Hip" -p "Root";
	rename -uid "2E09F289-4B80-B42F-4FFA-72ADB333E7AA";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "twistJoints" -ln "twistJoints" -dv 2 -min 0 -max 10 
		-at "long";
	addAttr -ci true -k true -sn "bendyJoints" -ln "bendyJoints" -min 0 -max 1 -at "bool";
	setAttr ".t" -type "double3" -3.9673347473144389 -2.7880966958778978e-05 -4.8076391220092791 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.8125258804530537 179.97569125048855 1.4109855217351779 ;
	setAttr ".dl" yes;
	setAttr ".typ" 2;
	setAttr -k on ".fat" 4.5298591378422826;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Knee" -p "Hip";
	rename -uid "FC61B565-462B-C7C5-4529-9BAC48E1A2D2";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 22.183233434763245 3.4972025275692431e-14 1.0658141036401503e-14 ;
	setAttr ".ro" 2;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -9.9392333795734871e-15 -8.1377473295257943e-15 -1.6144183055831691 ;
	setAttr -k on ".fat" 3.1240407847188156;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Ankle" -p "Knee";
	rename -uid "BC5D9D63-4978-CB8C-9112-B98CEFE82054";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	addAttr -ci true -k true -sn "worldOrient" -ln "worldOrient" -min 0 -max 5 -en "xUp:yUp:zUp:xDown:yDown:zDown" 
		-at "enum";
	setAttr ".t" -type "double3" 20.153472616257758 6.4837024638109142e-14 -6.2172489379008766e-15 ;
	setAttr ".ro" 3;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -1.8113321901927908 0.068913164858595735 3.0239298777806614 ;
	setAttr ".pa" -type "double3" 3.1147589914174403 -1.2104724556304993 -11.405913270501992 ;
	setAttr ".dl" yes;
	setAttr ".typ" 4;
	setAttr -k on ".fat" 1.926491817243269;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
	setAttr -k on ".worldOrient" 3;
createNode joint -n "Heel" -p "Ankle";
	rename -uid "A38EBD2D-4E61-7C04-CE62-E09D72B1A672";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.36999999999999988 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 3.8433985114097555 -2.4786556708879246 0.030732266096351601 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 1.1927080055488192e-15 1.9170293712843516e-14 -3.2760801143662344e-15 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "Heel";
	setAttr -k on ".fat" 1.926491817243269;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "Toes" -p "Ankle";
	rename -uid "27CBE467-4F63-07D6-F9AD-9BB8929C7E6A";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 3.154643595218654 5.8551265001316501 6.1284310959308641e-14 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" 4.6661257553496399e-05 4.66612573647174e-05 90 ;
	setAttr ".pa" -type "double3" -0.00019030234564052423 0.00053514845282692043 25.864574245063647 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "Toes";
	setAttr -k on ".fat" 1.5620203923594076;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "FootSideInner" -p "Toes";
	rename -uid "3E2BD2F2-405B-3A05-A2B9-388D794CC07B";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.29999999999999993 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 0.29390382766722745 -0.93664613446800216 -2.4185170651908066 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -2.4265706493099007e-20 8.3489346432794349e-15 -1.8822787391431398e-14 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "BigToe";
	setAttr -k on ".fat" 1.5620203923594076;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "FootSideOuter" -p "Toes";
	rename -uid "2EFC3F12-4F12-AE91-1C37-0EA774C21A9B";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.29999999999999993 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 0.29393911361694336 -0.9362332900207736 2.5141408915516417 ;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -2.4265706493099007e-20 8.3489346432794349e-15 -1.8822787391431398e-14 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "PinkyToe";
	setAttr -k on ".fat" 1.5620203923594076;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode joint -n "ToesEnd" -p "Toes";
	rename -uid "39682BAE-49D4-A5A3-45D1-5083314AF73C";
	addAttr -ci true -k true -sn "fat" -ln "fat" -dv 0.29999999999999993 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatY" -ln "fatY" -dv 1 -min 0 -at "double";
	addAttr -ci true -k true -sn "fatZ" -ln "fatZ" -dv 1 -min 0 -at "double";
	addAttr -ci true -sn "fatYabs" -ln "fatYabs" -at "double";
	addAttr -ci true -sn "fatZabs" -ln "fatZabs" -at "double";
	setAttr ".t" -type "double3" 4.905842304229731 -5.5511151231257827e-16 -3.5527136788005009e-15 ;
	setAttr ".ro" 5;
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
	setAttr ".jo" -type "double3" -2.4265706493099019e-20 1.9878252803545021e-15 -1.8822782210991101e-14 ;
	setAttr ".dl" yes;
	setAttr ".typ" 18;
	setAttr ".otp" -type "string" "ToesEnd";
	setAttr -k on ".fat" 1.5620203923594076;
	setAttr -k on ".fatY";
	setAttr -k on ".fatZ";
createNode transform -s -n "persp";
	rename -uid "6BE635B5-4434-9674-98FF-059780957A22";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 11.769100450364389 83.04453380036631 77.819550224674629 ;
	setAttr ".r" -type "double3" -22.538352730582204 8.5999999999997865 -2.0104514256684168e-16 ;
createNode camera -s -n "perspShape" -p "persp";
	rename -uid "2726B0CB-45B6-050C-DEBF-22B973EB28B6";
	setAttr -k off ".v" no;
	setAttr ".fl" 34.999999999999993;
	setAttr ".coi" 85.212753825505644;
	setAttr ".imn" -type "string" "persp";
	setAttr ".den" -type "string" "persp_depth";
	setAttr ".man" -type "string" "persp_mask";
	setAttr ".tp" -type "double3" 0 50.38233405899939 0 ;
	setAttr ".hc" -type "string" "viewSet -p %camera";
createNode transform -s -n "top";
	rename -uid "41BC161D-4F15-D035-7D89-7999F163D6F6";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -41.803405315080624 1002.8234754638605 -1.297188496426311 ;
	setAttr ".r" -type "double3" -89.999999999999986 0 0 ;
createNode camera -s -n "topShape" -p "top";
	rename -uid "AFD6C3DF-4178-C477-5623-00808E1D0D54";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 931.59558425675812;
	setAttr ".ow" 15.713148786926046;
	setAttr ".imn" -type "string" "top";
	setAttr ".den" -type "string" "top_depth";
	setAttr ".man" -type "string" "top_mask";
	setAttr ".tp" -type "double3" -42.085886307431295 71.227891207102402 0.18168258117405012 ;
	setAttr ".hc" -type "string" "viewSet -t %camera";
	setAttr ".o" yes;
createNode transform -s -n "front";
	rename -uid "B0891093-4789-07B4-5E6E-0CB8362A80E7";
	setAttr ".v" no;
	setAttr ".t" -type "double3" -0.87645242615790764 84.090209017436649 1005.6825796284137 ;
createNode camera -s -n "frontShape" -p "front";
	rename -uid "C62AC874-4F76-AC22-8ADE-689D186C0264";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1002.2048529319266;
	setAttr ".ow" 4.9386989935018271;
	setAttr ".imn" -type "string" "front";
	setAttr ".den" -type "string" "front_depth";
	setAttr ".man" -type "string" "front_mask";
	setAttr ".tp" -type "double3" -0.87645242615790764 84.090209017436649 3.4777266964871387 ;
	setAttr ".hc" -type "string" "viewSet -f %camera";
	setAttr ".o" yes;
createNode transform -s -n "side";
	rename -uid "D2F32F32-41FF-C193-A082-B8AE13C15DD0";
	setAttr ".v" no;
	setAttr ".t" -type "double3" 1003.485310982108 67.420260536077762 -6.5584911339872702e-06 ;
	setAttr ".r" -type "double3" 0 89.999999999999986 0 ;
createNode camera -s -n "sideShape" -p "side";
	rename -uid "A7E01B0E-4BB6-27E6-22A3-DBB07C56CA35";
	setAttr -k off ".v" no;
	setAttr ".rnd" no;
	setAttr ".coi" 1003.485310982108;
	setAttr ".ow" 71.936110077609612;
	setAttr ".imn" -type "string" "side";
	setAttr ".den" -type "string" "side_depth";
	setAttr ".man" -type "string" "side_mask";
	setAttr ".tp" -type "double3" -4.8849813083506888e-15 67.428803065125322 -5.9396931817445875e-15 ;
	setAttr ".hc" -type "string" "viewSet -s %camera";
	setAttr ".o" yes;
createNode transform -n "cn_master_ctl";
	rename -uid "46AE77CC-424F-DDA6-879C-8D9A65EA36BC";
	setAttr -l on ".v";
	setAttr ".ovs" no;
	setAttr ".ove" yes;
	setAttr ".ovrgbf" yes;
	setAttr ".ovrgb" -type "float3" 255 255 0 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "cn_master_ctlShape" -p "cn_master_ctl";
	rename -uid "FB7A09C8-4A35-6CB3-D46D-15A46FB3F78E";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		3 86 0 no 3
		91 15.745750770000001 15.745750770000001 15.745750770000001 15.994336930000005
		 15.994336930000005 15.994336930000005 16.994336930000003 16.994336930000003 16.994336930000003
		 17.994336930000003 17.994336930000003 17.994336930000003 18.994336930000003 18.994336930000003
		 18.994336930000003 19.994336930000003 19.994336930000003 19.994336930000003 20.253014204999999
		 20.253014204999999 20.253014204999999 20.885202119999999 21.502214874 21.502214874
		 21.502214874 21.758286319 21.758286319 21.758286319 22.758286319 22.758286319 22.758286319
		 23.758286319 23.758286319 23.758286319 24.758286319 24.758286319 24.758286319 25.758286319
		 25.758286319 25.758286319 26.014851714999999 26.014851714999999 26.014851714999999
		 26.633484611 27.244006168999999 27.244006168999999 27.244006168999999 27.495894292999999
		 27.495894292999999 27.495894292999999 28.495894292999999 28.495894292999999 28.495894292999999
		 29.495894292999999 29.495894292999999 29.495894292999999 30.495894292999999 30.495894292999999
		 30.495894292999999 31.495894292999999 31.495894292999999 31.495894292999999 31.758026582999999
		 31.758026582999999 31.758026582999999 32.371381249000002 32.991210664 32.991210664
		 32.991210664 33.247937673999999 33.247937673999999 33.247937673999999 34.247937673999999
		 34.247937673999999 34.247937673999999 35.247937673999999 35.247937673999999 35.247937673999999
		 36.247937673999999 36.247937673999999 36.247937673999999 37.247937673999999 37.247937673999999
		 37.247937673999999 37.502186903999998 37.502186903999998 37.502186903999998 38.121090553499997
		 38.742038981499995 38.742038981499995 38.742038981499995
		89
		-16.982879132509684 1.3789593819674466e-15 -5.2186904469554278
		-18.2801733509469 1.3789593819674466e-15 -5.2186904469554278
		-19.577467569384236 2.0684390729511708e-15 -5.2186904469554278
		-20.874761787821587 2.0684390729511708e-15 -5.2186904469554278
		-20.874761787821587 2.0684390729511708e-15 -6.9582539292739378
		-20.874761787821587 3.4473984549186166e-16 -8.6978174115923323
		-20.874761787821587 1.3789593819674466e-15 -10.437380893910738
		-24.353888752458527 3.4473984549186143e-15 -6.9582539292739378
		-27.833015717095439 3.4473984549186143e-15 -3.4791269646369147
		-31.312142681732357 5.8605773733616494e-15 1.7236992274593083e-16
		-27.833015717095439 6.2053172188535107e-15 3.4791269646369147
		-24.353888752458527 6.2053172188535107e-15 6.9582539292738295
		-20.874761787821587 7.584276600820951e-15 10.437380893910738
		-20.874761787821587 5.8605773733616494e-15 8.6978174115923395
		-20.874761787821587 6.2053172188535107e-15 6.9582539292738295
		-20.874761787821587 4.8263578368860633e-15 5.2186904469553168
		-19.524805163934616 4.8263578368860633e-15 5.2186904469553168
		-18.174848540047662 4.1368781459023415e-15 5.2186904469553168
		-16.970587039561376 6.8947969098372332e-16 5.040057418535107
		-16.126975844063189 3.4473984549186143e-15 7.8503401808534257
		-13.108983524796516 4.8263578368860633e-15 13.00964654306417
		-7.9753774208335919 6.2053172188535107e-15 16.053339120578553
		-5.2186904469553133 4.8263578368860633e-15 16.865688976542831
		-5.2186904469553133 3.4473984549186143e-15 18.202046580302508
		-5.2186904469553133 6.2053172188535107e-15 19.53840418406195
		-5.2186904469553133 3.4473984549186143e-15 20.874761787821587
		-6.9582539292739378 3.4473984549186143e-15 20.874761787821587
		-8.6978174115923395 6.2053172188535107e-15 20.874761787821587
		-10.437380893910738 6.2053172188535107e-15 20.874761787821587
		-6.9582539292739378 3.4473984549186143e-15 24.353888752458527
		-3.4791269646369147 1.1721154746723299e-14 27.833015717095439
		5.2652791965291126e-17 5.8605773733616494e-15 31.312142681732357
		3.4791269646369147 1.1721154746723299e-14 27.833015717095439
		6.9582539292738295 3.4473984549186166e-16 24.353888752458527
		10.437380893910738 3.4473984549186143e-15 20.874761787821587
		8.6978174115923395 3.4473984549186143e-15 20.874761787821587
		6.9582539292738295 3.4473984549186143e-15 20.874761787821587
		5.2186904469553133 3.4473984549186143e-15 20.874761787821587
		5.2186904469553133 2.7579187639348933e-15 19.535826406697069
		5.2186904469553133 1.3789593819674466e-15 18.196891025572555
		5.220548701350074 7.584276600820951e-15 16.915380737333049
		7.9620578737593499 4.8263578368860633e-15 16.061230553243984
		13.015983600645372 4.8263578368860633e-15 13.069080621146927
		16.021650240680184 3.4473984549186143e-15 8.0286716021986599
		16.931183348560658 -2.7579187639348933e-15 5.2186904469553186
		18.24570949498094 -3.1026586094267554e-15 5.2186904469553186
		19.560235641401341 -4.1368781459023415e-15 5.2186904469553186
		20.874761787821587 -4.1368781459023415e-15 5.2186904469553186
		20.874761787821587 -3.1026586094267554e-15 6.9582539292738295
		20.874761787821587 -1.3789593819674466e-15 8.6978174115923323
		20.874761787821587 -2.7579187639348933e-15 10.437380893910738
		24.353888752458527 -4.1368781459023415e-15 6.9582539292738295
		27.833015717095439 -5.8605773733616494e-15 3.4791269646369147
		31.312142681732357 -6.5500570643453736e-15 1.7236992274593083e-16
		27.833015717095439 -7.584276600820951e-15 -3.4791269646369147
		24.353888752458527 -6.5500570643453736e-15 -6.9582539292738295
		20.874761787821587 -8.2737562918046831e-15 -10.437380893910738
		20.874761787821587 -6.5500570643453736e-15 -8.6978174115923395
		20.874761787821587 -6.5500570643453736e-15 -6.9582539292738295
		20.874761787821587 -6.5500570643453736e-15 -5.2186904469553168
		19.506774510160064 -6.5500570643453736e-15 -5.2186904469553168
		18.138787232498544 -6.2053172188535107e-15 -5.2186904469553168
		16.893375421803309 -3.1026586094267554e-15 -5.2906776775597626
		16.035495027244892 -4.1368781459023415e-15 -8.0054251977516664
		13.024711249961907 -6.5500570643453736e-15 -13.067095118122149
		7.9522164563653535 -9.6527156737721265e-15 -16.067054022179164
		5.2186904469553133 -5.8605773733616494e-15 -16.855425404134376
		5.2186904469553133 -4.8263578368860633e-15 -18.195204198696786
		5.2186904469553133 -1.1721154746723299e-14 -19.534982993259199
		5.2186904469553133 -4.8263578368860633e-15 -20.874761787821587
		6.9582539292739378 -4.8263578368860633e-15 -20.874761787821587
		8.6978174115923395 -7.584276600820951e-15 -20.874761787821587
		10.437380893910738 -7.584276600820951e-15 -20.874761787821587
		6.9582539292739378 -4.8263578368860633e-15 -24.35388875245852
		3.4791269646369147 -1.1721154746723299e-14 -27.833015717095439
		5.2652791965291126e-17 -6.5500570643453736e-15 -31.312142681732357
		-3.4791269646369147 -1.1721154746723299e-14 -27.833015717095439
		-6.9582539292738295 -1.3789593819674466e-15 -24.353888752458527
		-10.437380893910738 -5.8605773733616494e-15 -20.874761787821587
		-8.6978174115923395 -5.8605773733616494e-15 -20.874761787821587
		-6.9582539292738295 -5.8605773733616494e-15 -20.874761787821587
		-5.2186904469553133 -5.8605773733616494e-15 -20.874761787821587
		-5.2186904469553133 -4.8263578368860633e-15 -19.54791376007487
		-5.2186904469553133 -4.1368781459023415e-15 -18.221065732328157
		-5.2186904469553133 -3.1026586094267554e-15 -16.894217704581301
		-7.9598312550386554 -6.5500570643453736e-15 -16.062548652827605
		-13.058197608849531 -5.8605773733616494e-15 -13.044812437878297
		-16.072496755866016 -4.1368781459023415e-15 -7.9430090161346492
		-16.924944542617368 -3.1026586094267554e-15 -5.1897561405409425
		;
createNode transform -n "cn_masterOffset_ctl" -p "cn_master_ctl";
	rename -uid "788F6254-4BAB-8634-4C24-05ADEEA378E2";
	setAttr -l on ".v";
	setAttr ".ovs" no;
	setAttr ".ove" yes;
	setAttr ".ovrgbf" yes;
	setAttr ".ovrgb" -type "float3" 255 255 0 ;
	setAttr -l on ".tx";
	setAttr -l on ".ty";
	setAttr -l on ".tz";
	setAttr -l on ".rx";
	setAttr -l on ".ry";
	setAttr -l on ".rz";
	setAttr -l on ".sx";
	setAttr -l on ".sy";
	setAttr -l on ".sz";
createNode nurbsCurve -n "cn_masterOffset_ctlShape" -p "cn_masterOffset_ctl";
	rename -uid "02E25D10-4F56-364F-A333-B6A8E6D96656";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 10 0 no 3
		11 0 1 2 3 4 5 6 7 8 9 10
		11
		11.412092582037292 0 -11.412765654211727
		16.139738997755927 0 0
		11.412092582037292 0 11.412765654211727
		-0.00067307217443294816 0 16.140412069930356
		-11.390135478495973 0 11.412765654211727
		-16.138172236118514 0 0
		-11.390135478495973 0 -11.412765654211727
		-0.00067307217443294816 0 -16.140412069930356
		11.412092582037292 0 -11.412765654211727
		16.139738997755927 0 0
		11.412092582037292 0 11.412765654211727
		;
createNode transform -n "cn_body_ctl";
	rename -uid "0503667C-419B-9F56-D2B0-6E82BDF213C7";
	setAttr ".ovs" no;
	setAttr ".ove" yes;
	setAttr ".ovrgbf" yes;
	setAttr ".ovrgb" -type "float3" 0 255 255 ;
	setAttr ".t" -type "double3" 1.0262204379053426e-15 50.375 2.7880967536475509e-05 ;
createNode nurbsCurve -n "cn_body_ctlShape" -p "cn_body_ctl";
	rename -uid "2454DC1F-445C-4304-8C0B-D3BC5B089514";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 4 0 no 3
		5 0 1 2 3 4
		5
		16.866143433447526 -2.6481404611934811e-15 -3.9722106917902218e-15
		1.3240702305967405e-15 2.6481404611934811e-15 16.866143433447526
		-16.866143433447526 2.6481404611934811e-15 3.9722106917902218e-15
		-1.3240702305967405e-15 -2.6481404611934811e-15 -16.866143433447526
		16.866143433447526 -2.6481404611934811e-15 -3.9722106917902218e-15
		;
createNode transform -n "cn_cog_ctl" -p "cn_body_ctl";
	rename -uid "5DEB64BB-4A8E-4B6C-7B89-C8A2CA268E0D";
	setAttr ".ovs" no;
	setAttr ".ove" yes;
	setAttr ".ovrgbf" yes;
	setAttr ".ovrgb" -type "float3" 0 255 255 ;
createNode nurbsCurve -n "cn_cog_ctlShape" -p "cn_cog_ctl";
	rename -uid "7A1D2BCC-4BFF-EFF9-2690-F2BBF77F5CDD";
	setAttr -k off ".v";
	setAttr ".cc" -type "nurbsCurve" 
		1 25 0 no 3
		26 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
		26
		-2.7928117713047307 0 -2.7051722356501733
		-2.7928117713047307 0 -8.3471457536527325
		-2.7928117713047307 0 -8.3471457536527325
		-5.5321004705568235 0 -8.2981507058352353
		0 0 -13.830251176392089
		5.5321004705568235 0 -8.2981507058352353
		2.7660502352784118 0 -8.2981507058352353
		2.7660502352784118 0 -2.7660502352784118
		8.2981507058352353 0 -2.7660502352784118
		8.2981507058352353 0 -5.5321004705568235
		13.830251176392089 0 0
		8.2981507058352353 0 5.5321004705568235
		8.2981507058352353 0 2.7660502352784118
		2.7660502352784118 0 2.7660502352784118
		2.7660502352784118 0 8.2981507058352353
		5.5321004705568235 0 8.2981507058352353
		0 0 13.830251176392089
		-5.5321004705568235 0 8.2981507058352353
		-2.7660502352784118 0 8.2981507058352353
		-2.7660502352784118 0 2.7660502352784118
		-8.2981507058352353 0 2.7660502352784118
		-8.2981507058352353 0 5.5321004705568235
		-13.830251176392089 0 0
		-8.2981507058352353 0 -5.5321004705568235
		-8.2981507058352353 0 -2.7660502352784118
		-2.7660502352784118 0 -2.7660502352784118
		;
createNode joint -n "cn_root_jnt";
	rename -uid "A6D3A756-4806-C3AF-6E3C-C090E52C36DB";
	setAttr ".mnrl" -type "double3" -360 -360 -360 ;
	setAttr ".mxrl" -type "double3" 360 360 360 ;
createNode animCurveUA -n "SDK1FKPinkyFinger1_R_rotateZ";
	rename -uid "77B48672-4A5D-1647-7906-F0A74CECB9DC";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "spread" -ln "spread" -smn -5 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -5 29.999999999999996 0 0 10 -59.999999999999993;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKIndexFinger1_R_rotateZ";
	rename -uid "E5B31922-4EDA-0D43-CE74-4C82B5789DCE";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "spread" -ln "spread" -smn -5 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -5 -20 0 0 10 40;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKRingFinger1_R_rotateZ";
	rename -uid "DB1DAADD-496B-BC8E-F308-459756DF9E5F";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "spread" -ln "spread" -smn -5 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -5 14.999999999999998 0 0 10 -29.999999999999996;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKCup_R_rotateX";
	rename -uid "536C38A5-4369-7DD1-987F-D2A11096535C";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "cup" -ln "cup" -smn 0 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  0 0 10 65;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKIndexFinger3_R_rotateY";
	rename -uid "874BB5AE-461B-FD87-8EF2-B6BA88D6A2DF";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "indexCurl" -ln "indexCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKIndexFinger2_R_rotateY";
	rename -uid "9BB6B382-4A68-3B9C-AB4B-FFA0A34496D0";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "indexCurl" -ln "indexCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK2FKIndexFinger1_R_rotateY";
	rename -uid "3C199B4F-4407-B202-139B-FFB3E7840CE2";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "indexCurl" -ln "indexCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  0.98788672685623169 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0.15517689287662506 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 0.98788672685623169;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0.15517689287662506;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKMiddleFinger1_R_rotateY";
	rename -uid "F1F5D673-4450-53F1-1FF6-A08EB0B2753E";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "middleCurl" -ln "middleCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKMiddleFinger3_R_rotateY";
	rename -uid "692B44A7-4A8F-8852-82F9-B0824FD1A203";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "middleCurl" -ln "middleCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKMiddleFinger2_R_rotateY";
	rename -uid "C4CCF49A-4340-2BB1-A62B-FABA3B5F1D88";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "middleCurl" -ln "middleCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKRingFinger3_R_rotateY";
	rename -uid "B6D45516-4148-7545-1ECC-7BB8909FA66B";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "ringCurl" -ln "ringCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKRingFinger2_R_rotateY";
	rename -uid "9487EE3F-4627-88EC-2200-638135F3369D";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "ringCurl" -ln "ringCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK2FKRingFinger1_R_rotateY";
	rename -uid "11B78D45-4F6E-A40B-FA8B-DDB0F626C205";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "ringCurl" -ln "ringCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK2FKPinkyFinger1_R_rotateY";
	rename -uid "B132B0D7-41AA-E31B-101E-66A226E70E18";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "pinkyCurl" -ln "pinkyCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKPinkyFinger2_R_rotateY";
	rename -uid "128FE326-4DB8-8A1A-BAF9-A4853B50DC36";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "pinkyCurl" -ln "pinkyCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKPinkyFinger3_R_rotateY";
	rename -uid "54E8A7E7-4D1A-5827-8E84-069E643EF0A0";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "pinkyCurl" -ln "pinkyCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKThumbFinger2_R_rotateY";
	rename -uid "A766C0EC-409C-5A99-FB5F-C8A957475850";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "thumbCurl" -ln "thumbCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKThumbFinger3_R_rotateY";
	rename -uid "07D626D5-43AD-47DF-4929-C9897FFEB270";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "thumbCurl" -ln "thumbCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 1;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr -s 3 ".kit[0:2]"  2 1 1;
	setAttr -s 3 ".kot[0:2]"  2 1 1;
	setAttr -s 3 ".kix[1:2]"  1 0.98788672685623169;
	setAttr -s 3 ".kiy[1:2]"  0 0.15517690777778625;
	setAttr -s 3 ".kox[1:2]"  0.98788672685623169 1;
	setAttr -s 3 ".koy[1:2]"  0.15517690777778625 0;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKPinkyFinger1_L_rotateZ";
	rename -uid "FB859726-42F9-76D4-3D70-AA851B5E75BB";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "spread" -ln "spread" -smn -5 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -5 29.999999999999996 0 0 10 -59.999999999999993;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKIndexFinger1_L_rotateZ";
	rename -uid "ED47B450-4E87-36EF-3D98-3AA2FE95EA4E";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "spread" -ln "spread" -smn -5 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -5 -20 0 0 10 40;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKRingFinger1_L_rotateZ";
	rename -uid "0AAC0612-4DD6-48F6-41B8-8B93F910AA19";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "spread" -ln "spread" -smn -5 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -5 14.999999999999998 0 0 10 -29.999999999999996;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKCup_L_rotateX";
	rename -uid "7ED79196-4E42-5752-5531-BC8E07B16B80";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "cup" -ln "cup" -smn 0 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 2 ".ktv[0:1]"  0 0 10 65;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKIndexFinger2_L_rotateY";
	rename -uid "0108260A-47AA-1F49-768C-EDA432A4D49A";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "indexCurl" -ln "indexCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKIndexFinger3_L_rotateY";
	rename -uid "E6659E0F-4022-FD74-3F52-CB8CA0684B2A";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "indexCurl" -ln "indexCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK2FKIndexFinger1_L_rotateY";
	rename -uid "400A161E-4C59-138C-0EAB-D8B631DE4766";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "indexCurl" -ln "indexCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKMiddleFinger2_L_rotateY";
	rename -uid "8F09665E-4959-7275-EAAA-149CA752F180";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "middleCurl" -ln "middleCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKMiddleFinger3_L_rotateY";
	rename -uid "D9039EC0-4BDC-2162-16DA-B09E31236669";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "middleCurl" -ln "middleCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKMiddleFinger1_L_rotateY";
	rename -uid "E240C986-4201-DEAE-2C72-278AE5339B2C";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "middleCurl" -ln "middleCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKRingFinger2_L_rotateY";
	rename -uid "7A07FDF7-478E-32F0-CA47-F9BCAD850B92";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "ringCurl" -ln "ringCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKRingFinger3_L_rotateY";
	rename -uid "011EEF9A-4C35-72BD-B3F3-438BB014308D";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "ringCurl" -ln "ringCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK2FKRingFinger1_L_rotateY";
	rename -uid "BACBFE62-455E-42AE-978E-C89EDCF78060";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "ringCurl" -ln "ringCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKPinkyFinger2_L_rotateY";
	rename -uid "7E7E0395-432A-6D39-0678-3D895FCCB13D";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "pinkyCurl" -ln "pinkyCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKPinkyFinger3_L_rotateY";
	rename -uid "96BD74D0-480F-2FEF-AEB5-3FAB3731870B";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "pinkyCurl" -ln "pinkyCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK2FKPinkyFinger1_L_rotateY";
	rename -uid "9418EF68-45CA-6F0F-BB6E-A287F26BC33D";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "pinkyCurl" -ln "pinkyCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKThumbFinger2_L_rotateY";
	rename -uid "26A2DB76-4E04-ABC4-3D46-E79B106A9759";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "thumbCurl" -ln "thumbCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode animCurveUA -n "SDK1FKThumbFinger3_L_rotateY";
	rename -uid "B06B3584-47E6-25FA-D6CF-079A8F206503";
	addAttr -s false -ci true -sn "drivingSystemOut" -ln "drivingSystemOut" -at "message";
	addAttr -ci true -sn "thumbCurl" -ln "thumbCurl" -smn -2 -smx 10 -at "float";
	setAttr ".tan" 2;
	setAttr ".wgt" no;
	setAttr -s 3 ".ktv[0:2]"  -2 -18 0 0 10 90;
	setAttr ".pre" 4;
	setAttr ".pst" 4;
createNode multiplyDivide -n "RootFat";
	rename -uid "26671755-4A8A-0659-6280-26B2A35A4051";
createNode multiplyDivide -n "Spine1Fat";
	rename -uid "F78D659F-4EE8-E50E-0718-E39417B9C848";
createNode multiplyDivide -n "ChestFat";
	rename -uid "BFFE2C60-441E-2EF9-DD81-869F0E1C1B51";
createNode multiplyDivide -n "ScapulaFat";
	rename -uid "C286B331-4CAE-FB07-A890-BABC41F7F350";
createNode multiplyDivide -n "ShoulderFat";
	rename -uid "F38092DC-4838-1320-9412-DCAE45D69406";
createNode multiplyDivide -n "ElbowFat";
	rename -uid "98AA4B9B-48CB-ED54-D86B-8C911E0F5D0C";
createNode multiplyDivide -n "WristFat";
	rename -uid "AB321C0C-4896-6AFF-5995-6780721E3D9F";
createNode multiplyDivide -n "MiddleFinger1Fat";
	rename -uid "66E1B789-4C1F-2056-199B-92847AA2E6A3";
createNode multiplyDivide -n "MiddleFinger2Fat";
	rename -uid "B1008F9B-4DE8-07DE-8191-7B9B0FE1963E";
createNode multiplyDivide -n "MiddleFinger3Fat";
	rename -uid "ABDD6B25-47AB-5D76-88BF-C9BA078DFF90";
createNode multiplyDivide -n "MiddleFinger4Fat";
	rename -uid "C06C346F-4DE9-C8A4-C157-58B3D262E796";
createNode multiplyDivide -n "ThumbFinger1Fat";
	rename -uid "6BD02AAD-4C13-27F4-93BE-BFB72E47575A";
createNode multiplyDivide -n "ThumbFinger2Fat";
	rename -uid "9DB1E559-48AB-24C0-5E0E-82B218396917";
createNode multiplyDivide -n "ThumbFinger3Fat";
	rename -uid "67D75A04-4EF8-6223-AD97-9B8CF72ECB88";
createNode multiplyDivide -n "ThumbFinger4Fat";
	rename -uid "F9B4066C-47A0-F3E1-11C9-A4B125F91D6C";
createNode multiplyDivide -n "IndexFinger1Fat";
	rename -uid "0E318F4B-4513-D642-F8E8-CF829E604FAB";
createNode multiplyDivide -n "IndexFinger2Fat";
	rename -uid "7E7522AB-414D-E939-3221-49BB8D1C0FE0";
createNode multiplyDivide -n "IndexFinger3Fat";
	rename -uid "A0028EFB-4467-B011-1DAB-F3AF4D852913";
createNode multiplyDivide -n "IndexFinger4Fat";
	rename -uid "DCC4B14D-486D-6BA3-3A47-B0B48442752F";
createNode multiplyDivide -n "CupFat";
	rename -uid "80D5CAC5-433D-D721-ED58-3E8C39853380";
createNode multiplyDivide -n "PinkyFinger1Fat";
	rename -uid "0C802936-40CF-0A42-1C55-0A810F68B277";
createNode multiplyDivide -n "PinkyFinger2Fat";
	rename -uid "DF2B5B5C-45D8-B633-CC5A-3E959F2C8E36";
createNode multiplyDivide -n "PinkyFinger3Fat";
	rename -uid "805B3873-48A7-9664-2225-AC819F4848E1";
createNode multiplyDivide -n "PinkyFinger4Fat";
	rename -uid "9CD5466A-4864-149F-A443-718E78000F76";
createNode multiplyDivide -n "RingFinger1Fat";
	rename -uid "0C117805-41DA-8E1B-8E5E-59BAA6253502";
createNode multiplyDivide -n "RingFinger2Fat";
	rename -uid "B4ED6C6A-4F75-3432-9BE7-EEA91D2DA27B";
createNode multiplyDivide -n "RingFinger3Fat";
	rename -uid "C0C3C318-4452-49EC-B520-468B8E3CA4CC";
createNode multiplyDivide -n "RingFinger4Fat";
	rename -uid "F58BA4C6-4982-9318-6E23-B9B3059BD3EC";
createNode multiplyDivide -n "NeckFat";
	rename -uid "5E8DF451-4466-F2DB-C7E7-008FC77191DB";
createNode multiplyDivide -n "HeadFat";
	rename -uid "0AE90054-4188-FE00-4331-01B6B75D8049";
createNode multiplyDivide -n "EyeFat";
	rename -uid "4A05B974-45D3-A7A3-F238-F698AE61F68B";
createNode multiplyDivide -n "EyeEndFat";
	rename -uid "55DA8911-40C3-5696-6B59-DEBDFC3912C8";
createNode multiplyDivide -n "JawFat";
	rename -uid "5FD6A175-4DF3-35F0-64D4-B1807FB1AA19";
createNode multiplyDivide -n "JawEndFat";
	rename -uid "1DB6C1E9-4041-5AE7-A7C3-6A9884431B6F";
createNode multiplyDivide -n "HeadEndFat";
	rename -uid "F312DB38-4C9B-081C-E5F9-598B51A48CEF";
createNode multiplyDivide -n "HipFat";
	rename -uid "6327A615-4484-83AF-9BC6-548C1124F5FF";
createNode multiplyDivide -n "KneeFat";
	rename -uid "2E070290-46E3-6827-F158-418D04A2A704";
createNode multiplyDivide -n "AnkleFat";
	rename -uid "E6F7CCB6-4095-DBB5-6A82-D2B70940B466";
createNode multiplyDivide -n "HeelFat";
	rename -uid "FF237732-47FE-4D26-AE2A-D481E77DB09B";
createNode multiplyDivide -n "ToesFat";
	rename -uid "FAEFD3B5-41A4-86A1-9D0D-20B3E501E963";
createNode multiplyDivide -n "FootSideInnerFat";
	rename -uid "F3B0176B-4258-1726-9722-DD86BDB53A2D";
createNode multiplyDivide -n "FootSideOuterFat";
	rename -uid "2DB25730-447D-FB25-CEEE-419373B7CFF4";
createNode multiplyDivide -n "ToesEndFat";
	rename -uid "9C7FA9B6-4512-185F-3BB7-378B9683BD39";
createNode lightLinker -s -n "lightLinker1";
	rename -uid "303C1AD0-4B97-84EA-419D-DE91D55E4746";
	setAttr -s 38 ".lnk";
	setAttr -s 38 ".slnk";
createNode shapeEditorManager -n "shapeEditorManager";
	rename -uid "378ECEA6-461B-F155-1CB7-F980A5E28093";
createNode poseInterpolatorManager -n "poseInterpolatorManager";
	rename -uid "5FBA071E-4831-C90A-CD38-7EBDB1940B0D";
createNode displayLayerManager -n "layerManager";
	rename -uid "10B7D14D-4C4B-9F28-5A90-669EF4AB40F2";
	setAttr -s 2 ".dli[1]"  1;
	setAttr -s 2 ".dli";
createNode displayLayer -n "defaultLayer";
	rename -uid "30EED761-4E07-E293-7323-A49F6B45EAE0";
createNode renderLayerManager -n "renderLayerManager";
	rename -uid "32CFD150-4767-56C7-2E52-CAA8476718CC";
createNode renderLayer -n "defaultRenderLayer";
	rename -uid "62094698-4122-394F-DF85-969C87A79F7B";
	setAttr ".g" yes;
createNode displayLayer -n "Hi";
	rename -uid "0A687AD5-42DA-C8FA-03BB-AAAA3C8BD622";
	setAttr ".dt" 2;
	setAttr ".do" 1;
createNode script -n "uiConfigurationScriptNode";
	rename -uid "F8C7E458-47FF-74B5-658A-9F979263B90B";
	setAttr ".b" -type "string" (
		"// Maya Mel UI Configuration File.\n//\n//  This script is machine generated.  Edit at your own risk.\n//\n//\n\nglobal string $gMainPane;\nif (`paneLayout -exists $gMainPane`) {\n\n\tglobal int $gUseScenePanelConfig;\n\tint    $useSceneConfig = $gUseScenePanelConfig;\n\tint    $nodeEditorPanelVisible = stringArrayContains(\"nodeEditorPanel1\", `getPanel -vis`);\n\tint    $nodeEditorWorkspaceControlOpen = (`workspaceControl -exists nodeEditorPanel1Window` && `workspaceControl -q -visible nodeEditorPanel1Window`);\n\tint    $menusOkayInPanels = `optionVar -q allowMenusInPanels`;\n\tint    $nVisPanes = `paneLayout -q -nvp $gMainPane`;\n\tint    $nPanes = 0;\n\tstring $editorName;\n\tstring $panelName;\n\tstring $itemFilterName;\n\tstring $panelConfig;\n\n\t//\n\t//  get current state of the UI\n\t//\n\tsceneUIReplacement -update $gMainPane;\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Top View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Top View\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"top\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n"
		+ "            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n"
		+ "            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n"
		+ "\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Side View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Side View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"side\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 1\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n"
		+ "            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n"
		+ "            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 0\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n"
		+ "            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Front View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Front View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"front\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"smoothShaded\" \n            -activeOnly 0\n            -ignorePanZoom 0\n            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n"
		+ "            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 0\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n"
		+ "            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 1\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n"
		+ "            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 1\n            -height 1\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"modelPanel\" (localizedPanelLabel(\"Persp View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tmodelPanel -edit -l (localizedPanelLabel(\"Persp View\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        modelEditor -e \n            -camera \"persp\" \n            -useInteractiveMode 0\n            -displayLights \"default\" \n            -displayAppearance \"wireframe\" \n            -activeOnly 0\n            -ignorePanZoom 0\n"
		+ "            -wireframeOnShaded 0\n            -headsUpDisplay 1\n            -holdOuts 1\n            -selectionHiliteDisplay 1\n            -useDefaultMaterial 0\n            -bufferMode \"double\" \n            -twoSidedLighting 0\n            -backfaceCulling 0\n            -xray 0\n            -jointXray 0\n            -activeComponentsXray 0\n            -displayTextures 1\n            -smoothWireframe 0\n            -lineWidth 1\n            -textureAnisotropic 0\n            -textureHilight 1\n            -textureSampling 2\n            -textureDisplay \"modulate\" \n            -textureMaxSize 16384\n            -fogging 0\n            -fogSource \"fragment\" \n            -fogMode \"linear\" \n            -fogStart 0\n            -fogEnd 100\n            -fogDensity 0.1\n            -fogColor 0.5 0.5 0.5 1 \n            -depthOfFieldPreview 1\n            -maxConstantTransparency 1\n            -rendererName \"vp2Renderer\" \n            -objectFilterShowInHUD 1\n            -isFiltered 0\n            -colorResolution 256 256 \n            -bumpResolution 512 512 \n"
		+ "            -textureCompression 0\n            -transparencyAlgorithm \"frontAndBackCull\" \n            -transpInShadows 0\n            -cullingOverride \"none\" \n            -lowQualityLighting 0\n            -maximumNumHardwareLights 1\n            -occlusionCulling 0\n            -shadingModel 0\n            -useBaseRenderer 0\n            -useReducedRenderer 0\n            -smallObjectCulling 0\n            -smallObjectThreshold -1 \n            -interactiveDisableShadows 0\n            -interactiveBackFaceCull 0\n            -sortTransparent 1\n            -controllers 1\n            -nurbsCurves 1\n            -nurbsSurfaces 1\n            -polymeshes 1\n            -subdivSurfaces 1\n            -planes 1\n            -lights 1\n            -cameras 1\n            -controlVertices 1\n            -hulls 1\n            -grid 0\n            -imagePlane 1\n            -joints 1\n            -ikHandles 1\n            -deformers 1\n            -dynamics 1\n            -particleInstancers 1\n            -fluids 1\n            -hairSystems 1\n            -follicles 1\n"
		+ "            -nCloths 1\n            -nParticles 1\n            -nRigids 1\n            -dynamicConstraints 1\n            -locators 1\n            -manipulators 1\n            -pluginShapes 1\n            -dimensions 1\n            -handles 1\n            -pivots 1\n            -textures 1\n            -strokes 1\n            -motionTrails 1\n            -clipGhosts 1\n            -greasePencils 1\n            -shadows 0\n            -captureSequenceNumber -1\n            -width 779\n            -height 710\n            -sceneRenderFilter 0\n            $editorName;\n        modelEditor -e -viewSelected 0 $editorName;\n        modelEditor -e \n            -pluginObjects \"gpuCacheDisplayFilter\" 1 \n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"ToggledOutliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"ToggledOutliner\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 1\n            -showReferenceMembers 1\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n"
		+ "            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -isSet 0\n            -isSetMember 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            -renderFilterIndex 0\n            -selectionOrder \"chronological\" \n            -expandAttribute 0\n            $editorName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"outlinerPanel\" (localizedPanelLabel(\"Outliner\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\toutlinerPanel -edit -l (localizedPanelLabel(\"Outliner\")) -mbv $menusOkayInPanels  $panelName;\n\t\t$editorName = $panelName;\n        outlinerEditor -e \n            -docTag \"isolOutln_fromSeln\" \n            -showShapes 0\n            -showAssignedMaterials 0\n            -showTimeEditor 1\n            -showReferenceNodes 0\n            -showReferenceMembers 0\n            -showAttributes 0\n            -showConnected 0\n            -showAnimCurvesOnly 0\n            -showMuteInfo 0\n            -organizeByLayer 1\n            -organizeByClip 1\n            -showAnimLayerWeight 1\n            -autoExpandLayers 1\n            -autoExpand 0\n            -showDagOnly 1\n            -showAssets 1\n            -showContainedOnly 1\n            -showPublishedAsConnected 0\n            -showParentContainers 0\n"
		+ "            -showContainerContents 1\n            -ignoreDagHierarchy 0\n            -expandConnections 0\n            -showUpstreamCurves 1\n            -showUnitlessCurves 1\n            -showCompounds 1\n            -showLeafs 1\n            -showNumericAttrsOnly 0\n            -highlightActive 1\n            -autoSelectNewObjects 0\n            -doNotSelectNewObjects 0\n            -dropIsParent 1\n            -transmitFilters 0\n            -setFilter \"defaultSetFilter\" \n            -showSetMembers 1\n            -allowMultiSelection 1\n            -alwaysToggleSelect 0\n            -directSelect 0\n            -displayMode \"DAG\" \n            -expandObjects 0\n            -setsIgnoreFilters 1\n            -containersIgnoreFilters 0\n            -editAttrName 0\n            -showAttrValues 0\n            -highlightSecondary 0\n            -showUVAttrsOnly 0\n            -showTextureNodesOnly 0\n            -attrAlphaOrder \"default\" \n            -animLayerFilterOptions \"allAffecting\" \n            -sortOrder \"none\" \n            -longNames 0\n"
		+ "            -niceNames 1\n            -showNamespace 1\n            -showPinIcons 0\n            -mapMotionTrails 0\n            -ignoreHiddenAttribute 0\n            -ignoreOutlinerColor 0\n            -renderFilterVisible 0\n            $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"graphEditor\" (localizedPanelLabel(\"Graph Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Graph Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n"
		+ "                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 1\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 1\n                -showCompounds 0\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n                -highlightActive 0\n                -autoSelectNewObjects 1\n                -doNotSelectNewObjects 0\n                -dropIsParent 1\n                -transmitFilters 1\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n"
		+ "                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 1\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"GraphEd\");\n            animCurveEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 1\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 1\n                -snapTime \"integer\" \n                -snapValue \"none\" \n"
		+ "                -showResults \"off\" \n                -showBufferCurves \"off\" \n                -smoothness \"fine\" \n                -resultSamples 1\n                -resultScreenSamples 0\n                -resultUpdate \"delayed\" \n                -showUpstreamCurves 1\n                -showCurveNames 0\n                -showActiveCurveNames 0\n                -stackedCurves 0\n                -stackedCurvesMin -1\n                -stackedCurvesMax 1\n                -stackedCurvesSpace 0.2\n                -displayNormalized 0\n                -preSelectionHighlight 0\n                -constrainDrag 0\n                -classicMode 1\n                -valueLinesToggle 1\n                -outliner \"graphEditor1OutlineEd\" \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dopeSheetPanel\" (localizedPanelLabel(\"Dope Sheet\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dope Sheet\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"OutlineEd\");\n            outlinerEditor -e \n                -showShapes 1\n                -showAssignedMaterials 0\n                -showTimeEditor 1\n                -showReferenceNodes 0\n                -showReferenceMembers 0\n                -showAttributes 1\n                -showConnected 1\n                -showAnimCurvesOnly 1\n                -showMuteInfo 0\n                -organizeByLayer 1\n                -organizeByClip 1\n                -showAnimLayerWeight 1\n                -autoExpandLayers 1\n                -autoExpand 0\n                -showDagOnly 0\n                -showAssets 1\n                -showContainedOnly 0\n                -showPublishedAsConnected 0\n                -showParentContainers 1\n                -showContainerContents 0\n                -ignoreDagHierarchy 0\n                -expandConnections 1\n                -showUpstreamCurves 1\n                -showUnitlessCurves 0\n                -showCompounds 1\n                -showLeafs 1\n                -showNumericAttrsOnly 1\n"
		+ "                -highlightActive 0\n                -autoSelectNewObjects 0\n                -doNotSelectNewObjects 1\n                -dropIsParent 1\n                -transmitFilters 0\n                -setFilter \"0\" \n                -showSetMembers 0\n                -allowMultiSelection 1\n                -alwaysToggleSelect 0\n                -directSelect 0\n                -displayMode \"DAG\" \n                -expandObjects 0\n                -setsIgnoreFilters 1\n                -containersIgnoreFilters 0\n                -editAttrName 0\n                -showAttrValues 0\n                -highlightSecondary 0\n                -showUVAttrsOnly 0\n                -showTextureNodesOnly 0\n                -attrAlphaOrder \"default\" \n                -animLayerFilterOptions \"allAffecting\" \n                -sortOrder \"none\" \n                -longNames 0\n                -niceNames 1\n                -showNamespace 1\n                -showPinIcons 0\n                -mapMotionTrails 1\n                -ignoreHiddenAttribute 0\n                -ignoreOutlinerColor 0\n"
		+ "                -renderFilterVisible 0\n                $editorName;\n\n\t\t\t$editorName = ($panelName+\"DopeSheetEd\");\n            dopeSheetEditor -e \n                -displayKeys 1\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"integer\" \n                -snapValue \"none\" \n                -outliner \"dopeSheetPanel1OutlineEd\" \n                -showSummary 1\n                -showScene 0\n                -hierarchyBelow 0\n                -showTicks 1\n                -selectionWindow 0 0 0 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"timeEditorPanel\" (localizedPanelLabel(\"Time Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Time Editor\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"clipEditorPanel\" (localizedPanelLabel(\"Trax Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Trax Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = clipEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 0 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"sequenceEditorPanel\" (localizedPanelLabel(\"Camera Sequencer\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Camera Sequencer\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = sequenceEditorNameFromPanel($panelName);\n            clipEditor -e \n                -displayKeys 0\n                -displayTangents 0\n                -displayActiveKeys 0\n                -displayActiveKeyTangents 0\n                -displayInfinities 0\n                -displayValues 0\n                -autoFit 0\n                -snapTime \"none\" \n                -snapValue \"none\" \n                -initialized 0\n                -manageSequencer 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperGraphPanel\" (localizedPanelLabel(\"Hypergraph Hierarchy\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypergraph Hierarchy\")) -mbv $menusOkayInPanels  $panelName;\n"
		+ "\n\t\t\t$editorName = ($panelName+\"HyperGraphEd\");\n            hyperGraph -e \n                -graphLayoutStyle \"hierarchicalLayout\" \n                -orientation \"horiz\" \n                -mergeConnections 0\n                -zoom 1\n                -animateTransition 0\n                -showRelationships 1\n                -showShapes 0\n                -showDeformers 0\n                -showExpressions 0\n                -showConstraints 0\n                -showConnectionFromSelected 0\n                -showConnectionToSelected 0\n                -showConstraintLabels 0\n                -showUnderworld 0\n                -showInvisible 0\n                -transitionFrames 1\n                -opaqueContainers 0\n                -freeform 0\n                -imagePosition 0 0 \n                -imageScale 1\n                -imageEnabled 0\n                -graphType \"DAG\" \n                -heatMapDisplay 0\n                -updateSelection 1\n                -updateNodeAdded 1\n                -useDrawOverrideColor 0\n                -limitGraphTraversal -1\n"
		+ "                -range 0 0 \n                -iconSize \"smallIcons\" \n                -showCachedConnections 0\n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"hyperShadePanel\" (localizedPanelLabel(\"Hypershade\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Hypershade\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"visorPanel\" (localizedPanelLabel(\"Visor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Visor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"nodeEditorPanel\" (localizedPanelLabel(\"Node Editor\")) `;\n\tif ($nodeEditorPanelVisible || $nodeEditorWorkspaceControlOpen) {\n"
		+ "\t\tif (\"\" == $panelName) {\n\t\t\tif ($useSceneConfig) {\n\t\t\t\t$panelName = `scriptedPanel -unParent  -type \"nodeEditorPanel\" -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels `;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n"
		+ "                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                $editorName;\n\t\t\t}\n\t\t} else {\n\t\t\t$label = `panel -q -label $panelName`;\n\t\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Node Editor\")) -mbv $menusOkayInPanels  $panelName;\n\n\t\t\t$editorName = ($panelName+\"NodeEditorEd\");\n            nodeEditor -e \n                -allAttributes 0\n                -allNodes 0\n                -autoSizeNodes 1\n                -consistentNameSize 1\n                -createNodeCommand \"nodeEdCreateNodeCommand\" \n                -connectNodeOnCreation 0\n                -connectOnDrop 0\n                -copyConnectionsOnPaste 0\n                -defaultPinnedState 0\n                -additiveGraphingMode 0\n                -settingsChangedCallback \"nodeEdSyncControls\" \n                -traversalDepthLimit -1\n                -keyPressCommand \"nodeEdKeyPressCommand\" \n"
		+ "                -nodeTitleMode \"name\" \n                -gridSnap 0\n                -gridVisibility 1\n                -crosshairOnEdgeDragging 0\n                -popupMenuScript \"nodeEdBuildPanelMenus\" \n                -showNamespace 1\n                -showShapes 1\n                -showSGShapes 0\n                -showTransforms 1\n                -useAssets 1\n                -syncedSelection 1\n                -extendToShapes 1\n                -editorMode \"default\" \n                $editorName;\n\t\t\tif (!$useSceneConfig) {\n\t\t\t\tpanel -e -l $label $panelName;\n\t\t\t}\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"createNodePanel\" (localizedPanelLabel(\"Create Node\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Create Node\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"polyTexturePlacementPanel\" (localizedPanelLabel(\"UV Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"UV Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"renderWindowPanel\" (localizedPanelLabel(\"Render View\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Render View\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"shapePanel\" (localizedPanelLabel(\"Shape Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tshapePanel -edit -l (localizedPanelLabel(\"Shape Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextPanel \"posePanel\" (localizedPanelLabel(\"Pose Editor\")) `;\n\tif (\"\" != $panelName) {\n"
		+ "\t\t$label = `panel -q -label $panelName`;\n\t\tposePanel -edit -l (localizedPanelLabel(\"Pose Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynRelEdPanel\" (localizedPanelLabel(\"Dynamic Relationships\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Dynamic Relationships\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"relationshipPanel\" (localizedPanelLabel(\"Relationship Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Relationship Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"referenceEditorPanel\" (localizedPanelLabel(\"Reference Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Reference Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"componentEditorPanel\" (localizedPanelLabel(\"Component Editor\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Component Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"dynPaintScriptedPanelType\" (localizedPanelLabel(\"Paint Effects\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Paint Effects\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"scriptEditorPanel\" (localizedPanelLabel(\"Script Editor\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Script Editor\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"profilerPanel\" (localizedPanelLabel(\"Profiler Tool\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Profiler Tool\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"contentBrowserPanel\" (localizedPanelLabel(\"Content Browser\")) `;\n\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Content Browser\")) -mbv $menusOkayInPanels  $panelName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\t$panelName = `sceneUIReplacement -getNextScriptedPanel \"Stereo\" (localizedPanelLabel(\"Stereo\")) `;\n"
		+ "\tif (\"\" != $panelName) {\n\t\t$label = `panel -q -label $panelName`;\n\t\tscriptedPanel -edit -l (localizedPanelLabel(\"Stereo\")) -mbv $menusOkayInPanels  $panelName;\nstring $editorName = ($panelName+\"Editor\");\n            stereoCameraView -e \n                -camera \"persp\" \n                -useInteractiveMode 0\n                -displayLights \"default\" \n                -displayAppearance \"wireframe\" \n                -activeOnly 0\n                -ignorePanZoom 0\n                -wireframeOnShaded 0\n                -headsUpDisplay 1\n                -holdOuts 1\n                -selectionHiliteDisplay 1\n                -useDefaultMaterial 0\n                -bufferMode \"double\" \n                -twoSidedLighting 1\n                -backfaceCulling 0\n                -xray 0\n                -jointXray 0\n                -activeComponentsXray 0\n                -displayTextures 0\n                -smoothWireframe 0\n                -lineWidth 1\n                -textureAnisotropic 0\n                -textureHilight 1\n                -textureSampling 2\n"
		+ "                -textureDisplay \"modulate\" \n                -textureMaxSize 16384\n                -fogging 0\n                -fogSource \"fragment\" \n                -fogMode \"linear\" \n                -fogStart 0\n                -fogEnd 100\n                -fogDensity 0.1\n                -fogColor 0.5 0.5 0.5 1 \n                -depthOfFieldPreview 1\n                -maxConstantTransparency 1\n                -objectFilterShowInHUD 1\n                -isFiltered 0\n                -colorResolution 4 4 \n                -bumpResolution 4 4 \n                -textureCompression 0\n                -transparencyAlgorithm \"frontAndBackCull\" \n                -transpInShadows 0\n                -cullingOverride \"none\" \n                -lowQualityLighting 0\n                -maximumNumHardwareLights 0\n                -occlusionCulling 0\n                -shadingModel 0\n                -useBaseRenderer 0\n                -useReducedRenderer 0\n                -smallObjectCulling 0\n                -smallObjectThreshold -1 \n                -interactiveDisableShadows 0\n"
		+ "                -interactiveBackFaceCull 0\n                -sortTransparent 1\n                -controllers 1\n                -nurbsCurves 1\n                -nurbsSurfaces 1\n                -polymeshes 1\n                -subdivSurfaces 1\n                -planes 1\n                -lights 1\n                -cameras 1\n                -controlVertices 1\n                -hulls 1\n                -grid 1\n                -imagePlane 1\n                -joints 1\n                -ikHandles 1\n                -deformers 1\n                -dynamics 1\n                -particleInstancers 1\n                -fluids 1\n                -hairSystems 1\n                -follicles 1\n                -nCloths 1\n                -nParticles 1\n                -nRigids 1\n                -dynamicConstraints 1\n                -locators 1\n                -manipulators 1\n                -pluginShapes 1\n                -dimensions 1\n                -handles 1\n                -pivots 1\n                -textures 1\n                -strokes 1\n                -motionTrails 1\n"
		+ "                -clipGhosts 1\n                -greasePencils 1\n                -shadows 0\n                -captureSequenceNumber -1\n                -width 0\n                -height 0\n                -sceneRenderFilter 0\n                -displayMode \"centerEye\" \n                -viewColor 0 0 0 1 \n                -useCustomBackground 1\n                $editorName;\n            stereoCameraView -e -viewSelected 0 $editorName;\n            stereoCameraView -e \n                -pluginObjects \"gpuCacheDisplayFilter\" 1 \n                $editorName;\n\t\tif (!$useSceneConfig) {\n\t\t\tpanel -e -l $label $panelName;\n\t\t}\n\t}\n\n\n\tif ($useSceneConfig) {\n        string $configName = `getPanel -cwl (localizedPanelLabel(\"Current Layout\"))`;\n        if (\"\" != $configName) {\n\t\t\tpanelConfiguration -edit -label (localizedPanelLabel(\"Current Layout\")) \n\t\t\t\t-userCreated false\n\t\t\t\t-defaultImage \"vacantCell.xP:/\"\n\t\t\t\t-image \"\"\n\t\t\t\t-sc false\n\t\t\t\t-configString \"global string $gMainPane; paneLayout -e -cn \\\"single\\\" -ps 1 100 100 $gMainPane;\"\n\t\t\t\t-removeAllPanels\n"
		+ "\t\t\t\t-ap false\n\t\t\t\t\t(localizedPanelLabel(\"Persp View\")) \n\t\t\t\t\t\"modelPanel\"\n"
		+ "\t\t\t\t\t\"$panelName = `modelPanel -unParent -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels `;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 1\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 0\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 779\\n    -height 710\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t\t\"modelPanel -edit -l (localizedPanelLabel(\\\"Persp View\\\")) -mbv $menusOkayInPanels  $panelName;\\n$editorName = $panelName;\\nmodelEditor -e \\n    -cam `findStartUpCamera persp` \\n    -useInteractiveMode 0\\n    -displayLights \\\"default\\\" \\n    -displayAppearance \\\"wireframe\\\" \\n    -activeOnly 0\\n    -ignorePanZoom 0\\n    -wireframeOnShaded 0\\n    -headsUpDisplay 1\\n    -holdOuts 1\\n    -selectionHiliteDisplay 1\\n    -useDefaultMaterial 0\\n    -bufferMode \\\"double\\\" \\n    -twoSidedLighting 0\\n    -backfaceCulling 0\\n    -xray 0\\n    -jointXray 0\\n    -activeComponentsXray 0\\n    -displayTextures 1\\n    -smoothWireframe 0\\n    -lineWidth 1\\n    -textureAnisotropic 0\\n    -textureHilight 1\\n    -textureSampling 2\\n    -textureDisplay \\\"modulate\\\" \\n    -textureMaxSize 16384\\n    -fogging 0\\n    -fogSource \\\"fragment\\\" \\n    -fogMode \\\"linear\\\" \\n    -fogStart 0\\n    -fogEnd 100\\n    -fogDensity 0.1\\n    -fogColor 0.5 0.5 0.5 1 \\n    -depthOfFieldPreview 1\\n    -maxConstantTransparency 1\\n    -rendererName \\\"vp2Renderer\\\" \\n    -objectFilterShowInHUD 1\\n    -isFiltered 0\\n    -colorResolution 256 256 \\n    -bumpResolution 512 512 \\n    -textureCompression 0\\n    -transparencyAlgorithm \\\"frontAndBackCull\\\" \\n    -transpInShadows 0\\n    -cullingOverride \\\"none\\\" \\n    -lowQualityLighting 0\\n    -maximumNumHardwareLights 1\\n    -occlusionCulling 0\\n    -shadingModel 0\\n    -useBaseRenderer 0\\n    -useReducedRenderer 0\\n    -smallObjectCulling 0\\n    -smallObjectThreshold -1 \\n    -interactiveDisableShadows 0\\n    -interactiveBackFaceCull 0\\n    -sortTransparent 1\\n    -controllers 1\\n    -nurbsCurves 1\\n    -nurbsSurfaces 1\\n    -polymeshes 1\\n    -subdivSurfaces 1\\n    -planes 1\\n    -lights 1\\n    -cameras 1\\n    -controlVertices 1\\n    -hulls 1\\n    -grid 0\\n    -imagePlane 1\\n    -joints 1\\n    -ikHandles 1\\n    -deformers 1\\n    -dynamics 1\\n    -particleInstancers 1\\n    -fluids 1\\n    -hairSystems 1\\n    -follicles 1\\n    -nCloths 1\\n    -nParticles 1\\n    -nRigids 1\\n    -dynamicConstraints 1\\n    -locators 1\\n    -manipulators 1\\n    -pluginShapes 1\\n    -dimensions 1\\n    -handles 1\\n    -pivots 1\\n    -textures 1\\n    -strokes 1\\n    -motionTrails 1\\n    -clipGhosts 1\\n    -greasePencils 1\\n    -shadows 0\\n    -captureSequenceNumber -1\\n    -width 779\\n    -height 710\\n    -sceneRenderFilter 0\\n    $editorName;\\nmodelEditor -e -viewSelected 0 $editorName;\\nmodelEditor -e \\n    -pluginObjects \\\"gpuCacheDisplayFilter\\\" 1 \\n    $editorName\"\n"
		+ "\t\t\t\t$configName;\n\n            setNamedPanelLayout (localizedPanelLabel(\"Current Layout\"));\n        }\n\n        panelHistory -e -clear mainPanelHistory;\n        sceneUIReplacement -clear;\n\t}\n\n\ngrid -spacing 5 -size 12 -divisions 5 -displayAxes yes -displayGridLines yes -displayDivisionLines yes -displayPerspectiveLabels no -displayOrthographicLabels no -displayAxesBold yes -perspectiveLabelPosition axis -orthographicLabelPosition edge;\nviewManip -drawCompass 0 -compassAngle 0 -frontParameters \"\" -homeParameters \"\" -selectionLockParameters \"\";\n}\n");
	setAttr ".st" 3;
createNode script -n "sceneConfigurationScriptNode";
	rename -uid "4EE0AB7D-4571-069D-6B92-5BB825F4B4F4";
	setAttr ".b" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".st" 6;
createNode lambert -n "asRed";
	rename -uid "4A922A94-46FE-3A12-7B12-56B6058BD83C";
	setAttr ".c" -type "float3" 1 0 0 ;
createNode shadingEngine -n "asRedSG";
	rename -uid "6D5FC385-4B80-7672-1559-408575F629FF";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo1";
	rename -uid "5B424217-4D05-A31E-E35F-7FBB17AE38FA";
createNode lambert -n "asRed2";
	rename -uid "3A332AB2-4FD8-6090-CEC0-FFB4071DD38B";
	setAttr ".c" -type "float3" 1 0 1 ;
createNode shadingEngine -n "asRed2SG";
	rename -uid "389262EA-4D5A-3FB7-FDFA-D78DBB49C4AD";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo2";
	rename -uid "C4113B1A-4C7A-46F1-BF78-4797F0D57950";
createNode lambert -n "asGreen";
	rename -uid "BD3A0AE2-44DF-3177-8208-86897516D06E";
	setAttr ".c" -type "float3" 0 1 0 ;
createNode shadingEngine -n "asGreenSG";
	rename -uid "D7716121-4801-1640-6F7A-D297A645674C";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo3";
	rename -uid "C4E7B4A2-4139-2F24-2567-998F68114EEC";
createNode lambert -n "asGreen2";
	rename -uid "B400924D-4EE6-6586-46BD-CEB07A71DB1A";
	setAttr ".c" -type "float3" 1 1 0 ;
createNode shadingEngine -n "asGreen2SG";
	rename -uid "85ADA8B3-422B-E5CA-A2DF-A3BD48F6D397";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo4";
	rename -uid "0FCAA94E-443D-FA02-FAB5-CFA5ADBCDCF6";
createNode lambert -n "asBlue";
	rename -uid "32468D1D-43E6-7A22-5979-799CD6F86CC1";
	setAttr ".c" -type "float3" 0 0 1 ;
createNode shadingEngine -n "asBlueSG";
	rename -uid "C4BA95F4-4B98-C05D-6BDB-39A569B26193";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo5";
	rename -uid "2F4DAF17-4144-D74F-A3A3-3D95AB23801D";
createNode lambert -n "asBlue2";
	rename -uid "AC4527F3-4BDD-7561-1210-05AA6208BD9C";
	setAttr ".c" -type "float3" 0 1 1 ;
createNode shadingEngine -n "asBlue2SG";
	rename -uid "9EFE2ADD-4714-8220-43BC-328AF2672578";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo6";
	rename -uid "041FE69A-40FF-DD07-1258-37B47AF13BB9";
createNode lambert -n "asWhite";
	rename -uid "85F9A3C1-4081-5DD1-2D74-A8B4709DB83D";
	setAttr ".c" -type "float3" 1 1 1 ;
createNode shadingEngine -n "asWhiteSG";
	rename -uid "E8345776-48E7-2CE2-28BF-66989F1EF422";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo7";
	rename -uid "318DAF37-4CDF-46F5-D196-8E90A3584456";
createNode lambert -n "asBlack";
	rename -uid "F16F34EF-49BC-2198-52D1-5EB14193183D";
	setAttr ".c" -type "float3" 0 0 0 ;
createNode shadingEngine -n "asBlackSG";
	rename -uid "A73CB89C-4E86-A7AD-E4A4-1B86066CF23E";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo8";
	rename -uid "72C574A5-4795-06A6-53C2-CBB5BA10D16F";
createNode lambert -n "asBones";
	rename -uid "2851B9E3-4A12-7404-48B5-13A6EA5F11FE";
	setAttr ".c" -type "float3" 0.77999997 0.75999999 0.72000003 ;
createNode shadingEngine -n "asBonesSG";
	rename -uid "080495D8-433A-D937-2643-998576559113";
	setAttr ".ihi" 0;
	setAttr ".ro" yes;
createNode materialInfo -n "materialInfo9";
	rename -uid "BA630AED-4276-13E0-0B6B-C2AC8349DEBE";
createNode nodeGraphEditorInfo -n "MayaNodeEditorSavedTabsInfo";
	rename -uid "8379108F-45CB-37E1-E903-22B629B5B7B4";
	setAttr ".tgi[0].tn" -type "string" "Untitled_1";
	setAttr ".tgi[0].vl" -type "double2" -611.90473758985229 -308.33332108126797 ;
	setAttr ".tgi[0].vh" -type "double2" 611.90473758985229 307.14284493809708 ;
createNode reference -n "modelRN";
	rename -uid "48916B2F-4A3C-DC0B-EFBF-55BBEE38DB23";
	setAttr ".phl[1]" 0;
	setAttr ".ed" -type "dataReferenceEdits" 
		"modelRN"
		"modelRN" 0
		"modelRN" 1
		5 4 "modelRN" "|model:Test_lod0_mesh.drawOverride" "modelRN.placeHolderList[1]" 
		"";
	setAttr ".ptag" -type "string" "";
lockNode -l 1 ;
select -ne :time1;
	setAttr -av -k on ".cch";
	setAttr -av -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".o" 1;
	setAttr -av ".unw" 1;
	setAttr -k on ".etw";
	setAttr -k on ".tps";
	setAttr -k on ".tms";
select -ne :hardwareRenderingGlobals;
	setAttr -k on ".ihi";
	setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
		 1 1 1 0 0 0 0 0 0 0 0 0
		 0 0 0 0 ;
select -ne :renderPartition;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 38 ".st";
	setAttr -cb on ".an";
	setAttr -cb on ".pt";
select -ne :renderGlobalsList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
select -ne :defaultShaderList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 14 ".s";
select -ne :postProcessList1;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
	setAttr -k on ".ihi";
	setAttr -s 2 ".r";
select -ne :initialShadingGroup;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
select -ne :initialParticleSE;
	setAttr -av -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".mwc";
	setAttr -cb on ".an";
	setAttr -cb on ".il";
	setAttr -cb on ".vo";
	setAttr -cb on ".eo";
	setAttr -cb on ".fo";
	setAttr -cb on ".epo";
	setAttr -k on ".ro" yes;
select -ne :defaultRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k on ".macc";
	setAttr -k on ".macd";
	setAttr -k on ".macq";
	setAttr -k on ".mcfr";
	setAttr -cb on ".ifg";
	setAttr -k on ".clip";
	setAttr -k on ".edm";
	setAttr -k on ".edl";
	setAttr -cb on ".ren";
	setAttr -av -k on ".esr";
	setAttr -k on ".ors";
	setAttr -cb on ".sdf";
	setAttr -av -k on ".outf";
	setAttr -cb on ".imfkey";
	setAttr -k on ".gama";
	setAttr -k on ".an";
	setAttr -cb on ".ar";
	setAttr -k on ".fs" 1;
	setAttr -k on ".ef" 10;
	setAttr -av -k on ".bfs";
	setAttr -cb on ".me";
	setAttr -cb on ".se";
	setAttr -k on ".be";
	setAttr -cb on ".ep";
	setAttr -k on ".fec";
	setAttr -av -k on ".ofc";
	setAttr -cb on ".ofe";
	setAttr -cb on ".efe";
	setAttr -cb on ".oft";
	setAttr -cb on ".umfn";
	setAttr -cb on ".ufe";
	setAttr -cb on ".pff";
	setAttr -cb on ".peie";
	setAttr -cb on ".ifp";
	setAttr -k on ".comp";
	setAttr -k on ".cth";
	setAttr -k on ".soll";
	setAttr -k on ".sosl";
	setAttr -k on ".rd";
	setAttr -k on ".lp";
	setAttr -av -k on ".sp";
	setAttr -k on ".shs";
	setAttr -av -k on ".lpr";
	setAttr -cb on ".gv";
	setAttr -cb on ".sv";
	setAttr -k on ".mm";
	setAttr -k on ".npu";
	setAttr -k on ".itf";
	setAttr -k on ".shp";
	setAttr -cb on ".isp";
	setAttr -k on ".uf";
	setAttr -k on ".oi";
	setAttr -k on ".rut";
	setAttr -cb on ".mb";
	setAttr -av -k on ".mbf";
	setAttr -k on ".afp";
	setAttr -k on ".pfb";
	setAttr -k on ".pram";
	setAttr -k on ".poam";
	setAttr -k on ".prlm";
	setAttr -k on ".polm";
	setAttr -cb on ".prm";
	setAttr -cb on ".pom";
	setAttr -cb on ".pfrm";
	setAttr -cb on ".pfom";
	setAttr -av -k on ".bll";
	setAttr -k on ".bls";
	setAttr -k on ".smv";
	setAttr -k on ".ubc";
	setAttr -k on ".mbc";
	setAttr -cb on ".mbt";
	setAttr -k on ".udbx";
	setAttr -k on ".smc";
	setAttr -k on ".kmv";
	setAttr -cb on ".isl";
	setAttr -cb on ".ism";
	setAttr -cb on ".imb";
	setAttr -k on ".rlen";
	setAttr -av -k on ".frts";
	setAttr -k on ".tlwd";
	setAttr -k on ".tlht";
	setAttr -k on ".jfc";
	setAttr -cb on ".rsb";
	setAttr -k on ".ope";
	setAttr -k on ".oppf";
	setAttr -cb on ".hbl";
select -ne :defaultResolution;
	setAttr -av -k on ".cch";
	setAttr -k on ".ihi";
	setAttr -av -k on ".nds";
	setAttr -k on ".bnm";
	setAttr -av -k on ".w";
	setAttr -av -k on ".h";
	setAttr -av -k on ".pa" 1;
	setAttr -av -k on ".al";
	setAttr -av -k on ".dar";
	setAttr -av -k on ".ldar";
	setAttr -k on ".dpi";
	setAttr -av -k on ".off";
	setAttr -av -k on ".fld";
	setAttr -av -k on ".zsl";
	setAttr -k on ".isu";
	setAttr -k on ".pdu";
select -ne :defaultColorMgtGlobals;
	setAttr ".cme" no;
select -ne :hardwareRenderGlobals;
	setAttr -k on ".cch";
	setAttr -cb on ".ihi";
	setAttr -k on ".nds";
	setAttr -cb on ".bnm";
	setAttr -k off ".ctrs" 256;
	setAttr -av -k off ".btrs" 512;
	setAttr -k off ".fbfm";
	setAttr -k off -cb on ".ehql";
	setAttr -k off -cb on ".eams";
	setAttr -k off -cb on ".eeaa";
	setAttr -k off -cb on ".engm";
	setAttr -k off -cb on ".mes";
	setAttr -k off -cb on ".emb";
	setAttr -av -k off -cb on ".mbbf";
	setAttr -k off -cb on ".mbs";
	setAttr -k off -cb on ".trm";
	setAttr -k off -cb on ".tshc";
	setAttr -k off ".enpt";
	setAttr -k off -cb on ".clmt";
	setAttr -k off -cb on ".tcov";
	setAttr -k off -cb on ".lith";
	setAttr -k off -cb on ".sobc";
	setAttr -k off -cb on ".cuth";
	setAttr -k off -cb on ".hgcd";
	setAttr -k off -cb on ".hgci";
	setAttr -k off -cb on ".mgcs";
	setAttr -k off -cb on ".twa";
	setAttr -k off -cb on ".twz";
	setAttr -k on ".hwcc";
	setAttr -k on ".hwdp";
	setAttr -k on ".hwql";
	setAttr -k on ".hwfr";
	setAttr -k on ".soll";
	setAttr -k on ".sosl";
	setAttr -k on ".bswa";
	setAttr -k on ".shml";
	setAttr -k on ".hwel";
connectAttr "Hi.di" "modelRN.phl[1]";
connectAttr "SDK1FKPinkyFinger1_R_rotateZ.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKIndexFinger1_R_rotateZ.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKRingFinger1_R_rotateZ.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKCup_R_rotateX.drivingSystemOut" "FitSkeleton.drivingSystem" -na
		;
connectAttr "SDK1FKIndexFinger3_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKIndexFinger2_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK2FKIndexFinger1_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKMiddleFinger1_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKMiddleFinger3_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKMiddleFinger2_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKRingFinger3_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKRingFinger2_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK2FKRingFinger1_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK2FKPinkyFinger1_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKPinkyFinger2_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKPinkyFinger3_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKThumbFinger2_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKThumbFinger3_R_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKPinkyFinger1_L_rotateZ.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKIndexFinger1_L_rotateZ.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKRingFinger1_L_rotateZ.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKCup_L_rotateX.drivingSystemOut" "FitSkeleton.drivingSystem" -na
		;
connectAttr "SDK1FKIndexFinger2_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKIndexFinger3_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK2FKIndexFinger1_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKMiddleFinger2_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKMiddleFinger3_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKMiddleFinger1_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKRingFinger2_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKRingFinger3_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK2FKRingFinger1_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKPinkyFinger2_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKPinkyFinger3_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK2FKPinkyFinger1_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKThumbFinger2_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "SDK1FKThumbFinger3_L_rotateY.drivingSystemOut" "FitSkeleton.drivingSystem"
		 -na;
connectAttr "RootFat.oy" "Root.fatYabs";
connectAttr "RootFat.oz" "Root.fatZabs";
connectAttr "Root.s" "Spine1.is";
connectAttr "Spine1Fat.oy" "Spine1.fatYabs";
connectAttr "Spine1Fat.oz" "Spine1.fatZabs";
connectAttr "Spine1.s" "Spine2.is";
connectAttr "Spine2.s" "Spine3.is";
connectAttr "Spine3.s" "Chest.is";
connectAttr "ChestFat.oy" "Chest.fatYabs";
connectAttr "ChestFat.oz" "Chest.fatZabs";
connectAttr "Chest.s" "Scapula.is";
connectAttr "ScapulaFat.oy" "Scapula.fatYabs";
connectAttr "ScapulaFat.oz" "Scapula.fatZabs";
connectAttr "Scapula.s" "Shoulder.is";
connectAttr "ShoulderFat.oy" "Shoulder.fatYabs";
connectAttr "ShoulderFat.oz" "Shoulder.fatZabs";
connectAttr "Shoulder.s" "Elbow.is";
connectAttr "ElbowFat.oy" "Elbow.fatYabs";
connectAttr "ElbowFat.oz" "Elbow.fatZabs";
connectAttr "Elbow.s" "Wrist.is";
connectAttr "WristFat.oy" "Wrist.fatYabs";
connectAttr "WristFat.oz" "Wrist.fatZabs";
connectAttr "Wrist.s" "MiddleFinger1.is";
connectAttr "MiddleFinger1Fat.oy" "MiddleFinger1.fatYabs";
connectAttr "MiddleFinger1Fat.oz" "MiddleFinger1.fatZabs";
connectAttr "MiddleFinger1.s" "MiddleFinger2.is";
connectAttr "MiddleFinger2Fat.oy" "MiddleFinger2.fatYabs";
connectAttr "MiddleFinger2Fat.oz" "MiddleFinger2.fatZabs";
connectAttr "MiddleFinger2.s" "MiddleFinger3.is";
connectAttr "MiddleFinger3Fat.oy" "MiddleFinger3.fatYabs";
connectAttr "MiddleFinger3Fat.oz" "MiddleFinger3.fatZabs";
connectAttr "MiddleFinger3.s" "MiddleFinger4.is";
connectAttr "MiddleFinger4Fat.oy" "MiddleFinger4.fatYabs";
connectAttr "MiddleFinger4Fat.oz" "MiddleFinger4.fatZabs";
connectAttr "Wrist.s" "ThumbFinger1.is";
connectAttr "ThumbFinger1Fat.oy" "ThumbFinger1.fatYabs";
connectAttr "ThumbFinger1Fat.oz" "ThumbFinger1.fatZabs";
connectAttr "ThumbFinger1.s" "ThumbFinger2.is";
connectAttr "ThumbFinger2Fat.oy" "ThumbFinger2.fatYabs";
connectAttr "ThumbFinger2Fat.oz" "ThumbFinger2.fatZabs";
connectAttr "ThumbFinger2.s" "ThumbFinger3.is";
connectAttr "ThumbFinger3Fat.oy" "ThumbFinger3.fatYabs";
connectAttr "ThumbFinger3Fat.oz" "ThumbFinger3.fatZabs";
connectAttr "ThumbFinger3.s" "ThumbFinger4.is";
connectAttr "ThumbFinger4Fat.oy" "ThumbFinger4.fatYabs";
connectAttr "ThumbFinger4Fat.oz" "ThumbFinger4.fatZabs";
connectAttr "Wrist.s" "IndexFinger1.is";
connectAttr "IndexFinger1Fat.oy" "IndexFinger1.fatYabs";
connectAttr "IndexFinger1Fat.oz" "IndexFinger1.fatZabs";
connectAttr "IndexFinger1.s" "IndexFinger2.is";
connectAttr "IndexFinger2Fat.oy" "IndexFinger2.fatYabs";
connectAttr "IndexFinger2Fat.oz" "IndexFinger2.fatZabs";
connectAttr "IndexFinger2.s" "IndexFinger3.is";
connectAttr "IndexFinger3Fat.oy" "IndexFinger3.fatYabs";
connectAttr "IndexFinger3Fat.oz" "IndexFinger3.fatZabs";
connectAttr "IndexFinger3.s" "IndexFinger4.is";
connectAttr "IndexFinger4Fat.oy" "IndexFinger4.fatYabs";
connectAttr "IndexFinger4Fat.oz" "IndexFinger4.fatZabs";
connectAttr "Wrist.s" "Cup.is";
connectAttr "CupFat.oy" "Cup.fatYabs";
connectAttr "CupFat.oz" "Cup.fatZabs";
connectAttr "Cup.s" "PinkyFinger1.is";
connectAttr "PinkyFinger1Fat.oy" "PinkyFinger1.fatYabs";
connectAttr "PinkyFinger1Fat.oz" "PinkyFinger1.fatZabs";
connectAttr "PinkyFinger1.s" "PinkyFinger2.is";
connectAttr "PinkyFinger2Fat.oy" "PinkyFinger2.fatYabs";
connectAttr "PinkyFinger2Fat.oz" "PinkyFinger2.fatZabs";
connectAttr "PinkyFinger2.s" "PinkyFinger3.is";
connectAttr "PinkyFinger3Fat.oy" "PinkyFinger3.fatYabs";
connectAttr "PinkyFinger3Fat.oz" "PinkyFinger3.fatZabs";
connectAttr "PinkyFinger3.s" "PinkyFinger4.is";
connectAttr "PinkyFinger4Fat.oy" "PinkyFinger4.fatYabs";
connectAttr "PinkyFinger4Fat.oz" "PinkyFinger4.fatZabs";
connectAttr "Cup.s" "RingFinger1.is";
connectAttr "RingFinger1Fat.oy" "RingFinger1.fatYabs";
connectAttr "RingFinger1Fat.oz" "RingFinger1.fatZabs";
connectAttr "RingFinger1.s" "RingFinger2.is";
connectAttr "RingFinger2Fat.oy" "RingFinger2.fatYabs";
connectAttr "RingFinger2Fat.oz" "RingFinger2.fatZabs";
connectAttr "RingFinger2.s" "RingFinger3.is";
connectAttr "RingFinger3Fat.oy" "RingFinger3.fatYabs";
connectAttr "RingFinger3Fat.oz" "RingFinger3.fatZabs";
connectAttr "RingFinger3.s" "RingFinger4.is";
connectAttr "RingFinger4Fat.oy" "RingFinger4.fatYabs";
connectAttr "RingFinger4Fat.oz" "RingFinger4.fatZabs";
connectAttr "Chest.s" "Neck.is";
connectAttr "NeckFat.oy" "Neck.fatYabs";
connectAttr "NeckFat.oz" "Neck.fatZabs";
connectAttr "Neck.s" "Head.is";
connectAttr "HeadFat.oy" "Head.fatYabs";
connectAttr "HeadFat.oz" "Head.fatZabs";
connectAttr "Head.s" "Eye.is";
connectAttr "EyeFat.oy" "Eye.fatYabs";
connectAttr "EyeFat.oz" "Eye.fatZabs";
connectAttr "Eye.s" "EyeEnd.is";
connectAttr "EyeEndFat.oy" "EyeEnd.fatYabs";
connectAttr "EyeEndFat.oz" "EyeEnd.fatZabs";
connectAttr "Head.s" "Jaw.is";
connectAttr "JawFat.oy" "Jaw.fatYabs";
connectAttr "JawFat.oz" "Jaw.fatZabs";
connectAttr "Jaw.s" "JawEnd.is";
connectAttr "JawEndFat.oy" "JawEnd.fatYabs";
connectAttr "JawEndFat.oz" "JawEnd.fatZabs";
connectAttr "Head.s" "HeadEnd.is";
connectAttr "HeadEndFat.oy" "HeadEnd.fatYabs";
connectAttr "HeadEndFat.oz" "HeadEnd.fatZabs";
connectAttr "Root.s" "Hip.is";
connectAttr "HipFat.oy" "Hip.fatYabs";
connectAttr "HipFat.oz" "Hip.fatZabs";
connectAttr "Hip.s" "Knee.is";
connectAttr "KneeFat.oy" "Knee.fatYabs";
connectAttr "KneeFat.oz" "Knee.fatZabs";
connectAttr "Knee.s" "Ankle.is";
connectAttr "AnkleFat.oy" "Ankle.fatYabs";
connectAttr "AnkleFat.oz" "Ankle.fatZabs";
connectAttr "Ankle.s" "Heel.is";
connectAttr "HeelFat.oy" "Heel.fatYabs";
connectAttr "HeelFat.oz" "Heel.fatZabs";
connectAttr "Ankle.s" "Toes.is";
connectAttr "ToesFat.oy" "Toes.fatYabs";
connectAttr "ToesFat.oz" "Toes.fatZabs";
connectAttr "Toes.s" "FootSideInner.is";
connectAttr "FootSideInnerFat.oy" "FootSideInner.fatYabs";
connectAttr "FootSideInnerFat.oz" "FootSideInner.fatZabs";
connectAttr "Toes.s" "FootSideOuter.is";
connectAttr "FootSideOuterFat.oy" "FootSideOuter.fatYabs";
connectAttr "FootSideOuterFat.oz" "FootSideOuter.fatZabs";
connectAttr "Toes.s" "ToesEnd.is";
connectAttr "ToesEndFat.oy" "ToesEnd.fatYabs";
connectAttr "ToesEndFat.oz" "ToesEnd.fatZabs";
connectAttr "FitSkeleton.drivingSystem_Fingers_R[0]" "SDK1FKPinkyFinger1_R_rotateZ.spread"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[1]" "SDK1FKIndexFinger1_R_rotateZ.spread"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[2]" "SDK1FKRingFinger1_R_rotateZ.spread"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[3]" "SDK1FKCup_R_rotateX.cup";
connectAttr "FitSkeleton.drivingSystem_Fingers_R[4]" "SDK1FKIndexFinger3_R_rotateY.indexCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[5]" "SDK1FKIndexFinger2_R_rotateY.indexCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[6]" "SDK2FKIndexFinger1_R_rotateY.indexCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[7]" "SDK1FKMiddleFinger1_R_rotateY.middleCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[8]" "SDK1FKMiddleFinger3_R_rotateY.middleCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[9]" "SDK1FKMiddleFinger2_R_rotateY.middleCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[10]" "SDK1FKRingFinger3_R_rotateY.ringCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[11]" "SDK1FKRingFinger2_R_rotateY.ringCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[12]" "SDK2FKRingFinger1_R_rotateY.ringCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[13]" "SDK2FKPinkyFinger1_R_rotateY.pinkyCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[14]" "SDK1FKPinkyFinger2_R_rotateY.pinkyCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[15]" "SDK1FKPinkyFinger3_R_rotateY.pinkyCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[16]" "SDK1FKThumbFinger2_R_rotateY.thumbCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_R[17]" "SDK1FKThumbFinger3_R_rotateY.thumbCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[0]" "SDK1FKPinkyFinger1_L_rotateZ.spread"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[1]" "SDK1FKIndexFinger1_L_rotateZ.spread"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[2]" "SDK1FKRingFinger1_L_rotateZ.spread"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[3]" "SDK1FKCup_L_rotateX.cup";
connectAttr "FitSkeleton.drivingSystem_Fingers_L[4]" "SDK1FKIndexFinger2_L_rotateY.indexCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[5]" "SDK1FKIndexFinger3_L_rotateY.indexCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[6]" "SDK2FKIndexFinger1_L_rotateY.indexCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[7]" "SDK1FKMiddleFinger2_L_rotateY.middleCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[8]" "SDK1FKMiddleFinger3_L_rotateY.middleCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[9]" "SDK1FKMiddleFinger1_L_rotateY.middleCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[10]" "SDK1FKRingFinger2_L_rotateY.ringCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[11]" "SDK1FKRingFinger3_L_rotateY.ringCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[12]" "SDK2FKRingFinger1_L_rotateY.ringCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[13]" "SDK1FKPinkyFinger2_L_rotateY.pinkyCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[14]" "SDK1FKPinkyFinger3_L_rotateY.pinkyCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[15]" "SDK2FKPinkyFinger1_L_rotateY.pinkyCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[16]" "SDK1FKThumbFinger2_L_rotateY.thumbCurl"
		;
connectAttr "FitSkeleton.drivingSystem_Fingers_L[17]" "SDK1FKThumbFinger3_L_rotateY.thumbCurl"
		;
connectAttr "Root.fat" "RootFat.i1y";
connectAttr "Root.fat" "RootFat.i1z";
connectAttr "Root.fatY" "RootFat.i2y";
connectAttr "Root.fatZ" "RootFat.i2z";
connectAttr "Spine1.fat" "Spine1Fat.i1y";
connectAttr "Spine1.fat" "Spine1Fat.i1z";
connectAttr "Spine1.fatY" "Spine1Fat.i2y";
connectAttr "Spine1.fatZ" "Spine1Fat.i2z";
connectAttr "Chest.fat" "ChestFat.i1y";
connectAttr "Chest.fat" "ChestFat.i1z";
connectAttr "Chest.fatY" "ChestFat.i2y";
connectAttr "Chest.fatZ" "ChestFat.i2z";
connectAttr "Scapula.fat" "ScapulaFat.i1y";
connectAttr "Scapula.fat" "ScapulaFat.i1z";
connectAttr "Scapula.fatY" "ScapulaFat.i2y";
connectAttr "Scapula.fatZ" "ScapulaFat.i2z";
connectAttr "Shoulder.fat" "ShoulderFat.i1y";
connectAttr "Shoulder.fat" "ShoulderFat.i1z";
connectAttr "Shoulder.fatY" "ShoulderFat.i2y";
connectAttr "Shoulder.fatZ" "ShoulderFat.i2z";
connectAttr "Elbow.fat" "ElbowFat.i1y";
connectAttr "Elbow.fat" "ElbowFat.i1z";
connectAttr "Elbow.fatY" "ElbowFat.i2y";
connectAttr "Elbow.fatZ" "ElbowFat.i2z";
connectAttr "Wrist.fat" "WristFat.i1y";
connectAttr "Wrist.fat" "WristFat.i1z";
connectAttr "Wrist.fatY" "WristFat.i2y";
connectAttr "Wrist.fatZ" "WristFat.i2z";
connectAttr "MiddleFinger1.fat" "MiddleFinger1Fat.i1y";
connectAttr "MiddleFinger1.fat" "MiddleFinger1Fat.i1z";
connectAttr "MiddleFinger1.fatY" "MiddleFinger1Fat.i2y";
connectAttr "MiddleFinger1.fatZ" "MiddleFinger1Fat.i2z";
connectAttr "MiddleFinger2.fat" "MiddleFinger2Fat.i1y";
connectAttr "MiddleFinger2.fat" "MiddleFinger2Fat.i1z";
connectAttr "MiddleFinger2.fatY" "MiddleFinger2Fat.i2y";
connectAttr "MiddleFinger2.fatZ" "MiddleFinger2Fat.i2z";
connectAttr "MiddleFinger3.fat" "MiddleFinger3Fat.i1y";
connectAttr "MiddleFinger3.fat" "MiddleFinger3Fat.i1z";
connectAttr "MiddleFinger3.fatY" "MiddleFinger3Fat.i2y";
connectAttr "MiddleFinger3.fatZ" "MiddleFinger3Fat.i2z";
connectAttr "MiddleFinger4.fat" "MiddleFinger4Fat.i1y";
connectAttr "MiddleFinger4.fat" "MiddleFinger4Fat.i1z";
connectAttr "MiddleFinger4.fatY" "MiddleFinger4Fat.i2y";
connectAttr "MiddleFinger4.fatZ" "MiddleFinger4Fat.i2z";
connectAttr "ThumbFinger1.fat" "ThumbFinger1Fat.i1y";
connectAttr "ThumbFinger1.fat" "ThumbFinger1Fat.i1z";
connectAttr "ThumbFinger1.fatY" "ThumbFinger1Fat.i2y";
connectAttr "ThumbFinger1.fatZ" "ThumbFinger1Fat.i2z";
connectAttr "ThumbFinger2.fat" "ThumbFinger2Fat.i1y";
connectAttr "ThumbFinger2.fat" "ThumbFinger2Fat.i1z";
connectAttr "ThumbFinger2.fatY" "ThumbFinger2Fat.i2y";
connectAttr "ThumbFinger2.fatZ" "ThumbFinger2Fat.i2z";
connectAttr "ThumbFinger3.fat" "ThumbFinger3Fat.i1y";
connectAttr "ThumbFinger3.fat" "ThumbFinger3Fat.i1z";
connectAttr "ThumbFinger3.fatY" "ThumbFinger3Fat.i2y";
connectAttr "ThumbFinger3.fatZ" "ThumbFinger3Fat.i2z";
connectAttr "ThumbFinger4.fat" "ThumbFinger4Fat.i1y";
connectAttr "ThumbFinger4.fat" "ThumbFinger4Fat.i1z";
connectAttr "ThumbFinger4.fatY" "ThumbFinger4Fat.i2y";
connectAttr "ThumbFinger4.fatZ" "ThumbFinger4Fat.i2z";
connectAttr "IndexFinger1.fat" "IndexFinger1Fat.i1y";
connectAttr "IndexFinger1.fat" "IndexFinger1Fat.i1z";
connectAttr "IndexFinger1.fatY" "IndexFinger1Fat.i2y";
connectAttr "IndexFinger1.fatZ" "IndexFinger1Fat.i2z";
connectAttr "IndexFinger2.fat" "IndexFinger2Fat.i1y";
connectAttr "IndexFinger2.fat" "IndexFinger2Fat.i1z";
connectAttr "IndexFinger2.fatY" "IndexFinger2Fat.i2y";
connectAttr "IndexFinger2.fatZ" "IndexFinger2Fat.i2z";
connectAttr "IndexFinger3.fat" "IndexFinger3Fat.i1y";
connectAttr "IndexFinger3.fat" "IndexFinger3Fat.i1z";
connectAttr "IndexFinger3.fatY" "IndexFinger3Fat.i2y";
connectAttr "IndexFinger3.fatZ" "IndexFinger3Fat.i2z";
connectAttr "IndexFinger4.fat" "IndexFinger4Fat.i1y";
connectAttr "IndexFinger4.fat" "IndexFinger4Fat.i1z";
connectAttr "IndexFinger4.fatY" "IndexFinger4Fat.i2y";
connectAttr "IndexFinger4.fatZ" "IndexFinger4Fat.i2z";
connectAttr "Cup.fat" "CupFat.i1y";
connectAttr "Cup.fat" "CupFat.i1z";
connectAttr "Cup.fatY" "CupFat.i2y";
connectAttr "Cup.fatZ" "CupFat.i2z";
connectAttr "PinkyFinger1.fat" "PinkyFinger1Fat.i1y";
connectAttr "PinkyFinger1.fat" "PinkyFinger1Fat.i1z";
connectAttr "PinkyFinger1.fatY" "PinkyFinger1Fat.i2y";
connectAttr "PinkyFinger1.fatZ" "PinkyFinger1Fat.i2z";
connectAttr "PinkyFinger2.fat" "PinkyFinger2Fat.i1y";
connectAttr "PinkyFinger2.fat" "PinkyFinger2Fat.i1z";
connectAttr "PinkyFinger2.fatY" "PinkyFinger2Fat.i2y";
connectAttr "PinkyFinger2.fatZ" "PinkyFinger2Fat.i2z";
connectAttr "PinkyFinger3.fat" "PinkyFinger3Fat.i1y";
connectAttr "PinkyFinger3.fat" "PinkyFinger3Fat.i1z";
connectAttr "PinkyFinger3.fatY" "PinkyFinger3Fat.i2y";
connectAttr "PinkyFinger3.fatZ" "PinkyFinger3Fat.i2z";
connectAttr "PinkyFinger4.fat" "PinkyFinger4Fat.i1y";
connectAttr "PinkyFinger4.fat" "PinkyFinger4Fat.i1z";
connectAttr "PinkyFinger4.fatY" "PinkyFinger4Fat.i2y";
connectAttr "PinkyFinger4.fatZ" "PinkyFinger4Fat.i2z";
connectAttr "RingFinger1.fat" "RingFinger1Fat.i1y";
connectAttr "RingFinger1.fat" "RingFinger1Fat.i1z";
connectAttr "RingFinger1.fatY" "RingFinger1Fat.i2y";
connectAttr "RingFinger1.fatZ" "RingFinger1Fat.i2z";
connectAttr "RingFinger2.fat" "RingFinger2Fat.i1y";
connectAttr "RingFinger2.fat" "RingFinger2Fat.i1z";
connectAttr "RingFinger2.fatY" "RingFinger2Fat.i2y";
connectAttr "RingFinger2.fatZ" "RingFinger2Fat.i2z";
connectAttr "RingFinger3.fat" "RingFinger3Fat.i1y";
connectAttr "RingFinger3.fat" "RingFinger3Fat.i1z";
connectAttr "RingFinger3.fatY" "RingFinger3Fat.i2y";
connectAttr "RingFinger3.fatZ" "RingFinger3Fat.i2z";
connectAttr "RingFinger4.fat" "RingFinger4Fat.i1y";
connectAttr "RingFinger4.fat" "RingFinger4Fat.i1z";
connectAttr "RingFinger4.fatY" "RingFinger4Fat.i2y";
connectAttr "RingFinger4.fatZ" "RingFinger4Fat.i2z";
connectAttr "Neck.fat" "NeckFat.i1y";
connectAttr "Neck.fat" "NeckFat.i1z";
connectAttr "Neck.fatY" "NeckFat.i2y";
connectAttr "Neck.fatZ" "NeckFat.i2z";
connectAttr "Head.fat" "HeadFat.i1y";
connectAttr "Head.fat" "HeadFat.i1z";
connectAttr "Head.fatY" "HeadFat.i2y";
connectAttr "Head.fatZ" "HeadFat.i2z";
connectAttr "Eye.fat" "EyeFat.i1y";
connectAttr "Eye.fat" "EyeFat.i1z";
connectAttr "Eye.fatY" "EyeFat.i2y";
connectAttr "Eye.fatZ" "EyeFat.i2z";
connectAttr "EyeEnd.fat" "EyeEndFat.i1y";
connectAttr "EyeEnd.fat" "EyeEndFat.i1z";
connectAttr "EyeEnd.fatY" "EyeEndFat.i2y";
connectAttr "EyeEnd.fatZ" "EyeEndFat.i2z";
connectAttr "Jaw.fat" "JawFat.i1y";
connectAttr "Jaw.fat" "JawFat.i1z";
connectAttr "Jaw.fatY" "JawFat.i2y";
connectAttr "Jaw.fatZ" "JawFat.i2z";
connectAttr "JawEnd.fat" "JawEndFat.i1y";
connectAttr "JawEnd.fat" "JawEndFat.i1z";
connectAttr "JawEnd.fatY" "JawEndFat.i2y";
connectAttr "JawEnd.fatZ" "JawEndFat.i2z";
connectAttr "HeadEnd.fat" "HeadEndFat.i1y";
connectAttr "HeadEnd.fat" "HeadEndFat.i1z";
connectAttr "HeadEnd.fatY" "HeadEndFat.i2y";
connectAttr "HeadEnd.fatZ" "HeadEndFat.i2z";
connectAttr "Hip.fat" "HipFat.i1y";
connectAttr "Hip.fat" "HipFat.i1z";
connectAttr "Hip.fatY" "HipFat.i2y";
connectAttr "Hip.fatZ" "HipFat.i2z";
connectAttr "Knee.fat" "KneeFat.i1y";
connectAttr "Knee.fat" "KneeFat.i1z";
connectAttr "Knee.fatY" "KneeFat.i2y";
connectAttr "Knee.fatZ" "KneeFat.i2z";
connectAttr "Ankle.fat" "AnkleFat.i1y";
connectAttr "Ankle.fat" "AnkleFat.i1z";
connectAttr "Ankle.fatY" "AnkleFat.i2y";
connectAttr "Ankle.fatZ" "AnkleFat.i2z";
connectAttr "Heel.fat" "HeelFat.i1y";
connectAttr "Heel.fat" "HeelFat.i1z";
connectAttr "Heel.fatY" "HeelFat.i2y";
connectAttr "Heel.fatZ" "HeelFat.i2z";
connectAttr "Toes.fat" "ToesFat.i1y";
connectAttr "Toes.fat" "ToesFat.i1z";
connectAttr "Toes.fatY" "ToesFat.i2y";
connectAttr "Toes.fatZ" "ToesFat.i2z";
connectAttr "FootSideInner.fat" "FootSideInnerFat.i1y";
connectAttr "FootSideInner.fat" "FootSideInnerFat.i1z";
connectAttr "FootSideInner.fatY" "FootSideInnerFat.i2y";
connectAttr "FootSideInner.fatZ" "FootSideInnerFat.i2z";
connectAttr "FootSideOuter.fat" "FootSideOuterFat.i1y";
connectAttr "FootSideOuter.fat" "FootSideOuterFat.i1z";
connectAttr "FootSideOuter.fatY" "FootSideOuterFat.i2y";
connectAttr "FootSideOuter.fatZ" "FootSideOuterFat.i2z";
connectAttr "ToesEnd.fat" "ToesEndFat.i1y";
connectAttr "ToesEnd.fat" "ToesEndFat.i1z";
connectAttr "ToesEnd.fatY" "ToesEndFat.i2y";
connectAttr "ToesEnd.fatZ" "ToesEndFat.i2z";
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asRedSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asRed2SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asGreenSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asGreen2SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asBlueSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asBlue2SG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asWhiteSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asBlackSG.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "asBonesSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asRedSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asRed2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asGreenSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asGreen2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asBlueSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asBlue2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asWhiteSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asBlackSG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "asBonesSG.message" ":defaultLightSet.message";
connectAttr "layerManager.dli[0]" "defaultLayer.id";
connectAttr "renderLayerManager.rlmi[0]" "defaultRenderLayer.rlid";
connectAttr "layerManager.dli[1]" "Hi.id";
connectAttr "asRed.oc" "asRedSG.ss";
connectAttr "asRedSG.msg" "materialInfo1.sg";
connectAttr "asRed.msg" "materialInfo1.m";
connectAttr "asRed2.oc" "asRed2SG.ss";
connectAttr "asRed2SG.msg" "materialInfo2.sg";
connectAttr "asRed2.msg" "materialInfo2.m";
connectAttr "asGreen.oc" "asGreenSG.ss";
connectAttr "asGreenSG.msg" "materialInfo3.sg";
connectAttr "asGreen.msg" "materialInfo3.m";
connectAttr "asGreen2.oc" "asGreen2SG.ss";
connectAttr "asGreen2SG.msg" "materialInfo4.sg";
connectAttr "asGreen2.msg" "materialInfo4.m";
connectAttr "asBlue.oc" "asBlueSG.ss";
connectAttr "asBlueSG.msg" "materialInfo5.sg";
connectAttr "asBlue.msg" "materialInfo5.m";
connectAttr "asBlue2.oc" "asBlue2SG.ss";
connectAttr "asBlue2SG.msg" "materialInfo6.sg";
connectAttr "asBlue2.msg" "materialInfo6.m";
connectAttr "asWhite.oc" "asWhiteSG.ss";
connectAttr "asWhiteSG.msg" "materialInfo7.sg";
connectAttr "asWhite.msg" "materialInfo7.m";
connectAttr "asBlack.oc" "asBlackSG.ss";
connectAttr "asBlackSG.msg" "materialInfo8.sg";
connectAttr "asBlack.msg" "materialInfo8.m";
connectAttr "asBones.oc" "asBonesSG.ss";
connectAttr "asBonesSG.msg" "materialInfo9.sg";
connectAttr "asBones.msg" "materialInfo9.m";
connectAttr "asRedSG.pa" ":renderPartition.st" -na;
connectAttr "asRed2SG.pa" ":renderPartition.st" -na;
connectAttr "asGreenSG.pa" ":renderPartition.st" -na;
connectAttr "asGreen2SG.pa" ":renderPartition.st" -na;
connectAttr "asBlueSG.pa" ":renderPartition.st" -na;
connectAttr "asBlue2SG.pa" ":renderPartition.st" -na;
connectAttr "asWhiteSG.pa" ":renderPartition.st" -na;
connectAttr "asBlackSG.pa" ":renderPartition.st" -na;
connectAttr "asBonesSG.pa" ":renderPartition.st" -na;
connectAttr "asRed.msg" ":defaultShaderList1.s" -na;
connectAttr "asRed2.msg" ":defaultShaderList1.s" -na;
connectAttr "asGreen.msg" ":defaultShaderList1.s" -na;
connectAttr "asGreen2.msg" ":defaultShaderList1.s" -na;
connectAttr "asBlue.msg" ":defaultShaderList1.s" -na;
connectAttr "asBlue2.msg" ":defaultShaderList1.s" -na;
connectAttr "asWhite.msg" ":defaultShaderList1.s" -na;
connectAttr "asBlack.msg" ":defaultShaderList1.s" -na;
connectAttr "asBones.msg" ":defaultShaderList1.s" -na;
connectAttr "defaultRenderLayer.msg" ":defaultRenderingList1.r" -na;
// End of Test_fit_v5.ma
