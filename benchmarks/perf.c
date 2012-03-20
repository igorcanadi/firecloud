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

int er;

    for (i = 0; i < 300; ++i) {
        t1[1] = rand()%3 + '0';
        t1[2] = rand()%10 + '0';
        t2[1] = rand()%3 + '0';
        t2[2] = rand()%10 + '0';
        char *a = (rand()%2) ? t3 : t4;
        int r = kv739_put(t1, a, buf);
if (r == -1) ++er;
        r = kv739_get(t2, buf);
if (r == -1) ++er;
    }

printf("errors: %d/600\n", er);

    return 0;

}
