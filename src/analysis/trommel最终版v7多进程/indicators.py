#!_*_coding:utf-8_*_
import magic
import re
import os

from indicator_config import *

#Imports from vFeed
from lib.core.methods import *
from lib.core.search import Search


#Function to search for keywords in file. Writes keyword, file name, number hits in file
def read_search_kw(ff, keyword, trommel_output,fp):
	try:

		with open (ff, 'r') as keyword_search:
			text = keyword_search.read()
			hits = re.findall(keyword, text, re.I)
			if hits:
				magic_mime = magic.from_file(ff, mime=True)
				magic_hit = re.search(mime_kw, magic_mime, re.I)
				if magic_hit:
                                        trommel_output.write("\"%s\" & %s & 二进制文件 & %d\n\n" % (keyword, fp, len(hits)))
				else:
                                        trommel_output.write("\"%s\" & %s & 文本文件 & %d\n\n" % (keyword, fp, len(hits)))

	except IOError:
		pass

#Function to search for keywords in file (case sensitive). Writes keyword, file name, number hits in file
def read_search_case_kw(ff, keyword, trommel_output,fp):
	try:
		with open (ff, 'r') as keyword_search:
			text = keyword_search.read()
			hits = re.findall(keyword, text)
			if hits:
				magic_mime = magic.from_file(ff, mime=True)
				magic_hit = re.search(mime_kw, magic_mime, re.I)
				if magic_hit:
                                        trommel_output.write("'%s' & %s & 二进制文件 & %d\n\n" % (keyword, fp, len(hits)))
				else:
                                        trommel_output.write("'%s' & %s & 文本文件 & %d\n\n" % (keyword, fp, len(hits)))
        except IOError:
		pass

#Function to search for keywords in file (case sensitive). Writes keyword, file name, number hits in file
def read_search_lua_kw(ff, keyword, trommel_output,fp):
	try:
		with open (ff, 'r') as keyword_search:
			text = keyword_search.read()
			hits = re.findall(keyword, text)
			if hits:
                                trommel_output.write("'%s' & %s & lua脚本文件 & %d\n\n" % (keyword, fp, len(hits)))
	except IOError:
		pass

#Function to search for keywords in file (case sensitive). Writes keyword, file name, number hits in file
def read_search_apk(ff, keyword,fp):
	try:
		with open (ff, 'r') as keyword_search:
			text = keyword_search.read()
			hits = re.findall(keyword, text, re.I)
			if hits:
				trommel_output.write("Android APK 关键字 '%s'的文件: %s 出现次数: %d\n\n" % (keyword, fp, len(hits)))
	except IOError:
		pass

#Function to search CVEs in CVE Community Edition Database in CVE Community Edition Database
def cve_search_func(cve_term):
	found_cve = Search(cve_term).cve()
	return found_cve		

#Function to return Exploit DB association with CVE in CVE Community Edition Database
def exploitdb_result(cve_term):
	edb = CveExploit(cve_term).get_edb()
	return edb

#Function to return Metasploit Module association with CVE in CVE Community Edition Database
def metasploit_result(cve_term):
	msf = CveExploit(cve_term).get_msf()
	return msf


#Function to text search in CVE Community Edition Database
def text_search(search_term, trommel_output):
	search_text = Search(search_term).text()
	cve_field = re.findall(r'CVE-\d+-\d+', search_text, re.S)
        #trommel_output.write("cvefile%s" %(cve_field))
	if search_text is not "null":
		cve_hit = '"(CVE-\d+-\d+ : .*\.)"'
		name_hit = re.findall(cve_hit, search_text)
		for match_hit in name_hit:
			#trommel_output.write("Check file version on embedded device - Found %s and it has been associated with %s\n" % (search_term, match_hit))
                        match_hitcve=match_hit.split(':',1)[0]
                        match_desccve=match_hit.split(':',1)[-1]
                        trommel_output.write("AAAA%s & %s & %s \n" % (search_term, match_hitcve, match_desccve))
                        '''
                        #从关联的漏洞中找Exploit-DB and Metasploit攻击模块
                        flagAttackM=0
                        for cve_hit in cve_field:
                                edb = exploitdb_result(cve_hit)
                                msf = metasploit_result(cve_hit)
                                #Exploit-DB result
                                if edb is not "null":
                                    url_match = "http://www.exploit-db.com/exploits/\d{1,8}"
                                    urls = re.findall(url_match, edb, re.S)
                                    for url_hit in urls:
                                        #trommel_output.write("%s has a known exploit: %s\n" % (cve_hit, url_hit))
                                        trommel_output.write("embedded -Found %s associated: %s:%s\n" % (search_term, match_hitcve, url_hit))
                                        flagAttackM=1
                                #Metasploit results
                                if msf is not "null":
                                    msf_fname = "metasploit-framework/modules/.*\.rb"
                                    msf_title = '"title": "(.*)"'
                                    msf_fn_match = re.findall(msf_fname, msf)
                                    msf_title_match = re.findall(msf_title, msf)
                                    for match in msf_fn_match:
                                         for match2 in msf_title_match:
                                             #trommel_output.write("%s is associated Metasploit: %s - %s\n" % (cve_hit, match2, match))
                                             trommel_output.write("embedded -Found %s associated: %s:%s - %s\n" % (search_term, match_hitcve, match2, match))
                                             flagAttackM=1
                        if flagAttackM==1:
                            flagAttackM=0
                        else:
                            trommel_output.write("embedded -Found %s associated: %s\n" % (search_term, match_hitcve))
                        '''
	#Searches above CVE in Exploit-DB and Metasploit
	for cve_hit in cve_field:
		edb = exploitdb_result(cve_hit)
		msf = metasploit_result(cve_hit)
		#Exploit-DB result
		if edb is not "null":
			url_match = "http://www.exploit-db.com/exploits/\d{1,8}"
			urls = re.findall(url_match, edb, re.S)
			for url_hit in urls:
				#trommel_output.write("%s has a known exploit: %s\n" % (cve_hit, url_hit))
				trommel_output.write("%s & %s\n" % (cve_hit, url_hit))
		#Metasploit results
		if msf is not "null":
			msf_fname = "metasploit-framework/modules/.*\.rb"
			msf_title = '"title": "(.*)"'
			msf_fn_match = re.findall(msf_fname, msf) 
			msf_title_match = re.findall(msf_title, msf)
			for match in msf_fn_match:
				for match2 in msf_title_match:
					#trommel_output.write("%s is associated with the following Metasploit Module: %s - %s\n" % (cve_hit, match2, match))
					trommel_output.write("%s & %s - %s\n" % (cve_hit, match2, match))



#Main function 	
def kw(ff, trommel_output, names):
        #截取文件名的后半部
        fp=ff.split('.extracted/')[-1]
        fp='./'+fp
        fname=ff.rsplit('/',1)[-1]
        fp = fp.replace('&',"\\\\&")


        trommel_output1=open(trommel_output+"/tmpfile1",'a')
        trommel_output2=open(trommel_output+"/tmpfile2",'a')
        trommel_output3=open(trommel_output+"/tmpfile3",'a')
        trommel_output4=open(trommel_output+"/tmpfile4",'a')
        trommel_output5=open(trommel_output+"/tmpfile5",'a')
        trommel_output6=open(trommel_output+"/tmpfile6",'a')
        trommel_output7=open(trommel_output+"/tmpfile7",'a')
        trommel_output8=open(trommel_output+"/tmpfile8",'a')
        trommel_output9=open(trommel_output+"/tmpfile9",'a')
        #trommel_output10=open(trommel_output+"/tmpfile10",'a')
        trommel_output11=open(trommel_output+"/tmpfile11",'a')
        trommel_output12=open(trommel_output+"/tmpfile12",'a')
        trommel_output13=open(trommel_output+"/tmpfile13",'a')
	#Search key or password related files & keywords
	if passwd in ff:
		trommel_output3.write("passwd & %s\n\n" % fp)
	if shadow in ff:
		trommel_output3.write("shadow & %s\n\n" % fp)
	if psk_hits in ff:
		trommel_output3.write(".psk & %s\n\n" % fp)
	if key_pass in ff:
		trommel_output3.write("keypass & %s\n\n" % fp)
	if k_wallet in ff:
		trommel_output3.write("kwallet & %s\n\n" % fp)	
	if open_vpn in ff:
		trommel_output3.write("ovpn & %s\n\n" % fp)
	if pgp_log in ff:
		trommel_output3.write("pgplog & %s\n\n" % fp)
	if pgp_policy in ff:
		trommel_output3.write("pgppolicy.xml & %s\n\n" % fp)
	if pgp_prefs in ff:
		trommel_output3.write("pgpprefs.xml & %s\n\n" % fp)
	if priv_kw in ff:
		trommel_output3.write("zzzzprivate & %s\n\n" % fp)
	if secret_kw in ff:
                trommel_output3.write("zzzzsecret & %s\n\n" % fp)
	if javaks in ff:
		trommel_output3.write("JavaKeyStore & %s\n\n" % fp)
	if sftpconfig in ff:
		trommel_output3.write("sftp-config & %s\n\n" % fp)
	if bitcoinfile in ff:
		trommel_output3.write("比特币钱包 & %s\n\n" % fp)
	if pwd_safe in ff:
		trommel_output3.write("Password Safe & %s\n\n" % fp)

	#Search for SSH related files (aaaa为排序符，排序后即删除)
	if auth_key_file in ff:
		trommel_output4.write("zzzz%s & SSH &  %s\n\n" % (fname, fp))
	if host_key_file in ff:
		trommel_output4.write("zzzz%s & SSH & %s\n\n" % (fname, fp))
	if id_rsa_file in ff:
		trommel_output4.write("zzzz%s & SSH & %s\n\n" % (fname, fp))
	if id_dsa_file in ff:
		trommel_output4.write("zzzz%s & SSH & %s\n\n" % (fname, fp))
	if dotPub in ff:
		trommel_output4.write("zzzz%s & SSH & %s\n\n" % (fname, fp))
	if id_ecdsa_file in ff:
		trommel_output4.write("zzzz%s & SSH & %s\n\n" % (fname, fp))
	if id_ed25519_file in ff:
		trommel_output4.write("zzzz%s & SSH & %s\n\n" % (fname, fp))
	read_search_kw(ff, id_dsa_file, trommel_output4,fp)
	read_search_kw(ff, host_key_file, trommel_output4,fp)
	read_search_kw(ff, auth_key_file, trommel_output4,fp)
	read_search_kw(ff, id_rsa_file, trommel_output4,fp)	
	read_search_kw(ff, id_ecdsa_file, trommel_output4,fp)
	read_search_kw(ff, id_ed25519_file, trommel_output4,fp)

	#Search for SSL related files - filenames: *.pem, *.crt, *.cer, *.p7b, *.p12, *.key
	if pem in ff:
		trommel_output4.write("zzzz%s & SSL & %s\n\n" % (fname, fp))
	if crt in ff:
		trommel_output4.write("zzzz%s & SSL & %s\n\n" % (fname, fp))
	if cer in ff:
		trommel_output4.write("zzzz%s & SSL & %s\n\n" % (fname, fp))
	if p7b in ff:
		trommel_output4.write("zzzz%s & SSL & %s\n\n" % (fname, fp))
	if p12 in ff:
		trommel_output4.write("zzzz%s & SSL & %s\n\n" % (fname, fp))
	if dotKey in ff:
		trommel_output4.write("zzzz%s & SSL & %s\n\n" % (fname, fp))
	if p15 in ff:
		trommel_output4.write("zzzz%s & SSL & %s\n\n" % (fname, fp))

	#Search for keyword of interest within files
	read_search_kw(ff, upgrade_kw, trommel_output1,fp)
	read_search_kw(ff, admin_kw, trommel_output1,fp)
	read_search_kw(ff, root_kw, trommel_output1,fp)
	read_search_kw(ff, password_kw, trommel_output1,fp)
	read_search_kw(ff, passwd_kw, trommel_output1,fp)
	read_search_kw(ff, pwd_kw, trommel_output1,fp)
	read_search_kw(ff, dropbear_kw, trommel_output1,fp)
	read_search_kw(ff, ssl_kw, trommel_output1,fp)
	read_search_kw(ff, telnet_kw, trommel_output1,fp)
	read_search_kw(ff, crypt_kw, trommel_output1,fp)
	read_search_kw(ff, auth_kw, trommel_output1,fp)
	read_search_kw(ff, sql_kw, trommel_output1,fp)
	read_search_kw(ff, passphrase_kw, trommel_output1,fp)
	read_search_kw(ff, rsa_key_pair, trommel_output1,fp)
	read_search_kw(ff, secretkey_kw, trommel_output1,fp)
	read_search_kw(ff, ssh_hot_keys, trommel_output1,fp)


	#Search for keywords "private key"(归为查找文件中存在的敏感关键字), IP addresses, URLs, and email addresses

	try:
		with open (ff, 'r') as privkey_keyword:
			text = privkey_keyword.read()
			hits = re.findall(private_key_kw, text, re.I)
			if hits:
				magic_mime = magic.from_file(ff, mime=True)
				magic_hit = re.search(mime_kw, magic_mime, re.I)
				if magic_hit:
                                    trommel_output1.write("\"private key\" & %s & 二进制文件 & %d\n\n" % (fp, len(hits)))
				else:
                                    trommel_output1.write("\"private key\" & %s & 文本文件 & %d\n\n" % (fp, len(hits)))
	except IOError:
		pass

	try:
		with open (ff, 'r') as ipaddr_keyword:
			text = ipaddr_keyword.read()
			hits = re.findall(ipaddr, text, re.S)
			for h in hits:
				magic_mime = magic.from_file(ff, mime=True)
				magic_hit = re.search(mime_kw, magic_mime, re.I)
				if magic_hit:
                                        trommel_output5.write("IP & %s & 二进制文件 & %s\n\n" % (h, fp))
				else:
                                        trommel_output5.write("IP & %s & 文本文件 & %s\n\n" % (h, fp))
	except IOError:
		pass

	try:
		with open (ff, 'r') as url_keyword:
			text = url_keyword.read()
			hits = re.findall(urls, text, re.S)
			for h in hits:
				magic_mime = magic.from_file(ff, mime=True)
				magic_hit = re.search(mime_kw, magic_mime, re.I)
                                for labels in '{}&%#':
                                    h = h.replace(labels," ")
				if magic_hit:
                                        trommel_output5.write("URL & %s & 二进制文件 & %s\n\n" % (h, fp))
				else:
                                        trommel_output5.write("URL & %s & 文本文件 & %s\n\n" % (h, fp))
	except IOError:
		pass

	try:
		with open (ff, 'r') as email_addr:
			text = email_addr.read()
			hits = re.findall(email, text, re.S)
			for h in hits:
				magic_mime = magic.from_file(ff, mime=True)
				magic_hit = re.search(mime_kw, magic_mime, re.I)
                                for labels in '{}&%#':
                                    h = h.replace(labels," ")
				if magic_hit:
                                        trommel_output5.write("email & %s & 二进制文件 & %s\n\n" % (h, fp))
				else:
                                        trommel_output5.write("email & %s & 文本文件 & %s\n\n" % (h, fp))
	except IOError:
		pass

	try:
		with open (ff, 'r') as seckey_keyword:
			text = seckey_keyword.read()
			hits = re.findall(secret_key_kw, text, re.I)
			if hits:
				magic_mime = magic.from_file(ff, mime=True)
				magic_hit = re.search(mime_kw, magic_mime, re.I)
				if magic_hit:
                                        trommel_output1.write("\"secret key\" & %s & 二进制文件 & %d\n\n" % (fp, len(hits)))
				else:
                                        trommel_output1.write("\"secret key\" & %s & 文本文件 & %d\n\n" % (fp, len(hits)))
	except IOError:
		pass


	#Search for files in /opt directory. This directory sometimes has specific files put there by the vendor. 
        opt_dir_kw = "/opt/"
	if opt_dir_kw in ff:
		trommel_output9.write("%s & %s\n\n" % (fname, fp))
        '''
	#Search for shell script files with .sh extension, rcS
	if shell_script in ff:
		trommel_output10.write("%s & %s & 非启动\n\n" % (fname, fp))
	if shell_script_rcs in ff:
		trommel_output10.write("%s & %s & 启动\n\n" % (fname, fp))
        '''

	#Search for web server binaries - apache, lighttpd, alphapd, httpd
	if apache_bin in ff:
		trommel_output11.write("%s & apache & %s\n\n" % (fname, fp))
	if lighttpd_bin in ff:
		text_search(lighttpd_bin, trommel_output2)
	if alphapd_bin in ff:
		text_search(alphapd_bin, trommel_output2)
	if httpd_bin in ff:
		trommel_output11.write("%s & httpd & %s\n\n" % (fname, fp))

	#Search for config files with these extensions *.conf, *.cfg, *.ini
	if config_1 in ff:
                trommel_output6.write("%s & .conf & %s\n\n" % (fname, fp))
	if config_2 in ff:
                trommel_output6.write("%s & .cfg & %s\n\n" % (fname, fp))
	if config_3 in ff:
		trommel_output6.write("%s & .ini & %s\n\n" % (fname, fp))

	#Search for database files with these extensions *.db and *.sqlite
	if db_file in ff:
		trommel_output7.write("%s & .db & %s\n\n" % (fname, fp))
	if sqlite_file in ff:
		trommel_output7.write("%s & .sqlite & %s\n\n" % (fname, fp))
	if sql_file in ff:
		trommel_output7.write("%s & .sql & %s\n\n" % (fname, fp))

	#Search for binary files of interest
	if ssh_bin in ff:
		trommel_output8.write("%s & ssh & %s\n\n" % (fname, fp))
	if sshd_bin in ff:
		trommel_output8.write("%s & sshd & %s\n\n" % (fname, fp))
	if scp_bin in ff:
		trommel_output8.write("%s & scp & %s\n\n" % (fname, fp))
	if sftp_bin in ff:
		trommel_output8.write("%s & sftp & %s\n\n" % (fname, fp))
	if tftp_bin in ff:
		trommel_output8.write("%s & tftp & %s\n\n" % (fname, fp))
	if dropbear_bin in ff:
		text_search(dropbear_bin, trommel_output2)
	if telnet_bin in ff:
		trommel_output8.write("%s & telnet & %s\n\n" % (fname, fp))
	if telnetd_bin in ff:
		trommel_output8.write("%s & telnetd & %s\n\n" % (fname, fp))
	if openssl_bin in ff:
		trommel_output8.write("%s & openssl & %s\n\n" % (fname, fp))		
	if busybox_bin in ff:
		text_search(busybox_bin, trommel_output2)	


	#WebApp specific - PHP, Javascript, VBScript, Lua
	#PHP untrusted user input functions
	if php_fn in ff:
		read_search_case_kw(ff, php_server_func, trommel_output12,fp)
		read_search_case_kw(ff, php_get_func, trommel_output12,fp)
		read_search_case_kw(ff, php_post_func, trommel_output12,fp)
		read_search_case_kw(ff, php_request_func, trommel_output12,fp)
		read_search_case_kw(ff, php_files_func, trommel_output12,fp)
		read_search_case_kw(ff, php_cookie_func, trommel_output12,fp)	
		read_search_case_kw(ff, php_split_kw, trommel_output12,fp)

		#PHP SQL related results
		read_search_case_kw(ff, php_sql_com1, trommel_output12,fp)
		read_search_case_kw(ff, php_sql_com2, trommel_output12,fp)
		read_search_case_kw(ff, php_sql_com3, trommel_output12,fp)

		#PHP shell injection function.
		read_search_kw(ff, php_shellexec_func, trommel_output12,fp)
		read_search_kw(ff, php_exec_func, trommel_output12,fp)
		read_search_kw(ff, php_passthru_func, trommel_output12,fp)
		read_search_kw(ff, php_system_func, trommel_output12,fp)

	#Javascript	functions of interest
	try:
		with open (ff, 'r') as js_file:
			text = js_file.read()
			hits = re.findall(script_word, text, re.S)
			if hits:
				read_search_kw(ff, alert_kw, trommel_output12,fp)
				read_search_kw(ff, src_kw, trommel_output12,fp)
				read_search_kw(ff, script_kw, trommel_output12,fp)
				read_search_kw(ff, script1_kw, trommel_output12,fp)
				read_search_case_kw(ff, doc_url_kw, trommel_output12,fp)
				read_search_case_kw(ff, doc_loc_kw, trommel_output12,fp)
				read_search_case_kw(ff, doc_referrer_kw, trommel_output12,fp)
				read_search_case_kw(ff, win_loc_kw, trommel_output12,fp)
				read_search_case_kw(ff, doc_cookies_kw, trommel_output12,fp)
				read_search_case_kw(ff, eval_kw, trommel_output12,fp)
				read_search_case_kw(ff, settimeout_kw, trommel_output12,fp)
				read_search_case_kw(ff, setinterval_kw, trommel_output12,fp)
				read_search_case_kw(ff, loc_assign_kw, trommel_output12,fp)
				read_search_case_kw(ff, nav_referrer_kw, trommel_output12,fp)
				read_search_case_kw(ff, win_name_kw, trommel_output12,fp)
	except IOError:
		pass

	#VBScript presence
	read_search_kw(ff, vbscript_kw, trommel_output12,fp)

	#Lua script functions of interest
	if lua_fn in ff:
		read_search_lua_kw(ff, lua_get, trommel_output12,fp)
		read_search_lua_kw(ff, lua_cgi_query, trommel_output12,fp)
		read_search_lua_kw(ff, lua_cgi_post, trommel_output12,fp)
		read_search_lua_kw(ff, lua_print, trommel_output12,fp)
		read_search_lua_kw(ff, lua_iowrite, trommel_output12,fp)
		read_search_lua_kw(ff, lua_ioopen, trommel_output12,fp)
		read_search_lua_kw(ff, lua_cgi_put, trommel_output12,fp)
		read_search_lua_kw(ff, lua_cgi_handhelp, trommel_output12,fp)
		read_search_lua_kw(ff, lua_execute, trommel_output12,fp)
		read_search_lua_kw(ff, lua_strcat, trommel_output12,fp)
		read_search_lua_kw(ff, lua_htmlentities, trommel_output12,fp)
		read_search_lua_kw(ff, lua_htmlspecialchars, trommel_output12,fp)
		read_search_lua_kw(ff, lua_htmlescape, trommel_output12,fp)
		read_search_lua_kw(ff, lua_htmlentitydecode, trommel_output12,fp)
		read_search_lua_kw(ff, lua_htmlunescape, trommel_output12,fp)
		read_search_lua_kw(ff, lua_iopopen, trommel_output12,fp)
		read_search_lua_kw(ff, lua_escapeshellarg, trommel_output12,fp)
		read_search_lua_kw(ff, lua_unescapeshellarg, trommel_output12,fp)
		read_search_lua_kw(ff, lua_escapeshellcmd, trommel_output12,fp)
		read_search_lua_kw(ff, lua_unescapeshellcmd, trommel_output12,fp)
		read_search_lua_kw(ff, lua_fhupo, trommel_output12,fp)
		read_search_lua_kw(ff, lua_fhpo, trommel_output12,fp)
		read_search_lua_kw(ff, lua_fsppo, trommel_output12,fp)
		read_search_lua_kw(ff, lua_ntopreaddir, trommel_output12,fp)


	#Search library base name against CVE Community Edition Database
	if lib_file in ff:
		base_name = re.search(r'lib[a-zA-Z]{1,20}', names, re.S)
		if base_name is not None:
			m = base_name.group()
			mm = m + ".so"
			text_search(mm, trommel_output2)


	#Search specific content related decompress and decompiled Android APKs
	#APK App permisssion					
	try:
		with open (ff, 'r') as file:
			text = file.read()
			hits = re.findall(perm, text, re.S)
			for h in hits:
				trommel_output13.write("Android权限 &  %s &  %s\n\n" % (fp, h))
	except IOError:
		pass

	#APK App package name
	try:
		with open (ff, 'r') as file:
			text = file.read()
			hits = re.findall(pkg_name, text, re.S)
			for h in hits:
				trommel_output13.write("Android程序包/应用程序名 & %s & %s\n\n" % (fp, h))
	except IOError:
		pass

        trommel_output1.close()
        trommel_output2.close()
        trommel_output3.close()
        trommel_output4.close()
        trommel_output5.close()
        trommel_output6.close()
        trommel_output7.close()
        trommel_output8.close()
        trommel_output9.close()
        #trommel_output10.close()
        trommel_output11.close()
        trommel_output12.close()
        trommel_output13.close()

	
