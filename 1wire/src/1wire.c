#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>
#include <fcntl.h>

#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <linux/gpio.h>

#include "1wire.h"

#define TRUE 1
#define FALSE 0

#define INT_1A 4
#define INT_1B 17
#define INT_2A 27
#define INT_2B 22

#define GPIO_1_ADDR 0x20
#define GPIO_2_ADDR 0x24

char busSearch[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_search"; // Path to search control file
//char busTimeout[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_timeout"; 
//char busTimeout_us[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_timeout_us";
char busRemove[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_remove"; // Path to slave remove file
char busSlaves[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_slaves"; // Path to slave list file

FILE* fsearch;
FILE* fremove;
FILE* fslaves;

int loop = TRUE;

char* slots[20];
int presence[20];
char** known_uids;
int known_uids_len;

int slot_queue[20];
int slot_queue_a = 0;
int slot_queue_b = 0;

char dataFile[] = "sats_data.dat";

int i2cfile;


struct gpiohandle_request req_a1;
struct gpiohandle_request req_b1;
struct gpiohandle_request req_a2;
struct gpiohandle_request req_b2;
struct gpiohandle_data gpio_data;


int main() {
    signal(SIGINT, INThandler); // intercept control-c
    printf("STARTED PROGRAM:\n");

    setup();
    enqueue_slot(1);
    handle_slot_queue();
    /*for(int i = 0; i < 10; i++) {
    	usleep(500000);
	char x = read_i2c_byte(GPIO_1_ADDR, 0x12);
	printf("Read byte: %d\n", x);
    }
	char x = read_i2c_byte(GPIO_1_ADDR, 0x13);*/
    /*for (int i = 0; i < 500; i++) {
    	usleep(250000);
        int x = gpio_read(req_a1);
        if (x == 0) {
            printf("INTERRUPT DETECTED; READ FROM A1\n");
	    x = read_i2c_byte(GPIO_1_ADDR, 0x0E);
	    printf("A1 FLAGS: %d\n", x);
	    x = read_i2c_byte(GPIO_1_ADDR, 0x12);
	    printf("A1 DATA: %d\n", x);
        }
    }*/
    while (loop) {
        usleep(10000); // 10ms
        handle_interrupt_updates();
        handle_slot_queue();
    }
    return 0;
}

int setup() {
    setup_i2c_devices();
    setup_gpio_inputs();
    load_data_file();
    //TODO
    for (int i = 0 ; i < 20; i++) {
    	slots[i] = NULL;
	presence[i] = 0;
    }
    setup_w1_config();
    return 0;
}

void setup_i2c_devices() {
    i2cfile = open("/dev/i2c-1", O_RDWR);
    setup_i2c_device(GPIO_1_ADDR);
//    setup_i2c_device(GPIO_2_ADDR);
}

int setup_i2c_device(int addr) {
    int a = 1;
    a &= send_i2c_byte(addr, 0x0A, 0x08);//IOCON
    a &= send_i2c_byte(addr, 0x04, 0xFF);//GPINTEN A
    a &= send_i2c_byte(addr, 0x0C, 0xFF);//GPPU A
    read_i2c_byte(addr, 0x12); // clear interrupts
    printf("GPIO A setup (chip %d): %d\n", addr, a);
    a = 1;
    a &= send_i2c_byte(addr, 0x05, 0xFF);//GPINTEN B
    a &= send_i2c_byte(addr, 0x0D, 0xFF);//GPPU B
    read_i2c_byte(addr, 0x13);	// clear interrupts
    printf("GPIO B setup (chip %d): %d\n", addr, a);
    return a;
}


int send_i2c_byte(unsigned char addr, unsigned char reg, unsigned char value) {
    unsigned char outbuf[2];
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[1];

    messages[0].addr  = addr;
    messages[0].flags = 0;
    messages[0].len   = sizeof(outbuf);
    messages[0].buf   = outbuf;

    outbuf[0] = reg;
    outbuf[1] = value;

    packets.msgs  = messages;
    packets.nmsgs = 1;
    if(ioctl(i2cfile, I2C_RDWR, &packets) < 0) {
        return 0;
    }

    return 1;
}

char read_i2c_byte(unsigned char addr, unsigned char reg) {
    unsigned char inbuf, outbuf;
    struct i2c_rdwr_ioctl_data packets;
    struct i2c_msg messages[2];

    outbuf = reg;
    messages[0].addr  = addr;
    messages[0].flags = 0;
    messages[0].len   = sizeof(outbuf);
    messages[0].buf   = &outbuf;

    messages[1].addr  = addr;
    messages[1].flags = I2C_M_RD;
    messages[1].len   = sizeof(inbuf);
    messages[1].buf   = &inbuf;

    packets.msgs      = messages;
    packets.nmsgs     = 2;
    if(ioctl(i2cfile, I2C_RDWR, &packets) < 0) {
        return -1;
    }
    return inbuf;

}

void setup_gpio_inputs() {
// ** This code from the RPi stackexchange: https://raspberrypi.stackexchange.com/questions/101718/control-gpio-pins-from-c ** //
    // ONE_TIME SETUP //
    //Opening device and getting file descriptor.
    int fd = open("/dev/gpiochip0",O_RDONLY);

    //structure for holding chip information
    //This structure is defined in /usr/include/linux/gpio.h
    struct gpiochip_info cinfo;

    //Getting the chip information via the ioctl system call
    //GPIO_GET_CHIPINFO_IOCTL defined also in /usr/include/linux/gpio.h
    int ret = ioctl(fd,GPIO_GET_CHIPINFO_IOCTL,&cinfo);

    //print out the chip information
    fprintf(stdout, "GPIO chip: %s, \"%s\", %u GPIO lines\n",
        cinfo.name, cinfo.label, cinfo.lines);

    //structure for holding line information.
    //structure defined in /usr/include/linux/gpio.h
    struct gpioline_info linfo;

    //get generic line information from system call
    ret = ioctl(fd,GPIO_GET_LINEINFO_IOCTL, &linfo);

    //Not sure what this line_offset is, but we specify the gpio number later.
    //fprintf(stdout,"line %2d: %s\n",linfo.line_offset,linfo.name);

    //Set up some handles for requests and data
    int lhfd;

    req_a1.lineoffsets[0] = INT_1A;
    req_a1.lines = 1; //have to indicate how many lines we are reading.
    req_a1.flags = GPIOHANDLE_REQUEST_INPUT; //Make this an input request
    lhfd = ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &req_a1); // get line handle

    req_b1.lineoffsets[0] = INT_1B;
    req_b1.lines = 1; //have to indicate how many lines we are reading.
    req_b1.flags = GPIOHANDLE_REQUEST_INPUT; //Make this an input request
    lhfd = ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &req_b1); // get line handle

    req_a2.lineoffsets[0] = INT_2A;
    req_a2.lines = 1; //have to indicate how many lines we are reading.
    req_a2.flags = GPIOHANDLE_REQUEST_INPUT; //Make this an input request
    lhfd = ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &req_a2); // get line handle

    req_b2.lineoffsets[0] = INT_2B;
    req_b2.lines = 1; //have to indicate how many lines we are reading.
    req_b2.flags = GPIOHANDLE_REQUEST_INPUT; //Make this an input request
    lhfd = ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &req_b2); // get line handle
}

int gpio_read(struct gpiohandle_request request) {
    int ret = ioctl(request.fd,  GPIOHANDLE_GET_LINE_VALUES_IOCTL, &gpio_data);
    return gpio_data.values[0];
}

int poll_interrupts() {
    int ret = 0;
    ret |= !gpio_read(req_a1);		// 000a	A1
    ret |= (!gpio_read(req_b1)) << 1;	// 00a0	B1
    //ret |= !gpio_read(req_a2) << 2;	// 0a00	A2
    //ret |= !gpio_read(req_b2) << 3;	// a000	B2

    return ret;
}

int handle_interrupt_updates() {
    int mask = poll_interrupts();
    if (mask & 0x1) {
    	get_pin_updates_from_interrupt(GPIO_1_ADDR, 0x0E, 0x12, 5); // CHIP 1 bus A - GPIO 5-9;
    }
    if (mask & (0x1 << 1)) {
    	get_pin_updates_from_interrupt(GPIO_1_ADDR, 0x0F, 0x13, 0); // CHIP 1 bus B - GPIO 0-4;
    }
    if (mask & (0x1 << 2)) {
    	//get_pin_updates_from_interrupt(GPIO_2_ADDR, 0x0E, 0x12, 15); // CHIP 2 bus A - GPIO 15-19;
    }
    if (mask & (0x1 << 3)) {
    	//get_pin_updates_from_interrupt(GPIO_2_ADDR, 0x0F, 0x13, 10); // CHIP 2 bus B - GPIO 10-14;
    }
    
}

int get_pin_updates_from_interrupt(unsigned char i2c_addr, unsigned char int_addr,
		unsigned char gpio_addr, int idx_offset) {
    char int_flags = read_i2c_byte(i2c_addr, int_addr);
    char gpio_states = read_i2c_byte(i2c_addr, gpio_addr);
    for (int i = 0; i < 5; i++) {
    	if (int_flags >> i & 0x1 == 1) {
	    int idx = idx_offset + i;
	    int state = (gpio_states >> i) & 0x1;
	    if (state == 1 && presence[idx] == 0) {	// FOB INSERTED
        printf("FOB CONNECTED: SLOT #%d\n", idx);
		enqueue_slot(idx);
		dispatch_add_event(idx, 0);
		presence[idx] = 1;
	    }
	    if (state == 0 && presence[idx] == 1){ // FOB REMOVED
        printf("FOB DISCONNECTED: SLOT #%d\n", idx);
		//printf("a\n");
		rmqueue_slot(idx);
		//printf("b\n");
		remove_fob_from_slot(idx);
		//printf("c\n");
		dispatch_remove_event(idx);
		presence[idx] = 0;
		//printf("d\n");
	    }
	}
    }
}

int dispatch_add_event(int slot, char* uid) {
    if (uid != NULL) {
        printf("FOB ADDED: SLOT #%d, UID %s\n", slot, uid);
	fflush(stdout);
    } else {
    	printf("FOB ADDED: SLOT #%d, NO UID\n", slot);
	fflush(stdout);
    }
    return 0;
}

int dispatch_remove_event(int slot) {
    printf("FOB  : SLOT #%d\n", slot);
    fflush(stdout);
    return 0;
}

int remove_fob_from_slot(int idx) {
    if (slots[idx] == NULL) { 	// slot is empty
        return 0;
    } else {			// slot is full
    	remove_w1_device(slots[idx]);	// remove from bus
	free(slots[idx]);		// remove string repr.
	slots[idx] = NULL;
	return 1;
    }
}

int handle_slot_queue() {
    if (slot_queue_a != slot_queue_b) { // a slot has been filled and needs to be updated
        size_t len;
        char* line = NULL;
        fslaves = fopen(busSlaves, "r");    // open the slave list file
        while(getline(&line, &len, fslaves) != -1 ){
            //printf(line);
	    if (!already_present(line) && line_found(line) && slot_queue_a != slot_queue_b) {	// new address found
		int slot = dequeue_slot();
	        slots[slot] = line;
		dispatch_add_event(slot, line);

	    } else {
            	free(line);
	    }
            line = NULL;
        }
        fclose(fslaves);
    }
    return 0;
}

int already_present(char* uid) {
    for (int i = 0; i < 20; i++) {
        if (slots[i] != NULL && strcmp(uid, slots[i]) == 0) {
	    return TRUE;
	}
    }
    return FALSE;
}

int line_found(char* line) {
   return strncmp(line, "not found", 9) != 0;
}

int enqueue_slot(int idx) {
    if ((slot_queue_b + 1) % 20 == slot_queue_a) { //queue full
        return -1;
    }
    slot_queue[slot_queue_b] = idx;
    slot_queue_b = (slot_queue_b + 1) % 20;
    return 1;
}

int dequeue_slot() {
    int ret = slot_queue[slot_queue_a];
    slot_queue_a = (slot_queue_a + 1) % 20;
    return ret;
}

int rmqueue_slot(int slot) {
    for (int i = slot_queue_a; i != slot_queue_b; i = (i+1) % 20){
        if (slot_queue[i % 20] == slot) {
	    for (int z = i; z != slot_queue_b; z = (z+1) % 20) {
	        slot_queue[z % 20] = slot_queue[(z + 1) % 20];
	    }
	    slot_queue_b = (slot_queue_b - 1) % 20;
	    return 1;
	}
    }
    return 0;
}

void print_queue() {
    printf("Slot queue: %d, %d [", slot_queue_a, slot_queue_b);
    for (int x = slot_queue_a; x != slot_queue_b; x = (x+1) % 20) {
        printf("%d, ", slot_queue[x]);
    }
    printf("]\n");
}

int handle_device_remove(int idx) {
    return 0;
}

int handle_device_add() {
    return 0;
}

int load_data_file() {
    // load the data
    return 0;
}

int setup_w1_config() {
    FILE* config;
    config = fopen(busSearch, "w"); // set to continuous search mode
    fprintf(config, "%s", "-1");
    fclose(config);

    return 0;
}

int remove_all_w1_devices() {
    fslaves = fopen(busSlaves, "r"); // open slave list file
    char* line;
    size_t len;

    while(getline(&line, &len, fslaves) != -1 ){ //Removes all devices from bus
        fremove = fopen(busRemove, "w"); // open file for writing
        fprintf(fremove, "%s", line);   // write EEPROM ID to remove
        fclose(fremove);                // close file
        free(line);
        line = NULL;
    }
    fclose(fslaves);
}

int remove_w1_device(char* device) {
    if (device == NULL) {
    	return -1;
    }
    fremove = fopen(busRemove, "w"); // open file for writing
    fprintf(fremove, "%s", device);   // write EEPROM ID to remove
    fclose(fremove);                // close file
}

int main_old() {
    signal(SIGINT, INThandler);

    FILE* fsearch;
    FILE* fremove;
    FILE* fslaves;

    char presentDev[] = "/home/pi/present_devices.txt"; // path to file read by Python code
    FILE* fdevs;

    char lastDevice[] = "2d-00003e07da1b\n"; // last EEPROM in list

    printf("Updating file: %s \n", presentDev);

    while(loop) {
        fslaves = fopen(busSlaves, "r"); // open slave list file
        char* line;
        size_t len;

        while(getline(&line, &len, fslaves) != -1 ){ //Removes all devices from bus
            fremove = fopen(busRemove, "w"); // open file for writing
            fprintf(fremove, "%s", line);   // write EEPROM ID to remove
            fclose(fremove);                // close file
            free(line);
            line = NULL;
        }
        fclose(fslaves);

        //TODO: Test with 25 devices on line
        

        blockingSearch(); // 3 of these seems to be enough to get it consistently?
        blockingSearch();
        blockingSearch();


        fslaves = fopen(busSlaves, "r");    // open the slave list file
        fdevs = fopen(presentDev, "w");     // open the Python eeprom list file
        while(getline(&line, &len, fslaves) != -1 ){
            //printf(line);
            fprintf(fdevs, "%s", line); // copy the EEPROMs into the python list file
            free(line);
            line = NULL;
        }
        fclose(fslaves);
        fclose(fdevs);

    };
    exit(0);
}

void blockingSearch() {
    FILE* fsearch;
    fsearch = fopen(busSearch, "w"); // open bus search file
    fprintf(fsearch, "1");          // trigger a search
    fclose(fsearch);
    size_t len;
    int iter_count = 0;
    int searchAgain = TRUE;
    while(searchAgain && iter_count++ < 10){ // search til device found or 0.5s pass
        usleep(50000); // sleep 50ms
        char* line = NULL;
        fsearch = fopen(busSearch, "r");
        getline(&line, &len, fsearch);
        if(!strcmp(line, "0\n")) {
            searchAgain = FALSE;
        }
        free(line);
        fclose(fsearch);
    }
}

void INThandler(int sig){
    printf("Writing data file & exiting... \n");
    loop = FALSE;
}
