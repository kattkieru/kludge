# libclang
export KLUDGE_LLVM_ROOT="/build/fabric-llvm/install"
export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/usd-deps/lib:/opt/gcc-4.8/lib64:$KLUDGE_LLVM_ROOT/lib"
export PYTHONPATH="$KLUDGE_LLVM_ROOT/lib/python:$PYTHONPATH"
