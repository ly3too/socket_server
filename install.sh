#!/bin/sh

mkdir -p $HOME/.local/myserver
cp * $HOME/.local/myserver/ -r
ln -s $HOME/.local/myserver/myserver $HOME/.local/bin/

echo "done install"
