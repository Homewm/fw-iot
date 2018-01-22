#!_*_coding:utf-8_*_
import argparse
import os
from datetime import datetime
import indicators

parser = argparse.ArgumentParser(description= "TROMMEL: Sift Through Directories of Files to Identify Indicators That May Contain Vulnerabilities")
parser.add_argument("-p","--path", required=True, help="Directory to Search")
parser.add_argument("-o","--output", required=True, help="Output Trommel Results File Name (no spaces)")

args = vars(parser.parse_args())

path = args['path']
output = args['output']

#Date informtion
yrmoday = datetime.now().strftime("%Y%m%d_%H%M%S")

#Save file name and date information to file in working directory script
#trommel_output =  file(output+'_Trommel_'+yrmoday,'wt')


#Main function		
def main():
        #判断临时目录是否存在
        tmpPath=path+'Dirs'
        existDir=os.path.exists(tmpPath)
        if not existDir:
            #创建
            os.makedirs(tmpPath)
        else:
            print '目录已存在'
        #Print information to terminal
	print "\nTrommel is working to sift through the directory of files.\nResults will be saved to '%s'\n" % (output)
	
        #create split file
        #trommel_output1 :查找⽂件中存在的敏感关键字（如admin， root， auth， pwd， passwd， password， upgrade， dropbear，   ssl，telnet，crypt，sql，passphrase，rsa_key_pair，secretkey，ssh_hot_keys，private key，secret key）
        file(tmpPath+'/tmpfile1','wt')
        #trommel_output2 :查找固件中包含的曾经曝出过漏洞的组件和动态链接库，并显示相关的CVE编号与描述，查找Exploit-DB和Metasploit中对应上述CVE编号的攻击模块
        file(tmpPath+'/tmpfile2','wt')
        #trommel_output3 :查找固件中的⼝令⽂件（如passwd， shadow， .psk， kwallet， Bitcoin Wallet， keypass， ovpn， pgplog，pgppolicy.xml，pgpprefs.xml，private info，secret info，JavaKeyStore，sftp-config，Password Safe）
        file(tmpPath+'/tmpfile3','wt')
        #trommel_output4 :查找SSH/SSL相关⽂件（如SSH : authorized_keys， host_key， id_rsa， id_dsa， .pub， id_ecdsa，  id_ed25519; SSL : .pem， .crt， .cer， .p7b， .p12， .key，.p15）
        file(tmpPath+'/tmpfile4','wt')
        #trommel_output5 :查找⽂件中的IP地址、 URL以及email字符串
        file(tmpPath+'/tmpfile5','wt')
        #trommel_output6 :查找固件中的配置⽂件（如*.conf， *.cfg， *.ini）
        file(tmpPath+'/tmpfile6','wt')
        #trommel_output7 :查找固件中的数据库⽂件（如*.db， *.sqlite，*.sql）
        file(tmpPath+'/tmpfile7','wt')
        #trommel_output8 :查找固件中的敏感⼆进制⽂件（如ssh， sshd， scp， sftp， tftp， dropbear， telnet， telnetd， openssl， busybox, 其他）
        file(tmpPath+'/tmpfile8','wt')
        #trommel_output9 :列出/opt下⾯的所有⽂件
        file(tmpPath+'/tmpfile9','wt')
        #trommel_output10 :列出所有的shell脚本
        file(tmpPath+'/tmpfile10','wt')
        #trommel_output11 :列出web组件（如apache，lighttpd， alphapd， httpd）
        file(tmpPath+'/tmpfile11','wt')
        #trommel_output12 :查找WebApp脚本（如php， js， vb， lua）中包含的敏感函数
        file(tmpPath+'/tmpfile12','wt')
        #trommel_output13 :查找固件中包含的安卓APK⽂件，定位APK⽂件中的敏感词以及APK的权限
        file(tmpPath+'/tmpfile13','wt')

	#Title written to file
        trommel_output0 = file(tmpPath+'/tmpfile0','wt')
	
	#User given name and path to user given directory to search
        #pathraw=path.split('_',1)[-1].split('.extracted')[0]
	#trommel_output0.write("固件名: %s \n\n" % (pathraw))
	
	#Count number of files within given path directory
	total = 0
	for root, dirs, files in os.walk(path, followlinks=False):
		total += len(files)
	trommel_output0.write("固件中共有 %d个文件\n\n" % total)
	
	#Disclaimer written to output file
	#trommel_output0.write("结果可能是漏洞。这些结果可能被确认为假阳性存在。\n\n")
        
        #trommel_output0.write("分析报告结果如下：\n\n")
		
    #Enumerate dir passed by user
	for root, dirs, files in os.walk(path):
		
		for names in files:
			ff = os.path.join(root,names)
			
			#Ignore any symlinks
			if not os.path.islink(ff):
				
				#Ignore the /dev directory. Script has problems with files in this directory
				dev_kw = "/dev/"
				if not dev_kw in ff:
				
					if path and output: 
						indicators.kw(ff, tmpPath, names)

						
							
if __name__ == '__main__':
    main()
