# IPVanish addon for Kodi on Linux platforms
This addon allows an IPVanish VPN connection to be managed from inside Kodi.

## Requirements
- Kodi 17 or newer (Python 3-based)
- OpenVPN installed

## Setup
Install the addon from zip file in the usual way.  Configure the IPVanish username and password, enable sudo if required, and set a password for sudo if required.  Kodi on LibreELEC runs as root so doesn't need sudo.

## Usage
The addon has been tested successfully with Ubuntu 22.04/24.04, Raspberry Pi OS (Debian bullseye) and LibreELEC 10.0, all with Kodi 19.
Connecting to a new host will automatically disconnect any existing OpenVPN instance.

## Notes
Not endorsed in any way by IPVanish.  Valid user account required.

Note that /etc/openvpn/update-resolv-conf in Ubuntu 24.04 may need edited.  The
first mention of ${dev}.openvpn should be replaced with just ${dev}, and the
whole line containing the second mention of ${dev}.openvpn should be replaced
with just a colon (:).

Round world flag icons from https://iconarchive.com/show/round-world-flags-icons-by-custom-icon-design.html

Waving flag background images by luis_molinero, https://www.freepik.com/free-vector/waving-flag-icon-collection_1152871.htm

Other icons from Ardis Icon Theme, https://iconduck.com/sets/ardis-icon-theme

## Bugs
- Disconnecting the VPN in LibreELEC leaves a zombie openvpn process hanging around.
- Expects particular output from the OpenVPN binary in order to estabish that a VPN connection has been made.
- Will produce an empty country list if the IPVanish host list cannot be retrieved for any reason.
