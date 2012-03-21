#include <stdio.h>
#include <assert.h>
#include <fcntl.h>
#include <limits.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/time.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <stdlib.h>
#include <assert.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>
#include <time.h>
#include <stdbool.h>
#include "lib739kv.h"
#define MAX_SERVERS 4
#define MAX_VALUE_LEN 2048
#define MAX_RETURN_LEN 3000
#ifdef VERBOSE
    #define LOG(x, args...) do { \
            struct timeval tv; \
            gettimeofday(&tv, NULL); \
            fprintf(stderr, "[%d.%06d] %s():%d -- " x "\n", tv.tv_sec, tv.tv_usec, __func__, __LINE__, ## args); \
        } while (false)
#else
    #define LOG(x, args...) do { } while(0)
#endif


char *servers[MAX_SERVERS];
int server_priority[MAX_SERVERS];
char killed[MAX_SERVERS];
int nodes_down;
int servers_size;
int last_unique_id;
struct sockaddr_in server_addresses[MAX_SERVERS];
// timeouts are in microseconds
// timeout i means that we wait that much in ith retry
int timeouts[3] = {4 * 1000, 4 * 1000, 4 * 1000};

// -1 on failure
// 0 on ok
int kv739_init(char *s[]) {
    int i, j;
    char ip_buffer[20];
    int port;

    LOG("Initializing the client...");

    srand(time(NULL));
    last_unique_id = rand() % 10000;

    for (servers_size = 0; servers_size < MAX_SERVERS && s[servers_size][0]; ++servers_size) {
        servers[servers_size] = (char *)malloc(sizeof(char) * (sizeof(s[servers_size]) + 1));
        if (servers[servers_size] == NULL) {
            return -1;
        }
        strcpy(servers[servers_size], s[servers_size]);

        server_priority[servers_size] = servers_size;
    }

    LOG("INIT'd severs.");

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
        LOG("IP %s, port %d", ip_buffer, port);
    }

    return 0;
}

void kv739_fail(char *server) {
    int i;

    LOG("Server %s is down", server);

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

    LOG("Server %s is back up", server);

    for (i = 0; i < servers_size; ++i) {
        if (strcmp(server, servers[i]) == 0) {
            killed[i] = 0;
            --nodes_down;
        }
    }

    assert(false);
}

int choose_random_node(int not_this_one) {
    int ret;

    if (nodes_down == servers_size || (not_this_one != -1 && (nodes_down + 1) == servers_size)) {
        return -1;
    }

    for (ret = rand() % servers_size; killed[ret] || ret == not_this_one; ret = rand() % servers_size);
    return ret;
}

int choose_best_node() {
    int p, pmax, i;

    if (nodes_down == servers_size) {
        return -1;
    }

    // 0 - 3
    // 1..2 - 2
    // 3..6 - 1
    // 7..14 - 0
    pmax = (1 << (servers_size - nodes_down)) - 1;
    p = rand() % pmax;

    for (i = 0; i < servers_size; ++i) {
        if (killed[server_priority[i]]) {
            continue;
        }

        if (p >= pmax / 2) {
            // i is the chosen server
            return server_priority[i];
        }

        pmax = pmax / 2;
    }

    assert(false);
}

// move it to the beginning of the list
void server_responsive(int server) {
    int i, t;

    if (killed[server]) {
        return;
    }

    for (i = 0; i < servers_size && server_priority[i] != server; ++i)
        ;

    assert(i < servers_size);

    for ( ; i >= 1; --i) {
        // swap
        t = server_priority[i-1];
        server_priority[i-1] = server_priority[i];
        server_priority[i] = t;
    }
}

// move it to the end of the list
void server_not_responsive(int server) {
    int i, t;

    for (i = 0; i < servers_size && server_priority[i] != server; ++i)
        ;

    assert(i < servers_size);

    for ( ; i+1 < servers_size; ++i) {
        // swap
        t = server_priority[i+1];
        server_priority[i+1] = server_priority[i];
        server_priority[i] = t;
    }

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
    timeout.tv_sec = timeout_usec / (1000 * 1000);
    timeout.tv_usec = timeout_usec % (1000 * 1000);

    retval = select(sck + 1, &read_fset, NULL, NULL, &timeout);

    if (retval > 0 && (retval = recvfrom(sck, ret, max_ret_size, 0, NULL, NULL)) < 0) {
        retval = -1;
    }

    // recvfrom doesn't null terminate the string
    if (retval > 0) {
        ret[retval] = '\0';
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
            if (state != 0 && state != 2) {
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
    value[i_val] = '\0';
    
    if (id_got == request_id && state == 4) {
        // parsing good
        return 0;
    }
    return -1;
}

// -1 on faliure
// 0 on OK
int send_query_string(char *query, char *value, int request_id) {
    int node_to_send_to = -1, iteration;
    char *return_buffer;
    int retval = 0;
    int sck;
    struct sockaddr_in *server;

    LOG("Sending %s with ID %d", query, request_id);

    return_buffer = (char *)malloc(sizeof(char) * (MAX_RETURN_LEN));
    if (return_buffer == NULL) {
        LOG("Failed to initialize return buffer");
        retval = -1;
        goto out;
    }

    // open the socket
    sck = socket(AF_INET, SOCK_DGRAM, 0);
    if (sck < 0) {
        LOG("Failed to open the socket");
        retval = -1;
        goto closesocket;
    }

    for (iteration = 0; iteration < 3; ++iteration) {
        node_to_send_to = choose_best_node();
        if (node_to_send_to == -1) {
            LOG("Failed to find a node to send to");
            retval = -1;
            goto closesocket;
        }

        LOG("Trying to send to server %s (iteration %d)", servers[node_to_send_to], iteration);

        server = &server_addresses[node_to_send_to];
        if (sendto(sck, query, strlen(query), 0, (struct sockaddr *)server, sizeof(*server)) != strlen(query)) {
            LOG("Sending failed. I might try another server.");
            retval = -1;
            // error, try another server
            continue;
        }

        LOG("Sending OK. Let's get the response.");

        do {
            retval = get_me_the_data_with_timeout(sck, return_buffer, MAX_RETURN_LEN, timeouts[iteration]);

            if (retval == -1) {
                // error, go out
                LOG("Error receiving data. Bailing out.");
                goto closesocket;
            } else if (retval == 0) {
                // timeout, try another server
                LOG("Query timed out. I might try another server.");
                server_not_responsive(node_to_send_to);
                retval = -1;
                break;
            } else {
                LOG("Got back: %s", return_buffer);
                server_responsive(node_to_send_to);
                if (parse_ok_reply(return_buffer, value, request_id) == 0) {
                    LOG("Response OK, happy times");
                    // i got ok response
                    retval = 0;
                    goto closesocket;
                }
                LOG("Response NOT ok, trying to receive more data");
            }
        } while (true);
    }

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

    query_string = (char *)malloc(sizeof(char) * (30 + strlen(key)));
    if (query_string == NULL) {
        LOG("Failed to initialize query string");
        return -1;
    }

    if (last_unique_id == INT_MAX) {
        last_unique_id = 0;
    }

    sprintf(query_string, "GET [%s] [%d]", key, ++last_unique_id);

    retval = send_query_string(query_string, value, last_unique_id);
    if (retval == 0 && strlen(value) == 0) {
        // no key
        retval = 1;
    }
    LOG("GET retval: %d, value: %s", retval, retval == -1 ? "" : value);

    free(query_string);
    return retval;
}

// -1 failure
// 0 all ok
// 1 no old value
int kv739_put(char *key, char *value, char *old_value) {
    int retval;
    char *query_string;

    query_string = (char *)malloc(sizeof(char) * (30 + strlen(key) + strlen(value)));
    if (query_string == NULL) {
        LOG("Failed to initialize query string");
        return -1;
    }

    if (last_unique_id == INT_MAX) {
        last_unique_id = 0;
    }

    sprintf(query_string, "PUT [%s] [%s] [%d]", key, value, ++last_unique_id);

    retval = send_query_string(query_string, old_value, last_unique_id);
    if (retval == 0 && strlen(old_value) == 0) {
        // no old value
        retval = 1;
    }
    LOG("PUT retval: %d, old value: %s", retval, retval == -1 ? "" : old_value);

    free(query_string);
    return retval;
}

#ifdef CLIENT_MAIN 
int main() {
    int i;
    char *s[5];
    char t1[100], t2[100], t3[100], t4[100], b[100];

    for (i = 0; i < 5; ++i) {
        s[i] = (char *)malloc(100);
    }

    sprintf(s[0], "127.0.0.1:10000");
    sprintf(s[1], "127.0.0.1:10001");
    sprintf(s[2], "127.0.0.1:10002");
    sprintf(s[3], "127.0.0.1:10003");
    sprintf(s[4], "");

    kv739_init(s);

    sprintf(t1, "k1");
    sprintf(t2, "k2");
    sprintf(t3, "a");
    sprintf(t4, "b");

    kv739_put(t1, t3, b);
    kv739_put(t2, t4, b);
    kv739_get(t1, b);
    kv739_get(t2, b);
    kv739_put(t2, t3, b);
    kv739_get(t2, b);

    return 0;
}
#endif
