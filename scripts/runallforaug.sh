### temporarily source the venv which jupyter operates on... sloppily located at ~/Desktop/python/python279/venv
### This script can only be run as user "evan", and is to be run from the directory that this file is located in.
source ~/Desktop/python/python279/venv/bin/activate
cd ..
python lp_loop.py
python resultsToIMG.py
DATE=`date +%Y%m%d`
cd images
mkdir $DATE
mv Adistributions_page.png Adistributions_pageset.png Adistributions_prod.png feature_counts.png Mdistributions.png page.png pageset.png prod.png solution_example.png -t $DATE
cd ../output
mkdir $DATE
mv atts.txt importanceDict.txt page_ms.txt pageset_ms.txt product_ms.txt -t $DATE
deactivate
