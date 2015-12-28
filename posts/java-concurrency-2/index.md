<!-- 
.. title: 《Java并发实践》总结二：结构化并发应用程序
.. slug: java-concurrency-2
.. date: 2015-12-28 08:10:20 UTC
.. tags: Java,Concurrency
.. category: 
.. link: 
.. description: 
.. type: text
-->

# 1 Executor框架

任务是一个逻辑执行单元，而线程是使任务异步执行的机制。串行执行会降低响应性和吞吐量；每个任务都分配一个线程会造成很大开销也不利于资源管理。

该框架包括一个灵活的线程池，提供了不同类型的任务的执行策略，并将任务提交过程和执行过程解耦，用Runnable来表示一个任务。此外Executor框架还提供了对生命周期的支持，以及统计信息的收集、应用程序管理机制和性能监视等机制。

执行策略定义了任务执行的"what, where, when, how"等方面。比如在什么线程中执行任务，按什么顺序执行，多少个任务可以并发执行，队列了可以有多少个任务在等待，在任务执行之前和之后应该进行哪些操作，如果要拒绝一个任务，应该选择哪一个？等等

当需要灵活的执行策略时，用Executor框架来代替手动编写Thread。

## 1.1 Executor

Executor接口如下，它是java.util.concurrent异步执行框架的基础。

```
public interface Executor{
    void execute(Runnable command);
}
```

Executor基于生产者消费者模式，提交任务的线程相当于生产者，执行任务的线程相当于消费者

## 1.2 ExecutorService

ExecutorService接口扩展了Executor，提供了生命周期的支持和提交任务的方法。ThreadPoolExecutor实现了这个接口，但一般通过Executors的工厂方法来创建和配置线程池。

### 1.2.1 线程池

线程池与任务队列密切相关，工作线程从任务队列里获取一个任务，执行完成任务，返回线程池，等待下一个任务。

线程池通过重用现有的线程而不是对每个任务创建新的线程来，1. 减少线程创建和销毁时的开销; 2. 当请求到达时，工作线程通常已经存在，提高了响应性。

Executors的工厂方法可以配置很多种线程池，比如
1. newFixedThreadPool: 固定大小的线程池，每提交一个任务就创建一个线程，直到达到指定的最大数量；
2. newCachedThreadPool: 一个可缓存的线程池，当线程池规模超过需要处理的任务数量时，将回收空闲线程，当需要增加时，将添加新的线程，规模不存在限制;
3. newSingleThreadExecutor: 创建单线程的Executor，确保任务依照队列中的顺序执行；
4. NewScheduledThreadPool: 固定长度的线程池，通过延时或定时的方法执行任务。

### 1.2.2 生命周期支持

因为向Executor提交的任务是异步执行，有一些可能已经完成，一些在运行，一些在等待，所以关闭ExecutorService提供了一些方法来关闭Executor。

ExecutorService有三种状态，运行、关闭和已终止。在创建后它即处于运行状态。shutdown方法执行后，它将不再接受新的任务，同时等待已提交的（包括还在等待的）任务执行完成；shudownNow方法将尝试取消所有运行的任务，不再启动等待的任务。ExecutorService关闭后，提交的任务将由Rejected execution handler处理，它会抛弃任务，或者抛出一个RejectedExecutionException。等所有任务都完成后，ExecutorService进入已停止状态，可以调用awaitTermination来等待ExecutorService停止，或者通过isTerminated来轮训。

比如下面的一个web服务器：
```
class LifecycleWebServer {
    private final ExecutorService exec = ...;
      
    public void start() throws IOException {
        ServerSocket socket = new ServerSocket(80);
        while (!exec.isShutdown()) {
            try {
                final Socket conn = socket.accept();
                exec.execute(new Runnable() {
                    public void run() { handleRequest(conn); }
                });
             } catch (RejectedExecutionException e) {
                if (!exec.isShutdown())
                    log("task submission rejected", e);
             }
        }
    }
							     
    public void stop() { exec.shutdown(); }
    
    void handleRequest(Socket connection) {
        Request req = readRequest(connection);
        if (isShutdownRequest(req))
            stop();
        else
            dispatchRequest(req);
    }
}
```

### 1.2.3 任务提交，完成和取消

Exectuor接口的execute方法只能接受Runnable，Runnable没有返回值。而扩展了的ExecutorService添加了submit方法允许提交Callable，Callable的call方法将返回一个值或者抛出异常。

Executor执行的任务有4个生命周期，创建，提交，开始和完成。Future表示一个任务的生命周期。将一个Runnable或者Callable通过submit方法提交给ExecutorService后返回一个Future，这个Future可以用来判断任务是否完成或者取消，以及获取任务的结果或者取消任务。

将Runnable或者Callable提交到ExecutorService的过程包括了一个安全地将Runnable或者Callable从提交线程发布到执行线程的过程；设置Future结果的过程也包括了，将计算结果从执行线程发布到任何通过get获得它的线程。

1. Future的get方法：如果任务已经完成，将立即返回结果或抛出异常；如果没有完成，get将阻塞，如果设置了超时参数，那么在指定时间内仍旧没有完成将抛出TimeoutException，然后再通过Future来取消任务；如果计算过程中抛出异常，该异常被封装成ExecutionException由get重新抛出，通过getCause来获取最初的异常；如果任务被取消，将抛出CancellationException。

2. 使用CompletionService：提交到ExecutorService的任务返回一个Future引用，要知道是否完成任务，需要一个个检查任务；而实现了CompletionService结合了Executor和一个BlockingQueue，把完成的Future<V>放入到一个BlockingQueue，这样就可以只要不断地从一个队列中获取完成的任务就可以了。

    ExecutorCompletionService实现了CompletionSetrvice接口，它的构造函数需要一个Executor，并创建一个BlockingQueue来保存计算完的结果。当提交任务时，该任务会被包装为QueueingFuture（一个Future的子类），然后改写了该子类的done方法，当计算完后，FutureTask的done方法会被调用，结果就被放到了BlockingQueue中国。
 
    摘自Stackoverflow：
    ExecutorService = incoming queue + worker threads
    CompletionService = incoming queue + worker threads + output queue

3. 使用invokeAll：如果有一组任务，一般的做法是一个个提交，获取n个Future，然后一个个获取结果。如果使用invokeAll，它需要一组任务并返回一组Future。它按照参数中任务结合的顺序添加任务，并将返回Future全部添加到返回的集合里。当所有任务都执行完毕后，或者调用线程被中断，或者超时，invokeAll将返回，超时未完成的任务会被取消。所以invokeAll返回的任务要么是已经完成的，要么是被取消的。注意：调用invokeAll本身会导致阻塞，直到所有任务结束或超时，这和CompletionService是不同的。通过后者可以按照任务完成的顺序从BlockingQueue中获取完成的任务。


## 1.3 ScheduledExecutorService

该接口继承了ExecutorService，用于定时或者延时的任务。ScheduledThreadPoolExecutor实现了这个接口，并继承了TreadPoolExecutor。可以通过上文的Executors的工厂方法newScheduledThreadPool来创建该对象或者直接用它的构造函数。

应该用它来替代Timer类，因为在定时的精准性以及异常处理上，ScheduledThreadPoolExecutor更好。

## 1.4 Executor框架的UML图

Image from http://www.uml-diagrams.org/java-7-concurrent-uml-class-diagram-example.html

![ExecutorUML.png](http://www.uml-diagrams.org/examples/java-7-concurrent-executors-uml-class-diagram-example.png " ")

*(未完待续)*


