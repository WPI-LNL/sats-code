

int main();

int setup();
void setup_i2c_devices();
int setup_i2c_device(int addr);
int send_i2c_byte(unsigned char addr, unsigned char reg, unsigned char value);
char read_i2c_byte(unsigned char addr, unsigned char reg);

void setup_gpio_inputs();
int gpio_read(struct gpiohandle_request request);
int poll_interrupts();
int handle_interrupt_updates();
int get_pin_updates_from_interrupt(unsigned char i2c_addr, unsigned char int_addr, unsigned char gpio_addr, int idx_offset);

int handle_device_remove(int idx);
int handle_device_add();

int load_data_file();

int remove_all_w1_devices();
int remove_w1_device(char* device);


void INThandler(int sig);
void blockingSearch();
