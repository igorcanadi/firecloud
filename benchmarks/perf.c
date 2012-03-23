#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <time.h>
#include "../client/lib739kv.h"

long long lags[10000];
int size_lags = 0;
long long global_clock;

void start_time() {
    return;
    struct timeval tv;
    gettimeofday(&tv, NULL);
    global_clock = tv.tv_usec + tv.tv_sec * 1000000;
}

void end_time() {
    return;
    struct timeval tv;
    gettimeofday(&tv, NULL);
    lags[size_lags++] = tv.tv_usec + tv.tv_sec * 1000000 - global_clock;
}

int main() {
    long long i;
    char *s[5];
    char t1[100], t2[100], t3[100], t4[100], b[100];
    char buf[1000];

    for (i = 0; i < 5; ++i) {
      s[i] = (char *)malloc(100);
    }

    /*sprintf(s[0], "128.105.112.7:8808");
    sprintf(s[1], "128.105.112.8:8808");
    sprintf(s[2], "128.105.112.9:8808");
    sprintf(s[3], "128.105.112.10:8808");*/
    sprintf(s[0], "192.168.56.101:8808");
    sprintf(s[1], "192.168.56.102:8808");
    sprintf(s[2], "192.168.56.103:8808");
    sprintf(s[3], "192.168.56.104:8808");

    sprintf(s[4], "");

    kv739_init(s);
    sprintf(t1, "k..");
    sprintf(t2, "k..");
    sprintf(t3, "yay");
    sprintf(t4, "wohoooooo");

    long long er = 0;
    int s_time = time(NULL); 

    for (i = 0; ; ++i) {
      t1[1] = rand()%3 + '0';
      t1[2] = rand()%10 + '0';
      t2[1] = rand()%3 + '0';
      t2[2] = rand()%10 + '0';
      char *a = (rand()%2) ? t3 : t4;

      start_time();
      int r = kv739_put(t1, a, buf);
      end_time();
      if (r == -1) ++er;
      start_time();
      r = kv739_get(t2, buf);
      end_time();
      if (r == -1) ++er;

      if (i % 1800 == 0) {
          printf("time elapsed: %d ----- errors: %lld/%lld\n", time(NULL) - s_time, er, i*2);
      }
    }

    for (i = 0; i < size_lags; ++i) {
        printf("%d\n", lags[i]);
    }

    return 0;
}
