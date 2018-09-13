exe: gen_help.o BCH.o Tools.o
	g++ gen_help.o BCH.o Tools.o -o exe

gen_help.o: gen_help.cpp
	g++ -c gen_help.cpp

BCH.o: BCH.cpp BCH.h
	g++ -c BCH.cpp

Tools.o:Tools.cpp Tools.h
	g++ -c Tools.cpp

clean:
	rm *.o