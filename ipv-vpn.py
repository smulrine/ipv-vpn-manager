import xbmc, xbmcaddon, xbmcgui, xbmcplugin, urllib.request, re, sys, os, subprocess
from urllib.parse import parse_qsl
import config
from config import __handle__, __url__, __language__

def disconnect_openvpn(silent):
  if not silent:
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
  errfile = open(config.errlog, mode='w')
  shell = False
  cmd = ['killall', '-SIGINT', 'openvpn']
  if config.addon.getSetting('use_sudo') == 'true':
    cmd = ['sudo'] + cmd
    if config.addon.getSetting('sudo_password') != '':
      cmd = 'echo \'' + config.addon.getSetting('sudo_password').replace('\\','\\\\').replace('\'','\\\'') + '\' | sudo killall -SIGINT openvpn'
      shell = True
  ps = subprocess.Popen(cmd, shell=shell, stdout=subprocess.PIPE, stderr=errfile)
  count = 0
  while count < 60:
    efp = open(config.errlog, mode='r')
    edata = efp.read()
    efp.close()
    if 'incorrect password attempt' in edata:
      xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
      xbmcgui.Dialog().ok(config.addonname, __language__(30006))
      break
    elif 'no process' in edata:
      if not silent:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        xbmcgui.Dialog().ok(config.addonname, __language__(30007))
      break
    else:
      xbmc.sleep(1000)
      if os.path.exists(config.vpnlog):
        vfp = open(config.vpnlog, mode='r')
        vdata = vfp.read()
        vfp.close()
        if 'process exiting' in vdata:
          if not silent:
            xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
            xbmcgui.Dialog().ok(config.addonname, __language__(30010))
          break
    count += 1
  if count == 60:
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    xbmcgui.Dialog().ok(config.addonname, __language__(30011))
  if not silent:
    xbmc.executebuiltin('Container.Refresh({0})'.format(__url__))

def connect_host(country, city, host):
  errcode = 30009
  config_downloaded = False
  vpn_connected = False
  if config.addon.getSetting('vpn_username') == '' or config.addon.getSetting('vpn_password') == '':
    errcode = 30012
  else:
    try:
      xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
      file = open(config.authfile, mode='w')
      file.write('{0}\n{1}'.format(config.addon.getSetting('vpn_username'), config.addon.getSetting('vpn_password')))
      file.close()
      req = urllib.request.Request('{0}-{1}-{2}-{3}.ovpn'.format(config.configs_url, country, city, host.split('.')[0]), headers={'User-Agent': 'Mozilla/5.0'}) 
      with urllib.request.urlopen(req) as response:
        remote_config = response.read()
      remote_config = remote_config.replace(b'ca ca.ipvanish.com.crt',b'ca '+bytes((os.path.join(config.addonhome, 'resources', 'ca.ipvanish.com.crt')), 'utf-8'))
      remote_config = remote_config.replace(b'auth-user-pass',b'auth-user-pass '+bytes(config.authfile, 'utf-8'))
      remote_config = remote_config.replace(b'keysize',b'#keysize')
      if os.path.exists('/etc/openvpn/update-resolv-conf'):
        remote_config += b'script-security 2\nup /etc/openvpn/update-resolv-conf\ndown /etc/openvpn/update-resolv-conf\n'
      file = open(config.cfgfile, mode='wb')
      file.write(remote_config)
      file.close()
      config_downloaded = True
    except Exception as e:
      xbmc.log('{0}: {1}: {2}'.format(config.addonname, __language__(30009), e), xbmc.LOGERROR)
      pass
  if config_downloaded:
    disconnect_openvpn(silent=True)
    errfile = open(config.errlog, mode='w')
    vpnfile = open(config.vpnlog, mode='w')
    shell = False
    cmd = ['openvpn', '--config', config.cfgfile]
    if config.addon.getSetting('use_sudo') == 'true':
      cmd = ['sudo'] + cmd
      if config.addon.getSetting('sudo_password') != '':
        cmd = 'echo \'' + config.addon.getSetting('sudo_password').replace('\\','\\\\').replace('\'','\\\'') + '\' | sudo openvpn --config ' + config.cfgfile
        shell = True
    ps = subprocess.Popen(cmd, shell=shell, stdout=vpnfile, stderr=errfile)
    count = 0
    while count < 60:
      efp = open(config.errlog, mode='r')
      edata = efp.read()
      efp.close()
      if 'incorrect password attempt' in edata:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        xbmcgui.Dialog().ok(config.addonname, __language__(30006))
        break
      elif 'command not found' in edata:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
        xbmcgui.Dialog().ok(config.addonname, __language__(30008))
        break
      else:
        xbmc.sleep(1000)
        vfp = open(config.vpnlog, mode='r')
        vdata = vfp.read()
        vfp.close()
        if 'Initialization Sequence Completed' in vdata:
          vpn_connected = True
          break
        elif 'AUTH_FAILED' in vdata:
          xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
          xbmcgui.Dialog().ok(config.addonname, __language__(30012))
          break
        elif 'Operation not permitted' in vdata:
          xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
          xbmcgui.Dialog().ok(config.addonname, __language__(30013))
          break
      count += 1
    if count == 60:
      xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
      xbmcgui.Dialog().ok(config.addonname, __language__(30014))
    elif vpn_connected:
      xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
      message = '{0} {1}'.format(__language__(30015), host)
      xbmcgui.Dialog().ok(config.addonname, message)
      xbmc.executebuiltin('Container.Refresh({0})'.format(__url__))
  else:
    xbmc.executebuiltin('Dialog.Close(busydialognocancel)')
    xbmcgui.Dialog().ok(config.addonname, __language__(errcode))

def display_hosts(country, city):
  def hostListSort(item):
    return (host_capacity[item],item)
  list_items = []
  host_list = []
  host_capacity = {}
  host_icon = {}
  host_fanart = {}
  host_ip = {}
  req = urllib.request.Request(config.addon.getSetting('vpn_url'), headers={'User-Agent': 'Mozilla/5.0'}) 
  with urllib.request.urlopen(req) as response:
    vpn_data = response.read().decode()
  for mystr in vpn_data.splitlines():
    server = re.search(' *<server name="(?P<host>[^"]+)" *capacity="(?P<capacity>[^"]+)" *city="' + city + '" *country="' + country + '" *icon="[^"]+" *ip="[^"]+" *status="(?P<status>[^"]+)" *visible="(?P<visible>[^"]+)".*$', mystr)
    if server:
      if (server['status'] == '1' and server['visible'] == '1' and server['host'] != '' and server['capacity'] != ''):
        try:
          capacity = int(server['capacity'])
        except:
          continue
        host_list.append(server['host'])
        host_capacity[server['host']] = capacity
        host_icon[server['host']] = os.path.join(config.addonhome, 'resources', 'images', country.lower()+'-icon.png')
        host_fanart[server['host']] = os.path.join(config.addonhome, 'resources', 'images', country.lower()+'.png')
  host_list.sort(key=hostListSort)
  for host in host_list:
    list_item = xbmcgui.ListItem(label='{0} ({1})'.format(host, host_capacity[host]))
    list_item.setArt({'thumb': host_icon[host], 'poster': host_icon[host], 'fanart': host_fanart[host]})
    url = '{0}?host={1}&city={2}&country={3}'.format(__url__, host, city, country)
    list_items.append((url, list_item, False))
  xbmcplugin.addDirectoryItems(__handle__, list_items, len(list_items))
  xbmcplugin.endOfDirectory(__handle__)

def display_cities(country):
  list_items = []
  city_list = []
  city_servers = {}
  city_icon = {}
  city_fanart = {}
  req = urllib.request.Request(config.addon.getSetting('vpn_url'), headers={'User-Agent': 'Mozilla/5.0'}) 
  with urllib.request.urlopen(req) as response:
    vpn_data = response.read().decode()
  for mystr in vpn_data.splitlines():
    server = re.search(' *<server name="[^"]+" *capacity="[^"]+" *city="(?P<city>[^"]+)" *country="' + country + '" *icon="[^"]+" *ip="[^"]+" *status="(?P<status>[^"]+)" *visible="(?P<visible>[^"]+)".*$', mystr)
    if server:
      if (server['status'] == '1' and server['visible'] == '1' and server['city'] != ''):
        if (not server['city'] in city_list):
          city_list.append(server['city'])
          city_servers[server['city']] = 1
          city_icon[server['city']] = os.path.join(config.addonhome, 'resources', 'images', country.lower()+'-icon.png')
          city_fanart[server['city']] = os.path.join(config.addonhome, 'resources', 'images', country.lower()+'.png')
        else:
          city_servers[server['city']] += 1
  city_list.sort()
  for city in city_list:
    list_item = xbmcgui.ListItem(label='{0} ({1})'.format(city, city_servers[city]))
    list_item.setArt({'thumb': city_icon[city], 'poster': city_icon[city], 'fanart': city_fanart[city]})
    url = '{0}?city={1}&country={2}'.format(__url__, city, country)
    list_items.append((url, list_item, True))
  xbmcplugin.addDirectoryItems(__handle__, list_items, len(list_items))
  xbmcplugin.endOfDirectory(__handle__)

def display_countries():
  def countryListSort(item):
    try:
      return config.server_countries[item]
    except:
      return item
  country_list = []
  country_servers = {}
  country_icon = {}
  country_fanart = {}
  list_item = xbmcgui.ListItem(label='{0}'.format(__language__(30016)))
  list_item.setArt({'thumb': os.path.join(config.addonhome, 'resources', 'images', 'settings.png')})
  list_items = [('{0}?settings=1'.format(__url__), list_item, False)]
  # LibreELEC leaves zombie openvpn processes hanging around
  # Check if they are real processes before displaying Disconnect VPN option
  vpn_running = False
  vpn_procs = subprocess.run(['pidof', 'openvpn'], capture_output=True, text=True)
  for vpn_proc in vpn_procs.stdout.split(' '):
    try:
      if os.system('grep -q config /proc/{0}/cmdline'.format(vpn_proc.rstrip())) == 0:
        vpn_running = True
        break
    except:
      pass
  if vpn_running:
    list_item = xbmcgui.ListItem(label='{0}'.format(__language__(30017)))
    list_item.setArt({'thumb': os.path.join(config.addonhome, 'resources', 'images', 'disconnect.png')})
    list_items.append(('{0}?disconnect=1'.format(__url__), list_item, False))
  req = urllib.request.Request(config.addon.getSetting('vpn_url'), headers={'User-Agent': 'Mozilla/5.0'}) 
  with urllib.request.urlopen(req) as response:
    vpn_data = response.read().decode()
  for mystr in vpn_data.splitlines():
    server = re.search(' *<server name="[^"]+" *capacity="[^"]+" *city="[^"]+" *country="(?P<country>[^"]+)" *icon="[^"]+" *ip="[^"]+" *status="(?P<status>[^"]+)" *visible="(?P<visible>[^"]+)".*$', mystr)
    if server:
      if (server['status'] == '1' and server['visible'] == '1' and server['country'] != ''):
        if (not server['country'] in country_list):
          country_list.append(server['country'])
          country_servers[server['country']] = 1
          country_icon[server['country']] = os.path.join(config.addonhome, 'resources', 'images', server['country'].lower()+'-icon.png')
          country_fanart[server['country']] = os.path.join(config.addonhome, 'resources', 'images', server['country'].lower()+'.png')
        else:
          country_servers[server['country']] += 1
  country_list.sort(key=countryListSort)
  for country in country_list:
    if country in config.server_countries:
      list_item = xbmcgui.ListItem(label='{0} ({1})'.format(config.server_countries[country], country_servers[country]))
    else:
      list_item = xbmcgui.ListItem(label='{0} ({1})'.format(country, country_servers[country]))
    list_item.setArt({'thumb': country_icon[country], 'poster': country_icon[country], 'fanart': country_fanart[country]})
    url = '{0}?country={1}'.format(__url__, country)
    list_items.append((url, list_item, True))
  xbmcplugin.addDirectoryItems(__handle__, list_items, len(list_items))
  xbmcplugin.endOfDirectory(__handle__)
  
def main(args):
  params = dict(parse_qsl(args[1:]))
  if params:
    if 'host' in params:
      connect_host(params['country'], params['city'], params['host'])
    elif 'city' in params:
      display_hosts(params['country'], params['city'])
    elif 'country' in params:
      display_cities(params['country'])
    elif 'settings' in params:
      config.addon.openSettings()
    elif 'disconnect' in params:
      disconnect_openvpn(silent=False)
    else:
      display_countries()
  else:
    display_countries()

if __name__ == '__main__':
  # Don't run unless we can find openvpn
  if os.system('type openvpn 2>/dev/null') != 0:
    xbmcgui.Dialog().ok(config.addonname, __language__(30008))
  else:
    main(sys.argv[2])
