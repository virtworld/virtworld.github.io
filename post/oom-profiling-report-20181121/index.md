这篇记录了2018年11月21日生产系统的一个联机交易服务应用OOM错误及排查过程。所有的包名、类名、方法名已作脱敏处理，涉及业务逻辑的代码均已删除但不影响问题分析，部分方法、调用栈栈做过简化，以方便阅读。

首先，介绍一下背景。出故障的Java应用部署在四台独立的物理机上，上面通过F5做负载均衡。应用本身比较老，Java版本是1.6，Jetty作为服务器。其中两台用的是IBM的虚拟机，另外两台用的是HotSpot 64-Bit Server（这就是另一个故事了^-^）。

# 生产分析（案发现场）

笔者到事故现场的时候，发生OOM的一台IBM的Java虚拟机已经宕掉了，另一台HotSpot堆开地比较大(Xmx4G)还活着。`jmap`看了下使用中的堆有3G左右，远大于平常的几百兆。`jstat -gcutil pid 1000`观察了一会儿，主要是想看一下Full GC。

<!--more-->

```shell
  S0     S1     E      O      P     YGC     YGCT    FGC    FGCT     GCT   
  ...
  0.00  65.49   7.64  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  23.78  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  36.68  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  45.94  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  56.85  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  68.72  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  72.30  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  82.62  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  84.30  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  91.72  99.94  99.19  40156  269.596   211  449.206  718.802
  0.00  65.49  99.96  99.94  99.19  40156  269.596   211  449.206  718.802
 76.42   0.00   6.27  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  15.07  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  34.83  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  48.93  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  57.36  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  70.52  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  82.41  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  87.38  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  92.91  99.95  99.19  40157  269.604   211  449.206  718.810
 76.42   0.00  96.91  99.95  99.19  40157  269.604   211  449.206  718.810
  0.00  82.96   0.00  99.97  99.19  40158  269.613   212  449.206  718.819
  0.00  82.96   0.00  99.97  99.19  40158  269.613   212  449.206  718.819
  0.00  82.96   0.00  99.97  99.19  40158  269.613   212  449.206  718.819
  0.00  82.96   0.00  99.97  99.19  40158  269.613   212  449.206  718.819
  0.00  82.96   0.00  99.97  98.43  40158  269.613   212  449.206  718.819
  0.00   0.00   9.74  91.36  99.15  40158  269.613   212  454.604  724.217
```

大约每10秒一次Minor GC。Full GC回收的老年代百分比不多（<9%），很快就会扩展堆上限。同时，在Full GC前后做了一下`jmap -heap`，下面是前后对比。

```shell
using thread-local object allocation.
Parallel GC with 53 thread(s)

Heap Configuration:
   MinHeapFreeRatio = 40
   MaxHeapFreeRatio = 70
   MaxHeapSize      = 4294967296 (4096.0MB)
   NewSize          = 1310720 (1.25MB)
   MaxNewSize       = 17592186044415 MB
   OldSize          = 5439488 (5.1875MB)
   NewRatio         = 2
   SurvivorRatio    = 8
   PermSize         = 21757952 (20.75MB)
   MaxPermSize      = 85983232 (82.0MB)

Heap Usage:
PS Young Generation
Eden Space:
   capacity = 434241536 (414.125MB)
   used     = 204966760 (195.4715347290039MB)
   free     = 229274776 (218.6534652709961MB)
   47.20109501454969% used
From Space:
   capacity = 9830400 (9.375MB)
   used     = 6427512 (6.129753112792969MB)
   free     = 3402888 (3.2452468872070312MB)
   65.384033203125% used
To Space:
   capacity = 9568256 (9.125MB)
   used     = 0 (0.0MB)
   free     = 9568256 (9.125MB)
   0.0% used
PS Old Generation
   capacity = 2840068096 (2708.5MB)
   used     = 2837510472 (2706.060859680176MB)
   free     = 2557624 (2.4391403198242188MB)
   99.90994497619258% used
PS Perm Generation
   capacity = 84148224 (80.25MB)
   used     = 83470136 (79.60332489013672MB)
   free     = 678088 (0.6466751098632812MB)
   99.19417431792738% used
```

Full GC之后：

```shell
using thread-local object allocation.
Parallel GC with 53 thread(s)

Heap Configuration:
   MinHeapFreeRatio = 40
   MaxHeapFreeRatio = 70
   MaxHeapSize      = 4294967296 (4096.0MB)
   NewSize          = 1310720 (1.25MB)
   MaxNewSize       = 17592186044415 MB
   OldSize          = 5439488 (5.1875MB)
   NewRatio         = 2
   SurvivorRatio    = 8
   PermSize         = 21757952 (20.75MB)
   MaxPermSize      = 85983232 (82.0MB)

Heap Usage:
PS Young Generation
Eden Space:
   capacity = 438697984 (418.375MB)
   used     = 67292736 (64.17535400390625MB)
   free     = 371405248 (354.19964599609375MB)
   15.339194264453242% used
From Space:
   capacity = 8847360 (8.4375MB)
   used     = 0 (0.0MB)
   free     = 8847360 (8.4375MB)
   0.0% used
To Space:
   capacity = 9043968 (8.625MB)
   used     = 0 (0.0MB)
   free     = 9043968 (8.625MB)
   0.0% used
PS Old Generation
   capacity = 2835152896 (2703.8125MB)
   used     = 2590127344 (2470.137924194336MB)
   free     = 245025552 (233.67457580566406MB)
   91.35758948500815% used
PS Perm Generation
   capacity = 83558400 (79.6875MB)
   used     = 82848712 (79.01068878173828MB)
   free     = 709688 (0.6768112182617188MB)
   99.15066827512256% used
```

老年代从2706MB(99.91%)下降到2470MB(91.36%)，同样说明Full GC能够释放的空间非常少。另外，从JVisualVM图形上来看，堆大小是缓慢但持续地增长的，怀疑堆内存泄漏可能性较高，遂dump了一份堆下来。

另外，还需要知道这个时候程序在忙什么，所以`jstack`打印了一份栈信息。线程池大约有74个线程，其中有55个线程的栈帧上有相同的业务方法。下面显示了其中一个：

```shell
"btpool0-4483" prio=10 tid=0x00007f803c0ab000 nid=0x2086 runnable [0x00007f801d8d6000]
   java.lang.Thread.State: RUNNABLE
	at java.net.SocketInputStream.socketRead0(Native Method)
	at java.net.SocketInputStream.read(SocketInputStream.java:129)
	at oracle.net.ns.Packet.receive(Unknown Source)
	at oracle.net.ns.DataPacket.receive(Unknown Source)
	at oracle.net.ns.NetInputStream.getNextPacket(Unknown Source)
	at oracle.net.ns.NetInputStream.read(Unknown Source)
	at oracle.net.ns.NetInputStream.read(Unknown Source)
	at oracle.net.ns.NetInputStream.read(Unknown Source)
	at oracle.jdbc.driver.T4CMAREngine.unmarshalUB1(T4CMAREngine.java:1099)
	at oracle.jdbc.driver.T4CMAREngine.unmarshalSB1(T4CMAREngine.java:1070)
	at oracle.jdbc.driver.T4C8Oall.receive(T4C8Oall.java:478)
	at oracle.jdbc.driver.T4CPreparedStatement.doOall8(T4CPreparedStatement.java:213)
	at oracle.jdbc.driver.T4CPreparedStatement.executeForRows(T4CPreparedStatement.java:952)
	at oracle.jdbc.driver.OracleStatement.doExecuteWithTimeout(OracleStatement.java:1160)
	at oracle.jdbc.driver.OraclePreparedStatement.executeInternal(OraclePreparedStatement.java:3285)
	at oracle.jdbc.driver.OraclePreparedStatement.execute(OraclePreparedStatement.java:3390)
	- locked <0x000000079061c498> (a oracle.jdbc.driver.T4CPreparedStatement)
	- locked <0x000000079039ba90> (a oracle.jdbc.driver.T4CConnection)
	at com.mycompany.XXX.parser.BizParser.subSave(BizParser.java:338)
	at com.mycompany.XXX.parser.BizParser.save(BizParser.java:210)
	at com.mycompany.XXXClient.spi.MessageReceiveImpl.receiveJsonData(MessageReceiveImpl.java:131)
    ...
```

最后三行为业务逻辑代码（包名隐去）。如果内存泄漏正在发生，程序当前执行的代码是最值得怀疑的。但是这也只能作为非直接证据，下面要看下dump。

# 堆转存分析（尸检）

用MAT加载dump，首先看下leak report。

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-leak-suspect.png" alt="MAT Leak Suspects" title="MAT Leak Suspects"  %}}

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-leak-1.png" alt="MAT Leak Suspects 1" title="MAT Leak Suspects 1"  %}}

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-leak-2.png" alt="MAT Leak Suspects 2" title="MAT Leak Suspects 2"  %}}

Leak report指向Oracle JDBC驱动的T4CPreparedStatement和T4CConnection对象，这与线程栈的描述吻合。有意思的是这里对象并不多：仅57个对象T4CPreparedStatement就占用了1.9GB。我们继续看下报告中的大对象：

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-big-objects.png" alt="MAT Big Objects" title="MAT Big Objects"  %}}

报告中的对象大小指的是对象的retained heap（即一个对象被回收后能释放的内存大小）。T4CPreparedStatement从名字上看应该是Oracle的PreparedStatement实现，这个对象本身不应该占据这么大空间，因为它并不含很多数据。事实上，就算是查询结果集ResultSet，也是每次从数据库中读取很小一部分，不会占用非常大的内存（不过发生过MyBatis把全表读到List中把内存撑爆的OOM）。

所以，上图中的空间应该是它引用的对象所占用的，这一点马上会确认。从另一方面说，光看这份Leak report不能得出内存泄漏的结论。因为通常内存泄漏的情况是对象不断地被创建，但又无法回收，而这份报告中只看到了那么几个大对象，除非这几个T4CPreparedStatement对象不断地引用新的对象，使它的retained heap越来越大。

接下来看类的直方图：

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-histogram.png" alt="MAT Histogram" title="MAT Histogram"  %}}

按照Retained heap排序，Oracle相关的T4CPreparedStatement、OracleSql、T4CConnection和Binder[]很突出。从直方图的对象数量（第二列）来看，异常的是T4CPreparedStatement（以及与它相关的OracleSql）有508,211个对象。数据库作为开销很大的操作，执行完后Statement和ResultSet应该立即关闭，在内存中保留几十万个Statement对象，是不正常的（即使Oracle有Statement缓存，但也不应该达到这个数量）。

这里引出了一个问题：Leak report只报告了57个T4CPreparedStatement（注意这个值与线程数量55非常接近），而堆中实际上有50多万个，会不会这么多T4CPreparedStatement之间相互有关联？

继续往下看支配树（dominator tree），先按照对象列表：

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-dominator-tree-overview-1.png" alt="MAT Dominator Tree Overview" title="MAT Dominator Tree Overview"  %}}

这张图确认了一点，那几个最大的对象本身只占用了很小的内存（shallow heap显示只有920字节），主要占用空间的是它们引用的对象。再看一眼按照类列表：

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-dominator-tree-overview-2.png" alt="MAT Dominator Tree Overview" title="MAT Dominator Tree Overview"  %}}

这里显示的和Leak report一致，不再重复解释。回到支配树的按对象列表模式，打开最大那个对象`0x78b009b10`的向外引用关系(outgoing reference):

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-dominator-tree-show-reference.png" alt="MAT Dominator Tree: Show Outgoing Reference" title="MAT Dominator Tree: Show Outgoing Reference"  %}}

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-dominator-tree-reference-1.png" alt="MAT Dominator Tree: Outgoing Reference" title="MAT Dominator Tree: Outgoing Reference"  %}}

按照retained size排序后，很容易发现对象`0x78b009b10`是一个链表的头部，它的next指向的另一个T4CPreparedStatement对象`0x78af6ccc8`。而`0x78af6ccc8`包含了prev变量正好指回`0x78b009b10`对象，它的next继续指向链表中的后面一个T4CPreparedStatement。从每个链表节点retained heap大小可以看出，这个链表正是占据了大部分内存的东西，并且可以基本确定这个链表非常之长，可能数万甚至几十万个T4CPreparedStatement（IBM Heap Analyzer有一个追踪到引用叶子节点的功能，MAT上没找到）。

堆分析到这一步可以确定问题是T4CPreparedStatement没有被正常回收引起，结合栈快照(前文jstack或者hprof转存本身也有栈快照信息)可以定位到（疑似）T4CPreparedStatement的泄漏的代码，最终泄漏的原因需要从代码中证明。

另外，我们知道T4CPreparedStatement需要储存SQL语句，而SQL语句可以帮我们定位代码，作为定位泄露源的辅助，我们需要找到这些SQL。笔者注意到T4CPreparedStatement和OracleSql对象数量很接近，可以说是1:1。从上图中也能看到，`0x78b009b10`这个T4CPreparedStatement引用了一个OracleSql对象，变量名为sqlObject，地址为`0x78af6b748`。那么这些OracleSql正是泄漏的SQL语句。

在Dominator Tree中确认一下OracleSql的属性，然后打开OQL，输入下面语句，直接拉出所有T4CPreparedStatement关联的SQL语句。

```sql
SELECT o.sqlObject.originalSql.toString() FROM 
INSTANCEOF "oracle.jdbc.driver.T4CPreparedStatement" o WHERE (o.sqlObject.originalSql != null)
```

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-oql.png" alt="MAT OQL" title="MAT OQL"  %}}

因为SQL语句涉及业务逻辑和数据，这里都隐去了。但是统计情况来看，共查询到508,120条SQL，正好是OracleSql对象的数量。通过表名粗略统计，其中有433,475条SQL涉及到某块业务，占比85.03，这块业务正好也是栈信息所指的代码，正式确认了泄漏点。查出来的SQL中，还涉及到其它业务，说明可能还有其它泄漏点，我们优先解决这85%的问题吧。

# 代码审查（搜查取证）

## 业务代码

我们从栈快照中的业务方法入手，下面回顾一下涉及到的类和方法（该调用栈已做脱敏和简化）：

```shell
...
at com.mycompany.XXX.parser.BizParser.subSave(BizParser.java:338)
at com.mycompany.XXX.parser.BizParser.save(BizParser.java:210)
at com.mycompany.XXXClient.spi.MessageReceiveImpl.receiveJsonData(MessageReceiveImpl.java:131)
...
```

先来看这个MessageReceiveImpl类的receiveJsonData方法（做了脱敏和简化），Java 6的代码资源关闭很冗长，将就着看吧：

```java
// 应用程序代码 MessageReceiveImpl.java

public class MessageReceiveImpl implements IMessageReceive {

    // 解析爬虫获取的HTML信息，并存入数据库
    public void receiveJsonData(...) {

        // 业务逻辑略...
        
        BizParser parser = new BizParser();
        Connection conn = null;
        
        try{
            conn = XXXRuntime.getDBConnection("dbName");
            
            // 业务逻辑略...（conn被作为参数传递给多个方法） 
            // 下面的parser.saveDB是调用栈中的方法。
            result = parser.save(conn, data);
            
            // 业务逻辑略...
            
        } catch (Exception e) {
            e.printStackTrace();
            try {
                if (conn != null) {
                    conn.rollback();
                }
            } catch (SQLException e1) {
                e1.printStackTrace();
            }
        } finally {
            try {
                if (conn != null) {
                    conn.close();
                    conn = null;
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }
}
```

跟踪这个`parser.save(conn, data)`方法。这个方法主要目的是解析网页HTML，并写入数据库。
这里进行了简化，实际上`save`和`subsave`分别是一个200多行的方法，里面有无数个if, for嵌套，
最深的有8层嵌套，非常令人迷醉。

```java
// 应用程序代码 BizParser.java

public class BizParser {

    // 解析字符串，并写入数据库。这里进行了简化，实际上这是一个200行的方法，
    // 里面有无数个if, for嵌套，最深的有8层嵌套，非常迷醉...
    public void save(Connection conn, String data) throws Exception {
        try {
			for (...) {
				if (...) {
					ps = conn.prepareStatement(sql);
					// 设置ps变量
					ps.execute();
					ps.close();

					sql = "...";
					ps = conn.prepareStatement(sql);

					if (...) {
						for (...) {
							if (...) {
								continue;
							}
							// 设置ps变量
						}

						ps.execute();
						ps.close();
					} else if (...) {
						for (...) {
							for (...) {
								if (...) {
									continue;
								}
								// 设置ps变量
							}
							ps.addBatch();
						}
						ps.executeBatch();
						ps.close();
					} else {
						continue;
					}
				} else if (...) {
					subSave(conn, data);
				} else {
					continue;
				}
			}
			conn.commit();
		} catch (Exception e) {
			conn.rollback();
			throw e;
		} finally {
			if (ps != null) {
				ps.close();
			}
		}
    }
    
    private void subSave(Connection conn, String data) throws Exception{

		if (...) {
			for (...) {
				if (...) {
					if (...) {
						continue;
					}
					
					// 初始化sql
					ps = conn.prepareStatement(sql);
					// 设置ps变量
					ps.execute();
					ps.close();
					// 改变sql
					ps = conn.prepareStatement(sql);
					
					if (...) {
						// ...
						for (...) {

							if (...) {
								continue;
							}
							// 设置ps变量
						}
						ps.execute();
						ps.close();
					} else if (...) {
						// ...
						for (...) {
							
							for (...) {

								if (...) {
									continue;
								}
								// 设置ps变量
							}

							ps.addBatch();
						}			
						ps.executeBatch();
						ps.close();
					} else {
						continue;
					}
				} else if (...) {
					// 这里居然递归了
					subSave(conn, data);
				} else {
					continue;
				}
			}
		}
	}
}
```

看完这段非常令人不适代码，问题已经找到了：PrepareStatement被不断创建，但是在continue和递归的情况下没有被close。并且大量的嵌套循环和递归调用加重了这个问题。

在研究这段代码的时候，笔者还发现了生成上的jar和测试环境的版本竟然不一致（非常的迷醉^-^），不过分别看了下后发现都有相同的问题。看了下最后提交记录，是在15年。

运维的同事提出了三个问题：

1. 代码中的PrepareStatement只是conn.prepareStatement(sql)时候创建了，并没有被执行，当ps变量指向新的PrepareStatement对象时，老的对象不会被GC回收掉吗？
2. MessageReceiveImpl.receiveJsonData方法在finally里关闭了Connection，为什么它的ps没有被关闭？
3. 15年的老代码，为什么最近才出问题？

## 为什么PS没有被GC自动回收？

JDBC的资源关闭是基本常识，代码规范要求先关闭ResultSet，再Statement，最后Connection，不关闭会导致资源泄漏。
开发知道执行完SQL后，不关闭这些资源很快会出现数据库问题。对于Oracle数据库来讲，很容易超过最大游标上限。这个上限一般设置为几百到一千。
这个数量在开发阶段很容易测出来。同时数据库也有对长时间没有关闭的连接的监控，DBA也会发现问题。

```shell
java.sql.SQLException: ORA-01000: maximum open cursors exceeded
```

但是从代码上来看，这次所有没有关闭的ps都没有被执行，反而使问题不容易发现。那么，回到第一个问题，GC为什么没有回收掉这些看上去没有用的ps。

笔者先做了个简单的实验:

```java
conn = XXXRuntime.getDBConnection("dbName");
PreparedStatement ps = null; 
for( int i = 0; i < 10000000; i++) {
    ps = conn.prepareStatement("select * from "
		+ "some_table st where st.status = ?");
	ps.setString(1, "00");
}
ps.close();
conn.close();
log.info("Your survived...");
Thread.sleep(10000L);
```

把-Xmx设置为64m，一开马上就OOM，dump导出来和故障差不多。所以在即使ps没有执行，不关闭也不会被回收掉。

为了确认`conn.prepareStatement(sql)`获取的Statement不会自动被回收的原因，需要看下odjbc14.jar的源码。

> Oracle数据库驱动的版本是ojdbc14.jar

根据调用栈可知实际上的涉及的类是oracle.jdbc.driver.T4CPreparedStatement。
根据之前MAT上对dump的分析，我们知道内存泄漏的主要地方是由T4CPreparedStatement构成的链表，
所以在源码中我们查找的一个目标是prev和next变量。

这两个变量定义在T4CPreparedStatement的父类OraclePreparedStatement的父类OracleStatement中：

```java
// oracle.jdbc.driver.OracleStatement

public abstract class OracleStatement implements oracle.jdbc.internal.OracleStatement, ScrollRsetStatement {

    // ...
    OracleStatement next;
    OracleStatement prev;
    // ...
}
```

接下来我们希望找到的证据是设置nnex和prev的代码。

由于T4CPreparedStatement是由Connection创建的，结合MAT的dump分析可以确定是`oracle.jdbc.driver.T4CConnection`这个类。
prepareStatement这个方法定义在其父类PhysicalConnection中：

```java
// oracle.jdbc.driver.PhysicalConnection

abstract class PhysicalConnection extends OracleConnection {

    public synchronized PreparedStatement prepareStatement(
        String var1) throws SQLException {
        
        return this.prepareStatement(var1, -1, -1);
    }

    public synchronized PreparedStatement prepareStatement(
        String var1, int var2, int var3) throws SQLException {
        
        // ...

        OraclePreparedStatement var4 = null;
        if(this.statementCache != null) {
            var4 = (OraclePreparedStatement)this.statementCache
                .searchImplicitCache(var1, 1, var2 == -1 && var3 == -1 ? 1 : 
                            ResultSetUtil.getRsetTypeCode(var2, var3));
        }

        if(var4 == null) {
            var4 = this.driverExtension
                .allocatePreparedStatement(this, var1, var2, var3);
        }
        return var4;
    }
}
```

如果启用了Statement缓存，ojdbc会先去查缓存。这个缓存的实现是LRUStatementCache，并且必须设置缓存尺寸，因此不存在无限增长的可能，所以排除缓存的问题。
接下去是`this.driverExtension.allocatePreparedStatement`这行代码，它的方法如下：

```java
// oracle.jdbc.driver.T4CDriverExtension

OraclePreparedStatement allocatePreparedStatement(
    PhysicalConnection var1, String var2, int var3, int var4) throws SQLException {

    return new T4CPreparedStatement(var1, var2, var3, var4);
}
```

所以，回到T4CPreparedStatement的构造方法上来，从基类OracleStatement的构造方法开始分析：

```java
// oracle.jdbc.driver.OracleStatement

OracleStatement(PhysicalConnection var1, int var2, int var3, int var4, int var5) throws SQLException {
    
    // ...
    this.connection.addStatement(this);
    
    // ...
}
```

这行代码比较可疑，继续点进去看：

```java
// oracle.jdbc.driver.PhysicalConnection

synchronized void addStatement(OracleStatement var1) {
    if(var1.next != null) {
        throw new Error("add_statement called twice on " + var1);
    } else {
        // 设置next指针
        var1.next = this.statements;
        if(this.statements != null) {
            // 设置prev指针
            this.statements.prev = var1;
        }

        this.statements = var1;
    }
}
```

虽然不确定Oracle出于什么原因做了这个链表，但是上面这个方法说明每次调用prepareStatement后，Statement会被添加到链表中，所以不会被GC回收。

## 为什么连接关闭后ps仍旧没有被回收？

第二个疑问是，从代码逻辑上看，尽管ps没有被关闭，但是connection最终是会被关闭的。Statement是从属于Connection的，所以正常来讲Connection关闭的时候Statement应该也会被关闭。

一种可能的解释是，业务代码递归层次太多，可能还没有到connection.close内存就已经吃不消了。
但这个可能性很小，因为自上次启动以来，这段业务代码至少也被调用了至少几千次。如果都没有关闭连接，那就不是OOM了，数据库就会连不上。

所以回到ojdbc，查看PhysicalConnection的关闭代码：

```java
// oracle.jdbc.driver.PhysicalConnection

public synchronized void close() throws SQLException {
    if(this.lifecycle != 2 && this.lifecycle != 4) {
        if(this.lifecycle == 1) {
            this.lifecycle = 2;
        }

        try {
            if(this.closeCallback != null) {
                this.closeCallback.beforeClose(this, this.privateData);
            }

            // 关闭Statement
            this.closeStatements(true);
            this.needLine();
            if(this.isProxy) {
                this.close(1);
            }

            this.logoff();
            this.cleanup();
            if(this.timeout != null) {
                this.timeout.close();
            }

            if(this.closeCallback != null) {
                this.closeCallback.afterClose(this.privateData);
            }
        } finally {
            this.lifecycle = 4;
        }
    }
}
```

上面这段代码中，重要的是this.closeStatements(true):

```java
// oracle.jdbc.driver.PhysicalConnection

synchronized void closeStatements(boolean var1) throws SQLException {
    if(var1 && this.isStatementCacheInitialized()) {
        this.statementCache.close();
        this.statementCache = null;
        this.clearStatementMetaData = true;
    }

    OracleStatement var2;
    OracleStatement var3;
    for(var2 = this.statements; var2 != null; var2 = var3) {
        var3 = var2.nextChild;
        if(var2.serverCursor) {
            var2.close();
            this.removeStatement(var2);
        }
    }

    // 这里循环遍历链表，并关闭Statement
    for(var2 = this.statements; var2 != null; var2 = var3) {
        var3 = var2.next;
        var2.close();
        this.removeStatement(var2);
    }
}
```

这里最后一个循环对statement的链表进行了遍历并关闭每一个statement。因此，
当T4CConnection（PhysicalConnection的子类）被关闭的时候，所有的T4CPreparedStatement理应被释放。
这和实际情况相反，所以要从更高层的代码看一下，它是如何处理连接关闭的。

我们回到业务代码：

数据库的链接是MessageReceiveImpl.receiveJsonData的通过
`XXXRuntime.getDBConnection("dbName")`获取的。我们来看下这个方法：

```java
// 应用程序代码 XXXRuntime.java

public static Connection getDBConnection(String connName) throws SQLException {
    return DBConnectionFactory.getConnection(connName);
}
```

DBConnectionFactory是一个抽象类，它的getConnection是一个静态方法，如下：

```java
// 应用程序代码 DBConnectionFactory.java

public static Connection getConnection(String name) throws SQLException{
    return getFactory().getInstance(name);
}
```

getFactory()返回的是一个类型为DBConnectionFactory的对象(即它的具体实现)。
这个实现类配置在XML中，在应用启动的时候进行初始化，实际配置为PooledConnectionFactory类，它的getInstance方法如下：

```java
// 应用程序代码 PooledConnectionFactory

public Connection getInstance(String name) throws SQLException{

    // ...

    DataSource ds = (DataSource)dataSources.get(name);
    java.sql.Connection conn = ds.getConnection();
    return new DefaultQueryConnection(name, conn);
}
```

这里的dataSources变量是一个Map<String, javax.sql.DataSource>对象。
在应用初始化的时候，PooledConnectionFactory会根据XML中数据源的配置，初始化dataSources。

具体初始化代码这里省略，初始化后map里的DataSource是org.apache.commons.dbcp.datasources.SharedPoolDataSource。

> 数据库连接池dbcp的版本是commons-dbcp-1.2.2.jar

初始化参数配置在XML中，关键的几个参数如下：

```xml
<driver>oracle.jdbc.driver.OracleDriver</driver> 
<url>****</url> 
<user>****</user> 
<password>****</password> 
<loginTimeout>0</loginTimeout> 
<logWriter>system.out</logWriter> 
<maxActive>600</maxActive>
<maxWait>1000</maxWait> 
<maxIdle>60</maxIdle>
```

看到了连接池，因此合理的怀疑是conn.close()并不会调用到ojdbc的连接关闭方法，而是被放入池中。

在我们进入到dbcp的代码前，先看下上段代码中DefaultQueryConnection的构造方法（因为从SharedPoolDataSource获取的conntion被传递进了构造方法）
以及它的close方法（因为我们关心的是连接如何被关闭）。

DefaultQueryConnection继承自ConnectionWrapper（也是应用自身的代码）：

```java

// 应用程序代码 ConnectionWrapper.java

public abstract class ConnectionWrapper implements Connection
{
  protected java.sql.Connection connection = null;

  protected ConnectionWrapper(String name, java.sql.Connection connection){
    this.connection = connection;
    this.name = ((name == null) ? connection.toString() : name);
  }
  
  public void close() throws SQLException {
    this.connection.close();
  }
  // ...
}
```

可见业务代码中conn.close()其实调用的是从SharedPoolDataSource获取到的连接对象的的close方法。

所以，我们要进入dbcp的源码来确认一下SharedPoolDataSource的getConnection方法返回的Connection是如何实现close方法的。SharedPoolDataSource.getConnection()的定义在其父类中，下面做了点简化：

```java
// org.apache.commons.dbcp.datasources.InstanceKeyDataSource

public Connection getConnection(String username, String password) throws SQLException {

    PooledConnectionAndInfo info = this.getPooledConnectionAndInfo(username, password);
    Connection con = info.getPooledConnection().getConnection();
    return con;
}
```

PooledConnectionAndInfo定义如下：

```java
// org.apache.commons.dbcp.datasources.PooledConnectionAndInfo

final class PooledConnectionAndInfo {
    private final PooledConnection pooledConnection;
    private final String password;
    private final String username;
    private final UserPassKey upkey;

    PooledConnectionAndInfo(PooledConnection pc, String username, String password) {
        this.pooledConnection = pc;
        this.username = username;
        this.password = password;
        this.upkey = new UserPassKey(username, password);
    }

    final PooledConnection getPooledConnection() {
        return this.pooledConnection;
    }

    final UserPassKey getUserPassKey() {
        return this.upkey;
    }

    final String getPassword() {
        return this.password;
    }

    final String getUsername() {
        return this.username;
    }
}
```

也就是说SharedPoolDataSource从PooledConnectionAndInfo中获取了一个PooledConnection对象，而PooledConnection是一个接口。
从MAT中查一下，可以知道它用的实现类是`PooledConnectionImpl`:


{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-oql-PooledConnection.png" alt="MAT finding the PooledConnection objects" title="MAT finding the PooledConnection objects"  %}}


我们来看下它的实现PooledConnectionImpl的构造方法和getConnection方法:

```java
// org.apache.commons.dbcp.cpdsadapter.PooledConnectionImpl

class PooledConnectionImpl implements PooledConnection, KeyedPoolableObjectFactory {
    
    private Connection connection = null;
    private Connection logicalConnection = null;
    
    PooledConnectionImpl(Connection connection, KeyedObjectPool pool) {
        this.connection = connection;
        // ...
    }
    
    public Connection getConnection() throws SQLException {
        this.assertOpen();
        if(this.logicalConnection != null && !this.logicalConnection.isClosed()) {
            throw new SQLException("PooledConnection was reused, withoutits previous Connection being closed.");
        } else {
            this.logicalConnection = new ConnectionImpl(this, this.connection);
            return this.logicalConnection;
        }
    }
}
```

PooledConnectionImpl里面的connection是构造方法传递进来的，MAT（下图）显示它实际上是一个Oracle的T4CConnection；
而另一个logicalConnection（也就是getConnection返回的）是一个org.apache.commons.dbcp.cpdsadapter.ConnectionImpl。
来看一下它的close方法：

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-oql-PooledConnection-2.png" alt="MAT finding the PooledConnection objects" title="MAT finding the PooledConnection objects"  %}}

```java
// org.apache.commons.dbcp.cpdsadapter.ConnectionImpl

class ConnectionImpl implements Connection {
    public void close() throws SQLException {
        this.assertOpen();
        this.isClosed = true;
        this.pooledConnection.notifyListeners();
    }
}
```

继续看PooledConnectionImpl的notifyListeners()。

```java
// org.apache.commons.dbcp.cpdsadapter.PooledConnectionImpl

class PooledConnectionImpl implements PooledConnection, KeyedPoolableObjectFactory {
    
    private Vector eventListeners;
    
    void notifyListeners() {
        ConnectionEvent event = new ConnectionEvent(this);
        Iterator i = this.eventListeners.iterator();

        while(i.hasNext()) {
            ((ConnectionEventListener)i.next()).connectionClosed(event);
        }

    }
}
```

这个eventListeners到底是什么呢，看一下dump(下图)，发现其实是org.apache.commons.dbcp.datasources.KeyedCPDSConnectionFactory。

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-oql-event-listener.png" alt="MAT Event Listener" title="MAT Event Listener"  %}}

也就是说调用SharedPoolDataSource.getConnection().close()时，实际上调用的是KeyedCPDSConnectionFactory.connectionClosed()方法。下面我们看下这个方法：

```java
// org.apache.commons.dbcp.datasources.KeyedCPDSConnectionFactory

class KeyedCPDSConnectionFactory implements KeyedPoolableObjectFactory, ConnectionEventListener {

    protected KeyedObjectPool _pool;

    public void connectionClosed(ConnectionEvent event) {
        PooledConnection pc = (PooledConnection)event.getSource();
        if(!this.validatingMap.containsKey(pc)) {
            PooledConnectionAndInfo info = (PooledConnectionAndInfo)this.pcMap.get(pc);
            if(info == null) {
                throw new IllegalStateException("close() was called on a Connection, but I have no record of the underlying PooledConnection.");
            }

            try {
                // 将连接放回池里
                this._pool.returnObject(info.getUserPassKey(), info);
            } catch (Exception var7) {
                System.err.println("CLOSING DOWN CONNECTION AS IT COULD NOT BE RETURNED TO THE POOL");

                try {
                    this.destroyObject(info.getUserPassKey(), info);
                } catch (Exception var6) {
                    System.err.println("EXCEPTION WHILE DESTROYING OBJECT " + info);
                    var6.printStackTrace();
                }
            }
        }
    }
}

```

关键是这行：this._pool.returnObject(info.getUserPassKey(), info)。通过MAT再看下dump。

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-oql-_pool.png" alt="MAT the _pool" title="MAT the _pool"  %}}

确定_pool实际上指的是是org.apache.commons.pool.impl.GenericKeyedObjectPool。继续看下它的returnObject方法：

> commons-pool的版本是commons-pool-1.3.jar

```java
// org.apache.commons.pool.impl.GenericKeyedObjectPool

public synchronized void returnObject(Object key, Object obj) throws Exception {
    boolean success = true;

    // this._testOnReturn会返回false，并且this._factory.validateObject会返回true，
    // 因此会进入else分支
    if(this._testOnReturn && !this._factory.validateObject(key, obj)) {
        success = false;

        try {
            this._factory.destroyObject(key, obj);
        } catch (Exception var9) {
            ;
        }
    } else {
        try {
            // this._factory指的是KeyedCPDSConnectionFactory，
            // 它的passivateObject方法是空的，等于什么都没执行
            this._factory.passivateObject(key, obj);
        } catch (Exception var8) {
            success = false;
        }
    }

    boolean shouldDestroy = false;
    
    // 这边获取了一个链表，这个链表里的元素是ObjectTimestampPair
    // ObjectTimestampPair由一个时间戳的long变量和一个PooledConnectionAndInfo组成
    // 也就是说这里的连接池就是一个由PooledConnectionAndInfo组成的链表
    // 而PooledConnectionAndInfo（前面已经分析过）是对物理连接T4CConnection和
    // 逻辑链接ConnectionImpl的包装。
    LinkedList pool = (LinkedList)((LinkedList)this._poolMap.get(key));
    if(null == pool) {
        pool = new LinkedList();
        this._poolMap.put(key, pool);
    }

    this.decrementActiveCount(key);
    
    // _maxIdle就是前面xml配置的maxIdle，即60
    // 如果配置了大于0的_maxIdle，并且连接池的大于等于这个值，
    // 当前这个连接会被标记为shouldDestroy
    if(this._maxIdle >= 0 && pool.size() >= this._maxIdle) {

        shouldDestroy = true;
    } else if(success) {
        // 如果连接池没有达到_maxIdle，连接被放回池里（用一个新的时间戳包装一下）
        pool.addLast(new GenericKeyedObjectPool.ObjectTimestampPair(obj));
        ++this._totalIdle;
    }

    this.notifyAll();
    if(shouldDestroy) {
        try {
            // 关闭连接
            this._factory.destroyObject(key, obj);
        } catch (Exception var7) {
            ;
        }
    }
}
```

上面把returnObject代码的逻辑简单注释了一下。简单地说，连接池是一个链表，如果它判断链表尺寸大于等于了最大空闲数（也就是我们先前XML中配置的60），
那么该连接会被关闭，否则会被放回链表里。我们先来看一下，这个链表有多大：

{{% figure class="center" src="/images/oom-profiling-report-20181121/mat-pool-size.png" alt="MAT Pool Size" title="MAT Pool Size"  %}}

Dump显示链表大小为28，没有达到最大空闲值，因此连接不会被关闭。我们再看下this._factory.destroyObject(key, obj)方法是不是真的会关闭连接：

```java
// org.apache.commons.dbcp.datasources.KeyedCPDSConnectionFactory

public void destroyObject(Object key, Object obj) throws Exception {
    if (obj instanceof PooledConnectionAndInfo) {
        PooledConnection pc = ((PooledConnectionAndInfo)obj).getPooledConnection();
        this.pcMap.remove(pc);
        pc.close();
    }
}
```

这里调用的是PooledConnectionImpl的close方法：

```java
public void close() throws SQLException {
    this.assertOpen();
    this.isClosed = true;

    try {
        if (this.pstmtPool != null) {
            try {
                this.pstmtPool.close();
            } finally {
                this.pstmtPool = null;
            }
        }
    } catch (RuntimeException var30) {
        throw var30;
    } catch (Exception var31) {
        throw new SQLNestedException("Cannot close connection (return to pool failed)", var31);
    } finally {
        try {
            this.connection.close();
        } finally {
            this.connection = null;
        }
    }
}
```

最终会调用的是`this.connection.close()`，而这里的connection就是我们前面分析过的Oracle的T4CConnection。至此，从应用程序代码到dbcp到ojdbc的连接关闭就分析完了。对于第二个问题“为什么连接关闭后ps仍旧没有被回收？”，答案是应用程序的关闭连接方法，实际上在下一层dbcp里进行了判断，如果连接池没有达到最大空闲数，连接会放回池里，不会关闭。

## 为什么15年的老代码会突然出问题？

这个问题比较简单，看一下最近上了什么代码就可以。检查版本管理器的提交记录后，发现涉事的代码最后一次提交的确在15年，但是11月19号（出事前两天）对数据源的配置进行了修改：

```xml
<maxActive>600</maxActive><!--30改600--> 
<maxWait>1000</maxWait> 
<maxIdle>60</maxIdle><!--8改60--> 
```

所以，内存泄漏一直都有，只是调大maxIdle参数延迟了连接被关闭，加重了内存泄漏问题。

# 总结和建议

1. 再次强调了代码规范里面关于ResultSet，Statement和Connection必须显示地关闭。Statement一旦从Connection中获取了，不管有没有执行过，都必须关闭。由于底层的框架再次封装以及不同JDBC实现的差异，不应该依靠Connection的关闭方法来做清理，也不能依赖GC来自动回收。
2. 调整线程池参数的要慎重，搞不好就会触发老坑。
