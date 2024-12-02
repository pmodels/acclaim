#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <hwloc.h>
#include <mpi.h>

void find_match(const char * mstr, char *mode); 

int main (int argc, char **argv)
{
    hwloc_topology_t topology;
    hwloc_obj_t root;
    char *cluster_mode;
    char *memory_mode;
    char *recv_buf;
    int rc;
    int wrank;
    int wsize;
    int happy;
    FILE *f;
    uint32_t row;
    uint32_t col;
    uint32_t chassis;
    uint32_t blade;
    uint32_t node;
    uint32_t group;
    uint32_t netloc;
    uint32_t *netlocs;
    char numa_str[64];
    char mcdram_str[64];

    rc = MPI_Init(&argc, &argv);
    if (rc != MPI_SUCCESS)
    {
        fprintf(stderr, "MPI_Init failed: %d\n", rc);
        exit(1);
    } 

    MPI_Comm_rank(MPI_COMM_WORLD, &wrank);
    MPI_Comm_size(MPI_COMM_WORLD, &wsize); 

/*
    rc = hwloc_topology_init(&topology);
    if (rc != 0)
    {
        fprintf(stderr, "hwloc_topology_init failed: %d\n", rc);
        exit(1);
    }

    rc = hwloc_topology_load(topology);
    if (rc != 0)
    {
        fprintf(stderr, "hwloc_topology_load failed: %d\n", rc);
        exit(1);
    }

    root = hwloc_get_root_obj(topology);

    cluster_mode = hwloc_obj_get_info_by_name(root, "ClusterMode");
    recv_buf = calloc(strlen(cluster_mode)+1, 1);
    MPI_Reduce(cluster_mode, recv_buf, strlen(cluster_mode), MPI_BYTE,
               MPI_BAND, 0, MPI_COMM_WORLD);
    if ((wrank == 0) && (strcmp(cluster_mode, recv_buf) != 0))
    {
        printf("Cluster Mode mismatch!\n");
        happy = 0;
    }
    else
    {
        happy = 1;
    }
    MPI_Bcast(&happy, 1, MPI_INT, 0, MPI_COMM_WORLD);
    free(recv_buf);
    if (!happy)
    {
         char data[64];
         char buf[sizeof(data)*wsize];
         memset(data, 0, sizeof(data));
         memset(buf, 0, sizeof(data)*wsize);
         strncpy(data, cluster_mode, strlen(cluster_mode));
         MPI_Gather(data, sizeof(data), MPI_BYTE,
                    buf, sizeof(data), MPI_BYTE,
                    0, MPI_COMM_WORLD);
         if (wrank == 0)
         {
             int i;
             for (i = 0; i < wsize; i++)
                 printf("\t%04d\t%s\n", i, &buf[i*sizeof(data)]);
         }
    }

    memory_mode = hwloc_obj_get_info_by_name(root, "MemoryMode");
    recv_buf = calloc(sizeof(memory_mode)+1, 1);
    MPI_Reduce(memory_mode, recv_buf, strlen(memory_mode), MPI_BYTE,
               MPI_BAND, 0, MPI_COMM_WORLD);
    if ((wrank == 0) && (strcmp(memory_mode, recv_buf) != 0))
    {
        printf("Memory Mode mismatch!\n");
        happy = 0;
    }
    else
    {
        happy = 1;
    }
    MPI_Bcast(&happy, 1, MPI_INT, 0, MPI_COMM_WORLD);
    free(recv_buf);
    if (!happy)
    {
         char data[64];
         char buf[sizeof(data)*wsize];
         memset(data, 0, sizeof(data));
         memset(buf, 0, sizeof(data)*wsize);
         strncpy(data, memory_mode, strlen(memory_mode));
         MPI_Gather(data, sizeof(data), MPI_BYTE,
                    buf, sizeof(data), MPI_BYTE,
                    0, MPI_COMM_WORLD);
         if (wrank == 0)
         {
             int i;
             for (i = 0; i < wsize; i++)
                 printf("\t%04d\t%s\n", i, &buf[i*sizeof(data)]);
         }
    }
*/

    f = fopen("/proc/cray_xt/cname", "rb");
    if (f == NULL)
    {
        perror("Failed to open file: /proc/cray_xt/cname");
        exit(1);
    }
    rc = fscanf(f, "c%d-%dc%ds%dn%d", &col, &row, &chassis, &blade, &node);
    if (rc != 5)
    {
        fprintf(stderr, "Failed to parse /proc/cray_xt/cname: %d\n", rc);
    }
    fclose(f);

    //
    // node  = bits 0..1
    // blade = bits 2..6
    // chassis = bits 7..9 (odd col 0-2, even col 3-5)
    // group = bits 9..18 (9 local groups)
    //
    group = 1 << ((col + row*12)/2);
    netloc = ((group & 0x1ff) << 9) |
             (((chassis+(3*(col&0x1))) & 0x7) << 6) | 
             ((blade & 0xf) << 2) |
             ((node & 0x3) << 0);
    
    netlocs = malloc(sizeof(*netlocs)*wsize);
    assert(netlocs);

    //printf ("rank:%d col:%d row:%d chassis:%d blade:%d node:%d\n",
    //        wrank, col, row, chassis, blade, node);
    printf ("rank:%d netloc:%x netloc:0x%x\n", wrank, netloc, netloc & ((0x1ff << 9) | (0x7 << 6) | (0xf << 2)));

    MPI_Gather(&netloc, 1, MPI_INT,
               netlocs, 1, MPI_INT,
               0, MPI_COMM_WORLD);

    /*
     * Cray Specific Method to read configuration
     */
    sprintf(numa_str, "numa_cfg\\[%d\\]=", node);
    sprintf(mcdram_str, "mcdram_cfg\\[%d\\]=", node);
    cluster_mode = calloc(64, 1);
    memory_mode = calloc(64, 1);
    find_match(numa_str, cluster_mode);
    find_match(mcdram_str, memory_mode);

    recv_buf = calloc(strlen(cluster_mode)+1, 1);
    MPI_Reduce(cluster_mode, recv_buf, strlen(cluster_mode), MPI_BYTE,
               MPI_BAND, 0, MPI_COMM_WORLD);
    if ((wrank == 0) && (strcmp(cluster_mode, recv_buf) != 0))
    {
        printf("Cluster Mode mismatch!\n");
        happy = 0;
    }
    else
    {
        happy = 1;
    }
    MPI_Bcast(&happy, 1, MPI_INT, 0, MPI_COMM_WORLD);
    free(recv_buf);
    if (!happy)
    {
         char data[64];
         char buf[sizeof(data)*wsize];
         memset(data, 0, sizeof(data));
         memset(buf, 0, sizeof(data)*wsize);
         strncpy(data, cluster_mode, strlen(cluster_mode));
         MPI_Gather(data, sizeof(data), MPI_BYTE,
                    buf, sizeof(data), MPI_BYTE,
                    0, MPI_COMM_WORLD);
         if (wrank == 0)
         {
             int i;
             for (i = 0; i < wsize; i++)
                 printf("\t%04d\t%s\n", i, &buf[i*sizeof(data)]);
         }
    }

    recv_buf = calloc(sizeof(memory_mode)+1, 1);
    MPI_Reduce(memory_mode, recv_buf, strlen(memory_mode), MPI_BYTE,
               MPI_BAND, 0, MPI_COMM_WORLD);
    if ((wrank == 0) && (strcmp(memory_mode, recv_buf) != 0))
    {
        printf("Memory Mode mismatch!\n");
        happy = 0;
    }
    else
    {
        happy = 1;
    }
    MPI_Bcast(&happy, 1, MPI_INT, 0, MPI_COMM_WORLD);
    free(recv_buf);
    if (!happy)
    {
         char data[64];
         char buf[sizeof(data)*wsize];
         memset(data, 0, sizeof(data));
         memset(buf, 0, sizeof(data)*wsize);
         strncpy(data, memory_mode, strlen(memory_mode));
         MPI_Gather(data, sizeof(data), MPI_BYTE,
                    buf, sizeof(data), MPI_BYTE,
                    0, MPI_COMM_WORLD);
         if (wrank == 0)
         {
             int i;
             for (i = 0; i < wsize; i++)
                 printf("\t%04d\t%s\n", i, &buf[i*sizeof(data)]);
         }
    }

    if (wrank == 0)
    {
        int groups;
        int chassis;
        int blades;

        groups  = count_links(netlocs, wsize, (0x1ff << 9));
        chassis = count_links(netlocs, wsize, (0x1ff << 9) | (0x7 << 6));
        blades  = count_links(netlocs, wsize, (0x1ff << 9) | (0x7 << 6) | (0xf << 2));
        printf("cluster_mode %s\tmemory_mode %s\tgroups %d\tchassis %d\tblades %d\n",
               cluster_mode,
               memory_mode,
               groups,
               chassis,
               blades);
    }

    free(netlocs);

    MPI_Finalize();

    return 0;
}

int count_links (uint32_t *netlocs, int size, uint32_t mask)
{
    int i; 
    uint32_t *groups;
    uint32_t last;
    int cnt;

    int ifunc(const void *a, const void *b) { const uint32_t *ia = a; const uint32_t *ib = b; return (*ia < *ib); }

    groups = malloc(sizeof(*groups)*size);
    assert(groups);

    for (i = 0; i < size; i++)
    {
        groups[i] = netlocs[i] & mask;
    }
    qsort(groups, size, sizeof(uint32_t), ifunc);

    for (i = 0, cnt = 0, last = ~0; i < size; i++)
    {
        if (groups[i] != last)
        {
            cnt += 1;
            last = groups[i];
        }
    }
    free(groups);

    return cnt;
}

#include <regex.h>

void find_match(const char * mstr, char *mode)
{
    FILE *f;
    int r;
    char *fdata;
    long len;
    regex_t preg;
    regmatch_t mreg[1];
    
    r = regcomp(&preg, mstr, 0);

    f = fopen ("/.hwinfo.cray", "rb");
    fseek(f, 0, SEEK_END);
    len = ftell(f);
    fdata = malloc(len);
    fseek(f, 0, SEEK_SET);
    fread(fdata, sizeof(char), len, f);
    fclose(f);

    r = regexec(&preg, fdata, 1, mreg, 0);
    if ((r == 0) && (mreg[0].rm_so > -1))
    {
        sscanf(fdata+mreg[0].rm_so+strlen(mstr)-2, "%s", mode);
    }
    regfree(&preg);
    free(fdata);
    return;
}
