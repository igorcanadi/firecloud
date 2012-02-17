
#DEFINE END -1
#DEFINE INIT 0
#DEFINE FAIL 1
#DEFINE RECOVER 2
#DEFINE GET 3
#DEFINE PUT 4


void kv739_init(char *servers[]);
void kv739_fail(char * server);
void kv739_recover(char * server);
int kv739_put(char * key, char * value, char * old_value);
int kv739_get(char * key, char * value);


/*
 * Operation header block
 */
typedef struct {
  unsigned long time;
  int id;
  int type;
  int data;
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
    arr[i] = &list[i];
  }
  kv739_init(arr);
}

void fail(header head, int fd) {
  char name[255];
  read(fd, &name, 255);
  kv739_fail(&name);
}

void recover(header head, int fd) {
  char name[255];
  read(fd, &name, 255);
  kv739_fail(&name);
}

void get(header head, int fd) { 
  char ke[129];
  char val[2049];
  int rcode;

  read(fd, &ke, 129);
  
  rcode = kv739_get(&ke, &val);
  
  // do something with rcode and value
}

void put(header head, int fd) { 
  char ke[129];
  char val[2049];
  char oldval[2049];
  int rcode;

  read(fd, &ke, 129);
  read(fd, &val, head.data);

  rcode = kv739_put(&ke, &val, &oldval);

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
