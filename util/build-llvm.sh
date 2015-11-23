#!/bin/sh

VER=$1
if [ -z "$VER" ]; then
  echo "Usage: $0 <LLVM version>"
  exit 1
fi

set -e

TAG=RELEASE_$(echo $VER | tr -d '.')/final
svn co http://llvm.org/svn/llvm-project/llvm/tags/$TAG llvm-$VER
svn co http://llvm.org/svn/llvm-project/cfe/tags/$TAG llvm-$VER/tools/clang
svn co http://llvm.org/svn/llvm-project/clang-tools-extra/tags/$TAG llvm-$VER/tools/clang/tools/extra
svn co http://llvm.org/svn/llvm-project/compiler-rt/tags/$TAG llvm-$VER/projects/compiler-rt
svn co http://llvm.org/svn/llvm-project/libcxx/tags/$TAG llvm-$VER/projects/libcxx
svn co http://llvm.org/svn/llvm-project/libcxxabi/tags/$TAG llvm-$VER/projects/libcxxabi
patch -d llvm-$VER/projects/libcxxabi -p2 <<EOF
Index: libcxxabi/trunk/src/cxa_default_handlers.cpp
===================================================================
--- libcxxabi/trunk/src/cxa_default_handlers.cpp
+++ libcxxabi/trunk/src/cxa_default_handlers.cpp
@@ -101,19 +101,21 @@
 unexpected_handler
 set_unexpected(unexpected_handler func) _NOEXCEPT
 {
-	if (func == 0)
-		func = default_unexpected_handler;
-	return __sync_swap(&__cxa_unexpected_handler, func);
+    if (func == 0)
+        func = default_unexpected_handler;
+    return __atomic_exchange_n(&__cxa_unexpected_handler, func,
+                               __ATOMIC_ACQ_REL);
 //  Using of C++11 atomics this should be rewritten
 //  return __cxa_unexpected_handler.exchange(func, memory_order_acq_rel);
 }
 
 terminate_handler
 set_terminate(terminate_handler func) _NOEXCEPT
 {
-	if (func == 0)
-		func = default_terminate_handler;
-	return __sync_swap(&__cxa_terminate_handler, func);
+    if (func == 0)
+        func = default_terminate_handler;
+    return __atomic_exchange_n(&__cxa_terminate_handler, func,
+                               __ATOMIC_ACQ_REL);
 //  Using of C++11 atomics this should be rewritten
 //  return __cxa_terminate_handler.exchange(func, memory_order_acq_rel);
 }
Index: libcxxabi/trunk/src/cxa_handlers.cpp
===================================================================
--- libcxxabi/trunk/src/cxa_handlers.cpp
+++ libcxxabi/trunk/src/cxa_handlers.cpp
@@ -102,14 +102,14 @@
     __terminate(get_terminate());
 }
 
-extern "C" new_handler __cxa_new_handler = 0;
+new_handler __cxa_new_handler = 0;
 // In the future these will become:
 // std::atomic<std::new_handler>  __cxa_new_handler(0);
 
 new_handler
 set_new_handler(new_handler handler) _NOEXCEPT
 {
-    return __sync_swap(&__cxa_new_handler, handler);
+    return __atomic_exchange_n(&__cxa_new_handler, handler, __ATOMIC_ACQ_REL);
 //  Using of C++11 atomics this should be rewritten
 //  return __cxa_new_handler.exchange(handler, memory_order_acq_rel);
 }
EOF

GCC_ROOT=/opt/gcc-4.8
mkdir -p llvm-$VER/build
cd llvm-$VER/build
cmake .. \
  -DCMAKE_C_COMPILER=$GCC_ROOT/bin/gcc \
  -DCMAKE_CXX_COMPILER=$GCC_ROOT/bin/g++ \
  -DCMAKE_INSTALL_PREFIX=/opt/llvm-$VER \
  -DCMAKE_CXX_LINK_FLAGS="-L$GCC_ROOT/lib64 -Wl,-rpath,$GCC_ROOT/lib64" \
  -DGCC_INSTALL_PREFIX=$GCC_ROOT \
  -DCMAKE_BUILD_TYPE="Release" -DLLVM_TARGETS_TO_BUILD="X86"
make -j$(nproc)
cd ../..
echo "Run 'sudo make -C llvm-$VER/build install' to install in /opt/llvm-$VER"
