# Hgg_Signal_Bkg_Fit_Plotter

## Installation
First, setup the environment with the Higgs Combination tools: https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideHiggsAnalysisCombinedLimit
Currently working with 74X (check latest on HiggsCombine twiki).


#### Step 1: Get Combine   

```
export SCRAM_ARCH=slc6_amd64_gcc491
cmsrel CMSSW_7_4_7
cd CMSSW_7_4_7/src
cmsenv
git clone https://github.com/cms-analysis/HiggsAnalysis-CombinedLimit.git HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit
git fetch origin
git checkout v6.3.1
scramv1 b clean
scramv1 b
```

#### Step 2: Get bbggLimits code    
```
cd ${CMSSW_BASE}/src/HiggsAnalysis/
git clone  https://github.com/maojiajing/Hgg_Signal_Bkg_Fit_Plotter.git
cd ${CMSSW_BASE}/src/HiggsAnalysis/Hgg_Signal_Bkg_Fit_Plotter/
scramv1 b
```
## Maximum Likelihood Fit
```
cd ${CMSSW_BASE}/src/HiggsAnalysis/Hgg_Signal_Bkg_Fit_Plotter/
cmsenv
cd test/
combine --datacard HggRazorCard_bin13.txt -M MaxLikelihoodFit --saveWorkspace --saveShapes --saveNormalization --X-rtd TMCSO_AdaptivePseudoAsimov=50 -n SMHHForBkgPlots
```

## PLotting

## Total Background
```
python ../scripts/TotalBkg_JM.py -i MaxLikelihoodFitResult.root -o test_out --signalNormalization 0.37697 0.35948 --signalFactor 20 100 --addHiggs --text "TEST" --unblind

```

## Background Only Fit
```
python ../scripts/BOnly_JM.py -i MaxLikelihoodFitResult.root -o test_out_bin13_BOnly_ --signalNormalization 1 0.35948 --signalFactor 1 100 --addHiggs --text "TEST" --unblind

```
## Signal plus background Fit 
```
python ../scripts/SnB_JM.py -i MaxLikelihoodFitResult.root -o test_out_bin13_SnB_ --signalNormalization 1 0.35948 --signalFactor 1 100 --addHiggs --text "TEST" --unblind
```
