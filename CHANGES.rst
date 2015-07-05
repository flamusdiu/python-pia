Changelog
=========

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