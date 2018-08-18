# 背景

昨天碰到一个很奇怪的轮询任务卡住的问题。轮询调度框架会按照数据库里配置，周期性地定时启动一些任务。每个定时任务都是一个普通的Java程序，它处理一个周期内累积的业务请求。虽然每次只处理数量非常有限的数百笔业务，但是每笔业务的逻辑都相对复杂，相当于一个时间很短（通常几分钟）的批处理程序。正常情况下，一个任务在运行的时候会将它执行的SQL、读取的文件以及访问的接口信息打印到日志里。

问题是有一个任务在执行一段时间后突然不再处理业务，停止输出日志，但没有报错，进程也没有退出。

<!--more-->

# 问题分析

接到问题的时候，先是想把堆栈信息打出来看看，但是因为生产上没有JDK，所以先查了日志和系统状态：日志上面没有异常，如果是接口调用，最终会超时，不可能一直卡住；而且系统资源很空闲，CPU基本是闲置的，内存、IO压力很低。因此，第一感觉是什么东西锁住了，但一问运维的同事又说是单线程应用，所以感觉很奇怪，奈何没有JDK，堆栈没法看。

生产服务器上装东西（包括JDK）很麻烦，要走一堆流程，但是应急处理时修改启动脚本还是合规的。所以我想远程连上去看看，就给轮询任务的启动脚本的JVM参数里面配了JMX:

```property
-Dcom.sun.management.jmxremote.port=9000
-Dcom.sun.management.jmxremote.ssl=false
-Dcom.sun.management.jmxremote.authenticate=false
```

我特意找了一个没有在用的端口，但是一启动发现报端口已被使用的异常。再换了几个还是一样，想来应该是防火墙在搞鬼。修改网络规则又有很麻烦的一堆流程，所以想办法找了一个应用服务器常用但是没在用的端口，一试启动果然没报错。

接着在本地开启jconsole和jvisualvm，连上生产服务器，过一会问题重现了。下面是堆使用情况记录：

{{% figure class="center" src="/images/java-console-printing/heap-usage.png" alt="堆使用情况记录" title="堆使用情况记录" %}}

第一段比较密集的GC是在处理第一种场景的业务（这里没有问题），到16:12左右进入了第二段的另一种场景，但是没过几分钟卡住了，这时候堆上对象的创建明显变地很少，GC频率下降。

下面是主线程调用栈（删改了部分内容），隔个几分钟重新dump还是一样。

```txt
2018-08-15 17:44:02
JVM Info...

"main" - Thread t@1
   java.lang.Thread.State: RUNNABLE
	at java.io.FileOutputStream.writeBytes(Native Method)
	at java.io.FileOutputStream.write(FileOutputStream.java:277)
	at java.io.BufferedOutputStream.flushBuffer(BufferedOutputStream.java:76)
	at java.io.BufferedOutputStream.flush(BufferedOutputStream.java:134)
	- locked <6c566c56> (a java.io.BufferedOutputStream)
	at java.io.PrintStream.write(PrintStream.java:452)
	- locked <74b874b8> (a java.io.PrintStream)
	at sun.nio.cs.StreamEncoder$CharsetSE.writeBytes(StreamEncoder.java:355)
	at sun.nio.cs.StreamEncoder$CharsetSE.implFlushBuffer(StreamEncoder.java:425)
	at sun.nio.cs.StreamEncoder.flushBuffer(StreamEncoder.java:138)
	- locked <74ce74ce> (a java.io.OutputStreamWriter)
	at java.io.OutputStreamWriter.flushBuffer(OutputStreamWriter.java:187)
	at java.io.PrintStream.write(PrintStream.java:501)
	- locked <74b874b8> (a java.io.PrintStream)
	at java.io.PrintStream.print(PrintStream.java:643)
	at java.io.PrintStream.append(PrintStream.java:1039)
	at java.io.PrintStream.append(PrintStream.java:51)
	at java.lang.StackTraceElement.appendTo(StackTraceElement.java:180)
	at java.lang.Throwable.appendTo(Throwable.java:305)
	at java.lang.Throwable.printStackTrace(Throwable.java:332)
	at java.lang.Throwable.printStackTrace(Throwable.java:212)
	at java.lang.Throwable.printStackTrace(Throwable.java:163)
	at com.xxx.service.XXXService.someMethod(someMethod.java:285)
	at ...
```

似乎是卡在了奇怪的地方。`someMethod`(实际上不叫这个名字，只是把和业务相关的名字都改了一下，下同)在try...catch块里new一个对象的时候抛出了一个自定义异常:

```java
public void someMethod(){

    try{
        // ...
        SomeObject object = new SomeObject(); // <-报错
        // ...
    }catch(Exception e){
        e.printStackTrace();
    }
}
```

虽然在SomeObject的构造方法里面会抛出异常的设计让人感觉很不舒服，但我注意到这个代码还有一个不合理的地方：轮询任务里面打印日志有专门的类来处理，像下面这样，使用原生的日志打印很少见：

```java
getLogger().error("对象new不出来了^-^");
```

尽管如此，`printStackTrace`也不应该卡住。

再来看下线程状态，没有线程处于`BLOCKED`状态，而卡住的主线程的状态是`RUNNABLE`，但文档里说：

> Thread state for a runnable thread. A thread in the runnable state is executing in the Java virtual machine but it **may be waiting for other resources** from the operating system such as processor. 

所以即使是RUNNABLE的，也可能处于等待某些资源的状态，可是这个打印报错栈的方法到底在等待什么呢？不仅程序卡住了，现在脑子也卡住了。

根据运维同事反馈，在终端上手动启动那个Java程序没有问题，但是轮询调度启动有时候就会卡住，但是两者启动方式都是调用同一个Shell脚本。这个就很有意思了，同一个Shell脚本启动的，能有什么差别呢？手动输入shell命令启动该脚本，所有日志除了打印到屏幕上，还会打印到文件里；调度起的只会往文件里打印输出。然后再翻一下日志，没有发现`printStackTrace`的输出，难道说它只打印到了终端上，而调度启动的任务没有相应的终端去消费输入流导致输入流满了，然后就...卡住了？

接着去翻了调度框架的代码，它用的是`Runtime.getRuntime.exec(...)`来调的shell脚本：

```java

Runtime run = null;
Process p = null;
BufferedInputStream in = null;
BufferedReader br = null;

try{

    Runtime run = Runtime.getRuntime();
    p = run.exec( getCommand());
    in = new BufferedInputStream( p.getInputStream());
    br = new BufferedReader( new InputStreamReader( in));

    String s = null;
    while( (s = br.readLine()) != null){
        getLogger().trace( s);
    }

} catch( IOException){
    e.printStackTrace();
} finally{
    if( br != null){
        try{
            br.close();
        } catch (IOException e){
            e.printStackTrace();
        }
    }

    if( p != null) {
        p.destory();
    }
}
```

显然它只读了getInputSteam方法返回的输入流，这个输入流是被调用程序的标准输出流；而还有一个getErrorStream方法返回的被调用程序的错误输出流没有被处理。而`printStackTrace`方法是打印到错误流里的。问题找到了。在这个程序里面，只是碰巧卡在了`printStackTrace`，任何输入到错误流的数据（比如`Systen.err.print("...")`），最终都会导致程序卡住。

# 总结

这个问题之所以难定位，

- 一是主观上之前没有碰到过类似情况，经验不足，以后要记得`Runtime.getRuntime().exec()`的这个坑；
- 二是直接引起问题的代码看上去非常的正常，真正造成问题的代码隐藏在背后，甚至不在同一个程序里面，所以在定位问题的时候还是要多想一层。










