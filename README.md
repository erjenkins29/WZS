## Definitions
- product problem:
- page problem:
- pageset problem:
- problem-type: either the product problem, page problem, or pageset problem.  
- LP: linear programming

### 1. project structure:
$WZS is the main directory, which contains the following folder structure:
- WZS/bak -- for backing up anything
- WZS/data -- raw data to be read by scripts
- WZS/eda -- folder for exploratory data analysis (ipython notebooks)
- WZS/examples -- .py files containing the input for each problem type.  "nicest" form of the data (e.g. what the data looks like after post-processing).  Use these to understand results of solutions
- WZS/images -- imaged versions of output from various scripts
- WZS/output -- where output from scripts goes

### 2. modules:
these are python modules meant for importing into scripts for analysis or automation.
- WZS/rankLP.py -- contains data transformation functions, LP problem creation methods, and a function for forcing a solution to an LP problem
- WZS/emailnotice.py (no read/write access) -- contains function emailEvan(msg), which sends a string msg to my email address.  import with the following syntax: "from emailnotice import emailEvan"
- WZS/examples/df9xx.py -- contains a transformed dataframe.  import with the following syntax:  "from examples.df922 import df"

Sidenote:  notice the __init__.py files, these are empty files to help python understand where to look for modules.

### 3. scripts:
- WZS/runall.sh -- runs the following two scripts in succession
- WZS/lp_loop.py -- loops 400 times through each problem-type to find a set of solutions.  400 iterations takes 12-14 hours on average.
- WZS/resultsToIMG.py -- run after the lp_loop function. converts the output data into user-friendly images for viewing.

### 4. data:
raw data located in WZS/data
post-processed data importable via WZS/examples/df9xx-- see part 2.

### 5. documentation:
- Problem Statement.ipynb -- Problem/solution summary document
- rankLP walkthrough.ipynb -- guide for how to use the rankLP module
- README -- contains these details + more specifics on the specific modules/scripts.


## How to execute scripts

##### >./runall.sh

runs the two scripts detailed below.  must be in the $WZS project directory to execute, running as user evan.

##### > python lp_loop,py

will loop 400 times over each problem type, forcing a solution each time.  On a 70 row, 40-ish column dataset, this usually takes <2 minutes per iteration, so 400 iterations will take somewhere between 10-14 hours.

Output: 4 files, stored in $WZS/output/
$WZS/output/MimportanceDict.txt - dict of lists, storing the number of solutions per iteration per problem-type
$WZS/output/page_ms.txt
$WZS/output/pageset_ms.txt
$WZS/output/product_ms.txt


##### > python resultsToIMG.py

requires that lp_loop completed without error, generating the 4 output files mentioned above.  generates image summaries of the results.

Output: 5 images, stored in $WZS/images/
$WZS/images/feature_counts.png
$WZS/images/Mdistributions.png
$WZS/images/page.png
$WZS/images/pageset.png
$WZS/images/prod.png
