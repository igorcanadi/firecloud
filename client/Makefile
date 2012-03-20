all: lib739kv.o
	gcc -shared -W1,-soname,lib739kv -o lib739kv.so lib739kv.o

lib739kv.o:
	gcc -fPIC -c lib739kv.c -DVERBOSE

clean:
	rm -f lib739kv.o lib749kv.so
