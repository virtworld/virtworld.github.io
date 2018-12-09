>本文记录的是一次对某系统的批处理应用程序的调优过程。主要涉及统计信息收集、代码分析调优、JVM调优以及从单机批处理向多机的拆分过程。

## **批处理模式**
不论需要处理的业务逻辑如何，大部分批处理程序（也包括我们要讨论的）都遵照一种通用的编程模型。虽然不同的公司内部可能对批处理的各种术语有不同的表述，但为了描述清晰，
下文将采用<a rel="JSR-352" href="https://www.jcp.org/en/jsr/detail?id=352">`JSR-352`</a>标准定义的批处理领域语言(Domain Language)。下面我们会对一些基本概念做简略描述。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/batch_model.png" alt="批处理程序模型" title="批处理程序模型" %}}

如上图所示，我们的批处理程序包含多个作业(Job)，一个作业又包含多个步骤(Step)，一个步骤内部的执行逻辑遵循经典的读取、处理和写入模式。
我们称一个正在运行的批处理程序为批处理实例(Batch Instance)， 同样的有作业实例(Job Instance)和步骤实例(Step Instance)。
不同的批处理会定时运行，根据运行时间点和频率分为日终(End-of-Day)和月末(End-of-Month)批处理。
我们称批处理时间和业务数据时间挂钩，而非日历时间。比如，一个在2018年1月15日03:00am开始运行的批处理，它处理的是2018年1月14日产生的数据，那么我们称它为2018/01/14日终批处理实例。
批处理虽然是非实时数据处理，但是也有需要在XX时间段内完成的要求，这通常是因为要满足为下游系统提供数据的要求。

作业以及其步骤的执行规则一般定义在XML或者数据库中。首先，我们来看一个作业的内部。
一个作业的正常执行步骤通常有先后逻辑关系，所以一般是串行地按顺序执行(`Step1->Step2->Step3->END`)。
但在一个步骤失败的情况下，可以采用不同的策略：

* 尝试重复执行该步骤，并在重复指定次数仍失败后改用其他策略(`Step1->Step1'->Step1''...`);
* 跳过该步骤，继续执行下一个步骤(`Step1->Step3->END`);
* 终止作业(`Step1->END`);
* 进入条件分支(`Step1->Step4->Step5->END`)， 如下图。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/batch_branch.png" alt="作业内步骤的条件分支" title="作业内步骤的条件分支" %}}

接着，我们再来看作业间的关系。作业可以作业一个步骤嵌套在另一个作业中，多个相互独立的作业也可以并行执行。如下图：

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/batch_jobs.png" alt="作业嵌套和并行执行" title="作业嵌套和并行执行" %}}

<!--more-->

## **系统概述**

这篇文章讲述的是银行的某个系统。对于存量客户的一些数据分析，需要通过批处理的形式来计算。具体的业务逻辑与本文无关，因此不会涉及。

无论是日终还是月末的批处理程序，都是设定在下午4点开始运行，并且要求在晚上0点前完成。我们的批处理程序包含3个作业，下面称为`Job P`, `Job E`, `Job C`。
其中`Job P`包括两个步骤：`Step P1(EoM)`和`Step P2(EoD)`, `Job E`包括两个步骤：`Step E1(EoM)`和`Step E2(EoD)`, 
`Job C`包括四个步骤：`Step C1(EoD)`, `Step C2(EoD)`, `Step C3(EoD)`和`Step C4(EoD)`。
其中步骤`Step P1(EoM)`和`Step E1(EoM)`只会在月末运行，其它步骤每天都会执行。
三个作业的运行顺序是完全串行的，即`Job P(Step P1 -> Step P2) -> Job E(Step E1 -> Step E2) -> Job C(Step C1 -> Step C2 -> Step C3 -> Step C4)`。
但是在每个步骤内部采用多线程的方式处理数据。

每个步骤内部的处理逻辑都非常相似：

1. (阶段1) 从数据库 (Oracle 11g) 读取记录并组装成Java对象;
2. (阶段2) 将Java对象转换成XML的表现形式;
3. (阶段3) 将XML报文发送给计算引擎，并取回响应XML报文;
4. (阶段4) 将响应XML转换成Java对象;
5. (阶段5) 将Java对象批量保存到数据库中;

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/batch_deployment.png" alt="部署图" title="批处理应用部署图" %}}

如上图所示，批处理应用部署在一台服务器上（单进程多线程运行）. 计算引擎是一个专有软件，就像一个**黑盒子**, 它被部署在两台IBM WerSphere Application Server上. 所有服务器都是物理机，x3850，32个CPU物理核心和250GB内存。

## **问题描述**

随着业务的增长，每日/每月需要处理的数据量增长很快。我们以`Job P`的`Step P1`月末批处理为例，在2016年9月末，大约有859K笔数据需要处理；而到了2017年9月，这个数据量达到了1273K，一年增长近50%。下图展示了数据量的增长情况。 

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/batch_cost.png" alt="items need to be processed at the end-of-month" title="Step P1的数据量随时间增长的情况" %}}

系统最初在2015年末上线的时候，月末批处理大约需要4.5个小时；到16年末，这个时间增长到了7.5个小时。我们前面说过这个批处理从每天4pm开始，需要在12pm前结束，也就是允许的时间是8个小时。

在17年初的时候，由于我忙于别的项目，公司找了一个外包高级工程师对此进行优化。经过一个多月的压力测试，给出的方案是将每个步骤并发的线程数从20增加到40~60不等，并在两台计算引擎的物理服务器上将WebSphere Application Server数量分别从2增加到5。

显示这个解决方案解决方案有问题，在没有找到性能瓶颈的时候，单纯的增加并发数，不一定能提升性能，运气如果足够好，也只能解一时之急。但是这的确给我们争取了一点时间。上线后，2017年5月末的批处理耗时降到了6个小时。
 
到2017年11月份，公司终于让我从项目中抽出时间来着手这个批处理的问题了；而此时月末批处理用时再次达到8小时，并且由于超时，不得不进行人工干预。问题再次变得很紧迫，而此时再单纯地增加并发数已经没有用处。

> 一点感受：公司从来不会优先考虑的性能优化问题，除非问题已经到了非解决不可的地步。所以在系统设计时就应该考虑到这点。 

## **性能优化过程概述**

整个性能调优的过程就是一个优化和测试的循环。从测试中发现最大的性能瓶颈，解决这个瓶颈，然后再次运行测试查看效果并发现新的优化方向。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/performance_tuning_cycle.png" alt="调优过程" title="调优过程" %}}

因为所有作业的步骤的处理逻辑都类似，所以在实际调优过程中，我以耗时最长的步骤`Step P1`作为测试和优化的参考。

对于每一次组测试，以下统计数据会被收集：

1. CPU占用率;
2. CPU IO wait 占用率;
3. CPU System 占用率;
4. 等待CPU时间的线程数;
5. 被阻塞的线程数;
6. 内存换入/换出;
7. 抢占式/非抢占式上下文切换;
8. 网络负载;
9. JVM GC统计信息;
10. 主要代码逻辑的耗时统计;
11. Oracle AWR报告。

## **第一轮测试：寻找瓶颈**

接手这个任务的时候，我观察了生产环境批处理的运行情况：其中计算引擎服务器CPU、内存、磁盘IO等资源使用率都非常低，数据库服务器压力也不大；而批处理服务器CPU占用率在50-60%。所以压力测试监控的主要目标是批处理服务器，另外也要看下网络是否带宽是否有压力等。因为上一任负责性能调优的工程师没有留下压测时收集的统计信息，所以我想不如先完整的根据不同的并发数运行几次`Step P1`，收集一些数据看看。

### **测试配置**

网络管理员告知我，开发环境的负载均衡设备比较老，压力测试可能会吃不住。虽然我觉得批处理单机并发数最高也不过60，应该不成问题，但在第一轮测试时，我还是搭了两套环境：其中一套完全模拟生成环境；另一套则将计算引擎使用Jar包的模式集成到批处理程序上，替换Web Service的部署模式（省去了Load Balancer）。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/batch_deployment_test1.png" alt="部署图" title="第一轮测试的两套环境" %}}

所有的服务器（计算引擎、批处理、数据库）的配置都是一样的，并且与生产环境基本相同：

| 配置项      | 值     |
| :--------- |:---------:|
| 型号        | X3850  |
| CPU个数     | 4         |
| 单个CPU核数 | 8         |
| CPU总逻辑核数 | 64         |
| 内存        | 250GB     |



下面是第一轮测试中各组测试，及每组测试下的两套环境（分别对应Web模式部署的计算引擎和Jar包部署的计算引擎）的运行配置。

<table>
   <tr>
      <td width=120 style="background-color:#F8F5EC"><b>测试组</b></td>
      <td colspan=2 style="background-color:#F8F5EC"><b>第一组测试</b></td>
      <td colspan=2 style="background-color:#F8F5EC"><b>第二组测试</b></td>
      <td colspan=2 style="background-color:#F8F5EC"><b>第三组测试</b></td>
      <td colspan=2 style="background-color:#F8F5EC"><b>第四组测试</b></td>
      <td colspan=2 style="background-color:#F8F5EC"><b>第五组测试</b></td>
      <td rowspan=2 style="background-color:#F8F5EC"><b>生产对照</b></td>
   </tr>
   <tr>
      <td style="background-color:#F8F5EC"><b>测试环境</b></td>
      <td style="background-color:#F8F5EC"><b>Web</b></td>
      <td style="background-color:#F8F5EC"><b>Jar</b></td>
      <td style="background-color:#F8F5EC"><b>Web</b></td>
      <td style="background-color:#F8F5EC"><b>Jar</b></td>
      <td style="background-color:#F8F5EC"><b>Web</b></td>
      <td style="background-color:#F8F5EC"><b>Jar</b></td>
      <td style="background-color:#F8F5EC"><b>Web</b></td>
      <td style="background-color:#F8F5EC"><b>Jar</b></td>
      <td style="background-color:#F8F5EC"><b>Web</b></td>
      <td style="background-color:#F8F5EC"><b>Jar</b></td>
   </tr>
   <tr>
      <td>测试范围</td>
      <td colspan=11><center>Job P: Step P1</center></td>
   </tr>
   <tr>
      <td>批处理时间</td>
      <td colspan=11><center>2017/10/31 月末批处理</center></td>
   </tr>
   <tr>
      <td>数据量</td>
      <td colspan=11><center>1,296,345笔</center></td>
   </tr>
   <tr>
      <td>批量提交</td>
      <td colspan=11><center>每2000笔提交一次</center></td>
   </tr>
   <tr>
      <td>并发数</td>
      <td colspan=2><center>20</center></td>
      <td colspan=2><center>30</center></td>
      <td colspan=2><center>40</center></td>
      <td colspan=2><center>50</center></td>
      <td colspan=2><center>60</center></td>
      <td><center>40</center></td>
    </tr>
   <tr>
      <td>JVM最大堆</td>
      <td colspan=2><center>1G</center></td>
      <td colspan=2><center>2G</center></td>
      <td colspan=2><center>2G</center></td>
      <td colspan=2><center>3G</center></td>
      <td colspan=2><center>3G</center></td>
      <td><center>2G</center></td>
    </tr>
</table>

### **测试结果**

测试收集到的数据中大部分没有显示出问题，比如各台服务器的内存使用、数据库AWR报告、网络负载等，因此下面不再详细列出。
但是`Step P1`中个阶段的耗时情况，以及各服务器的CPU使用率和JVM GC的情况比较有意思，下面列出来。

#### **耗时数据**

下面是各组测试`Step P1`步骤的整体耗时情况对比：
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_cost_all.png" alt="第一轮测试整体耗时" title="第一轮测试整体耗时" %}}

可以看到无论是Jar包模式部署的计算引擎还是Web Service独立服务器部署的方式，当线程数达到30时，再往上增加并发量提升性能有限；相反在Web Service模式下，当线程数超过50时，吞吐量反而会下降。
因为两种模式下，吞吐量非常接近，我们基本可以确定计算引擎服务器，及其与批处理服务器间的网络不是瓶颈（事实上这两者间的网络通信即使在并发180线程的时候也只占用了50%左右的带宽，而且计算引擎服务器资源使用率非常低）。
那么剩下来只能是批处理服务器（以及批处理程序本身）或者数据库服务器的问题了。

下面是单笔业务处理的耗时情况。回顾一下之前我们提到过每一笔业务处理的逻辑分为5个阶段，读数据库->封装XML->调用引擎->解析XML->写入数据库。我们设置了每2000笔提交一次，因此这里的每笔耗时将平摊写入数据库总耗时：
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_cost_single.png" alt="第一轮测试整体耗时" title="第一轮测试单笔业务处理平均耗时" %}}

理想状态下，提高并发量，单笔业务处理耗时不会改变。上图的20和30线程基本符合这种情况。但是从40线程以上，单笔业务处理时间开始显著增加，尤其是采用Web Service的部署模式。

让我们将上图分阶段深入挖掘一下：下面是单笔业务处理的分阶段平均耗时。其中封装XML的阶段2和解析XML的阶段4因为占用时间非常少，因此没有统计。
下图仅展示了第一阶段（读DB）、第三阶段（调引擎）和第五阶段（写DB）。写入数据库的每笔平均耗时仍旧为总耗时均摊到每笔业务处理上。
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_cost_single_segmented.png" alt="第一轮测试整体耗时" title="第一轮测试单笔业务处理平均分阶段耗时" %}}
这张图非常有意思。首先，这张图明确了主要耗时是在第一阶段（读取数据库记录并封装成Java对象）和第三阶段（调引擎）。其次，一阶段耗时随着并发量上升吞吐量下降非常明显，远高于其它几个阶段。我的第一个猜测是读取数据库记录的SQL存在问题。

#### **GC数据**

下面是GC总用时和Full GC用时图（20线程测试组未统计）：
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_gc_cost.png" alt="第一轮测试GC/Full GC用时" title="第一轮测试GC/Full GC用时" %}}

下图是GC总用时占批处理总耗时的比例（20线程测试组未统计）：
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_gc_proportion.png" alt="第一轮测试GC用时占比" title="第一轮测试GC用时占比" %}}

可见GC操作用时非常可观。下面整个`Step P1`步骤运行过程Full GC发生的次数：
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_gc_times.png" alt="第一轮测试Full GC次数" title="第一轮测试Full GC次数" %}}

我们以40线程的Web Service模式部署为例，来细看一下堆的使用情况：我们使用jstat -gcutil命令来记录GC堆的使用情况，以及GC发生次数及耗时。
随机取了一分钟的日志段，YGC（年轻代GC事件次数）增加了862，FGC（完整GC事件次数）增加了5。下表是老年代在这一分钟的使用率变化图：
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_gc_util_old.png" alt="第一轮测试一分钟内老年代占用率变化" title="第一轮测试一分钟内老年代占用率变化" %}}

如此频繁的垃圾回收，基本上可以说明堆大小不够大了。

#### **批处理服务器数据**

下面展示一下批处理服务器CPU总使用情况：
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_server_batch_cpu_total.png" alt="第一轮测试批处理服务器CPU" title="第一轮测试批处理服务器CPU" %}}
可见当并发量的上升对批处理服务器的CPU有不小的压力。iostat命令收集到的CPU统计信息显示CPU时间基本上都是在用户态上，系统太和IO等待上占比非常低，这里就不再列出。

下面是平均等待线程数，平均阻塞线程数平均基本约为0下面不展示，收集的是vmstat的r和b列的值。
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_server_batch_vmstat_r.png" alt="第一轮测试批处理服务器平均等待线程数" title="第一轮测试批处理服务器平均等待线程数 " %}}
vmstat的r列表示运行(run)队列，等待CPU调度; b列表示阻塞(block)队列，等待资源可用状态。如果运行队列超过了CPU数量，那么必然有任务进入等待。因为我们服务器有64个逻辑处理器，我想CPU虽然有压力，但是还不至于是瓶颈。

#### **数据库服务器数据**

下面是数据库服务器（两台平均）CPU使用率。
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test1_server_db_cpu_total.png" alt="第一轮测试数据库服务器CPU" title="第一轮测试数据库服务器CPU" %}}
可见数据库CPU压力比较小，另外因为vmstat反馈的运行队列和阻塞队列都很小，所以省略。

### **小节**
这轮测试可以排除计算引擎服务器, 数据库服务器以及网络导致的问题，缩小范围到批处理服务器以及批处理程序上。首先，增加JVM最大堆大小应该能解决过于频繁地GC的问题; 其次, 第一阶段和第三阶段单笔业务处理耗时，随并发量增加显著升高。从问题最严重的第一阶段着手，怀疑是SQL问题，需要进行更进一步的测试。

> 一点感受：一次性能测试中可能会发现很多问题，首先从那个最严重的问题开始优化。

## **第二轮测试：缩小范围**

在第二轮测试中，测试服务器的配置不变，部署模式采用第一轮测试Web Service方式，只进行20线程和60线程两组测试，每组仍旧是1,296,345笔业务。
我们主要收集的统计信息是处理逻辑的第一阶段的各SELECT SQL执行的次数以及平均耗时情况，以及将ResultSet转换成Java对象的用时情况。

总共涉及到如下7个SQL(表名、字段名做过修改）

| 编号    | SQL |
| :--:   | :-- |
| 1 | select * from RCM partition(P_201709) where id = ? and type = ? |
| 2 | select * from RCCM partition(P_201709) where cid = ? |
| 3 | select * from RCBC partition(P_201709) where id = ? and type = ? |
| 4 | select * from RCCM partition(P_201709) where cno in (?, ?) and rc = ? |
| 5 | select * from RDCM partition(P_201709) where id ix (?, ?) and type = ? |
| 6 | select * from RDM partition(P_201709) where id in (?, ?) and type = ? |
| 7 | select * from RCM where month <= ? and month > ? and id = ? and type = ? order by month desc |

每个SQL测试结果如下：

| 编号 | 平均每笔业务SQL执行次数 | 平均SQL执行时间(60线程) | 组装对象时间 (60线程)|  平均SQL执行时间(20线程) | 组装对象时间 (20线程)|
| :--: | :--: | :--:   | :--: | :--:   | :--: |
| 1    | 2     | 9.07 ms | **21.38 ms** | 3.51 ms | **7.72 ms**|
| 2    | 2.84  | 6.7 ms  | 3.12 ms  | 2.08 ms | 1.42 ms|
| 3    | 2.01  | 6.2 ms  | 0.86 ms  | 1.9 ms  | 0.43 ms|
| 4    | 1.8   | 3.57 ms | 0.41 ms  | 1.77 ms | 0.17 ms|
| 5    | 1.83  | 9.95 ms | 1.29 ms  | 4.6 ms  | 0.48 ms|
| 6    | 1.83  | 8.92 ms | 0.73 ms  | 3.96 ms | 0.27 ms|
| 7    | 1     | 81.56 ms| **198.59 ms**| 37.17 ms| **82.73ms**|

第一阶段总体耗时如下：

|      | 平均SQL执行时间(60线程) | 组装对象时间 (60线程)|  平均SQL执行时间(20线程) | 组装对象时间 (20线程)|
| :--: | :--: | :--:   | :--: | :--:   |
| 耗时 | 188.23 ms | 256.37 ms | 81.83 ms | 104.75 ms|

这里有几个问题需要解释一下。首先，通常用*取所有字段不是一个好主意，但是我们的确需要用到这些表的所有字段；其次，除了第7条SQL外，我们都使用了分区表查询，所有查询字段都有分区索引，并且它们都返回一条记录。
而第7条SQL将做全表查询，它将返回13条排序后的记录，这个解释了为什么它的SQL执行时间会比较长。

这里的主要问题是从ResultSet组装成Java对象的消耗异常地大，尤其是在编号1和7的SQL上（加粗部分）。那么问题应该是出在代码上了，下一步就要做代码审查了。

## **代码审查(1)**

Code Review的主要内容是第一阶段将ResultSet转换为Java对象的部分。这一般是批处理框架的一部分，但是框架本身就是自主开发的，这部分代码被写成了一些通用的方法。下面以上一小节第7条SQL为例，该条SQL返回13条结果，每条结果有110列来说明。

以下所有代码的变量名以及部分逻辑经过处理。首先我们来看SELECT语句执行后，将ResultSet转换为List<SomeObject>的过程：

```java
ResultSet rs = preparedStatement.executeQuery();
ResultSetMetaData rsmd = rs.getMetaData();
List<SomeObject> someObjects = new ArrayList<SomeObject>();
while( rs.next()){
    SomeObject someObject = new SomeObject();
    InvokeUtil.invokeClassWithMetaData( someObject, rs, rsmd);
    someObjects.add( someObject);
}
```

开发者将这个转换过程做成了通用的方法`invokeClassWithMetaData`，我们看下这个方法内部：

```java
public static void invokeClassWithMetaData( Object daoEntity, ResultSet rs, ResultSetMetaData rsmd) throws ReadingDataException {

    try{

        for( int i = 1; i <= rsmd.getColumnCount(); i++){

            String colName = rsmd.getColumnName();
            if( rs.getObject(i) != null){

                DataElement dataElement = new DataElement();
                int type = rsmd.getColumnType(i);
                if( type == Types.CHAR || type == Types.VARCHAR || type = Types.VARBINARY){

                    dataElement.setValue( rs.getString(colName));
                    dataElement.setProperty( "DataType", "String");
                }else if( type == Types.DECIMAL || type == Types.NUMERIC){

                    dataElement.setValue( rs.getDouble(colName));
                    dataElement.setProperty( "DataType", "Number");
                }

                invokeSetMethodValue( daoEntity, colName, dataElement);
            }
        }
    } catch( SQLException e){
        throw new ReadingDataException(e);
    } catch( InvokeException e){
        throw new ReadingDataException(e);
    }
}
```

在我们这个例子中每笔业务的处理`invokeClassWithMetaData`会被调用13次。`invokeClassWithMetaData`方法的第一个问题是使用没有必要的`try`。
为了给每个字段设置值，在第22行又有一个通用方法`invokeSetMethodValue`，在我们的例子中，SQL返回110个字段，也就是说这个`invokeSetMethodValue`方法在每笔业务处理时会被调用13 x 110 = 1,430次。
现在我们再来看以下`invokeSetMethodValue`：

```java
public static Object invokeSetMethodValue( Object dml, String colName, DataElement dataElement) throws InvokeException{

    String setMethodName = getSetMethodName( colName);
    String setMethodName2 = getSetMethodName2( colName);
    String realMethodName = getRealMethodName( setMethodName);
    String realMethodName2 = getRealMethodName( setMethodName2);

    if( realMethodName != null){
        try{
            Class<?>[] parameterClasses = getMethodParameter(dml, realMethodName);
            Object colValue = getObjectValue( parameterClasses[0], dataElement);
            dml.getClass().getMethod( realMethodName, parameterClasses).invoke( dml, new Object[]{colValue});
        } catch( Exception e){
            throw new InvokeException("Error occured while setting values using reflection.", e);
        }
    }

    if( realMethodName2 != null){
        try{
            Class<?>[] parameterClasses = getMethodParameter(dml, realMethodName2);
            Object colValue = getObjectValue( parameterClasses[0], dataElement);
            dml.getClass().getMethod( realMethodName2, parameterClasses).invoke( dml, new Object[]{colValue});
        } catch( Exception e){
            throw new InvokeException("Error occured while setting values using reflection.", e);
        }
    }

    return dml;
}
```

`invokeSetMethodValue`方法试图将数据库字段名字与Java对象的set方法名称配对。现在我们看下第3-6行的`getSetMethodName`, `getSetMethodName2`和`getRealMethodName`方法的实现。

```java
private static String getSetMethodName(String colName){
    if( colName == null || "".equals( colName)){
        return null;
    } else{
        return "set" + colName.subString(0, 1).toUpperCase() + colName.subString(1).toLowerCase();
    }
}
```

```java
private static String getSetMethodName2(String colName){
    if( colName == null || "".equals( colName)){
        return null;
    } else{
        return "set" + colName.toLowerCase().replaceAll("_", "");
    }
}
```

以上两个方法虽然很简单，但是也会同样地被调用1,430次。这里的String操作方法像substring都是有O(n)时间复杂度的，也许会带来一定的消耗?

```java
private static String getRealMethodName(Object object, String methodName){
    List<Method> methods = getObjectAllMethods( object);
    for( int i = 0; i < methods.size(); i++){
        Method method = methods.get( i);
        if( method.equalsIgnoreCase( method.getName())){
            return method.getName();
        }
    }

    return null;
}
```

`getRealMethodName`找到对象的的set方法的名字，然后返回给调用者`invokeSetMethodValue`. 我们看下它的第二行`getObjectAllMethods`的实现。

```java
public static List<Method> getObjectAllMethods(Object object){
    
    List<Method> methodList = new ArrayList<Method>();
    Class<?> c = object.getClass();
    Method[] methods = c.getMethods();
    for(Method method : methods){
        methodList.add( method);
    }

    return methodList;
}
```

首先，我觉得是不是可以用`Arrays.asList(methods)`来代替上面那串循环, 这样可以干净很多；其次, 因为我们的结果集有110列，那么意味着对应的Java对象也有110个get方法和set方法。所以当上面这个`getObjectAllMethods`返回一个列表给`getRealMethodName`方法时，这个列表的大小是220。 如果你回过去看`getRealMethodName`方法里的for循环, 每笔业务处理它会发生1,430 x 220 = 314,600次。 

最后，我们回到`invokeSetMethodValue`方法的第10行和第20行的`getMethodParameter`调用。这个方法迭代这个220个方法列表返回方法的`method.getParameterTypes()`，具体代码没有贴出来，但是在最坏的情况下每笔业务`getParameterTypes`会被调用314,600 次。

回到我们最初的入口：
```java
ResultSet rs = preparedStatement.executeQuery();
ResultSetMetaData rsmd = rs.getMetaData();
while( rs.next()){
    SomeObject someObject = new SomeObject();
    InvokeUtil.invokeClassWithMetaData( someObject, rs, rsmd); // This line causes the whole problem..
}
```

我想我们遇到的问题是，对于每一笔要处理的业务，上面SQL的ResultSet可能需要超过629k次方法调用来完成将数据放到一个Java对象中。这个估算非常地粗略，但是我像可以解释为什么第一阶段要花这么多时间。对于我们测试的数据来讲，共有1,296,345笔业务，那么第一阶段读取数据库这部分可能需要发生的方法调用次数可能达到万亿级别。

对于这个问题的解决方法也许就是非常简单的直接调用set方法，而不是用那么多的反射调用。下面是一个非常原始的将ResultSet方法转换为Java对象的做法：

```java
rs = preparedStatement.executeQuery();
List<SomeObject> someObjects = new ArrayList<SomeObject>();
while( rs.next()){
    someObjects.add( getSomeObject( rs));
}
```

```java
private SomeObject getSomeObject( ResultSet rs) throws SQLException{
    SomeObject someObject = new SomeObject();
    someObject.setAttribute1( rs.getString("attribute1"));
    someObject.setAttribute2( rs.getString("attribute2"));
    //..............
    return someObject;
}
```

上面这个方案当然有它的缺点。首先，这个代码不是通用的。你必需为每一个对象写一个`getSomeObject()`；其次, 它非常不灵活。如果你要添加或者删除一个数据库字段，那么你也需要改代码。我相信现在那些个开源的持久化框架也许可能会有更优雅更高效地解决方案，并且如果如果我被要求重新写一下这个批处理程序的化，我一定会去研究一下。但是现实是，系统上线这些年来，批处理数据库对象总共也只有个位数个，所以我想还是让修改方案保持简单些吧。

> 一点感受：从第二轮测试中我们可以看到其实完成一笔业务也只有几百毫秒，如果这是一个交易量不大的实时系统，这完全可以接受；但是如果是一个要处理百万量级业务、并且有时间要求的批处理程序，那么即使每笔业务多花几毫秒，也是非常可怕的。

## **第三轮测试：方案验证**

按照上一小节的优化方案实施后，我们进行了第三轮测试。测试环境部署同第一轮测试Web部署模式。测试分为5组，从30并发线程数到70并发线程数（如下表所示）。为了不引入第二个变量，我特意没有调整最大堆大小。这点优化我们稍后再做。

<table>
   <tr>
      <td style="background-color:#F8F5EC"><b>第三轮测试</b></td>
      <td style="background-color:#F8F5EC"><b>第一组</b></td>
      <td style="background-color:#F8F5EC"><b>第二组</b></td>
      <td style="background-color:#F8F5EC"><b>第三组</b></td>
      <td style="background-color:#F8F5EC"><b>第四组</b></td>
      <td style="background-color:#F8F5EC"><b>第五组</b></td>
   </tr>
   <tr>
      <td>测试范围</td>
      <td colspan=5><center>Job P: Step P1</center></td>
   </tr>
   <tr>
      <td>批处理时间</td>
      <td colspan=5><center>2017/10/31 月末批处理</center></td>
   </tr>
   <tr>
      <td>数据量</td>
      <td colspan=5><center>1,296,345笔</center></td>
   </tr>
   <tr>
      <td>批量提交</td>
      <td colspan=5><center>每2000笔提交一次</center></td>
   </tr>
   <tr>
      <td>并发数</td>
      <td>30</td>
      <td>40</td>
      <td>50</td>
      <td>60</td>
      <td>70</td>
    </tr>
   <tr>
      <td>JVM最大堆</td>
      <td>2G</td>
      <td>2G</td>
      <td>3G</td>
      <td>3G</td>
      <td>4G</td>
    </tr>
</table>

### **耗时数据**
下面是优化前后的总体耗时情况对比。在线程数30的测试组中，优化更新以后（红色线）比优化更新前耗时减少了116分钟（44%），而且这个优势随着线程数增加更加明显。
我们注意到随着线程数提高，优化后的批处理程序整体用时呈下降趋势，与原先的情况形成明显对比；但我们也注意到并发数在40线程以后，增加并发量对于吞吐量的提升不太明显，也许暗示着存在其它瓶颈？

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_cost_all.png" alt="Total time used  (minutes)" title="Total time used  (minutes)" %}}

下图显示单笔业务处理的平均耗时情况，红色是优化前，蓝色是优化后。可以得出和上面那张总耗时类似的结论。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_cost_single.png" alt="Average time used for processing one item (ms)" title="Average time used for processing one item (ms)" %}}

下图是第一阶段（也就是读数据库并组装Java对象的阶段）的优化前后耗时对比，注意途中的Step 1是指第一阶段而不是批处理作业中的一个步骤，下面Step 3/5也是一样。我们的优化方案其实就是针对这一阶段的，用时下降了6(30线程)-16倍(60线程)之多。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_cost_single_segmented1.png" alt="Time used for step 1 (ms)" title="Time used for step 1 (ms)" %}}


下面两张图是第三阶段（调用引擎和写数据库）的优化前后耗时对比。我们没有对此步骤进行优化，但有意思的是它们的用时似乎也减少了。
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_cost_single_segmented3.png" alt="Time used for step 2 (ms)" title="Time used for step 2 (ms)" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_cost_single_segmented5.png" alt="Time used for step 3 (ms)" title="Time used for step 3 (ms)" %}}

### **GC数据**
下图三张图分别是Full GC次数、GC总用时以及GC用时占总批处理时间比例的更新前后对比。图中可见尽管我们没有调整堆大小，但是我们减少了很多对象创建和销魂的过程，Full GC次数和耗时减少了超过一半。
同样我们也注意到，GC用时比例仍旧非常高，这应该在提高堆大小后得到解决。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_gc_times.png" alt="Full GC Count" title="Full GC Count" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_gc_cost.png" alt="Time used for GC (minutes)" title="Time used for GC (minutes)" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_gc_proportion.png" alt="GC cost / total cost" title="GC cost / total cost" %}}

### **服务器数据**
下面两张图为批处理服务器的CPU利用率变化以及运行队列长度的变化。可见批处理服务器压力大幅减少。
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_server_batch_cpu_total.png" alt="批处理服务器CPU利用率变化" title="批处理服务器CPU利用率变化" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_server_batch_vmstat_r.png" alt="批处理服务器运行队列长度变化" title="批处理服务器运行队列长度变化" %}}

下面两张图为数据库服务器的CPU利用率变化以及运行队列长度的变化。数据库服务器压力出现上升。
{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_server_db_cpu_total.png" alt="数据库服务器CPU利用率变化" title="数据库服务器CPU利用率变化" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test3_server_db_vmstat_r.png" alt="数据库服务器运行队列长度变化" title="数据库服务器运行队列长度变化" %}}

### **小节**

在第三轮测试中，我们证明了之前代码审查后的优化是有效的。对于40个线程的并发模式来说，`Step P1`的用时从4小时降到了2个小时。除了调整堆大小这点优化还没有实施以外，这轮测试也提示了还存在潜在的问题：因为我们看到了“增加并发量对于吞吐量的提升不太明显”这一情况。我想可以研究一下，第三阶段的代码，因为现在第三阶段的耗时占比最大了。如果第一阶段的代码是有缺陷的，那么其它地方可能也存在同样的问题。

## **分布式批处理方案**
在我们继续深入挖掘代码中存在的问题之前，我想先考虑一下横向扩展的可能性。因为毕竟单台机器处理能力有限，再怎么进行代码优化也是有极限的。而如果能通过简单地增加服务器的方式支持业务量持续增长的话，那么这个问题才能得到真正的解决。

因为批处理框架本身支持多线程方式运行，我们先来研究一下它是如何给多个线程分配任务的。

首先，每一笔待处理的业务都有一个独一无二的编号；根据业务编号对待处理的数据排序，然后根据rownum按比例分配到n个线程上。

```sql
select * from 
  (select rownum as rn, inner.* from  
    ( select * from master_table order by business_id) inner 
   where rownum < ?) outer 
where outer.rn >= ? 
```

上面`select * from master_table order by business_id`部分表示的获取实际的业务数据的SQL，外面的两层SELECT将筛选，并选取最里层排序后的部分数据。实际使用当中把星号换成需要的字段。

假设说我们有两个线程，要处理下面10笔（伪造的）master_table里的数据：

| business_id | attribute1 |
| :-- | :-- |
| 20180602214300000001 | 100.000000|
| 20180602214300000002 | 100.000000|
| 20180602214300000003 | 100.000000|
| 20180602214300000004 | 100.000000|
| 20180602214300000005 | 100.000000|
| 20180602214300000006 | 100.000000|
| 20180602214300000007 | 100.000000|
| 20180602214300000008 | 100.000000|
| 20180602214300000009 | 100.000000|
| 20180602214300000010 | 100.000000|

对于第一个线程来说，它将上述SQL第一个参数设置为1，第二个参数设置为6，那么它将取到以下待处理的业务：

| rn | business_id | attribute1 |
| :-- | :-- | :-- |
| 1 | 20180602214300000001 | 100.000000|
| 2 | 20180602214300000002 | 100.000000|
| 3 | 20180602214300000003 | 100.000000|
| 4 | 20180602214300000004 | 100.000000|
| 5 | 20180602214300000005 | 100.000000|

而对于第二个线程来说，它将上述SQL第一个参数设置为6，第二个参数设置为11，那么它将取到以下待处理的业务：

| rn | business_id | attribute1 |
| :-- | :-- | :-- |
| 6 | 20180602214300000006 | 100.000000|
| 7 | 20180602214300000007 | 100.000000|
| 8 | 20180602214300000008 | 100.000000|
| 9 | 20180602214300000009 | 100.000000|
| 10 | 20180602214300000009 | 100.000000|


上面每个线程取数据的上边界和下边界可以根据线程编号、线程总数和业务数据总量来自动计算。既然能将任务分配给多线程，那么我们也可以实现多进程的同时处理。只要给进程也加上进程编号，和进程总数即可。
在单个进程我们使用下面的SQL取业务数据：

```sql
select * from master_table order by business_id
```

在多个进程中，我们对上述SQL稍作修改：

```sql
select * from master_table 
 where mod( substr( business_id, length(business_id) - 3, 3), ?) = ?
 order by business_id
```

因为我们的business_id是一个20位的纯数字字符串，我们取它最后三位数字，然后与第一个参数(进程总数)取模，当模等于第二个参数(进程编号)时，这部分取出来的数据就是该进程需要处理的数据。
然后再用前面那种两层rownum的方法，将这部分数据再次分配给进程中的多个线程去处理。因为业务编号是顺序分配的，这种分配方法可以近似平均的将全量数据分配给所有工作进程。
虽然，这条SQL执行时可能会慢一点，但是每个进程只要执行一次，是可以接受的。

我们的目的是验证将单机单进程改造成多台服务器上的多进程批处理是否能够提升性能。因此上述修改只需要对原有程序做很小的改动，在批处理的配置文件里加上进程编号和进程总数的参数，然后修改一下查询SQL。
而在将来对批处理程序进行改造的时候，还需要考虑分布式协助问题，比如如果一台服务器崩溃了的情况等等。但就目前的性能测试用途而言，这样修改就足够了。

## **代码审查(2)**

在验证我们的分布式批处理方案之前，还需要对第三轮测试提出的一些问题进行分析。第三轮压力测试我们怀疑`Step P1`每笔业务处理的第三阶段(调用引擎)存在问题，而第三阶段主要就是调用一个Web Service接口。
我抛开批处理程序，用SoapUI做了一下压力测试，发现接口平均响应时间在20-30ms。前几轮测试显示100-30ms显然是有问题了。

我翻了一下代码，发现调用Web Service接口用的是比较老的Apache Axis。比较奇怪的是，批处理框架对这个远程调用做了好几层封装，最后变成了一个叫做ClientService类。下面是简化版的调用过程：

```java
public class ClientService{

    public String callEngine(String req){
        
        Service  service = new Service();
        Call call = (Call) service.createCall();
        call.setTargetEndpointAddress(new URL(...));
        ...
        return ret = (String) call.invoke( new Object[] { req } );
    }
}


```

在每一笔业务处理的时候，都会执行上述代码。虽然我没使用过Axis，但是逻辑上讲，接口调用是无状态的，这里唯一的变量就是req(请求报文)，所以我想很多初始化工作似乎是重复的。

因此我在批处理程序启动的时候，创建n个ClientService对象，把这部分初始化工作完成，然后把这n个对象放到一个LinkedBlockingQueue里面，每个线程要用的时候take一个用完再put进去。

线程在调用的时候只要执行，下面这个行代码就可以了。

```java
(String) call.invoke( new Object[] { req } );
```

实际上会比这里的描述地要复杂一些，但是大体上如此。

## **第四轮测试：最终对比**

### **测试配置**

第四轮测试的部署架构如下

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/batch_deployment_test4.png" alt="第四轮两组测试的部署图" title="第四轮两组测试的部署图" %}}

这次我们将批处理应用和计算引擎在三台服务器上均部署，对计算引擎的调用仍旧走负载均衡设备，由它再次分发到三台机器的计算引擎接口上，数据库调用方式不变。机器的配置情况不变。

第四轮的测试分两组，每组均采用三机，每机单进程50线程方式运行，数据量仍旧是1,296,345。下面我们将测试结果与其他几轮测试结果，共四组，进行横向比较。

在第四轮测试前，已经完成了一次代码评审以及优化，并进行了优化前后的压力测试：

1. (优化前)优化前的程序；
2. (优化1)第一次代码审查优化后的程序。

第四轮测试分两组，分别是

1. (优化1+2)在第一次代码审查的优化基础上，将批处理程序按照前面分布式批处理的方案；
2. (优化1+2+3)包括分布式批处理等之前所有优化的基础上，调整了堆大小限制到16GB，同时对Axis客户端代码进行了复用。

### **测试结果**

#### **耗时数据**

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_cost_all.png" alt="各组优化后总耗时横向对比" title="各组优化后总耗时横向对比" %}}

上图最左边数据是优化前单机单进程50线程的`Step P1`步骤的用时，大约4个小时；第二个数据是优化了ResultSet转换为Java对象的代码后的单机单进程50线程的`Step P1`用时，大约1.8小时；
第三个数据是改成三台服务器，每台单进程50线程以后的`Step P1`用时，大约42分钟；最后一个数据是优化了接口调用和JVM堆大小后的用时，同样是三台服务器，每台50线程，大约15分钟。从247分钟到15分钟，速度提升了超过16倍。

我们再来看下单笔调用耗时情况：

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_cost_single.png" alt="单笔平均耗时横向比较" title="单笔平均耗时横向比较" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_cost_single_segmented.png" alt="单笔分阶段平均耗时横向比较" title="单笔分阶段平均耗时横向比较" %}}

第一次优化后单笔调用速度有显著提升，主要是因为对读数据库阶段的优化；第二阶段改为分布式调用后，三台服务器分别有50个线程同时运行，单笔速度反而略有下降；第三次优化后，调用接口速度得到了显著提升，同时因为调整了JVM堆大小，其它阶段也有相应的提升。

#### **GC数据**

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_gc_cost.png" alt="Full GC / 总GC耗时对比" title="Full GC / 总GC耗时对比" %}}

上图中优化前和优化1均是一台服务器运行批处理的GC用时，后两者则是三台服务器的平均值（下同）。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_gc_times.png" alt="Full GC发生次数对比" title="Full GC发生次数对比" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_gc_proportion.png" alt="GC所用时间占批处理全部时间比例" title="GC所用时间占批处理全部时间比例" %}}

#### **批处理服务器数据**

由于分布式批处理测试的时候，计算引擎和批处理分别都部署在同样的三台服务器上。在优化前和优化1的方案中单进程50线程批处理计算分摊到两台计算引擎服务器，而现在则是150个线程分摊到三台服务器上，压力也有所提升。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_server_batch_cpu_total.png" alt=对比"批处理服务器CPU利用率" title="批处理服务器CPU利用率对比" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_server_batch_vmstat_r.png" alt="批处理服务器运行队列长度对比" title="批处理服务器运行队列长度对比" %}}

#### **数据库服务器数据**

与耗时减少相反的是，数据库的压力逐次增大，也说明了压力逐渐从批处理服务器转移到数据库上。

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_server_db_cpu_total.png" alt="数据库服务器CPU利用率" title="数据库服务器CPU利用率" %}}

{{% figure class="center" src="/images/java-batch-performance-tuning-chn/result_test4_server_db_vmstat_r.png" alt="数据库服务器运行队列长度对比" title="数据库服务器运行队列长度对比" %}}

## **总结**

我们总共进行了四处优化：

1. 批处理ResultSet转换到Java对象的方式；
2. 批处理Web Service接口调用；
3. 调整了JVM堆大小的参数；
4. 将批处理改成了分布式处理。

从吞吐量来看，原本247分钟处理1,296,345，约合87.47TPS；现在是15.33分钟处理同样多的数据，约合1409.38TPS，提升16倍。
而且更重要的是，我们证明了我们的方案可以支持横向扩展。从目前数据库的压力来看，还可以进一步提高并发数。







