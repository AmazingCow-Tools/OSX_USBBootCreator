COWTODO
====
Made with <3 by [Amazing Cow](http://www.amazingcow.com).

## Intro:
To make a Linux Bootable USB Disk on OSX, you normally have to check which
disk is your usb disk with```diskutil(8)```next convert the .iso to .img with
```hdiutil(1)```and after all copy the contents of the img generated with 
```hdiutil(8)```to your USB Disk with```dd(1)```.  
In the middle of process, you must unmount and after eject the disk.

Actually is pretty easy thing to do, not so many flags to remember and the
process is very safe, except for```dd(1)```. 

But since we do a lot of Linux USB disks (yep, Amazing Cow <3 Linux) 
we want to automate this process a little bit. Is very tedious keep repeating
the same keystrokes for a pretty dummy task...

So here are our simple program to automate some tedious parts of creating 
a usb boot disk in OSX.

####Note:
**WE FOLLOWED THE STEPS LISTED IN UBUNTU USB CREATION PAGE ON OSX TO CREATE 
THIS SCRIPT. WE ARE VERY HAPPY WITH IT, BUT TAKE CARE,**```dd```**MUST BE 
DONE WITH SUPERUSER PRIVILEGES AND YOU'RE MESSING WITH YOUR DISKS, SO TAKE 
A DOUBLE, TRIPLE, 100^100 CHECK BEFORE HIT ENTER :)**


## Install:
```$ ln -f path/to/usbbootcreator.py /usr/local/bin/usb-boot-creator```

or use the makefile:

```$ sudo make install```


## Usage:
```
usb-boot-creator [-hv] [-i] [-V] [--disk <name> --image <path>]

Options:
 *-h --help           : Show this screen.
 *-v --version        : Show app version and copyright.
 *-i --interactive    : Runs in interactive (safer?) mode. Verbose is assumed.
  -V --verbose        : Verbose mode, show more helpful output.
     --disk <name>    : The name of the disk (without the path).
     --image <path>   : The path of .img (If .iso is passed it will be converted).
```

#####Notes:
TAKE A LOT OF CARE, you will need perform```dd(1)```as superuser, 
so doublecheck your disk name before do anything stupid.

Options marked with * are exclusive, i.e. the```usb-boot-creator```will 
run that and exit successfully after the operation.
 
## License:
This software is released under GPLv3.

## TODO:
Check the TODO file.

## Others:
Check our repos and take a look at our [open source site](http://opensource.amazingcow.com).
