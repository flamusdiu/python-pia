Private Internet Access Configuration
=====================================
-----------------
Command-line tool
-----------------

DESCRIPTION
===========
       pia  auto  configures  PIA  (Private  Internet Access - https://www.privateinternetaccess.com/). Supports Networkmanager, Connman, OpenVPN. PIA is "Fast, multi-gigabit VPN Tunnel
       gateways, worldwide, from the most trusted name in anonymous VPN" (from the website).

OPTIONS
=======
       -h, --help
           show this help message and exit

       -a, --auto-configure
           Automatically generates configurations

       -r, --remove-configurations
           Removes auto-generated configurations

       -e {nm,cm,openvpn}, --exclude {nm,cm,openvpn}
           Excludes modifying the configurations of the listed program. Maybe used more then once.

        -v, --verbose
           Enables more verbose logging

       --version
           show program's version number and exit

INSTALLATION/USAGE
==================
       Login information is stored in /etc/private-internet-access/login.conf and must be owned by "root" with the permissions "0600."

       login.conf must have only two lines: username and password. It must not have any other information or OpenVPN auto-login will not work.

       Hosts may be listed when calling this command. Do not use spaces or quotes to list them. (Example: US_East, US_West) Only the listed hosts will configured when using -a.

MORE INFO
=========
       Wiki - https://wiki.archlinux.org/index.php/private-internet-access-vpn

