#include <stdio.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <unistd.h>
#include "lib739kv.h"
#define MAX_SERVERS 4
#define MAX_VALUE_LEN 2048
#define MAX_RETURN_LEN 3000

char *servers[MAX_SERVERS];
char killed[MAX_SERVERS];
int nodes_down;
int servers_size;
struct sockaddr_in server_addresses[MAX_SERVERS];

// -1 on failure
// 0 on ok
int kv739_init(char *s[]) {
    int i, j;
    char ip_buffer[20];
    int port;

    for (servers_size = 0; servers_size < MAX_SERVERS && s[servers_size][0]; ++servers_size) {
        servers[servers_size] = (char *)malloc(sizeof(char) * (sizeof(s[servers_size]) + 1));
        if (servers[servers_size] == NULL) {
            return -1;
        }
        strcpy(servers[servers_size], s[servers_size]);
    }

    for (i = 0; i < servers_size; ++i) {
        for (j = 0; servers[i][j] != 0 && servers[i][j] != ':'; ++j) {
            ip_buffer[j] = servers[i][j];
        }
        ip_buffer[j] = 0;

        if (servers[i][j] == 0) {
            return -1;
        }

        port = 0;
        for (++j ; servers[i][j] != 0; ++j) {
            port = port * 10 + servers[i][j] - '0';
        }

        memset(&server_addresses[i], 0, sizeof(server_addresses[i]));
        server_addresses[i].sin_family = AF_INET;
        server_addresses[i].sin_addr.s_addr = inet_addr(ip_buffer);
        server_addresses[i].sin_port = htons(port);
    }

    return 0;
}

void kv739_fail(char *server) {
    int i;

    for (i = 0; i < servers_size; ++i) {
        if (strcmp(server, servers[i]) == 0) {
            killed[i] = 1;
            ++nodes_down;
        }
    }

    assert(false);
}

void kv739_recover(char *server) {
    int i;

    for (i = 0; i < servers_size; ++i) {
        if (strcmp(server, servers[i]) == 0) {
            killed[i] = 0;
            --nodes_down;
        }
    }

    assert(false);
}

// -1 on failure
// 0 on ok
int tcpip_send(int node_to_send_to, char *query, char *ret, int max_ret_size) {
    int sck, retval = 0;
    struct sockaddr_in serverAddress;

    // open the socket
    sck = socket(AF_INET, SOCK_STREAM, 0);
    if (sck < 0) {
        retval = -1;
    }

    // connect to the server
    if (retval != -1 && connect(sck, (struct sockaddr *) &server_addresses[node_to_send_to], sizeof(server_addresses[node_to_send_to])) < 0) {
        retval = -1;
    }


    if (retval != -1 && send(sck, query, strlen(query), 0) != strlen(query)) {
        retval = -1;
    }

    if (retval != -1 && recv(sck, ret, max_ret_size, 0) < 0) {
        retval = -1;
    }

    close(sck);
    return retval;
}

int choose_random_node() {
    int ret;

    if (nodes_down == servers_size) {
        return -1;
    }

    for (ret = rand() % servers_size; killed[ret]; ret = rand() % servers_size);
    return ret;
}

int send_query_string(char *query, char *value) {
    int node_to_send_to;
    char *return_buffer;
    int retval = 0;

    node_to_send_to = choose_random_node();
    if (node_to_send_to == -1) {
        retval = -1;
        goto out;
    }

    return_buffer = (char *)malloc(sizeof(char) * (MAX_RETURN_LEN));
    if (return_buffer == NULL) {
        retval = -1;
        goto out;
    }

    if (tcpip_send(node_to_send_to, query, return_buffer, MAX_RETURN_LEN) == -1) {
        retval = -1;
        goto out;
    }

    // return strings:
    // * OK [value]
    // * EM []

    // no key
    if (strncmp("EM", return_buffer, 2) == 0) {
        retval = 1;
    } else if (strncmp("OK", return_buffer, 2) == 0) {
        strncpy(value, return_buffer + 4, strlen(return_buffer) - 5);
    } else {
        // unrecognized return string
        assert(false);
    }

out:
    free(return_buffer);
    return retval;
}

// -1 on failure
// 0 on all ok
// 1 on no key
int kv739_get(char *key, char *value) {
    char *query_string;
    int retval;

    query_string = (char *)malloc(sizeof(char) * (7 + strlen(key)));
    if (query_string == NULL) {
        return -1;
    }
    sprintf(query_string, "GET [%s]", key);

    retval = send_query_string(query_string, value);

    free(query_string);
    return retval;
}

// -1 failure
// 0 all ok
// 1 no old value
int kv739_put(char *key, char *value, char *old_value) {
    int retval;
    char *query_string;

    query_string = (char *)malloc(sizeof(char) * (9 + strlen(key) + strlen(value)));
    if (query_string == NULL) {
        return -1;
    }
    sprintf(query_string, "PUT [%s] [%s]", key, value);

    retval = send_query_string(query_string, old_value);

    free(query_string);
    return retval;
}

int main() {
    int i;
    char *s[4];
    char t1[100], t2[100], t3[100];

    for (i = 0; i < 4; ++i) {
        s[i] = (char *)malloc(100);
    }

    sprintf(s[0], "127.0.0.1:9999");
    sprintf(s[1], "");

    kv739_init(s);

    sprintf(t1, "kita");
    sprintf(t2, "a");

    printf("should be 1: %d\n", kv739_put(t1, t2, t3));
    printf("should be 0: %d\n", kv739_get(t1, t2));
    printf("should be a: %s\n", t2);

    return 0;
}
