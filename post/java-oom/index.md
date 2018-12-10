# Out of Memory 错误产生原因

有两种内存分配失败会产生OOM错误：

1. 一种是本地堆内存不足，本地代码(native code)内存分配(malloc)失败。
2. 另一种是Java堆空间不足(GC无法回收足够的空间，并且Java堆无法继续扩展)，无法创建Java对象。

造成上述内存分配失败的原因又有四种：

1. 本地内存泄漏
2. Java堆内存泄漏
3. 堆开地太小
4. 请求的内存分配太大

<!--more-->

# 一般排查步骤

OOM发生时首先是要确定是哪一种原因。首先区分是本地内存还是Java堆的问题：查看发生OOM时Java堆的使用情况，如果Java堆已经扩展至上限，并且基本上已经被占用，那么很可能是Java堆的的问题，并且报错原因可能会有关键字如`Java heap`或者`GC`等；如果Java堆空间还有，但还是抛出了OOM，则可能是本地代码问题，并且可能会有本地代码报错的原因，比如出现`malloc failed`, `failed to fork OS thread`等，或者错误中出现指向本地代码文件(C++)的报错信息等。

接着排除非内存泄漏的情况：如果是堆太小，那么需要观察增加最大堆上限后程序的行为。如果程序进入稳定运行后堆使用率不再上升，则可以确定是堆太小。如果是请求分配的对象太大，则可以根据报错时线程dump，以及GC日志，结合代码排查是否有大对象分配。

然后对于Java堆泄漏的情况，需要进行heap dump分析（也就是所谓的“尸检”），Oracle JVM的转存为 *.hprof* 文件而IBM JVM的转存为 *.phd* 文件。推荐使用的工具是MAT（下文介绍）。

最后是本地内存分配失败。本地内存分配失败和Java堆没有关系，如果这个时候拿着Java Heap Dump分析就没有意义，而是应该使用系统层面的工具进行分析，比如pmap，gdb等工具。

# HotSpot OOM分析

根据Oracle官方手册，下面总结了HotSpot JVM OOM错误信息、发生原因和处理思路：

1. `java.lang.OutOfMemoryError: Java heap space`表示对象无法在Java堆上分配，造成此问题的原因包括：
   - 配置错误。分配的堆太小不足以运行应用；
   - finalize方法的调用。如果一个类重写了finalize方法，那么它的空间不会在GC的时候被回收。在GC之后，该对象会被放到一个队列里面，等待finalize方法被调用。处理这个队列的是一个低优先级的守护线程，如果入队的速率超过该线程处理的速率，会导致堆被逐渐占满，造成此类OOM错误。可以用以下方法检查这个队列的长度:
      1. JConsole中VM Summary页中的Objects pending for finalization（中文译作“暂挂最终处理”）的值；
         {{% figure class="center" src="/images/heap-dump-analysis/jconsole-vmsummary-finalize.png" alt="JConsole显示的finalization队列" title="JConsole显示的finalization队列"  %}}

      2. jmap命令的-finalizerinfo参数，比如：

            ```shell
            λ jmap -finalizerinfo 69636
            Attaching to process ID 69636, please wait...
            Debugger attached successfully.
            Server compiler detected.
            JVM version is 25.101-b13
            Number of objects pending for finalization: 0
            ```

    - 内存泄漏。对于一个长时间运行的应用比较可能的是它不断地创建并持有对象的引用，造成GC无法回收。这个问题通常是最难排查的，但是又最容易发生的，后文将介绍工具用于处理这个问题。

        可以参考[这篇](https://plumbr.io/outofmemoryerror/java-heap-space)文章。

2. `java.lang.OutOfMemoryError: GC Overhead limit exceeded`表示虽然对象可以在Java堆上分配，但是JVM需要花很大的力气进行GC操作后才能满足分配要求。这里具体是指在最近5个GC周期内，Java进程花费98%的时间在GC上，并且只能从GC中回收少于2%的空间。可以通过指定参数`-XX:-UseGCOverheadLimit`来关闭此OOM错误的抛出，但是通常在`GC Overhead limit exceeded`之后不久还是会触发`Java heap space`错误。造成此问题的原因和`java heap space`相似。

    可以参考[这篇](https://plumbr.io/outofmemoryerror/gc-overhead-limit-exceeded)文章。

3. ` java.lang.OutOfMemoryError: Requested array size exceeds VM limit`表示数组大小超过了平台特定数组大小的上限。这个错误是由JVM本地代码抛出的，并且发生在实际内存分配之前的校验函数中。抛出这个错误意味着数组长度超过了当前平台的寻址范围。

    理论上讲，Java的数组大小由数组索引int的范围决定（即上限为2,147,483,647），超过则无法编译。但实际上还受限于平台以及Java堆的上限。后者即为JVM启动参数`-Xmx`指定的大小，当尝试分配的数组超过这个大小的时候，会抛出 `java.lang.OutOfMemoryError: Java heap space`。前者则比较复杂，是在JVM编译时确定的。如下代码所示，在分配Java堆上分配数组内存之前校验了最大数组长度。

    ```c++
    // HotSpot JDK7: /src/share/vm/oops/objArrayKlass.cpp
    objArrayOop objArrayKlass::allocate(int length, TRAPS) {
        if (length >= 0) {
            if (length <= arrayOopDesc::max_array_length(T_OBJECT)) {
                int size = objArrayOopDesc::object_size(length);
                KlassHandle h_k(THREAD, as_klassOop());
                objArrayOop a = (objArrayOop)CollectedHeap::array_allocate(h_k, size, length, CHECK_NULL);
                assert(a->is_parsable(), "Can't publish unless parsable");
                return a;
            } else {
                // 数组尺寸超过给定类型元素的数组最大尺寸
                report_java_out_of_memory("Requested array size exceeds VM limit");
                JvmtiExport::post_array_size_exhausted();
                THROW_OOP_0(Universe::out_of_memory_error_array_size());
            }
        } else {
            THROW_0(vmSymbols::java_lang_NegativeArraySizeException());
        }
    }
    ```

    其中`arrayOopDesc::max_array_length`函数检查了数组长度上限：
    
    ```c++
    // HotSpot JDK7: /src/share/vm/oops/arrayOop.hpp
    static int32_t max_array_length(BasicType type) {
        assert(type >= 0 && type < T_CONFLICT, "wrong type");
        assert(type2aelembytes(type) != 0, "wrong type");

        // max_element_words_per_size_t为减去数组头部后的数组容量（单位为HeapWord），其中
        // 1. SIZE_MAX是定义在stdint.h中的size_t的最大长度，取决于编译器；
        // 2. HeapWordSize为4字节（32位系统）或8字节（64为系统），定义见下段代码；
        // 3. header_size()返回的是数组对象的头部大小（包括MarkWord, 类指针和数组长度）
        const size_t max_element_words_per_size_t =
        align_size_down((SIZE_MAX/HeapWordSize - header_size(type)), MinObjAlignment);
        
        // max_elements_per_size_t为减去数组头部后的数组容量（单位为指定的类型，比如int），其中
        // 1. type2aelembytes(type)是定义在globalDefinitions.hpp中的各类型的大小（如下段代码）
        const size_t max_elements_per_size_t =
        HeapWordSize * max_element_words_per_size_t / type2aelembytes(type);
        
        if ((size_t)max_jint < max_elements_per_size_t) {
        return align_size_down(max_jint - header_size(type), MinObjAlignment);
        }
        return (int32_t)max_elements_per_size_t;
    }
    ```

    HeapWordSize就是一个HeapWord的大小，定义如下，为一个指针的大小，32位系统为4字节，64位系统为8字节。

    ```c++
    class HeapWord {
            friend class VMStructs;
        private:
            char* i;
        #ifndef PRODUCT
        public:
            char* value() { return i; }
        #endif
    };

    const int HeapWordSize = sizeof(HeapWord);
    ```

    各种类型的尺寸定义：

    ```c++
    // HotSpot JDK7: /src/share/vm/utilities/globalDefinitions.hpp
    // size in bytes
    enum ArrayElementSize {
        T_BOOLEAN_aelem_bytes = 1,
        T_CHAR_aelem_bytes    = 2,
        T_FLOAT_aelem_bytes   = 4,
        T_DOUBLE_aelem_bytes  = 8,
        T_BYTE_aelem_bytes    = 1,
        T_SHORT_aelem_bytes   = 2,
        T_INT_aelem_bytes     = 4,
        T_LONG_aelem_bytes    = 8,
        #ifdef _LP64
        T_OBJECT_aelem_bytes  = 8,
        T_ARRAY_aelem_bytes   = 8,
        #else
        T_OBJECT_aelem_bytes  = 4,
        T_ARRAY_aelem_bytes   = 4,
        #endif
        T_NARROWOOP_aelem_bytes = 4,
        T_VOID_aelem_bytes    = 0
    };
    ```

    这个错误通常是程序错误，尝试创建一个过大的数组。

    关于此OOM异常的详细介绍可以参考[这篇](https://plumbr.io/outofmemoryerror/requested-array-size-exceeds-vm-limit)文章或者[Oracle](https://docs.oracle.com/javase/7/docs/webnotes/tsg/TSG-VM/html/memleaks.html#gbyuu)的文档。

4. `Exception in thread thread_name: java.lang.OutOfMemoryError: Metaspace`表示MetaSpace空间耗尽。由于JDK8以后永久代被取消，同时MetaSpace被引入，所以在JDK8之前，这个错误信息为`PermGen space`。

    MetaSpace用于存放被加载的Class，它不在Java Heap中，而是在本地内存当中。当需要加载的类很多或者很大，超过了MetaSpace的限制就会抛出这个错误。这个限制是由JVM启动参数`-XX:MaxMetaspaceSize=512m`指定的，可以通过调整该值来解决此问题。如果没有指定这个参数，那么MetaSpace的大小是无限的，直到出现本地内存分配失败为止，所以为了避免将这个错误隐藏起来，建议设置这个参数。

    对于PermGen Space问题的跟多介绍可以参考[这篇](https://plumbr.io/outofmemoryerror/permgen-space)的文章或者[Oracle](https://docs.oracle.com/javase/7/docs/webnotes/tsg/TSG-VM/html/memleaks.html#gbyuu)的文档；对于Metaspace问题可以参考[这篇](https://plumbr.io/outofmemoryerror/metaspace)文章或者[Oracle](https://docs.oracle.com/en/java/javase/11/troubleshoot/troubleshoot-memory-leaks.html#GUID-19F6D28E-75A1-4480-9879-D0932B2F305B)的文档。

5. `Exception in thread thread_name: java.lang.OutOfMemoryError: request <size> bytes for <reason>. Out of swap space?`表示本地堆内存分配失败和本地堆可能即将耗尽。当JVM请求的内存大于可用物理内存时，系统会把内存换出到交换空间（硬盘）上，当交换空间也满了的时候就会发生此错误。

    这个问题通常是由于系统层面的错误引起的，比如：
    1. 系统配置的交换空间不够；
    2. 其它进程占用了大量的内存资源；
    3. JVM进程出现本地内存泄漏。

    针对第一种情况，简单粗暴的方法是直接提高交换空间大小。但是对于Java程序来说使用交换空间通常会有很大的性能影响，因为GC停顿时间会上升好几个数量级，所以要么提高系统物理内存大小，要么进行优化以降低内存使用。

    针对第二种情况，应该将JVM进程或者内存消耗大户给隔离开来，单独使用一台机器。针对第三种情况，需要通过系统级别的工具分析JVM进程的内存使用情况。

    可以参考[这篇](https://plumbr.io/outofmemoryerror/out-of-swap-space)文章。

6. `Exception in thread thread_name: java.lang.OutOfMemoryError: <reason stack_trace_with_native_method>`表示在Java Native Interface中执行的代码发生了OOM错误，而不是在JVM代码中。通常错误栈中会显示本地方法名称。这通常需要系统级别的工具进行分析。

OOM是一种Error而不是Exception，但是还是继承自Throwable，因此我们可以捕获并且处理它，但是[JDK文档](https://docs.oracle.com/javase/8/docs/api/java/lang/Error.html)指出鉴于Error是非常严重的错误，应用程序不应该捕获它。

虽然OOM错误经常跟着Java程序停止响应甚至崩溃，但这并不是说OOM错误直接导致程序崩溃。它和其它异常一样，当一个线程抛出OOM，如果它没有被捕获，那么这个线程就会终止；如果有其它线程还在运行，它们还是会继续运行下去。但实际场景中，内存资源耗尽将导致级联式的OOM，所以经常影响到整个进程、甚至是系统。


# 参考资料

1. [JavaSE 11 Troubleshoot Guide](https://docs.oracle.com/en/java/javase/11/troubleshoot/)
2. [The 4 general reasons for OutOfMemoryError errors and how not to get fooled](https://www.ibm.com/developerworks/community/blogs/aimsupport/entry/4_general_reasons_for_outofmemoryerror_and_how_not_to_get_fooled?lang=en)
3. [Plumbr](https://plumbr.io/outofmemoryerror)


