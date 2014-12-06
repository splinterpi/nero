#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>
#include <signal.h>

#define PIPE_FILE    "/tmp/pilited.pipe"

// -----------------------------------------------------------------------------

int main(int argc, char **argv)
{
    int fd_r = open(PIPE_FILE, O_RDONLY|O_NONBLOCK);
    assert(fd_r != -1);

    // With the pipe open for read by the above, we can open the pipe for
    // write without the open call blocking.

    FILE *f = fopen(PIPE_FILE, "w");
    assert(f);
    setvbuf(f, NULL, _IOLBF, 0);

    close(fd_r);

    char buf[4096]; 
    int count;

    signal(SIGPIPE, SIG_IGN);

    for(;;) 
    { 
        count = read(0, buf, sizeof(buf)); 
        if (!count) break;

        // Ignore a possible EPIPE error if the pilited process isn't running.  
        fwrite(buf, 1, count, f);
    }

    exit(0);
}

// -----------------------------------------------------------------------------
