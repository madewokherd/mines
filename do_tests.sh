#!/bin/sh

SRCS="Information.hx IntSet.hx IntSetTest.hx RunTests.hx SolveResult.hx HashSet.hx HashSetTest.hx"

haxe -main RunTests $SRCS -js jsout.js -D node || exit 1

haxe -main RunTests $SRCS -cpp cppout || exit 1

#haxe -main RunTests $SRCS -cs csout || exit 1 # broken on ubuntu 15.04

cppout/RunTests || exit 1

#mono csout/bin/RunTests.exe || exit 1

node jsout.js || exit 1

