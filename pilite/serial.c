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

int
set_interface_attribs (int fd, int speed, int parity)
{
        struct termios tty;
        memset (&tty, 0, sizeof tty);
        if (tcgetattr (fd, &tty) != 0)
        {
                printf("error %d from tcgetattr", errno);
                return -1;
        }

        cfsetospeed (&tty, speed);
        cfsetispeed (&tty, speed);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
        // disable IGNBRK for mismatched speed tests; otherwise receive break
        // as \000 chars
        tty.c_iflag &= ~IGNBRK;         // ignore break signal
        tty.c_lflag = 0;                // no signaling chars, no echo,
                                        // no canonical processing
        tty.c_oflag = 0;                // no remapping, no delays
        tty.c_cc[VMIN]  = 0;            // read doesn't block
        tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

        tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl

        tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls,
                                        // enable reading
        tty.c_cflag &= ~(PARENB | PARODD);      // shut off parity
        tty.c_cflag |= parity;
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CRTSCTS;

        if (tcsetattr (fd, TCSANOW, &tty) != 0)
        {
                printf("error %d from tcsetattr", errno);
                return -1;
        }
        return 0;
}

void
set_blocking (int fd, int should_block)
{
        struct termios tty;
        memset (&tty, 0, sizeof tty);
        if (tcgetattr (fd, &tty) != 0)
        {
                printf("error %d from tggetattr", errno);
                return;
        }

        tty.c_cc[VMIN]  = should_block ? 1 : 0;
        tty.c_cc[VTIME] = 5;            // 0.5 seconds read timeout

        if (tcsetattr (fd, TCSANOW, &tty) != 0)
                printf("error %d setting term attributes", errno);
}


char *portname = "/dev/ttyAMA0";
char buf[256];
#define BATCH_SIZE 14
//#define BATCH_SIZE 2
// Scroll Speed in milliseconds 
#define SPEED 80
#define LED_HOLD_TIME 1000 * SPEED

int batch = BATCH_SIZE; 
int led_width = 0;

int
main(int argc, char **argv)
{
        // pgf : Have to open non blocking for some reason.
	int fd = open (portname, O_WRONLY | O_NONBLOCK | O_NOCTTY | O_SYNC);
	if (fd < 0)
	{
		printf("error %d opening %s: %s", errno, portname, strerror (errno));
		exit(1);
	}

	set_interface_attribs (fd, B9600, 0); 
	set_blocking (fd, 0);                // set no blocking

        int len; 

        write (fd, "$$$ALL,OFF\r", 11);  
        usleep(200000);
        write (fd, "$$$SPEED80\r", 11);  

        while ((len = read(0, buf, sizeof(buf)))) { 
            int ws; 
            char *ptr = buf;

            while(len) { 
               ws = (len > batch ? batch : len);

               int i; 
               char c; 
               for (i = 0; i < ws; i++)
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
                   else if (c == 128)            // Big empty square.
                       led_width += 8;  
                   else if (c == 123)       // temp symbol.
                       led_width += 5;  
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

               write (fd, ptr, ws);  
               len   -= ws;
               ptr   += ws; 
               batch -= ws;

               assert(batch >= 0);
               assert(len   >= 0);
               assert(ptr   <= buf + sizeof(buf));

               if (batch == 0)
               {
                   batch     = BATCH_SIZE;
                   usleep(LED_HOLD_TIME * led_width);
                   led_width = 0;

                   // Pause the scroll.
                   //write(fd, "$$$", 3);  
                   //write(fd, "\r\r", 2);
                   //usleep(5000000);
               } 
            }
        } 

        usleep((LED_HOLD_TIME * (led_width + 16)));

        //write (fd, "$$$", 3);  
        //write(fd, "\r\r", 2);

        exit(0);
}
