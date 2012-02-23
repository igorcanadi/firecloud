
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>

#define END 99
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


void init(header head) {
  // read N host names
  char lst[head.data][255];
  int i;

  for (i = 0; i < head.data; i++) {
    fread(&lst[i], 1, 255, stdin);
  }
  char *arr[head.data];
  for (i = 0; i < head.data; i++) {
    printf("init %s\n", &lst[i]);
    arr[i] = &lst[i];
  }
  //kv739_init(arr);
}

void fail(header head) {
  char name[255];
  fread(&name, 1, 255, stdin);
  //kv739_fail(&name);
  printf("fail %s", &name);
}

void recover(header head) {
  char name[255];
  fread(&name, 1, 255, stdin);
  //kv739_fail(&name);
  printf("recover %s", &name);
}

void get(header head) { 
  char ke[129];
  char val[2049];
  int rcode;

  fread(&ke, 1, 129, stdin);

  printf("GET [%s]", &ke);
  
  // rcode = kv739_get(&ke, &val);
  
  // do something with rcode and value
}

void put(header head) { 
  char ke[129];
  char val[2049];
  char oldval[2049];
  int rcode;

  fread(&ke, 1, 129, stdin);
  fread(&val, 1, head.data, stdin);

  printf("PUT [%s] [%s]", &ke, &val);

  //rcode = kv739_put(&ke, &val, &oldval);

  // do something with rcode and old val


}

void loop_stdin() {
  
  header head;
  int rval;
  while (1) {
    printf("Doing loop\n");
    rval = fread(&head, 1, sizeof(head), stdin);
    printf("read %d bytes\n", rval);
    if (rval < 1) {
      printf("read returned %d\n", rval);
      printf("errno %d", errno);
      break;
    }
    
    printf("switching #%d: type %u, data: %u\n", head.id, head.type, head.data);
    switch (head.type) {
      case END:
        return;
      case INIT:
        init(head);
        break;
      case FAIL:
        fail(head);
        break;
      case RECOVER:
        recover(head);
        break;
      case GET:
        get(head);
        break;
      case PUT:
        put(head);
        break;
      default:
        break;
    };
    }
  
}

int main(int argc, char** argv) {
  printf("Working.\n");
  loop_stdin();
}
