#include <stdio.h>
#include <string.h>

#include "1wire.h"

#define TRUE 1
#define FALSE 0

int main() {
    printf("Hello world\n");

    char busSearch[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_search";
    char busRemove[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_remove";
    char busSlaves[] = "/sys/bus/w1/devices/w1_bus_master1/w1_master_slaves";

    FILE* fsearch;
    FILE* fremove;
    FILE* fslaves;

    //while(FALSE) {
        fslaves = fopen(busSlaves, "r");
        char* line;
        size_t len;

        while(getline(&line, &len, fslaves) != -1 ){ //Removes all devices from bus
            fremove = fopen(busRemove, "w");
            fprintf(fremove, "%s", line);
            fclose(fremove);
        }
        fclose(fslaves);

        fsearch = fopen(busSearch, "w");
        fprintf(fsearch, "1");

        fslaves = fopen(busSlaves, "r");
        while(getline(&line, &len, fslaves) != -1 ){
            printf(line);
        }
        fclose(fslaves);

    //}

    printf("%s + \n", busSearch);
};



