#!/bin/bash
set -e
cd "$(dirname "$0")"
rm -rf /tmp/blog-preview && mkdir -p /tmp/blog-preview
tar --exclude=.git --exclude=public --exclude=resources -cf - . | tar -xf - -C /tmp/blog-preview
python3 scripts/redmine2md.py /tmp/blog-preview/content
hugo server -s /tmp/blog-preview
