#include "/Users/jburgess/Research/bayes_blocks/bayesblocks/include/BinnedBB.hh" 
#include "/Users/jburgess/Research/bayes_blocks/bayesblocks/include/lightcurve.hh"
#include<iostream>
#include<fstream>



int main(int argc, char *argv[])
{

  BinnedBB *bb = new BinnedBB();
  std::vector<int> *test = NULL;
  lightcurve *lc = NULL; 
  int NUM_EVTS = atoi( argv[1]);
  double START_TIME = atof(argv[2]);
  double NCP_PRIOR = atof(argv[3]);


  std::cout<< "Starting bayesblocks with \n"
	   <<NUM_EVTS<< " bins\n"
           <<START_TIME<< " start time\n"
           <<NCP_PRIOR<< " ncp_prior\n";


  double *data = new double [NUM_EVTS];
  double *binSizes = new double [NUM_EVTS];
  
  ifstream content, bins;
  ofstream lightCurve;
 
  bins.open("tmpBins.txt");
  content.open("tmpContents.txt");


  for (int i= 0; i<NUM_EVTS; i++)
    {
      bins >> binSizes[i];
      content >> data[i];
    }

 
  bb->SetStartTime(START_TIME);
  bb->SetData(data,NUM_EVTS);
  bb->SetBinSizes(binSizes);
  bb->GlobalOptimum(NCP_PRIOR);
  lc = bb->GetLightcurve();
  
  lightCurve.open("tmpLightCurve.txt");


  

  for ( int i = 0; i<lc->bins.size(); i++ )
    {
   
      lightCurve << lc->bins[i]<< "\t" <<lc->content[i] <<"\n";
    }
  
  lightCurve.close();
  content.close();
  bins.close();

  // bb->PrintLightCurve();


  return 0;
}
