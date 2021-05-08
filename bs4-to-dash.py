import requests, sqlite3, os, urllib
from urllib.request import urlretrieve # needed for python3 support -> see https://stackoverflow.com/a/21171861 
from bs4 import BeautifulSoup as bs


# CONFIGURATION
docset_name = 'Beautiful_Soup_4.docset'
output = docset_name + '/Contents/Resources/Documents/'


# create docset directory
if not os.path.exists(output): os.makedirs(output)

# add icon
icon = 'http://upload.wikimedia.org/wikipedia/commons/7/7f/Smile_icon.png'
urlretrieve(icon, docset_name + "/icon.png")


def update_db(name, path):

  typ = 'func'
  name = name.encode('ascii', 'ignore')

  cur.execute('CREATE TABLE IF NOT EXISTS searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
  cur.execute("SELECT rowid FROM searchIndex WHERE path = ?", (path,))
  fetched = cur.fetchone()
  if fetched is None:
      cur.execute('INSERT OR IGNORE INTO searchIndex(name, type, path) VALUES (?,?,?)', (name, typ, path))
      print('DB add >> name: %s, path: %s' % (name, path))
  else:
      print("record exists")


def add_urls():
 
  root_url = 'http://beautiful-soup-4.readthedocs.org/en/latest/'
 
  # start souping index_page
  data = requests.get(root_url).text
  soup = bs(data)

  # collected needed pages and their urls
  for link in soup.findAll('a'):
    name = link.text.strip().replace('\n', '')
    path = link.get('href')
    filtered = ('http', '/', 'index.zh.html', '#beautiful-soup-documentation')
    if path is not None and name is not None and not path.startswith(filtered):
      path = 'beautiful-soup-4.readthedocs.org/en/latest/index.html' + path
      update_db(name, path)


def add_infoplist():
  CFBundleIdentifier = 'bs4'
  CFBundleName = 'Beautiful Soup 4'
  DocSetPlatformFamily = 'bs4'

  info = " <?xml version=\"1.0\" encoding=\"UTF-8\"?>" \
         "<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\"> " \
         "<plist version=\"1.0\"> " \
         "<dict> " \
         "    <key>CFBundleIdentifier</key> " \
         "    <string>{0}</string> " \
         "    <key>CFBundleName</key> " \
         "    <string>{1}</string>" \
         "    <key>DocSetPlatformFamily</key>" \
         "    <string>{2}</string>" \
         "    <key>isDashDocset</key>" \
         "    <true/>" \
         "    <key>dashIndexFilePath</key>" \
         "    <string>{3}</string>" \
         "</dict>" \
         "</plist>".format(CFBundleIdentifier, CFBundleName, DocSetPlatformFamily, 'beautiful-soup-4.readthedocs.org/en/latest/' + 'index.html')
  open(docset_name + '/Contents/info.plist', 'wb').write(info.encode('utf-8'))

db = sqlite3.connect(docset_name + '/Contents/Resources/docSet.dsidx')
cur = db.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')

try:
    cur.execute('DROP TABLE searchIndex;')
except:
    pass
    cur.execute('CREATE TABLE IF NOT EXISTS searchIndex(id INTEGER PRIMARY KEY, name TEXT, type TEXT, path TEXT);')
    cur.execute('CREATE UNIQUE INDEX anchor ON searchIndex (name, type, path);')
# start
add_urls()
add_infoplist()

# # commit and close db
db.commit()
db.close()
