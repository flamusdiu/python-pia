Changelog
=========
2.8.1 (2016-07-13)
------------------
Fixes auto-login not working

2.8 (2016-07-13)
----------------
Changes because of this article:
https://www.privateinternetaccess.com/forum/discussion/21796/vpn-connection-failed-message-with-new-configuration-files

Note: The strong configurations are not working, yet. You can always manually configure them for now.
      I plan to add support soon.
2.7 (2016-05-30)
----------------
- Debugging (through the `-d` flag should work now.
- Fixed an issue when using `apps` in the configuration file. The sets it to ONLY
  configure the apps listed. While on the commandline, you can use `-e` to EXCLUDE applications
- Fixed `pia -r`. It now attempts removal of all configurations. This ignores the `hosts` flag in the
  configuration file to keep from having stale configurations left behind when changing between
  configurations.

2.6.2 (2016-05-29)
------------------
- Fixed default properties

2.6.1 (2016-05-29)
------------------
- Really fixed the spaces around properties.

2.6 (2016-05-27)
----------------
- Removed static docopt dependancy
- Updated setuptools version
- Added options to 'pia.conf' for naming cipher and authenication
  protocols. Only works for connman.
- Other bug fixes and code cleanup

2.5 (2015-10-28)
----------------
- Added option to change port number and protocol of the distance gateway. Set in the configuration file
  under '[configure]' by setting 'port = port#'. Valid port numbers are 80 (TCP), 443 (TCP), 110 (TCP),
  53 (UDP), 8080 (UDP), 9201 (UDP). You do not need to specify the protocol since only one port number
  is supported over a specific protocol. (Fixes Issue #3)

2.4.6 (2015-07-21)
------------------
- Added some more logging code and disabled Debug (oops -- left it on).
- Fixed a bug dealing with some of the logging code causing it to kill the script (Thanks @toppy!)

2.4.5 (2015-07-20)
------------------
- Moved code around to better support some functions
- Fixed a bug where an error would throw if the pia.conf was missing or didn't have all the configuration
  section
- Added logging (not completed yet). The "--debug" flag isn't nearly ready yet but will be soon.

2.4.1 (2015-07-10)
------------------
- Added doc statements for most functions
- More bug fixes + code refactoring

2.4 (2015-07-09)
----------------
- Added an option to '-r' to remove only specific configurations. It will remove the configuration from
  all applications.
- Other bug fixes and refactoring.

2.3 (2015-07-08)
----------------
- Added docopt (https://github.com/docopt/docopt) support. No extra modules need to be installed.
- Changed commandline parsing to use docopt.
- other minor fixes

2.2.1 (2015-07-07)
------------------
- Oops. Goblins ran off with login credentials for OpenVPN configs.
  I caught the goblins and returned the OpenVPN configs for auto-login to work.
- Minor bug fixes.

2.2 (2015-07-07)
----------------
- Added ability to add a configuration file. It must be in '/etc/private-internet-access-vpn' and
  named 'pia.conf.' I plan to add a way to override this in the next version.

  Note: that only a few sections are supported with a few options (mainly to replace the commandline
  switches). Options are parsed in the following order: Defaults > Conf File > Commandline switches

- Refactored the way each supported application is called to simplify the code.

2.1.1 (2015-07-05)
------------------
- Fixed missing setuptools if not installed

2.1 (2015-07-04)
----------------
- Minor fixes
- Added option to list known OpenVPN configurations. Each configuration will be marked if it's configured for an
  application.

2.0.1 (2015-07-04)
------------------
- Bug fixes
- Moved sources into 'src/'
- Fixed the way the templates configs are stored. Uses package-data instead of data-files.
  Some reason it was trying to store the template-configs directly in '/usr' which never should
  have happened.

2.0 (2015-07-03)
----------------
- Completely reworked script as a python module
- Added modular support for applications through creating files under
  applications/hooks

1.5 (2015-07-01)
----------------
- Renamed pia-auto-login.py to pia.
- Reworked script and updated man page.
- Added Connman support
