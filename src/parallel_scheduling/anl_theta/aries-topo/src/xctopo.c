#include <stdio.h>
//#include <stdlib.h>
//#include <string.h>
//#include <unistd.h>

#include "xctopo.h"

int xctopo_get_mycoords(xctopo_t * topo)
{
  FILE * procfile = fopen("/proc/cray_xt/cname","r");

  if (procfile!=NULL) {

    char a, b, c, d;
    int racki, rackj, chassis, blade, nic;

    /* format example: c1-0c1s2n1 c3-0c2s15n3 */
    fscanf(procfile, 
           "%c%d-%d%c%d%c%d%c%d", 
           &a, &racki, &rackj, &b, &chassis, &c, &blade, &d, &nic);

#ifdef DEBUG
    fprintf(stderr, "coords = (%d,%d,%d,%d) \n", racki, rackj, chassis, blade, nic);
#endif

    topo->racki   = racki;
    topo->rackj   = rackj;
    topo->chassis  = chassis;
    topo->blade  = blade;
    topo->nic = nic;

    fclose(procfile);

  } else {
    fprintf(stderr, "xctopo_get_mycoords: fopen has failed! \n");
    return 1;
  }

  return 0;
}


int xctopo_get_group(xctopo_t *topo)
{
  return topo->racki/2+ topo->rackj*6;
}


int xctopo_get_chassis(xctopo_t *topo)
{
  return (topo->racki%2)*3+topo->chassis;
}


int xctopo_get_blade(xctopo_t *topo)
{
  return topo->blade;
}


int xctopo_get_nic(xctopo_t *topo)
{
  return topo->nic;
}
