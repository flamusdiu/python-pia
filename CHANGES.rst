Changelog
=========
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