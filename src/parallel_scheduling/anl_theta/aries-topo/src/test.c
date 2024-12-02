#include <stdio.h>
#include <stdlib.h>
//#include <string.h>
//#include <unistd.h>
#include <mpi.h>
#include <unistd.h>

#include "xctopo.h"

int main(int argc, char * argv[])
{
  int rank, size;

  MPI_Init(&argc, &argv);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);
  MPI_Comm_size(MPI_COMM_WORLD, &size);

  FILE * procfile = fopen("/proc/cray_xt/cname","r");
  if (procfile!=NULL) {
    char str[255];
    fscanf(procfile, "%s", str);
    sleep(rank/250);
    printf("%d: /proc/cray_xt/cname = %s \n", rank, str);
    fclose(procfile);
  } else {
    fprintf(stderr, "fopen has failed! \n");
    exit(1);
  }

  xctopo_t topo;
  int rc = xctopo_get_mycoords(&topo);

  int racki   = topo.racki;
  int rackj   = topo.rackj;
  int raw_chassis  = topo.chassis;
  int blade = topo.blade;
  int nic = topo.nic;

  //printf("%d: xctopo coords = (%d,%d,%d,%d,%d) \n", rank, racki, rackj, raw_chassis, blade, nic);
 
  int group = xctopo_get_group(&topo);
  int chassis = xctopo_get_chassis(&topo);
  blade = xctopo_get_blade(&topo);
  nic = xctopo_get_nic(&topo);
  
  //printf("%d: group, chassis, blade, nic = (%d,%d,%d,%d) \n", rank, group, chassis, blade, nic);
  
  int uniq_chassis = group*6+chassis;
  int uniq_blade = uniq_chassis*16+blade;
  int uniq_node = uniq_blade*4 + nic;

  //printf("%d: group, uchassis, ublade, node = (%d,%d,%d,%d) \n", rank, group, uniq_chassis, uniq_blade, uniq_node);
 
  unsigned int gbit = (1 << group);  
  unsigned int result;

  MPI_Reduce(&gbit, &result, 1, MPI_UNSIGNED, MPI_LOR, 0, MPI_COMM_WORLD);

  if (rank == 0) {
    printf("results = %u\n", result);
  }

  MPI_Finalize();

  return 0;
}
