```python
print("1 + 1 = ", 1+1)
```

```c
#include <stdlib.h>
#include <unistd.h>
/* Petit programme qui teste si un arduino est branché */
int main(int argc, const char **argv){
    int fd = open("/dev/ttyUSB0", O_RDWR);
    if (fd < 0) return EXIT_FAILURE;
    close(fd);
    return EXIT_SUCCESS;
}
```
