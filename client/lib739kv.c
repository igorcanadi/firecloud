#include <stdio.h>
#include <fcntl.h>
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
#define MICRO_TIMEOUT 3000

char *servers[MAX_SERVERS];
char killed[MAX_SERVERS];
int nodes_down;
int servers_size;
int last_unique_id;
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

int choose_random_node() {
    int ret;

    if (nodes_down == servers_size) {
        return -1;
    }

    for (ret = rand() % servers_size; killed[ret]; ret = rand() % servers_size);
    return ret;
}

// -1 on error
// 0 on timeout
// number of bytes on success
int get_me_the_data_with_timeout(int sck, char *ret, int max_ret_size, int timeout_usec) {
    fd_set read_fset;
    struct timeval timeout;
    int retval = 0;

    FD_ZERO(&read_fset);
    FD_SET(sck, &read_fset);
    timeout.tv_sec = 0;
    timeout.tv_usec = timeout_usec;

    retval = select(sck + 1, &read_fset, NULL, NULL, &timeout);

    if (retval > 0 && (retval = recvfrom(sck, ret, max_ret_size, 0, NULL, NULL)) < 0) {
        retval = -1;
    }

    return retval;
}

// * OK [unique_id] [value]
// return 0 if i got the correct request_id
// return 1 if request_id is differnet
// return -1 if error in parsing
int parse_ok_reply(char *reply, char *value, int request_id) {
    int i, id_got = 0, state = 0, i_val = 0;

    if (strncmp("OK", reply, 2) != 0) {
        return -1;
    }
        
    for (i = 2; reply[i]; ++i) {
        if (reply[i] == '[') {
            if (state != 0 || state == 2) {
                return -1;
            }
            ++state;
        } else if (reply[i] == ']') {
            if (state == 1) {
                if (id_got != request_id) {
                    return 1;
                }
                ++state;
            } else if (state == 3) {
                ++state;
                break;
            } else {
                return -1;
            }
        } else if (state == 1) {
            if (reply[i] < '0' || reply[i] > '9') {
                return -1;
            }
            id_got = id_got * 10 + reply[i] - '0';
        } else if (state == 3) {
            value[i_val++] = reply[i];
        }
    }
    
    if (id_got == request_id && state == 4) {
        // parsing good
        return 0;
    }
    return -1;
}

int send_query_string(char *query, char *value, int request_id) {
    int node_to_send_to, i;
    char *return_buffer;
    int retval = 0;
    int sck;
    struct sockaddr_in *server;

    return_buffer = (char *)malloc(sizeof(char) * (MAX_RETURN_LEN));
    if (return_buffer == NULL) {
        retval = -1;
        goto out;
    }

    // open the socket
    sck = socket(AF_INET, SOCK_DGRAM, 0);
    if (sck < 0) {
        retval = -1;
        goto closesocket;
    }

    node_to_send_to = choose_random_node();
    if (node_to_send_to == -1) {
        retval = -1;
        goto closesocket;
    }
    server = &server_addresses[node_to_send_to];
    if (sendto(sck, query, strlen(query), 0, (struct sockaddr *)server, sizeof(*server)) != strlen(query)) {
        retval = -1;
        goto closesocket;
    }

    do {
        retval = get_me_the_data_with_timeout(sck, return_buffer, MAX_RETURN_LEN, MICRO_TIMEOUT);

        if (retval == -1) {
            // error
            goto closesocket;
        } else if (retval == 0) {
            // timeout TODO try another server
            goto closesocket;
        }

        if (parse_ok_reply(return_buffer, value, request_id) == 0) {
            // i got ok response
            break;
        }
    } while (true);

closesocket:
    close(sck);
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
    sprintf(query_string, "GET [%s] [%d]", key, ++last_unique_id);

    retval = send_query_string(query_string, value, last_unique_id);

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
    sprintf(query_string, "PUT [%s] [%s] [%d]", key, value, ++last_unique_id);

    retval = send_query_string(query_string, old_value, last_unique_id);

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

    sprintf(s[0], "127.0.0.1:10000");
    sprintf(s[1], "");

    kv739_init(s);

    sprintf(t1, "kita");
    sprintf(t2, "a");

    printf("should be 1: %d\n", kv739_put(t1, t2, t3));
    printf("should be 0: %d\n", kv739_get(t1, t2));
    printf("should be a: %s\n", t2);

    return 0;
}
