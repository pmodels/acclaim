/* 
   Contributors:
     Mike Stewart at NERSC
     Jeff Hammond at Intel
     Scott Parker at Argonne

  Description:
    Returns information about node locaction on the ALCF Cray XC40 system Theta.

    The XC40 Dragonfly network has the following geometry:
      4 computes nodes connect directly to each Aries router
      96 Aries routers form a group, within the group the routers are arranged in a 6x16 grid with 
         all to all connections between routers within each column (chassis in a group, 0-5)
         and row (blades in a chassis, 0-15)
      Theta has 9 groups, all to all connections exist between each group

     Node location is derived from the node canonical name found in the file /proc/cray_xt/cname
     The canonical name format is c(i)-(j)c(k)s(l)n(x)
       - rack location:
         - i: rack coord 
         - j: rack coord
       - k: chasis number in rack (0-2)
       - l: blade number in chassis (0-15)
       - x: nic number in blade (0-3)

     Theta rack to group mapping:
       c0-0, c1-0     -> 0
       c0-1, c1-1     -> 1
       c2-0, c3-0     -> 2
       c2-1, c3-1     -> 3
       c4-0, c5-0     -> 4
       c4-1, c5-1     -> 5
       c6-0, c7-0     -> 6
       c6-1, c7-1     -> 7
       c8-0, c9-0     -> 8
       c10-0, c11-0   -> 9

  useage:
    // declare topo variable
    xctopo_t topo;

    // gather raw topology information
    int rc = xctopo_get_mycoords(&topo);

    // print raw topo data
    printf("%d %d %d %d %d\n", topo.racki, topo.rackj, topo.chassis, topo.blade, topo.nic);

    // map raw topo data into a group, chasis, blade, and nic values
    int group = xctopo_get_group(&topo);
    int ch = xctopo_get_chassis(&topo);
    int blade = xctopo_get_blade(&topo);
    int nic = xctopo_get_nic(&topo));


*/

typedef struct xctopo_s
{
    int racki;
    int rackj;
    int chassis;
    int blade;
    int nic;
}
xctopo_t;


int xctopo_get_mycoords(xctopo_t * topo);
int xctopo_get_group(xctopo_t *topo);
int xctopo_get_chassis(xctopo_t *topo);
int xctopo_get_blade(xctopo_t *topo);
int xctopo_get_nic(xctopo_t *topo);



