
#include <stdio.h>
#include <stdlib.h>

#define END -1
#define INIT 0
#define FAIL 1
#define RECOVER 2
#define GET 3
#define PUT 4


    /*
 * Operation header block
 */
typedef struct {
  unsigned long long time;
  unsigned long long id;
  unsigned long long type;
  unsigned long long data;
} header;

/*
 * One hostname call
 */
typedef struct {
  char value[255];
} hostport;


void init(header head, int fd) {
  // read N host names
  char lst[head.data][255];
  int i;

  for (i = 0; i < head.data; i++) {
    read(fd, &lst[i], 255);
  }
  char *arr[head.data];
  for (i = 0; i < head.data; i++) {
    printf("init %s", &lst[i]);
    arr[i] = &lst[i];
  }
  //kv739_init(arr);
}

void fail(header head, int fd) {
  char name[255];
  read(fd, &name, 255);
  //kv739_fail(&name);
  printf("fail %s", &name);
}

void recover(header head, int fd) {
  char name[255];
  read(fd, &name, 255);
  //kv739_fail(&name);
  printf("recover %s", &name);
}

void get(header head, int fd) { 
  char ke[129];
  char val[2049];
  int rcode;

  read(fd, &ke, 129);

  printf("GET [%s]", &ke);
  
  // rcode = kv739_get(&ke, &val);
  
  // do something with rcode and value
}

void put(header head, int fd) { 
  char ke[129];
  char val[2049];
  char oldval[2049];
  int rcode;

  read(fd, &ke, 129);
  read(fd, &val, head.data);

  printf("PUT [%s] [%s]", &ke, &val);

  //rcode = kv739_put(&ke, &val, &oldval);

  // do something with rcode and old val


}

void loop_stdin() {
  
  
  header head;

  read(stdin, head, sizeof(header));

  switch (head.type) {
    case END:
      return;
    case INIT:
      break;
    case FAIL:
      break;
    case RECOVER:
      break;
    case GET:
      break;
    case PUT:
      break;
    default:
      break;
  }
  
}

int main(int argc, char** argv) {
  return 0;
}
