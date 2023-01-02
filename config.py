import xbmcaddon, xbmcvfs, sys, os

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
addon = xbmcaddon.Addon()
addonname = addon.getAddonInfo('name')
addonhome = addon.getAddonInfo('path')
addonprofile = addon.getAddonInfo('profile')
__language__ = addon.getLocalizedString

server_countries = {
 'AE': 'United Arab Emirates',
 'AL': 'Albania',
 'AR': 'Argentina',
 'AT': 'Austria',
 'AU': 'Australia',
 'BA': 'Bosnia and Herzegovina',
 'BE': 'Belgium',
 'BG': 'Bulgaria',
 'BO': 'Bolivia',
 'BR': 'Brazil',
 'BY': 'Belarus',
 'CA': 'Canada',
 'CH': 'Switzerland',
 'CL': 'Chile',
 'CN': 'China',
 'CO': 'Colombia',
 'CR': 'Costa Rica',
 'CY': 'Cyprus',
 'CZ': 'Czechia',
 'DE': 'Germany',
 'DK': 'Denmark',
 'EC': 'Ecuador',
 'EE': 'Estonia',
 'EG': 'Egypt',
 'ES': 'Spain',
 'FI': 'Finland',
 'FR': 'France',
 'GR': 'Greece',
 'HR': 'Croatia',
 'HK': 'Hong Kong',
 'HU': 'Hungary',
 'ID': 'Indonesia',
 'IE': 'Ireland',
 'IL': 'Israel',
 'IN': 'India',
 'IS': 'Iceland',
 'IT': 'Italy',
 'JP': 'Japan',
 'KE': 'Kenya',
 'KR': 'South Korea',
 'KZ': 'Kazakhstan',
 'LT': 'Lithuania',
 'LU': 'Luxembourg',
 'LV': 'Latvia',
 'MD': 'Moldova',
 'MX': 'Mexico',
 'MY': 'Malaysia',
 'NG': 'Nigeria',
 'NL': 'Netherlands',
 'NO': 'Norway',
 'NZ': 'New Zealand',
 'PE': 'Peru',
 'PK': 'Pakistan',
 'PL': 'Poland',
 'PT': 'Portugal',
 'PY': 'Paraguay',
 'RO': 'Romania',
 'RS': 'Serbia',
 'RU': 'Russia',
 'SA': 'Saudi Arabia',
 'SE': 'Sweden',
 'SG': 'Singapore',
 'SI': 'Slovenia',
 'SK': 'Slovakia',
 'TH': 'Thailand',
 'TR': 'Turkiye',
 'TW': 'Taiwan',
 'UA': 'Ukraine',
 'UK': 'United Kingdom',
 'US': 'United States',
 'UY': 'Uruguay',
 'VE': 'Venezuela',
 'ZA': 'South Africa',
}

configs_url = 'https://configs.ipvanish.com/configs/ipvanish'
cfgfile = os.path.join(xbmcvfs.translatePath(addonprofile), 'cfg.ovpn')
authfile = os.path.join(xbmcvfs.translatePath(addonprofile), 'auth.txt')
errlog = os.path.join(xbmcvfs.translatePath(addonprofile), 'stderr.log')
vpnlog = os.path.join(xbmcvfs.translatePath(addonprofile), 'openvpn.log')
