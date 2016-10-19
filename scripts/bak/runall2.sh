### temporarily source the venv which jupyter operates on... sloppily located at ~/Desktop/python/python279/venv
### This script can only be run as user "evan", and is to be run from the directory that this file is located in.
source ~/Desktop/python/python279/venv/bin/activate
python lp_loop_test_thresholds.py
python resultsToIMG.py
DATE=`date +%Y%m%d`
cd images
mkdir $DATE
mv feature_counts.png Mdistributions.png page.png pageset.png prod.png solution_example.png -t $DATE
cd ../output
mkdir $DATE
mv importanceDict.txt page_ms.txt pageset_ms.txt product_ms.txt -t $DATE
