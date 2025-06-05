//============================================================================
// Name        : main.cpp
// Author      : Pablo
// Version     :
// Copyright   : Hecho para Óptima.
// Description : Hello World in C++, Ansi-style
//============================================================================

#include <Initializer.h>
#include <InputReader.h>
#include <MapCreationDTO.h>
#include <MapManager.h>
#include <OutputWriter.h>
#include <colormod.h>
#include <InitializationStrategies.h>
#include <opencv2/core/hal/interface.h>
#include <opencv2/core/mat.hpp>
#include <opencv2/core/mat.inl.hpp>
#include <opencv2/core/types.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <cstdlib>
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <math.h>
#include <fstream>
#include <iostream>
#include <numeric>
//# define M_PI 3.14159265358979323846

using namespace std;
using namespace ORB_SLAM2;
typedef pair<int, int> Match;
class InputParser;
void scaleMap(MapManager* mpMapManager, InputReader* mpInputReader);
void fillMap(InitializationStrategy* mpInitializationStrategy, int numFrames, MapManager* mpMapManager, InputReader* mpInputReader);

int main(int argc, char **argv) {
	Color::Modifier red(Color::FG_RED);
	Color::Modifier yellow(Color::FG_YELLOW);
	Color::Modifier green(Color::FG_GREEN);
	Color::Modifier def(Color::FG_DEFAULT); 
	InputParser* inputParser = new InputParser(argc, argv);
	inputParser->checkArgs();

	if(!inputParser->calibFlag || !inputParser->outputFlag || !inputParser->detectionsFlag){
		cout<<endl<<red<<"LOS ARGUMENTOS '-c', '-d' y '-o' SON OBLIGATORIOS."<<endl;
		return 0;
	}
	

	//Rellenar variables con info del archivo
	InputReader* mpInputReader = new InputReader(inputParser);
	//return 0;
	if (mpInputReader->error){
		cout<<red<<"HUBO UN ERROR EN LA LECTURA DE LOS ARCHIVOS DE ENTRADA."<<endl;
		return -1;
	}
	cv::Mat mK = mpInputReader->GetK();
	//mpInputReader->showRadios();
	//return 0;


	
	int numFrames = mpInputReader->GetNumFrames();
	if (numFrames < 2) {
		cout<<red<< "NO HAY SUFICIENTES FRAMES PARA INICIALIZAR EL MAPA." << endl;
		return 0;
	}


	//Inicializar Mapa
	float distancia_inicializacion = mpInputReader->GetInitDist();
	cout<<endl<<distancia_inicializacion<<endl;
	InitializationStrategy* mpInitializationStrategy =
		FactoryInitializationStrategies::Get()->CreateInitializationStrategy(1, mpInputReader, distancia_inicializacion);

	MapManager* mpMapManager = mpInitializationStrategy->initialize();
	if(!mpMapManager) return -1;


	//Iterar sobre los frames para procesar las observaciones
	fillMap(mpInitializationStrategy, numFrames, mpMapManager, mpInputReader);

	//Calibrar Mapa en centimetros
	float scaleFactor = -1.0;
	if(inputParser->scaleFlag) scaleMap(mpMapManager, mpInputReader);
	else cout<<endl<<yellow<<"EL MAPA NO SERÁ ESCALADO PORQUE NO SE HA PASADO EL ARGUMENTO '-x'."<<def<<endl;


	//Generar salidas
	int f0 = mpInitializationStrategy->f0; int f1 = mpInitializationStrategy->f1;
	OutputWriter* mpOutputWriter = new OutputWriter(inputParser, mpInputReader,f0,f1);
	mpOutputWriter->calcularReproyecciones(mpMapManager, mpInputReader, inputParser->scaleFlag);
	string filename = "/Reproyecciones.csv";
	mpOutputWriter->guardarTriangulacion(filename, inputParser->scaleFlag);
	bool graficarNoVisibles = true;
	if(inputParser->imagesFlag) mpOutputWriter->graficarReproyecciones(mpInputReader, graficarNoVisibles, false);
	cout<< endl<<green<< "SALIDAS GUARDADAS EN " << mpOutputWriter->getStrOutputPath()<< endl;

	return 0;
}

void scaleMap(MapManager* mpMapManager, InputReader* mpInputReader){
	Color::Modifier yellow(Color::FG_YELLOW);
	Color::Modifier def(Color::FG_DEFAULT);	
	Color::Modifier green(Color::FG_GREEN); 
	string x = "-x";
	float distancia_calibracion = mpInputReader->getScaleDistance();
	float scaleFactor = mpMapManager->GetScaleFactor(distancia_calibracion);
	if (scaleFactor > 0){
		mpMapManager->ScaleMap(scaleFactor);
		cout<<endl<<green<<"EL MAPA FUE ESCALADO EXITOSAMENTE. "<<def<<endl;
	} 
}

void fillMap(InitializationStrategy* mpInitializationStrategy, int numFrames, MapManager* mpMapManager, InputReader* mpInputReader)
{
	int f0 = mpInitializationStrategy->f0;
	int f1 = mpInitializationStrategy->f1;
	vector<int> kfBefore,kfBetween,kfAfter,kfRestantes;
	for (int i = 0; i < numFrames; i++) {
		if (i < f0) kfBefore.push_back(i);
		if (i > f0 && i < f1) kfBetween.push_back(i);
		if (i > f1) kfAfter.push_back(i);
	}
	kfRestantes.reserve(kfBefore.size() + kfBetween.size() + kfAfter.size());
	kfRestantes.insert(kfRestantes.end(),kfBetween.begin(),kfBetween.end());
	kfRestantes.insert(kfRestantes.end(),kfAfter.begin(),kfAfter.end());
	kfRestantes.insert(kfRestantes.end(),kfBefore.rbegin(),kfBefore.rend());
	for (auto i : kfRestantes) {
		mpMapManager->CreateNewKeyFrame(i, mpInputReader);
	}
}

