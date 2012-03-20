all: perf.o 
	gcc perf.o ../client/lib739kv.o -o perf

perf.o:
	gcc -c perf.c 

clean:
	rm -f perf.o perf
