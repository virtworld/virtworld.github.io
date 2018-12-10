# 分析前准备

本节介绍了一般生产环境建议开启的JVM flag和系统参数，以便在OOM或者崩溃的时候收集信息。对于Oracle/IBM JDK通常我们需要收集heap dump(.prof/.phd)，thread dump(*.tdump/javacore.*.txt)，GC日志。

## 设置Out of Memory(OOM)时转存Java堆

在生产系统发生OOM时产生Java堆转存是必要的配置，因为这往往是OOM错误发生后收集分析数据的唯一机会。Oracle Hotspot JVM在启动参数上添加`-XX:+HeapDumpOnOutOfMemoryError`后会在发生OOM错误时进行heap dump。可以结合`-xx:HeapDumpPath=path`指定保存的dump的路径。

IBM JVM默认在OOM发生时产生heap dump和javacore文件，文件命名方式为`javacore.[date].[time].[index].txt`和`heapdump.[date].[time].[index].phd`。

需要注意的是，oracle Hotspot只会在第一次OOM时进行堆转存，而IBM JRE会在每一次OOM时都产生堆转存。通常第一个OOM错误时产生的堆转存是最适合拿来分析的，因为OOM会造成级联性地错误（发生了OOM错误的进程一般会持续抛出OOM）。但只要JVM进程还活着，就可以手动触发dump生成（参考[使用工具](#使用工具)）。

除了Java heap dump以外，Oracle JVM产生的HPROF dump文件中包含了一份线程栈快照，而IBM JVM也会在OOM时转存javacore文件，文件中包含线程栈的快照。

<!--more-->

## 设置进程崩溃时转存core

如果Java进程崩溃了，*nix类系统会转存一份core文件。core文件是某个时点，某一进程的内存的完整快照，可以使用gdb工具进行调式，主要用于本地内存分析。

有些系统默认会禁用core转存，可以使用以下命令来查看对core转存的限制，如果返回是0，则表示进程崩溃时不会转存core。

```shell
juliette1@ubuntu:~$ ulimit -c
0
```

在启用core转存时候需要注意，core文件可能很大，特别是设置的Java堆很大的时候。下面的命令可以启用core转存：

```shell
juliette1@ubuntu:~$ ulimit -c unlimited
juliette1@ubuntu:~$ ulimit -c
unlimited
```

core文件产生默认存放在程序所在目录，命名格式为core.*pid*。如果程序僵死，无法正常关闭，可以使用kill -6 *pid*来强制生成core。


## 设置打印GC日志

对于Oracle JDK，加上以下flag`-Xloggc:gc.log -XX:+PrintGCDetails -XX:+PrintGCDateStamps `，GC日志会被写到gc.log下。对于IBM JDK，启动参数为`-Xverbosegclog:gc.log`。

## 启用JMX监控

JMX可以被用来远程链接到Java程序，去收集和分析运行数据，主要用于性能分析器的实时监控。配置JMX允许远程链接本身不会带来额外的性能消耗。

```text
-Dcom.sun.management.jmxremote.port=9000
-Dcom.sun.management.jmxremote.ssl=false
-Dcom.sun.management.jmxremote.authenticate=false
```

## 使用工具

对于JVM故障诊断和性能分析，除了上面这些铺垫工作，还需要使用很多工具的辅助，而每个工具使用的问题场景不同，比如使用VisualVM, JConsole等用于监控类问题，使用MAT等用于故障后检查(“尸检”)；另外，每个工具可能采用不同的方式收集数据，这些方式又可能依赖于具体的虚拟机实现、操作系统，所以通常情况下，需要多种工具混合使用来定位问题。本文剩下部分记录了排查问题时常用的工具的常见使用方法，默认情况下JVM指的是HotSpot。

# JVM自带参数

JVM本身提供了很多选项用于帮助发现问题。除了本文中介绍的`-XX:HeapDumpOnOutOfMemoryError`和`-xx:HeapDumpPath=path`参数外，还有很多可用选项。主要分为错误时处理类(下面列出一些)、日志打印类(以Print开头的参数)、堆大小配置类以及GC调优类。常用的可参考[Oracle问题诊断手册](https://docs.oracle.com/en/java/javase/11/troubleshoot/command-line-options1.html)，完整的详见[Oracle官方文档](https://www.oracle.com/technetwork/java/javase/tech/vmoptions-jsp-140102.html)。

- **-XX:OnError=string** 发生致命错误时执行用户指定的命令
- **-XX:OnOutOfMemoryError=string** 发生OOM时执行用户指定的命令
- **-XX:ErrorFile=filename** 发生致命错误时保存的日志的位置
- ...

部分参数可以通过`jinfo -flag [+|-]<name> pid`命令动态添加和移除。比如说`jinfo -flag +PrintGC 138336`。部分可以动态修改的参数包括：

- HeapDumpOnOutOfMemoryError
- HeapDumpPath
- PrintGC
- PrintGCDetails
- PrintGCTimeStamps
- PrintClassHistogram
- PrintConcurrentLocks

## Native Memory Tracking (NMT)

JVM启动参数`-XX:NativeMemoryTracking=summary`或者`-XX:NativeMemoryTracking=detail`用于跟踪所有由JVM内存分配的内存（堆和非堆）。NMT选项不应该在生成上开启，因为它会带来较大的性能损失（官方文档称会带来5%-10%的性能下降以及额外的内存开销）。

通常我们关注的是堆内存的使用情况，因为大多数代码申请的内存都在堆上（除了依赖于sun.misc.Unsafe的代码，比如NIO中的direct allocated buffer和concurrent包等），所以泄漏往往在堆上面。但如果发现Java进程实际占用物理内存远远大于堆内存的情况，有可能需要对非堆内存进行分析，这时候NMT是一个好的选择。但NMT只能用于JVM分配的内存，如果由其它本地代码分配的内存，可能需要系统级的内存分析工具来支持。

开启了NMT参数后，可以用jcmd命令来查看内存使用报告。下面是一份summary级别的报告，使用命令`jcmd 77169 VM.native_memory summary`。

```shell
Total: reserved=1571248KB, committed=40108KB
-                 Java Heap (reserved=247808KB, committed=16384KB)
                            (mmap: reserved=247808KB, committed=16384KB) 
 
-                     Class (reserved=1056908KB, committed=5004KB)
                            (classes #413)
                            (malloc=140KB #220) 
                            (mmap: reserved=1056768KB, committed=4864KB) 
 
-                    Thread (reserved=11357KB, committed=11357KB)
                            (thread #12)
                            (stack: reserved=11308KB, committed=11308KB)
                            (malloc=36KB #57) 
                            (arena=13KB #22)
 
-                      Code (reserved=249682KB, committed=2618KB)
                            (malloc=82KB #389) 
                            (mmap: reserved=249600KB, committed=2536KB) 
 
-                        GC (reserved=819KB, committed=71KB)
                            (malloc=7KB #79) 
                            (mmap: reserved=812KB, committed=64KB) 
 
-                  Compiler (reserved=133KB, committed=133KB)
                            (malloc=2KB #28) 
                            (arena=131KB #3)
 
-                  Internal (reserved=2840KB, committed=2840KB)
                            (malloc=2808KB #1283) 
                            (mmap: reserved=32KB, committed=32KB) 
 
-                    Symbol (reserved=1366KB, committed=1366KB)
                            (malloc=910KB #88) 
                            (arena=456KB #1)
 
-    Native Memory Tracking (reserved=151KB, committed=151KB)
                            (malloc=94KB #1482) 
                            (tracking overhead=57KB)
 
-               Arena Chunk (reserved=185KB, committed=185KB)
                            (malloc=185KB) 
```

其中我们主要关注commited值，这个表示实际使用的内存空间。detail的报告会具体到每一个虚拟内存映射的使用情况，使用命令`jcmd 77169 VM.native_memory detail`：

```shell
...
Virtual memory map:
 
[0x00000000f0e00000 - 0x0000000100000000] reserved 247808KB for Java Heap from
    [0x00007ff2c2a5fbb2] ReservedSpace::initialize(unsigned long, unsigned long, bool, char*, unsigned long, bool)+0xc2
    [0x00007ff2c2a6058e] ReservedHeapSpace::ReservedHeapSpace(unsigned long, unsigned long, bool, char*)+0x6e
    [0x00007ff2c2a2d63b] Universe::reserve_heap(unsigned long, unsigned long)+0x8b
    [0x00007ff2c2581ce2] GenCollectedHeap::allocate(unsigned long, unsigned long*, int*, ReservedSpace*)+0x182
...
```

NMT可以追踪个部分内存的变化情况。首先需要建立一个基线，使用命令`jcmd 77169 VM.native_memory baseline`，然后再与基线做对比`jcmd 77169 VM.native_memory summary.diff`，会显示每部分内存的增减情况：

```shell
Total: reserved=1571249KB +10KB, committed=40109KB +10KB

-                 Java Heap (reserved=247808KB, committed=16384KB)
                            (mmap: reserved=247808KB, committed=16384KB)
 
-                     Class (reserved=1056908KB, committed=5004KB)
                            (classes #413)
                            (malloc=140KB #220)
                            (mmap: reserved=1056768KB, committed=4864KB)
 
-                    Thread (reserved=11357KB, committed=11357KB)
                            (thread #12)
                            (stack: reserved=11308KB, committed=11308KB)
                            (malloc=36KB #57)
                            (arena=13KB #22)
 
-                      Code (reserved=249682KB, committed=2618KB)
                            (malloc=82KB #389)
                            (mmap: reserved=249600KB, committed=2536KB)
 
-                        GC (reserved=819KB, committed=71KB)
                            (malloc=7KB #79)
                            (mmap: reserved=812KB, committed=64KB)
 
-                  Compiler (reserved=133KB, committed=133KB)
                            (malloc=2KB #28)
                            (arena=131KB #3)
 
-                  Internal (reserved=2840KB, committed=2840KB)
                            (malloc=2808KB #1283)
                            (mmap: reserved=32KB, committed=32KB)
 
-                    Symbol (reserved=1366KB, committed=1366KB)
                            (malloc=910KB #88)
                            (arena=456KB #1)
 
-    Native Memory Tracking (reserved=151KB +10KB, committed=151KB +10KB)
                            (malloc=94KB +8KB #1485 +119)
                            (tracking overhead=57KB +2KB)
 
-               Arena Chunk (reserved=185KB, committed=185KB)
                            (malloc=185KB)
```


# JDK命令行工具

## jstat

jstat常用排查GC相关的问题。下面是笔者常用的参数：

```shell
james@ubuntu:~/tmp$ jstat -gcutil -h10 -t 49343 1000
Timestamp         S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT   
         5531.1   0.47   0.00   0.00  75.37  53.90  55.24  42828   18.520     1    0.090   18.609
         5532.1   0.47   0.00  63.00  75.38  53.90  55.24  42834   18.523     1    0.090   18.613
         5533.1   0.00   0.47   0.00  75.39  53.90  55.24  42841   18.525     1    0.090   18.615
         5534.1   0.00   0.47  56.22  75.40  53.90  55.24  42847   18.528     1    0.090   18.617
         5535.1   0.47   0.00  15.52  75.41  53.90  55.24  42854   18.530     1    0.090   18.620
         5536.1   0.47   0.00  42.65  75.42  53.90  55.24  42860   18.532     1    0.090   18.622
         5537.1   0.00   0.47   0.00  75.43  53.90  55.24  42867   18.535     1    0.090   18.625
         5538.1   0.00   0.47  63.00  75.44  53.90  55.24  42873   18.537     1    0.090   18.627
         5539.1   0.47   0.00   0.00  75.45  53.90  55.24  42880   18.540     1    0.090   18.630
         5540.1   0.47   0.00  49.43  75.46  53.90  55.24  42886   18.543     1    0.090   18.633
Timestamp         S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT   
         5541.1   0.00   0.47   6.78  75.47  53.90  55.24  42893   18.546     1    0.090   18.636
         5542.1   0.00   0.47  35.87  75.48  53.90  55.24  42899   18.549     1    0.090   18.639
```

命令各参数含义：

- `-gcutil`参数为显示GC指标信息，常用的还有`-gcnew`、-gcold`等，详见Oracle[文档](https://docs.oracle.com/javase/7/docs/technotes/tools/share/jstat.html)；
- `-h10`表示每隔10行打印一个header，如上面输出所示；
- `-t`表示打印自JVM启动以来经过多少秒；
- `49343`表示的是本地虚拟机识别符local virtual machine identifier (LVMID)，通常（但不一定）是pid；
- `1000`表示的是每隔1000毫秒取样一次。

输出各指标含义：

- S0: Survivor 0 使用率
- S1: Survivor 1 使用率
- E: Eden 使用率
- O: 老年代使用率
- M: Metaspace 使用率
- CCS: Compressed class 使用率
- YGC: Young GC发生次数
- YGCT: Young GC总共时间（秒）
- FGC: Full GC发生次数
- FGCT: Full GC总共时间（秒）
- GCT: 总共GC时间（秒）

## jstack

jstack主要用于打印JVM进程或core文件线程跟踪信息，Oracle官方建议使用最新的jcmd替代jmap。线程状态有以下几种：

| 状态 | 描述|
| :-- | :-- |
| NEW | 线程还没有启动 |
| RUNNABLE | 线程正在JVM中运行 |
| BLOCKED | 线程被阻塞，等待一个monitor锁 |
| WAITING | 线程正在无限期地等待另一个线程执行某个特定的行为 |
| TIMED_WAITING | 线程正在一定时间内等待另一个线程执行某个特定的行为 |
| TERMINATED | 线程已经退出 |

1. jstack *pid*

    打印Java线程信息。如果添加[-l]参数，会让每个线程显示拥有的ownable synchronizer信息。如果添加[-F]参数，可以在进程hung的时候强制打印线程栈信息。

    ```shell
    james@ubuntu:~/tmp$ jstack 43717
    2018-12-04 18:48:03
    Full thread dump Java HotSpot(TM) 64-Bit Server VM (25.161-b12 mixed mode):

    "main" #1 prio=5 os_prio=0 tid=0x00007fa67800a800 nid=0xaacb waiting on condition [0x00007fa681d4c000]
    java.lang.Thread.State: TIMED_WAITING (sleeping)
        at java.lang.Thread.sleep(Native Method)
        at Temp.main(Temp.java:7)
    ...
    ```



1. jstack -m *pid*

    m表示混合模式，显示出Java线程栈帧和本地线程栈帧信息，以及死锁信息。其中带有\*号的是Java栈帧，没有\*的是本地C/C++栈帧。

    ```shell
    james@ubuntu:~/tmp$ jstack -m 43717
    Attaching to process ID 43717, please wait...
    Debugger attached successfully.
    Server compiler detected.
    JVM version is 25.161-b12
    Deadlock Detection:

    No deadlocks found.

    ----------------- 43723 -----------------
    0x00007fa681936709	__pthread_cond_timedwait + 0x129
    0x00007fa680a75dc7	_ZN2os5sleepEP6Threadlb + 0x297
    0x00007fa680870e3a	JVM_Sleep + 0x3ba
    0x00007fa6690186c7	* java.lang.Thread.sleep(long) bci:0 (Interpreted frame)
    0x00007fa6690082bd	* Temp.main(java.lang.String[]) bci:3 line:7 (Interpreted frame)
    0x00007fa6690007a7	<StubRoutines>
    0x00007fa6807ddae6	_ZN9JavaCalls11call_helperEP9JavaValueP12methodHandleP17JavaCallArgumentsP6Thread + 0x1056
    0x00007fa68081f072	_ZL17jni_invoke_staticP7JNIEnv_P9JavaValueP8_jobject11JNICallTypeP10_jmethodIDP18JNI_ArgumentPusherP6Thread + 0x362
    0x00007fa68083b8da	jni_CallStaticVoidMethod + 0x17a
    0x00007fa68171b0ff	JavaMain + 0x81f
    ----------------- 43731 -----------------
    0x00007fa681936709	__pthread_cond_timedwait + 0x129
    0x00007fa680a2f0ae	_ZN7Monitor5IWaitEP6Threadl + 0x44e
    ...
    ```

## jmap

jmap主要用于打印内存相关的JVM进程或core文件的统计信息，Oracle官方建议使用最新的jcmd替代jmap。启动jmap的用户id和jmap跟踪的JVM进程的用户id必需相同，否则会无法attach。

```shell
james@ubuntu:~/tmp$ jmap 43717
Attaching to process ID 43717, please wait...
Error attaching to process: sun.jvm.hotspot.debugger.DebuggerException: Can't attach to the process: ptrace(PTRACE_ATTACH, ..) failed for 43717: Operation not permitted
sun.jvm.hotspot.debugger.DebuggerException: sun.jvm.hotspot.debugger.DebuggerException: Can't attach to the process: ptrace(PTRACE_ATTACH, ..) failed for 43717: Operation not permitted
	at sun.jvm.hotspot.debugger.linux.LinuxDebuggerLocal$LinuxDebuggerLocalWorkerThread.execute(LinuxDebuggerLocal.java:163)
	at sun.jvm.hotspot.debugger.linux.LinuxDebuggerLocal.attach(LinuxDebuggerLocal.java:278)
	at sun.jvm.hotspot.HotSpotAgent.attachDebugger(HotSpotAgent.java:671)
    ...
```

除此之外，笔者在测试中还发现在使用同一用户的情况下，另一种情况也会导致无法attach:
因为Linux的安全机制Yama模块对一个进程查看其它进程的内存做了限制，具体可以参见[Kernel](/proc/sys/kernel/yama/ptrace_scope)。将下面这个配置改成0即可允许jmap访问其它JVM进程：

```shell
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
```


常用操作：

1. jmap *pid* 

    打印加载的共享模块的内存地址，占用空间和模块地址，类似pmap命令。

    ```shell
    james@ubuntu:~/tmp$ jmap 43717
    Attaching to process ID 43717, please wait...
    Debugger attached successfully.
    Server compiler detected.
    JVM version is 25.161-b12
    0x0000000000400000	7K	    /usr/lib/jvm/java-8-oracle/jre/bin/java
    0x00007fa67eda0000	125K	/usr/lib/jvm/java-8-oracle/jre/lib/amd64/libzip.so
    0x00007fa67efbc000	46K	    /lib/x86_64-linux-gnu/libnss_files-2.23.so
    0x00007fa67f1ce000	46K	    /lib/x86_64-linux-gnu/libnss_nis-2.23.so
    0x00007fa67f3da000	90K	    /lib/x86_64-linux-gnu/libnsl-2.23.so
    0x00007fa67f5f3000	34K	    /lib/x86_64-linux-gnu/libnss_compat-2.23.so
    0x00007fa67f7fc000	221K	/usr/lib/jvm/java-8-oracle/jre/lib/amd64/libjava.so
    ...
    ```
2. jmap -heap *pid*

    显示GC配置、Java堆配置和Java堆的使用情况。

    ```shell
    james@ubuntu:~/tmp$ jmap -heap 43717
    Attaching to process ID 43717, please wait...
    Debugger attached successfully.
    Server compiler detected.
    JVM version is 25.161-b12

    using thread-local object allocation.
    Mark Sweep Compact GC

    Heap Configuration:
    MinHeapFreeRatio         = 40
    MaxHeapFreeRatio         = 70
    MaxHeapSize              = 253755392 (242.0MB)
    NewSize                  = 5570560 (5.3125MB)
    MaxNewSize               = 84541440 (80.625MB)
    OldSize                  = 11206656 (10.6875MB)
    NewRatio                 = 2
    SurvivorRatio            = 8
    MetaspaceSize            = 21807104 (20.796875MB)
    CompressedClassSpaceSize = 1073741824 (1024.0MB)
    MaxMetaspaceSize         = 17592186044415 MB
    G1HeapRegionSize         = 0 (0.0MB)

    Heap Usage:
    New Generation (Eden + 1 Survivor Space):
    capacity = 5046272 (4.8125MB)
    used     = 567664 (0.5413665771484375MB)
    free     = 4478608 (4.2711334228515625MB)
    11.249175629058442% used
    Eden Space:
    capacity = 4521984 (4.3125MB)
    used     = 567664 (0.5413665771484375MB)
    free     = 3954320 (3.7711334228515625MB)
    12.553427875905797% used
    From Space:
    capacity = 524288 (0.5MB)
    used     = 0 (0.0MB)
    free     = 524288 (0.5MB)
    0.0% used
    To Space:
    capacity = 524288 (0.5MB)
    used     = 0 (0.0MB)
    free     = 524288 (0.5MB)
    0.0% used
    tenured generation:
    capacity = 11206656 (10.6875MB)
    used     = 0 (0.0MB)
    free     = 11206656 (10.6875MB)
    0.0% used

    751 interned Strings occupying 50632 bytes.
    ```

3. jmap -histo[:live] *pid*

    用于显示内存使用情况直方图，以类为单位统计内存使用。每一行显示，类的全限定名，实例数和占用堆空间大小。配合[-F]参数可以在进程无响应的时候强制显示直方图信息。

    ```shell
    james@ubuntu:~/tmp$ jmap -histo 43717

    num     #instances         #bytes  class name
    ----------------------------------------------
    1:           431         206160  [I
    2:          1856         185152  [C
    3:           208          56752  [B
    4:           477          54456  java.lang.Class
    5:          1484          35616  java.lang.String
    6:           537          26720  [Ljava.lang.Object;
    7:           388           9312  java.util.LinkedList$Node
    ...
    ```

4. jmap -dump:\<option\> *pid*

    JDK7以后通过jmap可以生成HPROF格式的heap dump。配合[-F]参数可以在进程无响应的时候强制生成dump文件。

    ```shell
    james@ubuntu:~/tmp$ jmap -dump:format=b,file=dump.hprof 43717
    Dumping heap to /home/james/tmp/dump.hprof ...
    Heap dump file created
    ```

## jinfo
jinfo主要用于显示JVM进程或core文件的配置信息和系统配置信息，以及动态修改部分JVM的参数。Oracle官方建议使用最新的jcmd替代jinfo。常用参数：

1. jinfo -sysprops *pid*

    显示系统变量

    ```shell
    james@ubuntu:~/tmp$ jinfo -sysprops 49343
    Attaching to process ID 49343, please wait...
    Debugger attached successfully.
    Server compiler detected.
    JVM version is 25.161-b12
    java.runtime.name = Java(TM) SE Runtime Environment
    java.vm.version = 25.161-b12
    sun.boot.library.path = /usr/lib/jvm/java-8-oracle/jre/lib/amd64
    java.vendor.url = http://java.oracle.com/
    java.vm.vendor = Oracle Corporation
    ...
    ```

2. jinfo -flags *pid*

    显示JVM启动参数

    ```shell
    james@ubuntu:~/tmp$ jinfo -flags 49343
    Attaching to process ID 49343, please wait...
    Debugger attached successfully.
    Server compiler detected.
    JVM version is 25.161-b12
    Non-default VM flags: -XX:CICompilerCount=3 -XX:InitialHeapSize=16777216 -XX:MaxHeapSize=253755392 -XX:MaxNewSize=84541440 -XX:MinHeapDeltaBytes=196608 -XX:NewSize=5570560 -XX:OldSize=11206656 -XX:+UseCompressedClassPointers -XX:+UseCompressedOops -XX:+UseFastUnorderedTimeStamps 
    Command line:
    ```

3. jinfo -flag [+|-]\<name\> *pid*

    动态添加或移除JVM参数。详见[JVM自带参数](#jvm自带参数)。


## jcmd

jcmd用于向JVM进程发送诊断命令，它必需运行在JVM相同的机器上，并且必需和JVM的启动用户id和组id相同。常见用法：

1. 显示正在运行的JVM

    不带任何参数的jcmd显示正在运行的JVM进程，显示的为pid和main类的名字。

    ```shell
    james@ubuntu:~/tmp$ jcmd
    50731 sun.tools.jcmd.JCmd
    49343 Temp
    ```

2. 显示所有可用选项

    `jcmd <process id/main class> help`显示所有jcmd可用的选项。

    ```shell
    james@ubuntu:~/tmp$ jcmd Temp help
    49343:
    The following commands are available:
    JFR.stop
    JFR.start
    JFR.dump
    JFR.check
    ...
    ```

3. 打印线程栈信息

    `jcmd <process id/main class> Thread.print`打印线程栈信息，和jstack类似。

4. 生成dump

    `jcmd <process id/main class> GC.heap_dump filename=dump.hprof`生成dump文件。效果和`jmap -dump:file=<file> <pid>`一样，官方推荐使用jcmd。

    ```shell
    james@ubuntu:~/tmp$ jcmd Temp GC.heap_dump filename=1912_dump.hprof
    49343:
    Heap dump file created
    ```
5. 生成直方图

    `jcmd <process id/main class> GC.class_histogram`生成各类（的实例）的内存使用情况，效果和`jmap -histo[:live] *pid*`一样，官方推荐使用jcmd。

    ```shell
    james@ubuntu:~/tmp$ jcmd Temp GC.class_histogram
    49343:

    num     #instances         #bytes  class name
    ----------------------------------------------
    1:       2559211       40947376  java.lang.Integer
    2:           566       10973032  [Ljava.lang.Object;
    3:          3292         202568  [C
    4:           395         123968  [B
    5:          3280          78720  java.lang.String
    6:           585          66568  java.lang.Class
    7:           615          24600  java.util.LinkedHashMap$Entry
    8:           515          16480  java.util.HashMap$Node
    9:           284          12896  [Ljava.lang.String;
    10:           19          10032  [Ljava.util.HashMap$Node;
    ```

6. 显示JVM相关信息
    
    `jcmd <process id/main class> VM.version`用于显示JVM版本：

    ```shell
    james@ubuntu:~/tmp$ jcmd Temp VM.version
    49343:
    Java HotSpot(TM) 64-Bit Server VM version 25.161-b12
    JDK 8.0_161
    ```

    `jcmd <process id/main class> VM.system_properties`用于显示系统参数

    ```shell
    james@ubuntu:~/tmp$ jcmd Temp VM.system_properties
    49343:
    #Wed Dec 05 03:09:19 PST 2018
    java.runtime.name=Java(TM) SE Runtime Environment
    sun.boot.library.path=/usr/lib/jvm/java-8-oracle/jre/lib/amd64
    java.vm.version=25.161-b12
    java.vm.vendor=Oracle Corporation
    ...
    ```

    `jcmd <process id/main class> VM.flags`用于显示JVM启动参数
    
    ```shell
    james@ubuntu:~/tmp$ jcmd Temp VM.flags
    49343:
    -XX:CICompilerCount=3 -XX:InitialHeapSize=16777216 -XX:MaxHeapSize=253755392 -XX:MaxNewSize=84541440 -XX:MinHeapDeltaBytes=196608 -XX:NewSize=5570560 -XX:OldSize=11206656 -XX:+UseCompressedClassPointers -XX:+UseCompressedOops -XX:+UseFastUnorderedTimeStamps 
    ```

    `jcmd <process id/main class> VM.uptime`显示JVM运行时间

    ```shell
    james@ubuntu:~/tmp$ jcmd Temp VM.uptime
    49343:
    28063.172 s
    ```

## jps

jps用来显示服务器上用户有权限访问的所有JVM进程。

```shell
james@ubuntu:~/tmp$ jps
60037 Jps
49343 Temp
```

`jps -v`显示传递给JVM的参数：

```shell
james@ubuntu:~/tmp$ jps -v
60054 Jps -Dapplication.home=/usr/lib/jvm/java-8-oracle -Xms8m
49343 Temp
```

`jps -l`显示main所在类的完整包名：

```shell
james@ubuntu:~/tmp$ jps -l
60105 sun.tools.jps.Jps
49343 Temp
```

`jps -m`显示传递给main方法的参数：
```shell
james@ubuntu:~/tmp$ jps -m
60167 Jps -m
49343 Temp
```
## jhat

jhat用于分析hprof格式的dump文件，运行`jhat dump.hprof`，然后它会启动一个Web服务器，让你浏览dump文件，默认是在7000端口。由于目前已经有更好的工具（比如MAT），jhat在JDK9中已正式被移除，在此不再介绍。

## 第三方工具

1. 阿里的[Arthas](https://github.com/alibaba/arthas)
2. [btrace](https://github.com/btraceio/btrace)
3. 谷歌的[gperftools](https://github.com/gperftools/gperftools)
4. Java字节码操作框架[ASM](https://asm.ow2.io/)

# 系统级分析工具

## vmstat

vmstat命令用来报告系统的CPU、内存和IO相关的信息，主要用于评估系统计算资源的负载。用法`vmstat 1`，1表示每隔1秒取样。输出样例如下：

```shell
james@ubuntu:~/tmp$ vmstat 1
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id  wa 
 0  0 594912 146044  10980 259764    2    3    18     9   56   44  0  0 99   0 
 0  0 594912 146044  10980 259848    0    0     0     0  306  564  0  0 100  0 
 0  0 594912 146044  10980 259848    0    0     0     0  272  526  0  0 100  0 
```

第一行各指标为系统启动以来的平均值，后续每隔指定时间输出实时结果。下面分别对上述输出的五个部分(procs, cpu, memory, swap, io)进行说明。

1. CPU调度队列长度(procs)

    - r列表示的是处于运行状态或者在运行队列中的进程数；
    - b列表示阻塞状态的线程数（比如等待磁盘IO）。

    这两个指标需要结合CPU逻辑核数来看。可以使用如下命令查看CPU核数。

    ```shell
    cat /proc/cpuinfo | grep processor | wc -l
    ```

    如果r值大于CPU的逻辑核数，那么表示可能存在CPU资源瓶颈（比如，并发量过大），线程等待被分配CPU时间。如果b值较大，则表示IO较慢。

2. CPU使用率(cpu)

    - us表示用户态CPU时间百分比（即CPU花在执行用户非系统调用上的时间比例）
    - sy表示内核态CPU时间百分比
    - id表示CPU空闲时间百分比
    - wa表示CPU用在IO等待上的时间百分比

    服务器CPU实际使用率是us+sy，如果us+sy保持在80%以上，可以认为CPU资源已经接近极限了。如果sy百分比较高，说明服务器上的程序正在进行大量系统调用，而不是处理业务逻辑代码；通常us应该高于sy，如果反过来，则说明当前程序花在处理实际业务逻辑代码上的工作量太低。

    服务器CPU实际空闲时间是id+wa，如果wa比较高，说明有CPU正在等待IO，不一定表示存在IO问题，只能说明有CPU资源没有被充分利用；反过来wa等于0不代表没有任何IO发生，可能是所有的CPU资源都忙于处理其它线程，不一定表示不存在IO问题。如果id比较高，表示服务器压力很低，通常表示不存在CPU或IO问题。



2. 内存信息Memory和swap
    
    - swpd表示虚拟内存（交换空间）使用量
    - free表示空闲内存量
    - buff表示用于缓冲区的内存大小
    - cache表示用于缓存的内存大小
    - si表示每秒内存页面从磁盘（虚拟内存）换入到内存的数量
    - so表示每秒内存页面从内存换出到磁盘（虚拟内存）的数量
   
   需要关注free，si和so的值的变化，当free很低时，系统会把最近不适用的内存换出到磁盘，这时候so会上升。理想状态下，si和so都应该在大部分时间保持0.

3. IO

   - bi表示每秒从IO设备读入的块
   - bo表示每秒写入到IO设备的块

4. System

    - in表示每秒钟中断发生次数
    - cs表示每秒钟上下文切换发生次数（CPU切换正在运行的线程的次数）


## iostat

iostat用于显示磁盘IO和CPU使用率。通常使用参数为`iostat -xcmt n`，其中n表示每个n秒打印一份报告。除了类似vmstat的CPU使用率外，iostat的报告比较直观的是磁盘%util指标，反映磁盘的繁忙程度。

```shell
james@ubuntu:~/tmp$ iostat -xcmt 5
Linux 4.15.0-34-generic (ubuntu) 	12/07/2018 	_x86_64_	(4 CPU)

12/07/2018 08:11:03 AM
avg-cpu:  %user   %nice %system %iowait  %steal   %idle
           0.16    0.01    0.26    0.04    0.00   99.54

Device:         rrqm/s   wrqm/s     r/s     w/s    rMB/s    wMB/s avgrq-sz avgqu-sz   await r_await w_await  svctm  %util
sda               1.10     2.88    3.67    0.69     0.07     0.03    45.40     0.02    4.73    1.05   24.42   0.38   0.16
```

## pmap

pmap报告进程的虚拟内存地址映射情况，可以用来查看本地代码的内存使用，用于内存泄漏分析。

```shell
james@ubuntu:~/tmp$ pmap -x 74934 | more
74934:   java Temp
Address           Kbytes     RSS   Dirty Mode  Mapping
0000000000400000       4       4       0 r-x-- java
0000000000400000       0       0       0 r-x-- java
0000000000600000       4       4       4 rw--- java
0000000000600000       0       0       0 rw--- java
0000000001e26000     132      12      12 rw---   [ anon ]
0000000001e26000       0       0       0 rw---   [ anon ]
00000000f0e00000    5440    4688    4688 rw---   [ anon ]
00000000f0e00000       0       0       0 rw---   [ anon ]
00000000f1350000   77120       0       0 -----   [ anon ]
...
00007f6fcc5fc000       0       0       0 rw--- ld-2.23.so
00007f6fcc5fd000       4       4       4 rw---   [ anon ]
00007f6fcc5fd000       0       0       0 rw---   [ anon ]
00007ffd6d88f000     132      36      36 rw---   [ stack ]
00007ffd6d88f000       0       0       0 rw---   [ stack ]
00007ffd6d8d2000      12       0       0 r----   [ anon ]
00007ffd6d8d2000       0       0       0 r----   [ anon ]
00007ffd6d8d5000       8       4       0 r-x--   [ anon ]
00007ffd6d8d5000       0       0       0 r-x--   [ anon ]
ffffffffff600000       4       0       0 r-x--   [ anon ]
ffffffffff600000       0       0       0 r-x--   [ anon ]
---------------- ------- ------- ------- 
total kB         2277132   30080   13764
```

pmap没有提供内存地址的区间，而是提供了映射占用的空间。

1. 第二列表示的是虚拟内存占用（包括交换空间），对应于top命令中的VIRT部分。
2. 第三列是实际物理内存占用，对应于top命令中的RES部分。
3. 第四列是脏内存大小，表示被修改过的部分。
4. 第五列表示的该映射是否可读，是否可写，是否可执行等。
5. 第六列表示的是映射类型，pmap这里会显示三种，一种是anon（表示anonymous）纯RAM内存，不对应具体磁盘上的文件或者swap空间；一种stack；另一种是对应于磁盘文件映射，会显示具体的文件名字。

关于Linux内存，[这篇](https://techtalk.intersec.com/2013/07/memory-part-2-understanding-process-memory/)文章讲的比较详细。对于更广泛意义上的现代操作系统内存，可以参考[这篇](https://akkadia.org/drepper/cpumemory.pdf)文章。


# 可视化分析工具

## JConsole

JConsole可以对内存、CPU、线程、类加载情况的情况进行动态可视化，并提供JVM和系统信息的查看。

1. JConsole查看的线程信息和jstack或jcmd功能差不多，包括线程跟踪信息和死锁检测等。

    {{% figure class="center" src="/images/heap-dump-analysis/jconsole-threads.PNG" alt="Threads info in JConsole" title="Threads info in JConsole"  %}}

2. JConsole可以查看不同区域的内存使用情况，包括堆内存（JVM用于分配新的对象的内存区域）和非堆内存（方法区以及JVM内部使用的内存），以及更加细分的老年代、Eden、Survivor区域等等。

    {{% figure class="center" src="/images/heap-dump-analysis/jconsole-mem.PNG" alt="Memory info in JConsole" title="Memory info in JConsole"  %}}


3. dump heap

    打开MBeans页面，在左侧的com.sun.management下面找到HotSpotDiagnostics->Operation，在右侧z好到p0和p1两个参数。 

    {{% figure class="center" src="/images/heap-dump-analysis/jconsole-heap-dump.PNG" alt="Heap dump using JConsole" title="Heap dump using JConsole"  %}}

    p0为dump文件输出位置，p1为true的时候会在dump前执行一次Full GC。

## Java Visual VM 

Java Visual VM (JVisualVM) 自JDK6u23开始到JDK8为止为Oracle JDK的一部分, JDK9及之后作为独立[项目](https://visualvm.github.io/)。基本功能如下：

1. 基本信息：JVM版本、JVM参数和系统属性；
    
    {{% figure class="center" src="/images/heap-dump-analysis/jvisuialvm-summary.PNG" alt="JVisualVM Summary" title="JVisualVM Summary"  %}}

2. 对内存、CPU、线程、类加载情况的情况进行动态可视化，并提供垃圾回收，堆dump操作；

    {{% figure class="center" src="/images/heap-dump-analysis/jvisuialvm-monitor.PNG" alt="JVisualVM Monitor" title="JVisualVM Monitor"  %}}

3. 对线程栈的运行情况进行动态可视化，并提供线程dump操作；

    {{% figure class="center" src="/images/heap-dump-analysis/jvisuialvm-threads.PNG" alt="JVisualVM Threads" title="JVisualVM Threads"  %}}

    右键选择应用，然后选择heap dump，会产生Java堆dump。JVisualVM可以对堆进行一些简单的分析，但建议对产生的dump另存为，然后使用MAT工具进行分析。

    {{% figure class="center" src="/images/heap-dump-analysis/jvisualvm-heap-dump.PNG" alt="Heap dump using JVisualVM" title="Heap dump using JVisualVM"  %}}

4. 浏览线程dump和堆dump文件；

    {{% figure class="center" src="/images/heap-dump-analysis/jvisualvm-thread-dump.PNG" alt="JVisualVM Threads Dump" title="JVisualVM Threads Dump"  %}}
 
    {{% figure class="center" src="/images/heap-dump-analysis/jvisuialvm-heap-dump.PNG" alt="JVisualVM Heap Dump" title="JVisualVM Heap Dump"  %}}

另外，VisualVM还提供一些[插件](https://visualvm.github.io/plugins.html)：

1. MBeans浏览器；
2. OQL Syntax Support
3. Visual GC Plugin
4. Kill Application
5. Tracer
6. Startup Profiler
7. ...

JVisualVM包含了JConsole提供的全部功能，并且还有提供采样器(Sampler)和性能分析器(Profiler)。两者都能对方法的执行时间（CPU）和对象的内存占用进行统计分析（如下图），但是两者原理不同。

{{% figure class="center" src="/images/heap-dump-analysis/jvisualvm-sampler.PNG" alt="JVisualVM Sampler" title="JVisualVM Sampler"  %}}
 
{{% figure class="center" src="/images/heap-dump-analysis/jvisualvm-profiler.PNG" alt="JVisualVM Profiler" title="JVisualVM Profiler"  %}}

- 采样器是定时对线程栈或者堆进行快照（取样），然后从样本中进行分析，这种方式对应用的性能影响较小，通常在还不清楚具体问题的时候进行盲分析，比如对线程栈的1000取样中有100次在执行某个方法等等；
- 性能分析器则是通过修改应用的字节码来记录每个方法的每次调用，以及每次调用花了多久，这种方式对性能有一定影响，通常是在我们清楚需要分析的问题的情况下（比如分析某个类的调用）进行详细的分析时使用。

## 其它(收费)工具

1. Java Flight Recorder

    JDK7u40以后自带的一个工具，但是在生成上使用的话，需要Oracle的商业许可。JFR可以持续的记录（或者记录一段时间）的JVM运行信息，包括CPU、内存、GC、线程、IO事件等，并且配合Java Mission Control可以对其记录结果进行可视化分析。

    详细介绍可以参考Oracle[文档](https://docs.oracle.com/en/java/javase/11/troubleshoot/diagnostic-tools.html#GUID-89C133E9-9E49-40F5-AD61-7A2FE89B1F78)

    {{% figure class="center" src="/images/heap-dump-analysis/jfr.png" alt="Java Flight Recorder" title="Java Flight Recorder"  %}}

2. JProfiler 

    {{% figure class="center" src="/images/heap-dump-analysis/jprofiler.png" alt="JProfiler" title="JProfiler"  %}}

    JProfiler是仅次于JVisualVM的最受欢迎的性能分析器，不过是收费的。同样包含JVisualVM大部分功能，界面更加好用一点。

3. NetBeans Profiler 

    {{% figure class="center" src="/images/heap-dump-analysis/netbeans.png" alt="Netbeans" title="Netbeans"  %}}

    NetBeans Profiler是NetBeans IDE插件（不收费），它不能单独运行（你不可能把它带上生成把^-^），功能上和JVisualVM差不多。



## MAT

MAT即Eclipse Memory Analyzer Tool是一个Java堆分析工具，主要用于诊断内存泄漏和高内存占用问题。

本节的主要参考了Eclipse的[官方文档](https://help.eclipse.org)和其它[参考资料](#参考资料)。

下面我们先介绍一些基本概念。

### Heap Dump及其获取

Heap Dump是Java程序在某一时刻的内存快照。通常在dump前会执行一次full GC。典型的dump包括以下内容（但取决于具体的dump格式）：

1. 所有的对象： 类、字段、基本变量和引用等；
2. 所有的类：类加载器、名称、父类和静态字段等；
3. GC Roots；
4. 线程栈和每一栈帧中的本地变量。

MAT默认支持Oracle JVM的dump文件HPROF格式。通过安装[插件](https://developer.ibm.com/javasdk/tools)可以支持IBM Jvm的portable heap dump (PHD)文件。关于针对IBM产品的MAT的更多支持可以参考[这篇](https://www.ibm.com/developerworks/cn/websphere/techjournal/1103_supauth/1103_supauth.html)文章。

除了在VM崩溃的时候获取dump，主动获取dump的方法有：

1. [jcmd](#jcmd)
2. [jmap](#jmap)
3. [JVisualVM](#java-visual-vm)
4. [JConsole](#jconsole)
5. IBM Application WebSphere Server管理控制台
    
    在WAS控制台中选择`Troubleshooting(故障诊断)->Java dumps and cores(Java转存和核心)`，然后在右边选择server名字，可以选择“转存堆”、“Java核心”或者“系统转存”

### 对象在内存中的表示

> The Java Virtual Machine does not mandate any particular internal structure for objects. -- The Java Virtual Machine Specification Chapter 2.7

JVM规范并没有对对象在内存中的布局做出规定，各JVM实现可以自行决定。其中比较常见的Hotspot虚拟机的对象在内存中的结构包括：

1. 一个Mark Word（长度为一个字，即32位JVM上的长度为32位，64位JVM则为64位）；
2. 一个Klass指针，指向对象的类（指针长度也为一个字，但是当64位JVM开启UseCompressedOops时，指针长度可以为32位，Oracle JDK 6 update 23版本以后默认开启）；
3. 如果是一个数组，还有一个32位的数据来表示长度；
4. 对象的成员变量。如果是基本类型，int为4 bytes，short为2 bytes等；如果是引用类型，每一个引用存放的都是一个指针；
5. padding。用于内存对齐，将对象的大小填充到8的倍数。

我们以下图T4CPreparedStatement对象的bindIndicators的成员变量为例。该变量是一个`short[39]`数组。

{{% figure class="center" src="/images/heap-dump-analysis/MemoryRepreserntation.png" alt="MAT Dominator Tree" title="MAT Dominator Tree"  %}}

根据上面的分析，bindIndicators的内存布局如下：

{{% figure class="center" src="/images/heap-dump-analysis/MemoryRepreserntation2.png" alt="short[39]数组的内存布局" title="short[39]数组的内存布局"  %}}

由于我们的JDK是1.6.0_45，默认开启了UseCompressedOops，所以指针的长度为32位。一个`short[39]`由以下几部分组成：

1. 对象头部Mark Word（8字节） + 类指针（4字节） + 数组大小（4字节）共16字节；
2. 数据本身占据了39x2共58字节；
3. 最后为了对齐，padding补上了2字节。

总共96字节，和图中Shallow Heap一致。

### GC Roots

GC Roots是那些可以被堆外直接访问的对象，GC算法在扫描存活对象的起点，包括：

- System Class: system/bootstrap class loader加载的类。比如rt.jar中的东西。
- JNI Local: 本地代码中的本地变量。
- JNI Global: 本地代码中的全局变量。
- Thread Block: 当前活跃线程引用的对象。
- Thread: 已启动并且尚未停止的线程。
- Busy Monitor: 所有调用了wait()或者notify()的对象，或者被synchronized的对象。
- Java Local: 线程栈帧中的输入参数或者本地创建的对象。
- Native Stack: 本地代码中的输入或输出参数。
- Finalizable: 进入finalizer队列的对象。
- Unfinalized: 重写了finalize方法，但是还没有被调用过的，并且还没有在finalizer队列里的对象。
- ...

### Shallow Heap vs. Retained Heap

一个对象的shallow heap指的是该对象占用的内存大小，包括对象头和对象成员变量等，但不包括被引用对象的大小（参考下文“对象在内存中的表示”）。

一个对象的retained heap指的是当这个对象被GC回收掉的时候，所有被回收掉的对象（包括它自己）的shallow heap的总和。换句话说retailed heap指的是一个对象被回收后能释放的内存大小。

比如，假设下图中A和B为GC Roots，当我们把C回收掉的时候，C、E、F、G和H都会被回收掉，因此C的retained size是C、E、F、G和H的shallow size的总和。

{{% figure class="center" src="/images/heap-dump-analysis/RetainedSet.png" alt="Retained Set example" title="Retained Set example"  %}}

### Dominator Tree

如果所有从GC Roots出发到达对象y的路径都必需经过对象x，那么我们说x是y的**支配者(Dominator)**。换句话说，如果x被回收掉了，y就可以被回收掉了。

如果x是与对象y最近的支配者，那么我们称x是y的**直接支配者(Immediate Dominator)**。

**Dominator Tree(支配树)**是从对象引用图转换过来的。在支配树中，每一个节点代表的对象都是它子节点的直接支配者，所以可以很清楚地识别依赖关系。

支配树的主要用途是为了方便查找那些占用了大量retained heap的对象以及存活对象的依赖关系。

下面给了一个具体的例子，左图为对象引用关系图，右图为由左图生成的支配树。

{{% figure class="center" src="/images/heap-dump-analysis/mat-dominator-tree.PNG" alt="Dominator Tree Example" title="Dominator Tree Example [origin: Eclipse Help Document]"  %}}

我们逐个节点来分析：

1. A和B节点：直接被GC Roots引用，因此它没有支配者；
2. C节点：从GC Roots出发没有必经的节点，因此它也没有支配者；
3. D和E节点：所有GC Roots出发的路径都必需通过C节点，但A和B可以是其中任意一个，所以它的(直接)支配者是C；
4. F节点：抵达F节点的路径都要经过D节点，因此D是它的(直接)支配者；
5. G节点：同F节点，最近的必经节点是E，因此E是它的直接支配者；
6. H节点：抵达H节点的路径要么是通过C->D->F->H，要么是C->E->G->H，最近的必经节点是C，所以C是它的直接支配者。

支配树有以下几个特点：

1. x节点的子树中的所有节点构成了x的retained set；
2. 如果x节点是y节点的直接支配者，那么x节点的直接支配者也是y节点的支配者，以此类推；
3. 支配树中的边不代表对象图中的引用关系。

主要概念介绍完了。下面来看下具体使用方法。

### 疑似泄漏报告

如果dump很大，MAT也会需要较大的内存来打开并解析它。当MAT完成加载以后，会显示一份疑似泄漏报告。这份报告是MAT自动分析的结论，下图是一个真实的生产dump文件的泄漏报告。

{{% figure class="center" src="/images/heap-dump-analysis/mat-leak-suspect.png" alt="MAT Leak Suspects" title="MAT Leak Suspects"  %}}

其中，MAT认为有两处泄漏，分别占据了1.9GB内存和319.2MB内存。继续往下看，MAT会指出这两处泄漏是什么：

{{% figure class="center" src="/images/heap-dump-analysis/mat-leak-1.png" alt="MAT Leak Suspects 1" title="MAT Leak Suspects 1"  %}}

第一处疑似泄漏是57个oracle.jdbc.driver.T4CPreparedStatement对象。

{{% figure class="center" src="/images/heap-dump-analysis/mat-leak-2.png" alt="MAT Leak Suspects 2" title="MAT Leak Suspects 2"  %}}

第二处疑似泄漏是87个oracle.jdbc.driver.T4CConnection对象。

### 查看对象直方图

选择导航栏中第二个图标（如下图红框中所示）。对象直方图是按照类为维度来统计的，对象数量、shallow heap和retained heap。

{{% figure class="center" src="/images/heap-dump-analysis/mat-histogram.png" alt="MAT Histogram" title="MAT Histogram"  %}}

上图中各类按照其实例化的对象的retained heap从大到小排序，第一个T4CPreparedStatement有508,211个对象实例，占据了400多MB内存，它的retained heap超过2G。

### 查看最大支配对象/支配类

选择导航栏中第三个图标（如下图红框中所示）。支配列表按照对象占据的retained heap从高到低列出了全部支配对象，显示对象的shallow heap，retained heap以及retained heap占堆的百分比。

{{% figure class="center" src="/images/heap-dump-analysis/mat-dt-objects.png" alt="MAT Dominator Tree (Objects)" title="MAT Dominator Tree (Objects)"  %}}

我们可以选择按照类来分组展示支配图，操作如下图所示。

{{% figure class="center" src="/images/heap-dump-analysis/mat-dt-grouping.png" alt="MAT Dominator Tree (Grouping by Classes)" title="MAT Dominator Tree (Grouping by Classes)"  %}}

{{% figure class="center" src="/images/heap-dump-analysis/mat-dt-classes.png" alt="MAT Dominator Tree (Classes)" title="MAT Dominator Tree (Classes)"  %}}

### 线程及其栈帧的内存

选择导航栏中第五个图标（如下图红框中所示）。线程栈信息、线程本地变量及其占用内存空间。

{{% figure class="center" src="/images/heap-dump-analysis/mat-threads.png" alt="MAT Threads" title="MAT Threads"  %}}

### 查询堆中的对象(OQL)

MAT支持对象查询语言(OQL)来检索堆中的对象。OQL是一个类似SQL的语言，它把类（或对象）当成表，字段当作是列。基本语法如下：

```sql
SELECT * FROM [ INSTANCEOF ]	<class_name> [ WHERE <filter-expression>]
```

比如，要查询所有T4CPreparedStatement对象的sqlObject成员对象的originalSql字符串。在导航栏第四个按钮（如下图）打开OQL页面，输出查询语句（如下），然后点击红色的感叹号按钮（或按F5）执行。

```sql
SELECT o.sqlObject.originalSql.toString() FROM INSTANCEOF "oracle.jdbc.driver.T4CPreparedStatement" o WHERE (o.sqlObject.originalSql != null)
```

{{% figure class="center" src="/images/heap-dump-analysis/mat-oql-1.png" alt="MAT OQL" title="MAT OQL"  %}}


关于OQL的具体语法，请参考[Eclipse MAT OQL Syntax](https://help.eclipse.org/neon/topic/org.eclipse.mat.ui.help/reference/oqlsyntax.html?cp=53_4_2)。
				

# 面向更复杂的业务场景

对于分布式应用等更复杂的业务场景，需要更复杂的监控工具。

1. Transaction Profilers (交易性能分析工具)类工具
   
   用于跟踪分布式应用架构上的每一笔业务交易的流程和执行情况，识别每一个流程节点的延迟并进行对比分析。比如XRebel和Stackify Prefix。

2. 应用性能监控工具(APM)

   用于两方面的监控，一方面是最终用户的使用体验，比如高负载情况下的平均响应时间；另一方面是应用的计算资源，确保在高负载下应用有足够的计算资源以及识别性能瓶颈。APM工具通常比较昂贵，比如New Relic， AppDynamics和Stackify Retrace等

# 统计

2015年ZeroTurnaround Inc.对1562名开发者作了Java性能分析相关的问卷调研，下面是几个有趣结果。

1. 工具的选择
    
    {{% figure class="center" src="/images/heap-dump-analysis/dpr-tools.PNG" alt="DPR Tools" title="DPR Tools"  %}}

2. 使用工具的数量

    {{% figure class="center" src="/images/heap-dump-analysis/dpr-tools-count.PNG" alt="DPR Tool Count" title="DPR Tool Count"  %}}

3. 性能问题的根源

    {{% figure class="center" src="/images/heap-dump-analysis/dpr-issues.PNG" alt="DPR Causes" title="DPR Causes"  %}}


# 参考资料

1. Eclipse[帮助文档](https://help.eclipse.org)。
2. Eclipse Memory Analyzer [Wiki页面](https://wiki.eclipse.org/MemoryAnalyzer)。
3. ZeroTurnaround - [Developer Productivity Report 2015](https://zeroturnaround.com/rebellabs/top-5-java-profilers-revealed-real-world-data-with-visualvm-jprofiler-java-mission-control-yourkit-and-custom-tooling/)
4. [JavaSE 11 Troubleshoot Guide](https://docs.oracle.com/en/java/javase/11/troubleshoot/)

