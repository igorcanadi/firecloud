
#include <sys/time.h>
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

int sleep_until(unsigned long);
unsigned long current_msec();
unsigned long start_time;
unsigned long current_usec();

#define CURRENT_USEC current_usec()
#define usec_to_msec(x)  (x) / 1000
#define CURRENT_MSEC usec_to_msec(CURRENT_USEC)


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
  char **lst = malloc(sizeof(char*) * (head.data + 1));
  char *st;
  int i;

  for (i = 0; i < head.data; i++) {
    st = (char*)malloc(sizeof(char)*255);
    lst[i] = st;
    fread(st, 1, 255, stdin);
  }
  st = (char*)malloc(sizeof(char)*255);
  st[0] = NULL;
  lst[head.data] = st;
  
  printf("at this loop\n");
  for (i =0; i < 4 && lst[i][0]; ++i) {
    printf("initing a server: %s\n", lst[i]);
  }

  kv739_init(lst);
}

void fail(header head) {
  char name[255];
  fread(&name, 1, 255, stdin);
  printf("failing: %s\n", &name);
  kv739_fail(&name);
  printf("fail %s\n", &name);
}

void recover(header head) {
  char name[255];
  fread(&name, 1, 255, stdin);
  kv739_recover(&name);
  printf("recover %s\n", &name);
}

void get(header head) { 
  char ke[129];
  char val[2049];
  int rcode;

  fread(&ke, 1, 129, stdin);

  
  unsigned long nao = CURRENT_USEC;
  rcode = kv739_get(&ke, &val);
  printf("+ -2 %ld\n", CURRENT_USEC - nao);

  if (rcode != 0) {
    val[0] = NULL;
  }

  printf("+ %d %ld %d [%s]\n", head.id, CURRENT_MSEC, rcode, &val);
  
  // do something with rcode and value
}

void put(header head) { 
  char ke[129];
  char val[2049];
  char oldval[2049];
  int rcode;

  fread(&ke, 1, 129, stdin);
  fread(&val, 1, head.data, stdin);

  unsigned long nao = CURRENT_USEC;
  rcode = kv739_put(&ke, &val, &oldval);
  printf("+ -2 %ld\n", CURRENT_USEC - nao);

  if (rcode != 0) {
    oldval[0] = NULL;
  }

  printf("+ %d %ld %d [%s]\n", head.id, CURRENT_MSEC, rcode, &oldval);

  // do something with rcode and old val
}

void wait_until_start() {
  if (start_time <= CURRENT_USEC) {
    printf("+ -1 ERROR: transcript stale by %ldus\n", start_time - CURRENT_USEC);
    //exit(1);
    return;
  }
  printf("sleeping for start by %d usec\n", start_time - CURRENT_USEC);
  usleep(start_time - CURRENT_USEC);
}

void loop_stdin() {
  
  header head;
  int rval;
  while (1) {
    //printf("Doing loop\n");
    rval = fread(&head, 1, sizeof(head), stdin);
    //printf("read %d bytes\n", rval);
    if (rval < 1) {
      //printf("read returned %d\n", rval);
      //printf("errno %d", errno);
      printf("+ -1 pipe read error\n");
      break;
    }
     
    //printf("Seq #%d scheduled for %u\n", head.id, head.time);
    
    if (head.type == INIT) {
      start_time = head.time * 1000;
      wait_until_start();
    } else {
      int offby = sleep_until(head.time);
      if (offby > 100000000) {
        /* We're way behind shceudle, fail. */
        printf("+ -1 ERROR: #%d Behind schedule %d us\n", head.id, offby);
        exit(1);
      }
    }
    
    
    //printf("switching #%d: type %u, data: %u\n", head.id, head.type, head.data);
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

unsigned long current_usec() {
  struct timeval tval;
  gettimeofday(&tval, NULL);
  double nao = tval.tv_sec;
  unsigned long msec = tval.tv_usec;
  unsigned long secmsec = tval.tv_sec * 1000 * 1000;
  return secmsec + msec;
}

unsigned long current_msec() {
  return CURRENT_MSEC;
}

// sleep until a given msec
int sleep_until(unsigned long time) {
  // time is in msec so conver to usec
  time = time * 1000;
  unsigned long nao = CURRENT_USEC;
  // internal fudge factor to allow for slight
  // internal delay in this file
  unsigned long offset = nao - start_time;
  if (offset > time) {
    /* this time has passed. too late */
    //printf("Too Late! %ld > %ld\n", offset, time);
    //printf("+ -2 %d\n", time - offset);
    return offset - time;
  }
  /* to sleep: */
  unsigned long sleepusec = time - offset;
  /* print slack time */
  if (sleepusec > 200000 * 1000) {
    printf("+ -1 ERROR: Sleeping WAAAY too long.\n");
    exit(1);
  }
  // print slace time
  usleep(sleepusec);
  return 0;
}


int main(int argc, char** argv) {
  printf("Working.\n");
  loop_stdin();
}
