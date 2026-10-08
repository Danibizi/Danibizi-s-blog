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

\* https://github.com/BurntSushi/ripg

### Descarga del código fuente

<pre>

dani@debiancad:/tmp$ git clone https://github.com/BurntSushi/ripgrep

Clonando en 'ripgrep'...

remote: Enumerating objects: 14062, done.

remote: Counting objects: 100% (83/83), done.

remote: Compressing objects: 100% (47/47), done.

remote: Total 14062 (delta 51), reused 36 (delta 36), pack-reused 13979 (from 2)

Recibiendo objetos: 100% (14062/14062), 5.67 MiB | 19.75 MiB/s, listo.

Resolviendo deltas: 100% (9840/9840), listo.

dani@debiancad:/tmp$ cd ripgrep/

dani@debiancad:/tmp/ripgrep$ ls

AI_POLICY.md  Cargo.toml       COPYING  GUIDE.md         README.md             tests

benchsuite    CHANGELOG.md     crates   HomebrewFormula  RELEASE-CHECKLIST.md  UNLICENSE

build.rs      ci               FAQ.md   LICENSE-MIT      rustfmt.toml

Cargo.lock    CONTRIBUTING.md  fuzz     pkg              scripts

</pre>

Como vemos ya tenemos el codigo fuente aqui, y para compilarlo usaremos cargo, que viene siendo el make en rust. Y @Cargo.toml@, el makefile.

La última versión (15.2.0) pide rustc 1.96 y mi rustc es el 1.85.1, así que da error. Por eso cambio a la versión 14.1.1 con @git checkout@.

<pre>

dani@debiancad:/tmp/ripgrep$ git checkout 14.1.1

dani@debiancad:/tmp/ripgrep$ cargo clean

</pre>

### Compilación

Ahora lo compilaremos.

<pre>

dani@debiancad:/tmp/ripgrep$ cargo build --release

(pega aquí tu salida)

</pre>

<pre>

dani@debiancad:/tmp/ripgrep$ ./target/release/rg --version

ripgrep 14.1.1 (rev 4649aa9700)

features:-pcre2

simd(compile):+SSE2,-SSSE3,-AVX2

simd(runtime):+SSE2,+SSSE3,+AVX2

PCRE2 is not available in this build of ripgrep.

</pre>

Como vemos se ha compilado con exito y automaticamente se ubica en este fichero, lo movere a /opt

### Instalación

<pre>

dani@debiancad:/tmp/ripgrep$ sudo mkdir -p /opt/ripgrep/bin

sudo cp target/release/rg /opt/ripgrep/bin/

dani@debiancad:/tmp/ripgrep$ ls /opt/ripgrep/bin/

rg

</pre>

Para poder ejecutarlo escribiendo solo rg, creo un enlace simbólico en /usr/local/bin.

<pre>

dani@debiancad:/tmp/ripgrep$ sudo ln -s /opt/ripgrep/bin/rg /usr/local/bin/rg

dani@debiancad:/tmp/ripgrep$ which rg

/usr/local/bin/rg

dani@debiancad:/tmp/ripgrep$ ls -l /usr/local/bin/rg

(pega aquí tu salida)

</pre>

 Uso del binario

<pre>

dani@debiancad:/opt/ripgrep/bin$ rg

rg: ripgrep requires at least one pattern to execute a search

</pre>

Como vemos ya podemos hacer uso del binario.


### Desinstalación limpia

Ahora procederemos a la desinstalacion limpia. Primero salgo del directorio que voy a borrar para que no dé error.

<pre>

dani@debiancad:/opt/ripgrep/bin$ cd \~

dani@debiancad:\~$ sudo rm /usr/local/bin/rg

sudo rm -rf /opt/ripgrep

rm -rf /tmp/ripgrep

hash -r

dani@debiancad:\~$ which rg

ls /opt/ripgrep

ls /tmp/ripgrep

ls -l /usr/local/bin/rg

ls: no se puede acceder a '/opt/ripgrep': No existe el fichero o el directorio

ls: no se puede acceder a '/tmp/ripgrep': No existe el fichero o el directorio

ls: no se puede acceder a '/usr/local/bin/rg': No existe el fichero o el directorio

</pre>

Como vemos se ha desinstalado con exito.
