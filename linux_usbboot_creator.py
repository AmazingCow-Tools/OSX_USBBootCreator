#!/usr/bin/python


## Imports ##
import os;
import os.path;
import getopt;
import sys;
import plistlib;

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
        print "[FATAL] {}".format(msg);
        exit(1);
    @staticmethod
    def verbose(msg):
        if(Globals.verbose):
            print msg;

################################################################################
## Helper Functions                                                           ##
################################################################################
def generate_disktutil_list():
    os.system("mkdir -p {}".format(Constants.TEMP_DISKUTIL_DIR));
    os.system("diskutil list -plist > {}".format(Constants.TEMP_DISKUTIL_LIST));

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
    os.system(convert_cmd);

    #OSX tends to put a .dmg extension so we check it and rename the file.
    outpath_dmg = outpath + ".dmg";
    if(os.path.isfile(outpath_dmg)):
        Log.verbose("{} ({}) to ({})".format("Renaming the output of hdiutil",
                                             outpath_dmg,
                                             outpath));
        mv_cmd = "mv {} {}".format(outpath_dmg, outpath);
        os.system(mv_cmd);

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
    os.system("diskutil unmountDisk {}".format(disk_path));

def eject_disk(disk_name):
    disk_path = "/dev/" + disk_name;
    Log.verbose("Eject disk ({})".format(disk_path));
    os.system("diskutil eject {}".format(disk_path));

def perform_dd(img_path, disk_name):
    disk_path = "/dev/r" + disk_name;
    dd_cmd = "sudo dd if={} of={} bs=1m".format(img_path, disk_path);

    Log.verbose("Starting dd - It needs to be superuser");
    Log.verbose("dd command - {}".format(dd_cmd));
    Log.verbose("{} {}".format("dd does not have output, when it ",
                               "was done a message will be printed."));
    os.system(dd_cmd);

    Log.verbose("dd done...");

################################################################################
## Print Functions                                                            ##
################################################################################
def print_disk_list():
    print "Your disks:"
    for info in Globals.disks_info:
        print "    Disk:", info["whole"];
        print "    Name:", info["volume"];
        print "    Size:", info["size"];
        print;


################################################################################
## Prompt Functions                                                           ##
################################################################################
def get_disk_to_use():
    print "Which disk is to use:";
    return raw_input();

def get_img_filename():
    print "Path for linux .img (If a .iso is passed it will be converted):";

    path     = raw_input();
    fullpath = check_image_path(path);

    return fullpath;

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

main();
