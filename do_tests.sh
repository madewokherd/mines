#!/bin/sh

SRCS="IntSet.hx IntSetTest.hx RunTests.hx"

haxe -main RunTests $SRCS -js jsout.js -D node || exit 1

haxe -main RunTests $SRCS -cpp cppout || exit 1

haxe -main RunTests $SRCS -cs csout || exit 1

cppout/RunTests || exit 1

mono csout/bin/RunTests.exe || exit 1

node jsout.js || exit 1

