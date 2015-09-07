#!/usr/bin/python
#coding=utf8
##----------------------------------------------------------------------------##
##               █      █                                                     ##
##               ████████                                                     ##
##             ██        ██                                                   ##
##            ███  █  █  ███                                                  ##
##            █ █        █ █        usbbootcreator.py                         ##
##             ████████████         Linux USB Boot Craetor                    ##
##           █              █       Copyright (c) 2015 AmazingCow             ##
##          █     █    █     █      www.AmazingCow.com                        ##
##          █     █    █     █                                                ##
##           █              █       N2OMatt - n2omatt@amazingcow.com          ##
##             ████████████         www.amazingcow.com/n2omatt                ##
##                                                                            ##
##                                                                            ##
##                  This software is licensed as GPLv3                        ##
##                 CHECK THE COPYING FILE TO MORE DETAILS                     ##
##                                                                            ##
##    Permission is granted to anyone to use this software for any purpose,   ##
##   including commercial applications, and to alter it and redistribute it   ##
##               freely, subject to the following restrictions:               ##
##                                                                            ##
##     0. You **CANNOT** change the type of the license.                      ##
##     1. The origin of this software must not be misrepresented;             ##
##        you must not claim that you wrote the original software.            ##
##     2. If you use this software in a product, an acknowledgment in the     ##
##        product IS HIGHLY APPRECIATED, both in source and binary forms.     ##
##        (See opensource.AmazingCow.com/acknowledgment.html for details).    ##
##        If you will not acknowledge, just send us a email. We'll be         ##
##        *VERY* happy to see our work being used by other people. :)         ##
##        The email is: acknowledgmentopensource@AmazingCow.com               ##
##     3. Altered source versions must be plainly marked as such,             ##
##        and must notbe misrepresented as being the original software.       ##
##     4. This notice may not be removed or altered from any source           ##
##        distribution.                                                       ##
##     5. Most important, you must have fun. ;)                               ##
##                                                                            ##
##      Visit opensource.amazingcow.com for more open-source projects.        ##
##                                                                            ##
##                                  Enjoy :)                                  ##
##----------------------------------------------------------------------------##

## Imports ##
import os;
import os.path;
import getopt;
import sys;
import plistlib;
try:
    from termcolor import colored;
except:
    print "termcolor cannot be imported - No colors for you :/";
    def colored(msg, color):
        return msg;

# TEMP_DISKUTIL_LIST = "/tmp/linux_usb_diskutil/listdisk.plist";
class Constants:
    TEMP_DISKUTIL_DIR  = os.path.expanduser("~/Desktop/linux_usb_diskutil/");
    TEMP_DISKUTIL_LIST = os.path.join(TEMP_DISKUTIL_DIR, "listdisk.plist");
    SUPPORTED_EXTS     = ".img", ".iso";

class Globals:
    verbose    = True;
    disks_info = None;

class Log:
    @staticmethod
    def fatal(msg):
        print ("{} {}".format(colored("[FATAL]", "red"),
                              msg));
        exit(1);
    @staticmethod
    def verbose(msg):
        if(Globals.verbose):
            print colored(msg, "magenta");

################################################################################
## Helper Functions                                                           ##
################################################################################
def checked_os_system(cmd, expected_ret = 0):
    ret_val = os.system(cmd);
    if(ret_val != expected_ret):
        Log.fatal("cmd: ({}) has exit status ({})", cmd, ret_val);

def generate_disktutil_list():
    checked_os_system("mkdir -p {}".format(Constants.TEMP_DISKUTIL_DIR));
    checked_os_system("diskutil list -plist > {}".format(Constants.TEMP_DISKUTIL_LIST));

    plist       = plistlib.readPlist(Constants.TEMP_DISKUTIL_LIST);
    whole_disks = plist["WholeDisks"];
    volumes     = plist["VolumesFromDisks"];
    other_info  = plist["AllDisksAndPartitions"];

    Globals.disks_info = [];

    for i in xrange(0, len(whole_disks)):
        info = { "whole"  : whole_disks[i],
                 "size"   : other_info[i]["Size"]};
        try:
            info["volume"] = volumes[i];
        except:
            info["volume"] = "Not mounted";

        Globals.disks_info.append(info);

def convert_iso_to_img(isopath):
    Log.verbose("Image File is a .iso it will be converted first");

    outpath = os.path.splitext(isopath)[0] + ".img";
    convert_cmd = "hdiutil convert -format UDRW -o {} {}".format(outpath, isopath);
    checked_os_system(convert_cmd);

    #OSX tends to put a .dmg extension so we check it and rename the file.
    outpath_dmg = outpath + ".dmg";
    if(os.path.isfile(outpath_dmg)):
        Log.verbose("{} ({}) to ({})".format("Renaming the output of hdiutil",
                                             outpath_dmg,
                                             outpath));
        mv_cmd = "mv {} {}".format(outpath_dmg, outpath);
        checked_os_system(mv_cmd);

    return outpath;

def check_disk_existance(disk_name):
    for info in Globals.disks_info:
        if(disk_name == info["whole"]):
            return True;
    return False;

def check_image_path(path):
    fullpath = os.path.abspath(os.path.expanduser(path));

    if(not os.path.isfile(fullpath)):
        Log.fatal("Path ({}) is not a valid file path...".format(path));

    name, ext = os.path.splitext(fullpath);
    ext = ext.lower();
    if(ext not in Constants.SUPPORTED_EXTS):
        Log.fatal("{} ({}) is not {}".format("Image File ext",
                                             ext,
                                             Constants.SUPPORTED_EXTS));
    if(ext == ".iso"):
        fullpath = convert_iso_to_img(fullpath);

    return fullpath;

def unmount_disk(disk_name):
    disk_path = "/dev/" + disk_name;
    Log.verbose("Unmount disk ({})".format(disk_path));
    checked_os_system("diskutil unmountDisk {}".format(disk_path));

def eject_disk(disk_name):
    disk_path = "/dev/" + disk_name;
    Log.verbose("Eject disk ({})".format(disk_path));
    checked_os_system("diskutil eject {}".format(disk_path));

def perform_dd(img_path, disk_name):
    disk_path = "/dev/r" + disk_name;
    dd_cmd = "sudo dd if={} of={} bs=1m".format(img_path, disk_path);

    Log.verbose("Starting dd - It needs to be superuser");
    Log.verbose("dd command - {}".format(dd_cmd));
    Log.verbose("{} {}".format("dd does not have output, when it ",
                               "was done a message will be printed."));
    checked_os_system(dd_cmd);

    Log.verbose("dd done...");

################################################################################
## Print Functions                                                            ##
################################################################################
def print_disk_list():
    print colored("Your disks:", "green");
    for info in Globals.disks_info:
        print "    Disk:", info["whole"];
        print "    Name:", info["volume"];
        print "    Size:", info["size"];
        print;


################################################################################
## Prompt Functions                                                           ##
################################################################################
def get_disk_to_use():
    print colored("Which disk is to use:", "yellow");
    return raw_input();

def get_img_filename():
    print colored("Path for linux .img (If a .iso is passed it will be converted):",
                  "yellow");

    path     = raw_input();
    fullpath = check_image_path(path);

    return fullpath;


################################################################################
## Script Initialization                                                      ##
################################################################################
def main():
    img_path = get_img_filename();

    generate_disktutil_list();
    print_disk_list();
    disk_name = get_disk_to_use();

    if(check_disk_existance(disk_name) == False):
        msg = "Disk ({}) is not a valid disk.".format(disk_name);
        Log.fatal(msg);

    unmount_disk(disk_name);
    perform_dd(img_path, disk_name);
    eject_disk(disk_name);

if __name__ == '__main__':
    main();
