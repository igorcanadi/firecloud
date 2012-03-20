#include <stdio.h>
#include <stdlib.h>
#include "../client/lib739kv.h"

int main() {
    int i;
    char *s[5];
    char t1[100], t2[100], t3[100], t4[100], b[100];
    char buf[1000];

    for (i = 0; i < 5; ++i) {
        s[i] = (char *)malloc(100);
    }

    sprintf(s[0], "127.0.0.1:10000");
    sprintf(s[1], "127.0.0.1:10001");
    sprintf(s[2], "127.0.0.1:10002");
    sprintf(s[3], "127.0.0.1:10003");
    sprintf(s[4], "");

    kv739_init(s);
    sprintf(t1, "k..");
    sprintf(t2, "k..");
    sprintf(t3, "yay");
    sprintf(t4, "wohoooooo");

    for (i = 0; i < 300; ++i) {
        t1[1] = rand()%3 + '0';
        t1[2] = rand()%10 + '0';
        t2[1] = rand()%3 + '0';
        t2[2] = rand()%10 + '0';
        char *a = (rand()%2) ? t3 : t4;
        kv739_put(t1, a, buf);
        kv739_get(t2, buf);
    }

    return 0;

}
