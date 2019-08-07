from ROOT import *
from HiggsAnalysis.Hgg_Signal_Bkg_Fit_Plotter.NiceColors import *
import argparse, sys
from HiggsAnalysis.Hgg_Signal_Bkg_Fit_Plotter.MyCMSStyle import *

# function definition
def MakeNewData(dataset,var):
   arg = dataset.get()
   print 'arg:'
   arg.Print()
   new_dataset = dataset.binnedClone("new_dataset","new_dataset")
   new_dataset.Print()
   out_dataset = new_dataset.emptyClone("empty_dataset","empty_dataset")
   out_dataset.Print()
   for binN in range(0,80):
   	binCenter = new_dataset.get(binN).getRealValue("mGammaGamma_bin2")
   	binContent = new_dataset.weight()
   	binErr = new_dataset.weightError()
	#print 'biN, Center, Content,  WeightErr = ',binN, binCenter,binContent,binErr
	y[binN] = binContent
	print 'biN, x, y  = ',binN, x[binN], y[binN]
	if binContent==0.0 :
		#print binN
		#out_dataset.set(out_dataset.get(binN),5,-100.0,100.0)
		out_dataset.set(out_dataset.get(binN),0.,-100.0,100.0)
#		#out_dataset.set(out_dataset.get(binN),1e-12,1.0,1.0)
		ey[binN] = 1.8 
	else:
		out_dataset.set(out_dataset.get(binN),binContent,binErr,binErr)
		ey[binN] = binErr 
	#print 'biN, ey = ',binN, ey[binN]
   return (out_dataset, y, ey)

def MakeTH1Hist(x, y, ey):
   h1f = TFile("h1.root", "RECREATE")
   h1 = TH1F("h1","h1",80,100,180)
   for binN in range(0,80):
	h1.SetBinContent(binN, y[binN])
	h1.SetBinError(binN, ey[binN])
        h1.SetBinErrorOption(TH1.kPoisson)
   c1 = TCanvas("c1", "c1", 800, 600)
   h1.Draw("pe")
   c1.SaveAs("h1.png")
   c1.Write()
   h1f.Close()
   return h1

def MakeFullBackgroundPdf(bkg_pdf, bkg_norm, hig_pdfs, hig_norms):
  if len(hig_pdfs) == 0: 
   	print 'No HIG background found'
	return bkg_pdf
  argPdfs = RooArgList()
  argNorms = RooArgList()
  argPdfs.add(bkg_pdf)
  argNorms.add(bkg_norm)
  if len(hig_pdfs) != len(hig_norms):
    print "list of higgs pdfs has different size wrt normalizations!"
    return None
  for hh in range(0, len(hig_pdfs)):
    hig_pdfs[hh].Print()
    argPdfs.add(hig_pdfs[hh])
    argNorms.add(hig_norms[hh])
  argNorms.Print()
  argPdfs.Print()
  if argNorms.getSize() != argPdfs.getSize():
    print 'ArgNorms and ArgPdfs have different sizes!'
    return None
  totPdf = RooAddPdf('totBkg', 'Nonresonant + single H background', argPdfs, argNorms)
  return totPdf

def MakeFullPdf(totBkg_pdf, totBkg_norm, sig_pdf, sig_norm):
  argPdfs = RooArgList()
  argNorms = RooArgList()
  argPdfs.add(totBkg_pdf)
  argNorms.add(totBkg_norm)
  argPdfs.add(sig_pdf)
  argNorms.add(sig_norm)
  argNorms.Print()
  argPdfs.Print()
  if argNorms.getSize() != argPdfs.getSize():
    print 'ArgNorms and ArgPdfs have different sizes!'
    return None
  totPdf = RooAddPdf('totBkg', 'Bkg + Signal', argPdfs, argNorms)
  return totPdf

def MakeFullPDF(bkg_pdf, bkg_norm, hig_pdfs, hig_norms, sig_pdf, sig_norm):
  if len(hig_pdfs) == 0: 
   	print 'No HIG background found'
	return bkg_pdf
  argPdfs = RooArgList()
  argNorms = RooArgList()
  argPdfs.add(bkg_pdf)
  argPdfs.add(sig_pdf)
  argNorms.add(bkg_norm)
  argNorms.add(sig_norm)
  if len(hig_pdfs) != len(hig_norms):
    print "list of higgs pdfs has different size wrt normalizations!"
    return None
  for hh in range(0, len(hig_pdfs)):
    hig_pdfs[hh].Print()
    argPdfs.add(hig_pdfs[hh])
    argNorms.add(hig_norms[hh])
  argNorms.Print()
  argPdfs.Print()
  if argNorms.getSize() != argPdfs.getSize():
    print 'ArgNorms and ArgPdfs have different sizes!'
    return None
  totPdf = RooAddPdf('totBkg', 'Nonresonant + single H background', argPdfs, argNorms)
  return totPdf

# load lib
gSystem.Load("libHiggsAnalysisCombinedLimit.so")
gROOT.SetBatch(kTRUE)

# cmd parser
parser =  argparse.ArgumentParser(description='Background fit plot maker')
parser.add_argument('-i', '--inputFile', dest="dname", type=str, default=None, required=True)
parser.add_argument('-o', '--outFile', dest="outf", type=str, default=".")
parser.add_argument('-L', '--lumi', dest='lumi', type=str, default='35.9')
parser.add_argument('-Sn', '--signalNormalization', dest='snorm', type=float, default=[10.0,10.0], nargs='+')
parser.add_argument('-Sf', '--signalFactor', dest='fsignal', type=float, default=[10.0,10.0], nargs='+')
parser.add_argument('-H', '--addHiggs', dest='addh', action='store_true', default=False)
parser.add_argument('-Hl', '--higgsList', dest='hlist', type=str, default=None, nargs='+',
                           choices=['ggh', 'vbf', 'tth', 'vh', 'bbh'] )
parser.add_argument('-t', '--text', dest='text', type=str, default='')
parser.add_argument('-u', '--unblind', dest='unblind', default=False, action='store_true')

opt = parser.parse_args()

tfile = TFile(opt.dname, "READ")
ofile = TFile(opt.outf+".root", "RECREATE")

w_all = tfile.Get("MaxLikelihoodFitResult")

w_all.Print()

cats = [2]
if 'High' in opt.outf or 'High' in opt.text: cats = [2,3]

Higgses = opt.hlist
if Higgses == None: Higgses = ['SMH']
#if Higgses == None: Higgses = ['ggh', 'vbf', 'tth', 'vh', 'bbh']

dims = [ 'mGammaGamma']
bins = [ 80]
xtitle = [ 'm_{#gamma#gamma} [GeV]']
ytitle = [ 'Events/(1 GeV)']
yLimits = {'mGammaGamma': [14, 90, 14, 60]}

x = [100.5+ix for ix in range(0,80)]
exl = [0.5 for ix in range(0,80)]
exh = [0.5 for ix in range(0,80)]
y = [0.0 for ix in range(0,80)]
ey = [1.8 for ix in range(0,80)]
eyl = [1.8 for ix in range(0,80)]
eyh = [1.8 for ix in range(0,80)]

for cc in cats:
 for iobs,obs in enumerate(dims):

  intc = 0
  print(cc, iobs, obs+'_bin'+str(cc))
  #if intc > 1: intc = cc - 2

  var = w_all.var(obs+'_bin'+str(cc))
  data_cat = w_all.obj('CMS_channel')
  catbin = ''
  #catbin = 'ch1_cat'
  #if cc == 0 or cc == 1: catbin = 'ch2_cat'
  data_cat.setRange("catcut",catbin+str(cc))
  print 'var'
  var.Print()
  print 'data_cat'
  data_cat.Print()

  sig_pdf_name = 'shapeSig_signal_bin'+str(cc)
  print sig_pdf_name
  sig_pdf = w_all.pdf(sig_pdf_name)
  sig_pdf.Print()
  normName = 'n_exp_final_binbin'
  sig_norm = RooRealVar('sig_norm', 'signal norm', w_all.obj(normName+str(cc)+'_proc_signal').getVal())
  print sig_norm

  bkg_pdf_name = 'shapeBkg_Bkg_bin'+str(cc)
  bkg_pdf = w_all.pdf(bkg_pdf_name)
  bkg_pdf.Print()
  #if cc == 0 or cc == 1: normName = 'n_exp_final_binch2_cat'
  bkg_norm = RooRealVar('bkg_norm', 'nonres bkg norm', w_all.obj(normName+str(cc)+'_proc_Bkg').getVal())
  print bkg_norm

  data2d = w_all.data("data_obs")
  data2d.Print()
  
  #data = data2d.reduce(RooArgSet(RooFit.CutRange('catcut')))
  #data = data2d.reduce(RooFit.CutRange('catcut'))
  #data = data2d.reduce("y==0")
  #hist_data = data2d.createHistogram("xaxis","yaxis",80,1)
  data = data2d
  data.Print()
#  sys.exit()

  hig_pdfs = []
  hig_norms = []
  totHiggs = 0
  if 1==1:
    for hh in Higgses:
      hig_pdf_name = 'shapeBkg_'+hh+'_bin'+str(cc)
      print hig_pdf_name
      hig_pdf = w_all.pdf(hig_pdf_name)
      hig_pdf.Print()
      hig_pdfs.append(hig_pdf)
      normNameHIG = 'n_exp_final_binbin'
      #if cc == 0 or cc == 1: normNameHIG = 'n_exp_binch2_cat'
      norm = RooRealVar(hh+'_norm', hh+' bkg norm', w_all.obj(normNameHIG+str(cc)+'_proc_'+hh).getVal() )
      hig_norms.append(norm)
      print hig_pdf_name, norm.getVal()
      totHiggs += w_all.obj(normNameHIG+str(cc)+'_proc_'+hh).getVal()

  totBkg = MakeFullBackgroundPdf(bkg_pdf, bkg_norm, hig_pdfs, hig_norms)
  totBkgNorm = totHiggs + bkg_norm.getVal()
  totBkgN_norm = totBkg.getNorm()
#  print totBkg
  print 'Total nonres:', bkg_norm.getVal(), 'total higgs:', totHiggs, 'total bkg', totBkgNorm
  print 'Total bkg:', totBkgN_norm
#  sys.exit()
  tot = MakeFullPDF(bkg_pdf, bkg_norm, hig_pdfs, hig_norms, sig_pdf, sig_norm)
  #tot = MakeFullPdf(totBkg, totBkgN_norm, sig_pdf, sig_norm)
  totNorm = totBkgNorm + sig_norm.getVal()
  print 'Total: ', totNorm, totBkgNorm, sig_norm.getVal()

  binning = bins[iobs]

  var.setRange("ALL",100,180)
  data, y, ey = MakeNewData(data2d,var)
  print y

  frame = var.frame(RooFit.Title(" "),RooFit.Bins(binning))
  dataind = 0
  #MakeNewData(data2d,var)
  #data_h1 = MakeTH1Hist(x,y,ey)


  #bkg_pdf.plotOn(frame,RooFit.LineColor(cNiceGreenDark), RooFit.LineStyle(kDashed), RooFit.Precision(1E-5), RooFit.Normalization(bkg_norm.getVal(), RooAbsReal.NumEvent))
#  tot.plotOn(frame,RooFit.LineColor(cNiceGreenDark), RooFit.LineStyle(kDashed), RooFit.Precision(1E-5), RooFit.Normalization(totNorm, RooAbsReal.NumEvent))
#  totBkg.plotOn(frame,RooFit.LineColor(cNiceBlueDark),RooFit.Precision(1E-5), RooFit.Normalization(totBkgNorm, RooAbsReal.NumEvent))
#  sig_pdf.plotOn(frame,RooFit.LineColor(cNiceRed), RooFit.Precision(1E-5), RooFit.Normalization(opt.snorm[intc]*opt.fsignal[intc],RooAbsReal.NumEvent))
  totBkg.plotOn(frame,RooFit.LineColor(cNiceBlueDark), RooFit.LineStyle(kDashed), RooFit.Precision(1E-5), RooFit.Normalization(totBkgNorm, RooAbsReal.NumEvent))
  sig_pdf.plotOn(frame,RooFit.LineColor(cNiceRed), RooFit.LineStyle(kDashed), RooFit.Precision(1E-5), RooFit.Normalization(sig_norm.getVal(),RooAbsReal.NumEvent))
  tot.plotOn(frame,RooFit.LineColor(cNiceGreenDark), RooFit.Precision(1E-5), RooFit.Normalization(totBkgNorm+sig_norm.getVal(), RooAbsReal.NumEvent))
  #tot.plotOn(frame,RooFit.LineColor(cNiceGreenDark), RooFit.Precision(1E-5), RooFit.Normalization(totNorm, RooAbsReal.NumEvent))
#  data.plotOn(frame,RooFit.DataError(RooAbsData.SumW2),RooFit.XErrorSize(0))


  #datahist = frame.getObject(0)
  #print 'data2d,data,datahist',data2d,data,datahist 
  #histo = data.createHistogram("histo",80,1,1)
  #bkghist = frame.getObject(dataind+1)
  toth = frame.getObject(dataind+2)
  totbkgh = frame.getObject(dataind+0)
  sigh = frame.getObject(dataind+1)

  data_h1 = TH1F("h1","h1",80,101,181)
  data_h1.SetLineColor(1)
  data_h1.SetMarkerColor(1)
  data_h1.SetMarkerSize(1)
  data_h1.SetMarkerStyle(20)
  for binN in range(0,80):
	data_h1.SetBinContent(binN, y[binN])
	data_h1.SetBinError(binN, ey[binN])
        data_h1.SetBinErrorOption(TH1.kPoisson)
	print 'data_h1', binN, data_h1.GetBinCenter(binN), y[binN]

  leg = TLegend(0.5, 0.55, 0.89, 0.89)
  leg.SetBorderSize(0)
  leg.SetFillStyle(0)
  leg.SetTextFont(43)
  leg.SetTextSize(20)
#  leg.SetNColumns(3)
  #leg.AddEntry(datahist, 'Data', 'pe')
  leg.AddEntry(data_h1, 'Data', 'pe1')
  leg.AddEntry(totbkgh, 'Total background', 'l')
  #leg.AddEntry(bkghist, 'Nonresonant background', 'l')
#  sigText = 'SM HH Signal (x20)'
#  if int(intc) == 1:
  sigText = 'Signal'
  #sigText = 'SM Higgs (x'+str(int(opt.fsignal[intc]))+')'
  leg.AddEntry(sigh, sigText, 'l')
  leg.AddEntry(toth, 'Signal plus background', 'l')

  SetGeneralStyle()
  c = TCanvas("c", "c", 800, 600)
  frame.Draw('')
  frame.GetXaxis().SetTitle(xtitle[iobs])
  frame.GetYaxis().SetTitle(ytitle[iobs])
  frame.SetMaximum(yLimits[obs][intc])
  frame.SetMinimum(0.000)
  leg.Draw('same')
  data_h1.Draw('pe1same')
  c.Update()
  SetPadStyle(c)
  c.Update()
  SetAxisTextSizes(frame)
  c.Update()

  topy = 0.91
  stepy = 0.08
  tlatex = TLatex()
  tlatex.SetNDC()
  tlatex.SetTextAngle(0)
  tlatex.SetTextColor(kBlack)
  tlatex.SetTextFont(63)
  tlatex.SetTextAlign(11)
  tlatex.SetTextSize(25)
#  tlatex.DrawLatex(0.11, topy, "CMS")
  tlatex.SetTextFont(53)
#  tlatex.DrawLatex(0.18, topy, "Preliminary")
  tlatex.SetTextFont(43)
  tlatex.SetTextSize(20)
  tlatex.SetTextAlign(31)
#  tlatex.DrawLatex(0.9, topy, "L = " + str(opt.lumi) + " fb^{-1} (13 TeV)")
  tlatex.SetTextAlign(11)
  tlatex.SetTextSize(25)
  Cat = ""
  #if int(intc) == 1:
  #  Cat = "Medium-purity category"
  if "|" in opt.text:
    an = opt.text.split("|")
#               tlatex.SetTextFont(63)
    tlatex.DrawLatex(0.14, topy-stepy*1, an[0])
#               tlatex.SetTextFont(43)
    tlatex.DrawLatex(0.14, topy-stepy*2, an[1])
    tlatex.DrawLatex(0.14, topy-stepy*3, Cat)
  else:
#               tlatex.SetTextFont(63)
    tlatex.DrawLatex(0.14, topy-stepy*1, opt.text)
#               tlatex.SetTextFont(43)
    tlatex.DrawLatex(0.14, topy-stepy*2, Cat)

  DrawCMSLabels(c, '77.5')
  c.Update()
  c.SaveAs(opt.outf+str(cc) + obs+".pdf")
  c.SaveAs(opt.outf+str(cc) + obs+".png")
  c.SaveAs(opt.outf+str(cc) + obs+".C")
  #datahist.Write()
  #hist_data.Write()
  frame.Write()
  data_h1.Write()
  c.Draw()
  c.Write()

ofile.Close()
