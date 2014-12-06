#include <errno.h>
#include <termios.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <assert.h>
#include <sys/select.h>
#include <signal.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

// Test it with
// who >/dev/tcp/127.0.0.1/20240

// -----------------------------------------------------------------------------

#define SPEED 80                             // Scroll Speed in milliseconds 
#define LED_HOLD_TIME 1000 * SPEED
#define MAX_BATCH_SIZE 14

#define PORT_NAME    "/dev/ttyAMA0"
#define LOCK_FILE    "/tmp/pilited.lck"
#define LOG_FILE     "/tmp/pilited.log"
#define PIPE_FILE    "/tmp/pilited.pipe"
#define SERIALD_PORT 20240
#define LINE_WIDTH   132

// -----------------------------------------------------------------------------

static void close_fds()
{
   int i; 

   for (i = getdtablesize(); i >= 0; i--) 
       close(i); 
}

// -----------------------------------------------------------------------------

static int open_serial_port()
{
    int speed  = B9600; 
    int parity = 0;
    
    // pgf : Have to open non blocking for some reason.
    int fd = open (PORT_NAME, O_WRONLY | O_NONBLOCK | O_NOCTTY | O_SYNC);

    if (fd < 0)
    {
        printf("error %d opening %s: %s", errno, PORT_NAME, strerror(errno));
        exit(1);
    }

    struct termios tty;
    memset(&tty, 0, sizeof(tty));

    if (tcgetattr(fd, &tty) != 0)
    {
        perror("tcgetattr");
        exit(2);
    }

    cfsetospeed(&tty, speed);
    cfsetispeed(&tty, speed);

    tty.c_iflag &= ~IGNBRK;                 // ignore break signal
    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl

    tty.c_oflag = 0;                // no remapping, no delays

    tty.c_lflag = 0;                // no signaling chars, no echo,
                                    // no canonical processing

    tty.c_cflag  = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
    tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls, enable reading
    tty.c_cflag &= ~(PARENB | PARODD); // shut off parity
    tty.c_cflag |= parity;
    tty.c_cflag &= ~CSTOPB;
    tty.c_cflag &= ~CRTSCTS;

    tty.c_cc[VMIN]  = 0;            // read doesn't block
    tty.c_cc[VTIME] = 0;            // 0 seconds read timeout

    if (tcsetattr (fd, TCSANOW, &tty) != 0)
    {
        perror("tcsetattr");
        exit(2); 
    }

    return fd;
}

// -----------------------------------------------------------------------------

static int listen_network()
{
    int s, on = 1;                        
    struct sockaddr_in s_name;    
  
    if ((s = socket(AF_INET, SOCK_STREAM, 0)) == -1)
    {
          perror("socket error");
          exit(2);
    }
  
    if (setsockopt(s, SOL_SOCKET, SO_KEEPALIVE, &on, sizeof(on)) < 0)
    {
          perror("setsockopt error");
          exit(2);
    }
  
    if (setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on)) < 0)
    {
          perror("setsockopt error");
          exit(2);
    }
  
    s_name.sin_family      = AF_INET;
    s_name.sin_port        = htons(SERIALD_PORT);
    s_name.sin_addr.s_addr = htonl(INADDR_ANY);
  
    if (bind(s, (struct sockaddr *)&s_name, sizeof(s_name)) < 0)
    {
        perror("bind error");
        exit(2);
    }
  
    if (listen(s, 5) < 0)
    {
         perror("listen error");
         exit(2);
    }

    return s;
}

// -----------------------------------------------------------------------------

static int get_msg(int listen_fd, char *msg, int msg_max_len)
{
    struct sockaddr_in saddr;  
    socklen_t namelength;

    fd_set readfds; 
    int fd_count, max_fd, len;

    static int sock_fd = 0;
    static int pipe_fd = 0;

    for (;;)
    {
        if (!pipe_fd)
            pipe_fd = open(PIPE_FILE, O_RDWR);

        assert(pipe_fd != -1 && pipe_fd > 0);

        FD_ZERO(&readfds);
        FD_SET(listen_fd, &readfds);
        FD_SET(pipe_fd  , &readfds);

        max_fd = pipe_fd; 

        if (sock_fd) 
        {
            FD_SET(sock_fd, &readfds);
            max_fd = sock_fd > pipe_fd ? sock_fd : pipe_fd; 
        }

        fd_count = select(max_fd + 1, &readfds, NULL, NULL, NULL);

        if (fd_count == -1)
        {
            perror("select error");
            exit(2);
        }

        if (FD_ISSET(listen_fd, &readfds)) 
        { 
            if (sock_fd) 
            {
                close(sock_fd);
                sock_fd = 0; 
            }

            namelength = sizeof(saddr);

            sock_fd = accept(listen_fd, (struct sockaddr *)&saddr, &namelength);

            if (sock_fd == -1)
            {
                perror("accept error");
                exit(2);
            }

            //printf("# New Connection\n"); 
            //printf("# Client address : %s\n", inet_ntoa(saddr.sin_addr));
            //printf("# Client port    : %d\n", ntohs(saddr.sin_port));
        }
        else if (sock_fd && FD_ISSET(sock_fd, &readfds)) 
        { 
            len = read(sock_fd, msg, msg_max_len); 

            if (len) 
                break;

            //printf("Network connection closed\n");

            close(sock_fd);
            sock_fd = 0; 
        }
        else if (pipe_fd && FD_ISSET(pipe_fd, &readfds)) 
        { 
            len = read(pipe_fd, msg, msg_max_len); 

            if (len) 
                break;

            //printf("Pipe closed\n");

            close(pipe_fd);
            pipe_fd = 0; 
        }
    }

    return len;
}

// -----------------------------------------------------------------------------

static void open_log_file() 
{ 
    close(1); 
    freopen(LOG_FILE, "a", stdout); 
    setvbuf(stdout, NULL, _IOLBF, 0);

    close(2);
    freopen(LOG_FILE, "a", stderr); 
    setvbuf(stdout, NULL, _IOLBF, 0);
}

// -----------------------------------------------------------------------------

static void get_lock()
{
    int lock_fd;
    lock_fd = open(LOCK_FILE, O_RDWR|O_CREAT, 0640);

    assert(lock_fd != -1);
    assert(lockf(lock_fd, F_TLOCK, 0) == 0);
}

// -----------------------------------------------------------------------------

static void create_pipe()
{
    struct stat buffer;
    int status;

    status = stat(PIPE_FILE, &buffer);

    if (status != 0)
    {
        mode_t old;
      
        old = umask(0);
        assert(mkfifo(PIPE_FILE, 0666) == 0);
        (void) umask(old);
    }
}

// -----------------------------------------------------------------------------

int main(int argc, char **argv)
{
    close_fds();
    daemon(0, 0);

    open_log_file(); 
    get_lock();

    create_pipe();

    int serial_fd = open_serial_port(); 

    write (serial_fd, "$$$ALL,OFF\r", 11);  
    usleep(200000);
    write (serial_fd, "$$$SPEED80\r", 11);  

    //printf("STARTED - awaiting connections\n");
    int listen_fd = listen_network();

    char msg[256];
    int msg_len;

    while (1) 
    {
        msg_len = get_msg(listen_fd, msg, sizeof(msg) - 1); 
        msg[msg_len] = '\0'; 

        //printf("Msg:|%s|\n", msg);

        int batch; 
        char *ptr = msg;

        while(msg_len) 
        { 
           batch = (msg_len > MAX_BATCH_SIZE ? MAX_BATCH_SIZE : msg_len);

           char c; 
           int i, led_width = 0;

           for (i = 0; i < batch; i++)
           {
               c = *(ptr + i); 

               if (c == 10) { 
                   led_width += 4;  
                   *(ptr + i) = ' ';
               }
               else if (c < 32)
                   led_width += 0;  
               else if (c > 128)
                   led_width += 0;  
               else if (c == 128)       // Big empty square.
                   led_width += 8;  
               else if (c == 176)       // temp symbol.
                   led_width += 2;  
               else if (strchr("ABCDEFGHKLMNOPQRSTUVWXYZmvwxz", c))
                   led_width += 6;  
               else if (strchr("abcdefghknopqrsuyJ<>", c))
                   led_width += 5;  
               else if (strchr(" 1I\"()jt[]`", c))
                   led_width += 4;  
               else if (strchr(",.:;", c))
                   led_width += 3;  
               else if (strchr("!il'", c))
                   led_width += 2;  
               else { 
                   led_width += 6;  
               }
           }

           write(serial_fd, ptr, batch);  
           msg_len -= batch;
           ptr     += batch; 

           assert(msg_len >= 0);
           assert(ptr <= msg + sizeof(msg));

           usleep(LED_HOLD_TIME * led_width);
        }
    } 

    // Pause the scroll.
    //write(serial_fd, "$$$", 3);  
    //write(serial_fd, "\r\r", 2);

    exit(0);
}

// -----------------------------------------------------------------------------
