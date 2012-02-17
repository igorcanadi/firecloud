int kv739_init(char *servers[]);
void kv739_fail(char * server);
void kv739_recover(char * server);
int kv739_get(char * key, char * value);
int kv739_put(char * key, char * value, char * old_value);
