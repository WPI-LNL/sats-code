#include <linux/gpio.h>
#include <stdio.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <string.h>
#include <unistd.h>

#include "onewire-controller.h"

#define ONEWIRE_LINE 26
#define W1_ADDR_LEN 56

struct gpiohandle_data gpio_data;
struct gpiohandle_request gpio_writerequest;
struct gpiohandle_request gpio_readrequest;
int fd;


long long slots[20];
int presence[20];
long long* known_uids;
int known_uids_len;

long long testyboi = 0x00003e08a09d2d;


int main(int argc, char** argv){
    setup_gpio_vars();
    usleep(250000);
    long long ret;
    ret = gpio_read();
    //gpio_write(1);
    for (int x = 0; x > -10000; x++) {
	    
        ret = gpio_read();
	if (ret!= 0)
	        printf("Value read is : %d\n", gpio_data.values[0]);
        usleep(25);
	
        //ret = gpio_read();
        //printf("Value read is : %d\n", gpio_data.values[0]);
        //usleep(250000);
	//gpio_write(1);
	//usleep(250000);
	//gpio_write(0);
	
	//ret = poll_presence(0x00003e09a09d);
	//ret = poll_presence(0x00003e08a09d2d);
	//printf("Presence: %lld\n", ret);
	//usleep(250000);
    }
    return 0;
}
/*
struct gpiohandle_request req;
struct gpiohandle_data data;
req.lineoffsets[0] = 4;
req.lines = 1;
req.flags = GPIOHANDLE_REQUEST_OUTPUT;
strcpy(req.consumer_label, "blinker");
int lhfd = ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &req);
data.values[0] = 1;
ret = ioctl(req.fd, GPIOHANDLE_SET_LINE_VALUES_IOCTL, &data);
data.values[0] = 0;
ret = ioctl(req.fd, GPIOHANDLE_SET_LINE_VALUES_IOCTL, &data);
*/


int setup_gpio_vars() {
    // ** This code from the RPi stackexchange: https://raspberrypi.stackexchange.com/questions/101718/control-gpio-pins-from-c ** //
    // ONE_TIME SETUP //
    //Opening device and getting file descriptor.
    fd = open("/dev/gpiochip0",O_RDONLY);

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
    fprintf(stdout,"line %2d: %s\n",linfo.line_offset,linfo.name);

    //Reading lines
    //Set up some handles for requests and data
    struct gpiohandle_request req;
    struct gpiohandle_data data;
    int lhfd;

    //Although req and data can read multiple gpios at a time, we'll use just one
    //This reads line offset 4, which corresponds to the BCM value in "gpio readall"
    gpio_readrequest.lineoffsets[0] = 26; //19
    //have to indicate how many lines we are reading.
    gpio_readrequest.lines = 1;
    //Make this an input request
    gpio_readrequest.flags = GPIOHANDLE_REQUEST_INPUT | GPIOHANDLE_REQUEST_BIAS_DISABLE;
    
    lhfd = ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &gpio_readrequest);

    gpio_writerequest.lineoffsets[0] = ONEWIRE_LINE;
    //have to indicate how many lines we are reading.
    gpio_writerequest.lines = 1;
    //Make this an input request
    gpio_writerequest.flags = GPIOHANDLE_REQUEST_OUTPUT | GPIOHANDLE_REQUEST_OPEN_SOURCE;
    
    lhfd = ioctl(fd, GPIO_GET_LINEHANDLE_IOCTL, &gpio_writerequest);

    //Optionally give the line a name
    //strcpy(req.consumer_label, "First Switch");
}

int gpio_write(int var) {

    int ret;
    gpio_data.values[0] = var;
    ret = ioctl(gpio_writerequest.fd, GPIOHANDLE_SET_LINE_VALUES_IOCTL, &gpio_data);
}

int gpio_read() {
    //Get a line handle. Note that req.fd is provided a handle for the next ioctl.
    int ret = ioctl(gpio_readrequest.fd,  GPIOHANDLE_GET_LINE_VALUES_IOCTL, &gpio_data);
    return gpio_data.values[0];
}



//long long known_devices[]

int find_device_in_list(long long* addresses, int length) {
    for (int i = 0; i < length; i++) {
        if (poll_presence(addresses[i])) {
            return addresses[i];
        }
    }
    return 0;
}

int find_device_not_in_list(long long* addresses, int length) {
    for (int i = 0; i < length; i++) {
        if (!poll_presence(addresses[i])) {
            return addresses[i];
        }
    }
    return 0;
}

int poll_presence(long long address) {
    reset_bus();
    write_byte((char)0xF0);
    int a, b;
    for (int i = 0; i < W1_ADDR_LEN; i++) {
        a = read_bit();
        b = read_bit();
        write_bit((address >> i) & 0x1);
        if (!(a | b)) {
	    printf("Search failed at %d\n", i);
            return 0;
        }
    }
    printf("search succeeded?\n");
    return address;
}

int reset_bus() {
    //gpio write low
    gpio_write(0);
    usleep(480);
    //gpio write high
    gpio_write(0);
    usleep(70);
    int ret = gpio_read();
    //return = gpio read
    usleep(410);
    return ret;
}

int write_byte(char b) {
    write_bits(b, 8);
}
char read_byte() {
    long long data = 0;
    read_bits(&data, 8);
    char b = data &0xFF;
    return b;
}

int write_bits(long long data, int nbits) {
    if (nbits > 64) {
        return -1;
    }
    for (int i = 0; i < nbits; i++) {
        write_bit((data >> i) & 0x1);
    }
    return nbits;
}

int read_bits(long long* data, int nbits) {
    *data = 0x0;
    if (nbits > 64) {
        return -1;
    }
    for (int i = 0; i < nbits; i++) {
        *data = (*data << 1) & read_bit();
    }
    return nbits;
}

int write_bit(int bit) {
    //write 0
    gpio_write(0);
    usleep(6);
    gpio_write(bit);
    usleep(54);
    usleep(10);
    return 0;
}

int read_bit() {
    //write 0
    gpio_write(0);
    usleep(6);
    //write 1
    gpio_write(1);
    usleep(9);
    int ret = !gpio_read();
    usleep(45);
    usleep(10);
    return ret;
}

