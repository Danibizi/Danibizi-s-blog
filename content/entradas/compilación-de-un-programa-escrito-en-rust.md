---
title: Compilación de un programa escrito en Rust
date: 2026-10-08T09:48:00
draft: false
description: Compilación de un programa escrito en Rust
ShowToc: false
cover:
  image: /img/Compilación en Rust_ guía visual.png
  alt: ''
tags:
  - 2ASIR
  - ASO
---

Para esta practica voy a instalar ripgrep, un grep pero escrito en rust.

\* https://github.com/BurntSushi/ripgrep

###  Descarga del código fuente


```plain
dani@debiancad:/tmp$ git clone https://github.com/BurntSushi/ripgrep
```

```plain
Clonando en 'ripgrep'...
```

```plain
remote: Enumerating objects: 14062, done.
```

```plain
remote: Counting objects: 100% (83/83), done.
```

```plain
remote: Compressing objects: 100% (47/47), done.
```

```plain
remote: Total 14062 (delta 51), reused 36 (delta 36), pack-reused 13979 (from 2)
```

```plain
Recibiendo objetos: 100% (14062/14062), 5.67 MiB | 19.75 MiB/s, listo.
```

```plain
Resolviendo deltas: 100% (9840/9840), listo.
```

```plain
dani@debiancad:/tmp$ cd ripgrep/
```

```plain
dani@debiancad:/tmp/ripgrep$ ls
```

```plain
AI_POLICY.md  Cargo.toml       COPYING  GUIDE.md         README.md             tests
```

```plain
benchsuite    CHANGELOG.md     crates   HomebrewFormula  RELEASE-CHECKLIST.md  UNLICENSE
```

```plain
build.rs      ci               FAQ.md   LICENSE-MIT      rustfmt.toml
```

```plain
Cargo.lock    CONTRIBUTING.md  fuzz     pkg              scripts
```


Como vemos ya tenemos el codigo fuente aqui, y para compilarlo usaremos cargo, que viene siendo el make en rust. Y @Cargo.toml@, el makefile.

La última versión (15.2.0) pide rustc 1.96 y mi rustc es el 1.85.1, así que da error. Por eso cambio a la versión 14.1.1 con @git checkout@.


```plain
dani@debiancad:/tmp/ripgrep$ git checkout 14.1.1
```

```plain
dani@debiancad:/tmp/ripgrep$ cargo clean
```


###  Compilación

Ahora lo compilaremos.


```plain
dani@debiancad:/tmp/ripgrep$ cargo build --release
```




```plain
dani@debiancad:/tmp/ripgrep$ ./target/release/rg --version
```

```plain
ripgrep 14.1.1 (rev 4649aa9700)
```

```plain
features:-pcre2
```

```plain
simd(compile):+SSE2,-SSSE3,-AVX2
```

```plain
simd(runtime):+SSE2,+SSSE3,+AVX2
```

```plain
```

```plain
PCRE2 is not available in this build of ripgrep.
```

Como vemos se ha compilado con exito y automaticamente se ubica en este fichero, lo movere a /opt

\### Instalación

```plain
dani@debiancad:/tmp/ripgrep$ sudo mkdir -p /opt/ripgrep/bin
```

```plain
sudo cp target/release/rg /opt/ripgrep/bin/
```

```plain
dani@debiancad:/tmp/ripgrep$ ls /opt/ripgrep/bin/
```

```plain
rg
```


Para poder ejecutarlo escribiendo solo rg, creo un enlace simbólico en /usr/local/bin.


```plain
dani@debiancad:/tmp/ripgrep$ sudo ln -s /opt/ripgrep/bin/rg /usr/local/bin/rg
```

```plain
dani@debiancad:/tmp/ripgrep$ which rg
```

```plain
/usr/local/bin/rg
```

```plain
dani@debiancad:/tmp/ripgrep$ ls -l /usr/local/bin/rg
```



### Uso del binario


```plain
dani@debiancad:/opt/ripgrep/bin$ rg
```

```plain
rg: ripgrep requires at least one pattern to execute a search
```


Como vemos ya podemos hacer uso del binario.


### Desinstalación limpia

Ahora procederemos a la desinstalacion limpia. Primero salgo del directorio que voy a borrar para que no dé error.


```plain
dani@debiancad:/opt/ripgrep/bin$ cd ~
```

```plain
dani@debiancad:~$ sudo rm /usr/local/bin/rg
```

```plain
sudo rm -rf /opt/ripgrep
```

```plain
rm -rf /tmp/ripgrep
```

```plain
hash -r
```

```plain
dani@debiancad:~$ which rg
```

```plain
ls /opt/ripgrep
```

```plain
ls /tmp/ripgrep
```

```plain
ls -l /usr/local/bin/rg
```

```plain
ls: no se puede acceder a '/opt/ripgrep': No existe el fichero o el directorio
```

```plain
ls: no se puede acceder a '/tmp/ripgrep': No existe el fichero o el directorio
```

```plain
ls: no se puede acceder a '/usr/local/bin/rg': No existe el fichero o el directorio
```

Como vemos se ha desinstalado con exito.
