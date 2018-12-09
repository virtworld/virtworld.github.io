Java 中有三种处理错误的机制：异常(Exception)、断言(Assertion) 和日志(Log)。这里介绍前两种。

# 断言

断言的格式`assert <condition>`或者`assert <condition> : <expression>`

上述两种形式的断言都会对条件进行检测，如果是false，则会抛出AssertionError异常。第二种带有表达式的断言仅仅是把表达式的内容传递给AssertionError以便之后处理，比如打印出来。比如：

```java
int x = 0;
assert x > 0 : "Now you see my assetion message.";
```

为了看到Assertion的报错，我们需要打开虚拟机的参数-ea，上述代码会输出：

<!--more-->

```text
Exception in thread "main" java.lang.AssertionError: Now you see my assetion message.
```

断言只用于在开发测试期间，向代码中插入的一些检测语句，以便定位程序内部错误。断言失败是致命的、不可恢复的错误。但是我们不用在程序发布时移除断言代码，因为默认情况下断言是被禁用的。启用和禁用断言是类加载器的工作，所以我们不需要重新编译代码。启用和禁用（默认）所有断言的虚拟机参数为-ea和-da：
```Shell
java -ea MyApp
java -da MyApp
```

我们也可以启用部分类的断言：
```shell
java -ea:MyClass -ea:com.example... MyApp
```

这里我们启用了MyClass类和com.example包及其子包中所有类的断言。我们也可以禁用部分断言：
```shell
java -ea:... -da:MyClass
```
那些Java系统的类的没有类加载器，需要使用-enablesystemassertion/-esa 参数来启用。

# 异常

所有异常继承自Throwable类。Throwable类下面分为Error和Exception两个子类。

1. Error类，描述了Java运行时系统内部的错误，或者资源耗尽的情况，应用程序不应该抛出这种类的对象。
2. Exception下面又有一个RuntimeException的子类，它描述的是程序错误导致的异常，比如空指针，数组越界等。Exception下的其它子类描述的是非程序错误导致的异常，比如IOException等。
   派生于Error和RuntimeException的类的所有异常称为未检查异常，其它的异常称为已检查异常，编译器确保对于所有已检查异常提供了异常处理器。

这里所有的异常，包括Error和Exception，都是发生在运行时的，不仅仅是RuntimeException。

## 抛出异常

如果一个方法调用了会抛出已检查异常的方法，或这个方法本身会throw出一个已检查异常的，并且该方法并没有捕获这个异常，那么就要在该方法的首部申明所有的这些异常类。未检查的异常要么不可控制（Error），要么应避免发生（RuntimeException）。如下：

```java
public void method() throws IOException {}
```

如果一个方法声明可能会抛出一个异常，它可能会抛出这个异常的对象或该异常子类异常的对象。比如上面的method方法，它可能抛出的是一个IOException也可能是其子类异常，比如FileNotFoundException异常的对象。

如果子类中覆盖了父类的方法，子类中可以抛出更特定的异常，或者根本不抛出异常，但是不能抛出比父类更加通用的异常。这和继承相反，异常范围随着继承变小。
一个出现在父类的方法的异常申明，不一定会出现在其子类的同名方法中。如果将子类向上转型为父类，那么编译器会要求你处理父类的（更大范围的）异常。

如果父类方法中没有抛出任何已检查异常，那么子类也不能抛出任何已检查异常。还有一种情况，如果类A继承了类B并且实现了接口C，而B和C有同名方法分别抛出异常X和Y，那么类A的该方法中X和Y都不可以抛。
因为扩展类方法的异常范围小于等于每一个父类和每一个父接口中该方法声明的异常。但是我们可以把它包装成一个RuntimeException抛出，后面会提到。

这里异常的限制对构造器不起作用。子类构造器可以抛出任意异常而不用关心父类构造器抛出了什么异常，但是因为父类构造器肯定会被子类调用，所以子类构造器的异常声明必需包含父类构造器的异常申明。子类构造器不能捕获父类构造器抛出的异常。

异常本身并不是方法签名的一部分，不能基于异常说明来重载方法。

抛出异常的语法如下，所有标准异常类都有一个默认构造器和一个接收字符串作为参数的构造器：

```java
throw new Exception("Error␣message");
```

我们也可以自定义异常类。自定义异常类最重要的是类的名字，因为类的名字通常已经表述了异常发生的原因。自定义的异常类必需派生自Exception或其子类。一般包含两个构造器，一个无参构造器，一个带有详细信息描述的构造器。

```java
class MyException extends IOException{
    public MyException(){}
    public MyException(String msg){
        super(msg);
    }
}
```


## 捕获异常

try...catch语句块的执行顺序：

1. 如果try语句块中的代码未抛出异常，程序将跳过catch子句继续执行剩下的代码；
2. 如果try语句块中的代码抛出了在catch子句中声明的异常，程序将跳过try语句块中剩下的代码，执行对应catch异常处理器中的代码，然后继续执行catch之后的代码。异常处理机制负责匹配与异常类型一致的第一个异常处理器，一旦匹配catch字句结束，不再继续搜索异常处理器。所以一般范围大的基类Exception被放在后面；
3. 如果try语句块中抛出了catch中未声明的异常，或者try之外的地方抛出了异常，那么这个方法会立即结束，错误被抛给调用者。

如果调用了一个会抛出已检查异常的方法或方法自身会抛出已检查异常，在知道如何处理的情况下才能捕获它进行处理，否则就应该继续传递这个异常。如果覆盖了父类的方法，而这个方法没有抛出异常，那么这个方法就必须捕获每一个已检查异常，或者包装成RuntimeException抛出。

可以通过多个catch子句捕获多个异常，一般特定的范围小的异常在前面，范围大的异常在后面，如果异常没有继承关系，则无所谓。如果颠倒这种关系，会报不可达错误。捕获的异常可以通过getMessage()获得异常的详细原因，或者e.getClass().getName()获取异常对象的实际类型。如下所示：

```java
try{
// ...
}catch(FileNotFoundException e){
    System.out.println(e.getMessage());
}catch(IOException e){
    System.out.println(e.getMessage());
}catch(Exception e){
    System.out.println(e.getMessage());
}
```

Java 7以后可以将彼此间不存在继承关系的异常合并到一个catch 子句中：

```java
try{
    // ...
}catch(FileNotFoundException | UnknownHostException e){
    // ...
}
```

捕获多个异常的时候，异常对象e隐含为final类型，不能在其子句中再次赋值。

我们可以在catch中再次抛出异常。这可能发生在我们只需要记录错误，但不处理错误，即抛出同一个异常；或者为了改变异常的类型。后者通常发生在一个子模块出错的时候，我们不想知道具体的细节，只需要知道这个模块发生了错误。这个时候我们将原始异常设置为新异常的原因，然后抛出新的异常。这种打包的方式可以让我们抛出更高级别的异常，而同时保留了底异常的信息。示例如下：

```java
try{
    // ...
}catch(SQLException e){
    Throwable t = new MySubsystemException("Database␣error");
    t.initCause(e);
    throw t;
}
```

用这种方法我们可以实现前面所提到的，在一个不能抛出已检查异常的方法中，需要抛出异常时，可以重新打包成一个RuntimeException然后抛出。

在Java 7中，如果catch语句再次抛出了一个声明范围大于方法声明抛出异常范围的异常时，比如下面代码，编译器会检查try语句块中实际可能抛出的异常，如果实际可能抛出的异常范围符合方法的声明范围，则没有问题。

```java
public void update() throws SQLException{
    try{
    // ... This might throw an SQLException
    }catch(Exception e){
    // ...
    throw e; // OK because try block can only throw SQLException
    }
}
```

try...catch...finally语句块的执行顺序：

1. try中的代码没有异常。程序会执行完try的语句，然后执行finally中的语句，然后继续执行finally之后的语句。

2. try中抛出在catch被捕获的异常。程序会执行try语句中的代码，直到抛出异常的语句为止。然后跳过try中剩余的代码，转去执行对应catch中的代码，然后执行finally中的代码。
如果catch中再次抛出了异常，并且没有被捕获，那么这个方法在finally代码被执行后立即结束，异常被抛给这个方法的调用者；如果catch没有再次抛出异常，则在finally执行完成后继续执行finally之后的语句。

3. try中抛出了不能被catch捕获的异常。程序会执行try语句中的代码，直到抛出异常的语句为止。然后跳过try中剩余的代码，执行finally里的代码，然后方法结束，异常被抛给调用者。

try语句也可以没有catch，只有finally。这时候当遇到异常时，finally语句执行后，异常会被再次抛出。

**警告**: 如果try语句和finally语句都有return语句，并且try语句执行到了return，然后跳转到finally继续执行return，那么后者的返回值将覆盖前者的返回值。

**警告**：如果try语句抛出异常，finally语句也抛出异常，那么try语句的异常将会丢失。对于这种情况，在Java 6及以前，我们需要用如下复杂的代码来实现`优先抛出try，再考虑finally`：

```java
InputStream in = ...;
Exception ex = null;

try{
    try{
        // ...
    }catch(Exception e){
        ex = e;
        throw e;
    }
}finally{
    try{
        in.close();
    }catch(Exception e){
        if(ex == null) throw e;
    }
}
```

而在Java 7中我们可以使用try-with-resources语句块。任何实现了AutoCloseable接口的类都可以被作为这里的资源放在try语句块后面的括号里：

```java
try(Resource1 res1 = ...; Resource2 res2 = ...){
    // ...
}
```

当try 正常退出或者抛出异常时，res1和res2 的close()方法都会被调用。如果try和close都抛出异常，那么try的异常会被重新抛出，close抛出的异常会被抑制：通过addSuppressed方法添加到try的异常中。

如果对这些被抑制的异常感兴趣，可以调用getSuppressed获取。try-with-resource语句也可以有catch和finally，它们会在资源关闭后执行。如果需要关闭资源，建议都使用try-with-resource。

## 栈分析

以下给出了三种堆栈跟踪的方法：

```java
public static void main(String[] args) {

    System.out.println("Calling printStackTrace()");
    try{
        ok();
    }catch(Exception e){
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);
        e.printStackTrace(pw);
        System.out.println(sw.toString());
    }
    
    System.out.println("Calling getStackTrace()");
    try{
        ok();
    }catch(Exception e){
        StackTraceElement[] frames = e.getStackTrace();
        for(StackTraceElement f : frames){
            System.out.println(f);
        }
    }
    
    System.out.println("Calling getAllStackTraces()");
    try{
        ok();
    }catch(Exception e){
        Map <Thread, StackTraceElement[]> map = Thread.getAllStackTraces();
        
        for(Thread t : map.keySet()){
            StackTraceElement[] frames = map.get(t);
            System.out.println("Thread: " + t.getName());
            
            for(StackTraceElement f : frames){
                System.out.println("    " + f);
            }
        }
    }
}

public static void ok () throws IOException{
    throw new IOException("Oops..");
}

```
它们的输出如下：
```text
Calling printStackTrace()
java.io.IOException: Oops..
at Test9.ok(Test9.java:47)
at Test9.main(Test9.java:12)
Calling getStackTrace()
Test9.ok(Test9.java:47)
Test9.main(Test9.java:22)
Calling getAllStackTraces()
Thread: Signal Dispatcher
Thread: main
java.lang.Thread.dumpThreads(Native Method)
java.lang.Thread.getAllStackTraces(Thread.java:1603)
Test9.main(Test9.java:34)
Thread: Attach Listener
Thread: Finalizer
java.lang.Object.wait(Native Method)
java.lang.ref.ReferenceQueue.remove(ReferenceQueue.java:143)
java.lang.ref.ReferenceQueue.remove(ReferenceQueue.java:164)
java.lang.ref.Finalizer$FinalizerThread.run(Finalizer.java:209)
Thread: Reference Handler
java.lang.Object.wait(Native Method)
java.lang.Object.wait(Object.java:502)
java.lang.ref.Reference.tryHandlePending(Reference.java:191)
java.lang.ref.Reference$ReferenceHandler.run(Reference.java:153)
```