#!/bin/bash
#Compilo los fuentes

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/Converter.d" -MT"src/Converter.o" -o "src/Converter.o" "../src/Converter.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/Converter2D-3D.d" -MT"src/Converter2D-3D.o" -o "src/Converter2D-3D.o" "../src/Converter2D-3D.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/InitializationStrategies.d" -MT"src/InitializationStrategies.o" -o "src/InitializationStrategies.o" "../src/InitializationStrategies.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/Initializer.d" -MT"src/Initializer.o" -o "src/Initializer.o" "../src/Initializer.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -std=c++17 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/InputReader.d" -MT"src/InputReader.o" -o "src/InputReader.o" "../src/InputReader.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/KeyFrame.d" -MT"src/KeyFrame.o" -o "src/KeyFrame.o" "../src/KeyFrame.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/Map.d" -MT"src/Map.o" -o "src/Map.o" "../src/Map.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/MapManager.d" -MT"src/MapManager.o" -o "src/MapManager.o" "../src/MapManager.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/MapPoint.d" -MT"src/MapPoint.o" -o "src/MapPoint.o" "../src/MapPoint.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/Optimizer.d" -MT"src/Optimizer.o" -o "src/Optimizer.o" "../src/Optimizer.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/OutputWriter.d" -MT"src/OutputWriter.o" -o "src/OutputWriter.o" "../src/OutputWriter.cc" -w

g++ -I$OPENCV_INCLUDE -I$EIGEN3_INCLUDE -I$PROJECT_INCLUDE -O0 -g3 -Wall -c -fmessage-length=0 -MMD -MP -MF"src/main.d" -MT"src/main.o" -o "src/main.o" "../src/main.cpp" -w

#Linkeo los archivos compilados para generar el ejecutable

g++ -L$OPENCV_LIB -L$G2O_LIB -o "triangulacionDeBayas"  ./src/Converter.o ./src/Converter2D-3D.o ./src/InitializationStrategies.o ./src/Initializer.o ./src/InputReader.o ./src/KeyFrame.o ./src/Map.o ./src/MapManager.o ./src/MapPoint.o ./src/Optimizer.o ./src/OutputWriter.o ./src/main.o  -lopencv_imgcodecs -lopencv_calib3d -lpthread -lopencv_imgproc -lopencv_core -lg2o

