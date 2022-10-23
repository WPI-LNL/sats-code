#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>

#include "1wire.h"

#define TRUE 1
#define FALSE 0

int loop = TRUE;

int main() {
    signal(SIGINT, INThandler);

    printf("Hello world\n");

    char busSearch[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_search";
    char busRemove[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_remove";
    char busSlaves[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_slaves";

    FILE* fsearch;
    FILE* fremove;
    FILE* fslaves;

    char presentDev[] = "/home/pi/present_devices.txt";
    FILE* fdevs;

    while(loop) {
        fslaves = fopen(busSlaves, "r");
        char* line;
        size_t len;

        while(getline(&line, &len, fslaves) != -1 ){ //Removes all devices from bus
            fremove = fopen(busRemove, "w");
            fprintf(fremove, "%s", line);
            fclose(fremove);
        }
        fclose(fslaves);

        //TODO: Test with 25 devices on line
        fsearch = fopen(busSearch, "w");
        fprintf(fsearch, "1");
        fclose(fsearch);
        usleep(400000); 

        fsearch = fopen(busSearch, "w");
        fprintf(fsearch, "1");
        fclose(fsearch);
        usleep(400000);

        fslaves = fopen(busSlaves, "r");
        fdevs = fopen(presentDev, "w");
        while(getline(&line, &len, fslaves) != -1 ){
            printf(line);
            fprintf(fdevs, "%s", line);
        }
        fclose(fslaves);
        fclose(fdevs);

    };
    exit(0);
};

void INThandler(int sig){
    printf("Goodbye ;)");
    loop = FALSE;
}


