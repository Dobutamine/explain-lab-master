

set -ex



pypy3 --help
pypy3 -c "import platform; print(platform._sys_version())"
test -f $PREFIX/lib-python/3/lib2to3/Grammar3.7*.pickle
test -f $PREFIX/lib-python/3/lib2to3/PatternGrammar3.7*.pickle
exit 0
