#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <signal.h>

#include "1wire.h"

#define TRUE 1
#define FALSE 0

char busSearch[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_search"; // Path to search control file
char busRemove[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_remove"; // Path to slave remove file
char busSlaves[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_slaves"; // Path to slave list file

int loop = TRUE;

int main() {
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
    char* line = 0x0;
    size_t len;
    int iter_count = 0;
    int searchAgain = TRUE;
    while(searchAgain && iter_count++ < 10){ // search til device found or 0.5s pass
        usleep(50000); // sleep 50ms
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
    printf("Goodbye ;) \n");
    loop = FALSE;
}


