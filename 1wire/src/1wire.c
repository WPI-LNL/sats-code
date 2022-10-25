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


    char busSearch[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_search"; // Path to search control file
    char busRemove[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_remove"; // Path to slave remove file
    char busSlaves[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_slaves"; // Path to slave list file

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
        }
        fclose(fslaves);

        //TODO: Test with 25 devices on line
        

        
        fsearch = fopen(busSearch, "w"); // open bus search file
        fprintf(fsearch, "1");          // trigger a search
        fclose(fsearch);
        
        int iter_count = 0;
        line = 0x0;
        int searchAgain = TRUE;
        while(searchAgain && iter_count++ < 5){ // search til device found or 0.5s pass
            usleep(100000); // sleep 100ms
            fsearch = fopen(busSearch, "r");
            getline(&line, &len, fsearch);
            if(!strcmp(line, "0")) {
                searchAgain = FALSE;
            }/*
            fslaves = fopen(busSlaves, "r"); // open slave list file
            while(getline(&line, &len, fslaves) != -1 ){} // read to the end
            if(!strcmp(line, lastDevice)){ // if the last device is found, we assume search is done
                searchAgain = FALSE;
            }*/
        }

        //TODO trigger another search?
    

        fslaves = fopen(busSlaves, "r");    // open the slave list file
        fdevs = fopen(presentDev, "w");     // open the Python eeprom list file
        while(getline(&line, &len, fslaves) != -1 ){
            //printf(line);
            fprintf(fdevs, "%s", line); // copy the EEPROMs into the python list file
        }
        fclose(fslaves);
        fclose(fdevs);

    };
    exit(0);
};

void INThandler(int sig){
    printf("Goodbye ;) \n");
    loop = FALSE;
}


