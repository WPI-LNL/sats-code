int main(int argc, char** argv);

int setup_gpio_vars();

int gpio_write(int var);
int gpio_read();

int find_device_in_list(long long* addresses, int length);
int find_device_not_in_list(long long* addresses, int length);

int poll_presence(long long address);

int reset_bus();
int write_byte(char b);
char read_byte();

int write_bits(long long data, int nbits);
int read_bits(long long* data, int nbits);

int write_bit(int bit);
int read_bit();

