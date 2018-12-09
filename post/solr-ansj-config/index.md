Solr可以检索很多种类的原始数据，而在这篇文章中，笔者的业务场景是检索数据库中大量的记录，也因为此，我们希望将自定义词库、同义词库等一并放入到数据库中而不是以默认的文本形式存放。

同时，我们选择ANSJ作为中文分词器，一是它的分词速度和准确性不错，二是它支持从文本、数据库等来源加载自定义词库，三是它支持词性标注（本文暂时中不会用到这点）。

我们将使用`Solr 7.3.1`和`ANSJ 5.1.6`，数据库使用的是MySQL 5.7.12以及Oracle 11g，操作系统为Ubuntu 16/Redhat。网上很多文章介绍的还是Solr 4或者Solr 5版本，但是Solr 6以后发生了很多变化，笔者在查找相关技术资料的时候饶了些弯路，所以特此记录下来。

我们首先介绍Solr和ANSJ的整合，然后是在Solr中引入Data Importer从数据库中导入数据，配置自定义此词库和同义词库，之后是扩展Solr的RequestHandler来实现ANSJ自定义词库的动态更新，最后是扩展Solr的SynonymGraphFilterFactory来实现从数据库中加载同义词库。

这篇文章不会介绍如何在Tomcat或其它服务器上部署Solr（我们内置的Jetty服务器），这篇文章也不会涉及到Solr集群。

<!--more-->

# 1 Solr和ANSJ整合

## 1.1 基本工具准备

1. 从官网下载并解压Solr的[压缩包](http://lucene.apache.org/solr/)；
2. ansj_seg，可以使用下面的Maven依赖，或者直接从Maven仓库下载[Jar包](http://central.maven.org/maven2/org/ansj/ansj_seg/5.1.6/ansj_seg-5.1.6.jar)
   
    ```xml
    <!-- https://mvnrepository.com/artifact/org.ansj/ansj_seg -->
    <dependency>
        <groupId>org.ansj</groupId>
        <artifactId>ansj_seg</artifactId>
        <version>5.1.6</version>
    </dependency>
    ```
3. nlp-lang，这是ANSJ依赖的自然语言处理包，下面是Maven依赖，或者直接下载[Jar包](http://central.maven.org/maven2/org/nlpcn/nlp-lang/1.7.7/nlp-lang-1.7.7.jar)
   
    ```xml
    <!-- https://mvnrepository.com/artifact/org.nlpcn/nlp-lang -->
    <dependency>
        <groupId>org.nlpcn</groupId>
        <artifactId>nlp-lang</artifactId>
        <version>1.7.7</version>
    </dependency>
    ```
4. ansj_lucene7_plug。Lucene是Solr用于对数据构建索引、检索等的核心模块，这里是一个很小的插件，用于将ansj适配到lucene上。[Jar包](http://central.maven.org/maven2/org/ansj/ansj_seg/5.1.6/ansj_seg-5.1.6.jar)
  
    ```xml
    <!-- https://mvnrepository.com/artifact/org.ansj/ansj_seg -->
    <dependency>
        <groupId>org.ansj</groupId>
        <artifactId>ansj_seg</artifactId>
        <version>5.1.6</version>
    </dependency>
    ```

下面我们进入Solr压缩包解压后的根目录，下文我用./表示这个根目录。大概长这样：

```shell
james@ubuntu:/app/solr-7.3.1$ ll
total 1572
drwxr-xr-x  9 james james   4096 May  9 09:31 ./
drwxr-xr-x  4 james root    4096 Jun 11 07:00 ../
drwxr-xr-x  3 james james   4096 May  9 09:31 bin/
-rw-r--r--  1 james james 791609 May  9 09:31 CHANGES.txt
drwxr-xr-x 12 james james   4096 May  9 09:31 contrib/
drwxr-xr-x  4 james james   4096 May  9 09:31 dist/
drwxr-xr-x  3 james james   4096 May  9 09:31 docs/
drwxr-xr-x  7 james james   4096 May  9 09:31 example/
drwxr-xr-x  2 james james  36864 May  9 09:31 licenses/
-rw-r--r--  1 james james  12872 May  9 09:31 LICENSE.txt
-rw-r--r--  1 james james 689623 May  9 09:31 LUCENE_CHANGES.txt
-rw-r--r--  1 james james  25453 May  9 09:31 NOTICE.txt
-rw-r--r--  1 james james   7679 May  9 09:31 README.txt
drwxr-xr-x 10 james james   4096 May  9 09:31 server/
```

我们要把上面的三个Jar包复制到`./server/solr-webapp/webapp/WEB-INF/lib`目录下。在这个目录下你还能找到许多被Solr所使用的jar包，包括一会儿我们要用到的`solr-core-7.3.1.jar`以及很多lucene的包。

## 1.2 启动Solr

我们回到./bin目录下来启动Solr：`./solr start -p 8983`。这里的参数p指定了Solr运行的端口，下面是启动成功的输出。如果你使用的是root用户，出于安全考虑，Solr会要求你增加`-force`参数来强制启动。

```shell
james@ubuntu:/app/solr-7.3.1/bin$ ./solr start -p 8983
*** [WARN] *** Your open file limit is currently 1024.  
 It should be set to 65000 to avoid operational disruption. 
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 3643. 
 It should be set to 65000 to avoid operational disruption. 
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
Waiting up to 180 seconds to see Solr running on port 8983 [-]  
Started Solr server on port 8983 (pid=3181). Happy searching!
```

我们可以在浏览器中看到Solr的控制面板：

{{% figure class="center" src="/images/solr-ansj-config/solr-started.png" alt="Solr控制面板" title="Solr控制面板"  %}}

## 1.3 创建核心

使用Solr自带的配置模板sample_techproducts_configs来创建一个核心，命令如下。`-c`参数是核心的名字，`-d`表示配置文件目录。

```shell
james@ubuntu:/app/solr-7.3.1/bin$ ./solr create_core -c cssename -d sample_techproducts_configs

Created new core 'cssename'
```

或者也可以使用默认的模板_default来创建一个核心，命令如下。

```shell
james@ubuntu:/app/solr-7.3.1/bin$ ./solr create_core -c csscname -d _default
WARNING: Using _default configset with data driven schema functionality. NOT RECOMMENDED for production use.
         To turn off: bin/solr config -c csscname -p 8983 -property update.autoCreateFields -value false

Created new core 'csscname'
```

创建完以后，刷新Solr控制台，在左侧的Core Selector中选择我们刚刚创建好的`cssename`核心。在出来的菜单里，选择`Query`，然后点击下方蓝色的`Execute Query`，如下图所示：

{{% figure class="center" src="/images/solr-ansj-config/solr-core-created.png" alt="Solr核心创建成功" title="Solr核心创建成功"  %}}

注意看到右侧的返回结果，`"numFound":0`表示Solr没有找到任何结果。当然应该如此，因为我们还没有添加任何数据。稍后再下一节中，我们会引入DataImporter来导入数据。

```json
{
  "responseHeader":{
    "status":0,
    "QTime":34,
    "params":{
      "q":"*:*",
      "_":"1528730693354"}},
  "response":{"numFound":0,"start":0,"docs":[]
  }}
```

## 1.4 切换为schema.xml

接下来，找到刚刚创建的`cssename`核心的目录，它在./server/solr/cssename下面。进入它的配置目录`./server/solr/cssename/conf`。由于我们是通过sample_techproducts_configs的配置文件创建的核心，而sample_techproducts_configs使用的是managed schema，如果想手动修改配置文件，我们需要做一下小改动。

首先停止Solr服务：

```shell
james@ubuntu:/app/solr-7.3.1$ ./bin/solr stop -all
Sending stop command to Solr running on port 8983 ... waiting up to 180 seconds to allow Jetty process 3181 to stop gracefully.
```

根据[官方文档](https://lucene.apache.org/solr/guide/6_6/schema-factory-definition-in-solrconfig.html)，我们先将managed-schema文件重命名成schema.xml:

```shell
james@ubuntu:/app/solr-7.3.1/server/solr/cssename/conf$ mv managed-schema schema.xml
```

然后在同一个目录下找到solrconfig.xml，移除里面的ManagedIndexSchemaFactory定义（如果有的话），接着添加一个schemaFactory的定义：

```xml
 <schemaFactory class="ClassicIndexSchemaFactory"/>
```

最后启动Solr：
```
james@ubuntu:/app/solr-7.3.1$ ./bin/solr start 
*** [WARN] *** Your open file limit is currently 1024.  
 It should be set to 65000 to avoid operational disruption. 
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
*** [WARN] ***  Your Max Processes Limit is currently 3643. 
 It should be set to 65000 to avoid operational disruption. 
 If you no longer wish to see this warning, set SOLR_ULIMIT_CHECKS to false in your profile or solr.in.sh
Waiting up to 180 seconds to see Solr running on port 8983 [\]  
Started Solr server on port 8983 (pid=5618). Happy searching!
```

## 1.5 配置ANSJ

在配置中文分词器前，我们先测试下分词功能。进入左侧`Analysis`菜单，在`Analyse Fieldname / FieldType:`中选择`text_general`，然后在`Field Value(Index)`或者`Field Value(Query)`中分别试着输入一些英文和中文短语。

{{% figure class="center" src="/images/solr-ansj-config/solr-analysis1.png" alt="配置中文分词器前的英文分词结果" title="配置中文分词器前的英文分词结果"  %}}

{{% figure class="center" src="/images/solr-ansj-config/solr-analysis2.png" alt="配置中文分词器前的中文分词结果" title="配置中文分词器前的中文分词结果"  %}}

我们可以看到Solr自身可以对简单的英文进行分词，但是默认情况下对中文没有效果。

再次打开schema.xml文件，然后增加一个fieldType的定义，这里的名字text_ansj可以自己取，用来表示字段类型名称，里面分别是构建索引时的分词器以及检索时的分词器，我们都指定为ANSJ。注意设置参数type的值，索引使用`index_ansj`（分词粒度更细）， 查询为`query_ansj`（分词粒度粗），这个会传递给ANSJ。如果不设置这个参数，ANSJ将使用默认模式，不会加载用户自定义词库。

```xml
  <fieldType name="text_ansj" class="solr.TextField" positionIncrementGap="100">  
    <analyzer type="index">  
         <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="index_ansj"/>  
    </analyzer>  
    <analyzer type="query">  
        <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="query_ansj"/>  
    </analyzer>  
  </fieldType>
```

还是在schema.xml里面，我们增加一个索引字段，这个字段表示的是数据。注意将type类型指定为我们刚刚定义的`text_ansj`类型。

```xml
<field name="cname" type="text_ansj" indexed="true" stored="true"/>  
```

配置完后，重启Solr，进入控制面板，选择核心cssename，确保没有看到任何报错信息。然后再次进入Analysis标签页，测试一下之前输入过的测试短语。如果配置没有问题，将会看到下面的输出：

{{% figure class="center" src="/images/solr-ansj-config/solr-analysis3.png" alt="配置中文分词器后的中文分词结果" title="配置中文分词器后的中文分词结果"  %}}

注意图中的详细输出，除了将短语`你好中国`正确的切分成了`你好`和`中国`两个词外，旁边的AT表示这个输出结果是ANSJ分词器产生的，然后ANSJ还给出了type（词性）字段，其中ns词性表示的是地名。

# 2 从数据库导入数据

## 2.1 基本工具准备

数据导入需要两个Solr自带的jar包，我们要把它们移动到Solr会自动加载的位置。我们先回到Solr的根目录，然后执行下面命令：

```shell
james@ubuntu:/app/solr-7.3.1$ cp ./dist/solr-dataimporthandler-7.3.1.jar ./server/solr-webapp/webapp/WEB-INF/lib/solr-dataimporthandler-7.3.1.jar
james@ubuntu:/app/solr-7.3.1$ cp ./dist/solr-dataimporthandler-extras-7.3.1.jar ./server/solr-webapp/webapp/WEB-INF/lib/solr-dataimporthandler-extras-7.3.1.jar
```

然后根据你的数据库类型，需要相应的JDBC驱动。比如笔者的两套环境分别是

1. Oracle 11g + JDK8：相应的JDBC驱动程序ojdbc8.jar, ojdbc8_g.jar, ojdbc8dms.jar, ojdbc8dms_g.jar, simplefan.jar等都放入`public class SolrJdbcReader implements JdbcReader {./server/solr-webapp/webapp/WEB-INF/lib/`目录下。
2. MySQL 5.7 + JDK8：相应的JDBC驱动程序mysql-connector-java-8.0.11.jar放入./server/solr-webapp/webapp/WEB-INF/lib/目录下。

## 2.2 准备数据

在数据库中准备好数据，以MySQL数据库为例，我们创建一张非常简单的表存放一些公司名称。
```sql
create database cssename;

use cssename;

create table cssename.cname (
    cid int,
    cname varchar(200)
);
```

然后用程序批量的插入一些测试数据。

## 2.3 配置数据源

在cssename核心的配置文件目录下(./server/solr/cssename/conf)，创建一个叫做data-config.xml的文件，然后在里面定义我们的数据源：

```xml
<?xml version="1.0" encoding="UTF-8"?>

<dataConfig>
  <!--可以配置多个数据源，下面一个是MySQL的配置，一个是Oracle的配置-->
  <dataSource name="MySQL120"
    type="JdbcDataSource"
    driver="com.mysql.jdbc.Driver"
    url="jdbc:mysql://192.168.0.120:3306/cssename?serverTimeZone=UTC"
    user="mysql"
    password="******" 
  />
  <dataSource name="Oracle120"
    type="JdbcDataSource"
    driver="oracle.jdbc.driver.OracleDriver"
    url="jdbc:oracle:thin:@192.168.0.120:1521/orcl"
    user="oracle"
    password="******" 
  />
  <document>
    <entity dataSource="MySQL120" 
        name="cname" 
        pk="id" query="SELECT cid, cname FROM cname">
        <!--column字段为数据库中的字段名，name字段为schema中定义的字段名-->
        <field column="cid" name="id"/>
        <field column="cname" name="CNAME"/>
    </entity>
  </document>

</dataConfig>
```

然后修改同一个配置目录下的solrconfig.xml文件，添加一个requestHandler。这个handler用到的是我们刚刚添加的dataImporter的jar包。

```xml
<requestHandler name="/dataimport" class="org.apache.solr.handler.dataimport.DataImportHandler">
    <lst name="defaults">
      <str name="config">data-config.xml</str>
    </lst>
</requestHandler>
```

## 2.4 导入数据

进入Solr的控制台，选择cssename下面的Dataimport标签（建议使用Chrome/Firefox等浏览器，IE10会有兼容性问题）。

如果上面配置没有问题，则可以看到下面截图所示的界面。在Command下面选择full-import，勾选Clean和Commit，Entity选择我们数据源中配置的cname。

{{% figure class="center" src="/images/solr-ansj-config/solr-dataimport1.png" alt="数据导入配置成功后界面" title="数据导入配置成功后界面"  %}}

最后点击Execute按钮，导入速度非常快，同时你可以点击Refresh Status查看导入进度。下面显示的是导入完成后的提示。我们导入了223,617个文档。

{{% figure class="center" src="/images/solr-ansj-config/solr-dataimport2.png" alt="数据成功导入后界面" title="数据成功导入后界面"  %}}

下面我们测试一下导入的数据。回到Solr控制台cssename核心下的Query标签，在q中输入查询条件，比如`cname:xxx`（这里xxx为cname字段上的存储的某条记录或者近似的内容），如果数据成功导入，我们可以查询到数据。下面是我们查询`cname:宁波市第二医院`的结果：

{{% figure class="center" src="/images/solr-ansj-config/solr-dataimport3.png" alt="查询结果" title="查询结果"  %}}

# 3 通过数据库加载ANSJ的自定义词库

我们将把全国的行政区划名称放入到数据库里，作为ANSJ的自定义词库在其初始化的时候加载。ANSJ自身已经提供数据库加载自定义词库的功能，只需要做好配置即可。

我们先看一下如果没有配置自定义词库，对地名的分词结果。同样在Analysis的标签下，我们在索引和查询文本框中分别输入`宁波市鄞州区首南街道`，下面是结果：

{{% figure class="center" src="/images/solr-ansj-config/solr-ansj-userdefined1.png" alt="配置自定义词库前的地名分词结果" title="配置自定义词库前的地名分词结果"  %}}

可见默认情况下ANSJ可以识别出`宁波市`，但是对于`鄞州区`以及下面的街道就完全不认识了。

## 3.1 导入数据库

下面我们先定义存放自定义词库的表，其中aname是自定义此，nature是词性，freq是词频，后两者可以不存，ANSJ会使用默认的userDefine词性和1000词频。然后我们导入全国行政区划库（可以从国家统计局网站爬取）。

```sql
create table cssename.area (
    aname varchar(200),
    nature varchar(10),
    freq int
);
```

## 3.2 配置自定义词库来源

进入`./server/solr-webapp/webapp/WEB-INF/classes`目录（如果classes目录不存在则创建一个），然后新建ANSJ的配置文件`ansj_library.properties`。在这个配置文件里面加入下面的配置：

```config
dic=jdbc://jdbc:mysql://192.168.0.120:3306/cssename?serverTimeZone=UTC|username|password|select aname as name, nature, freq from cssename.area
```

ANSJ会用`|`符号分割上面的配置，得到四个参数，分别是一个以`jdbc://`开头的数据库链接字符串，数据库用户名，数据库密码，和查询SQL。

## 3.3 测试

配置完成后重启Solr，然后再次输入`宁波市鄞州区首南街道`。下面是分词结果：

{{% figure class="center" src="/images/solr-ansj-config/solr-ansj-userdefined2.png" alt="配置自定义词库后的地名分词结果" title="配置自定义词库后的地名分词结果"  %}}

注意索引的分词和查询的分词是不一样的。回顾一下我们的配置Solr`text_ansj`字段类型：

```xml
  <fieldType name="text_ansj" class="solr.TextField" positionIncrementGap="100">  
    <analyzer type="index">  
         <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="index_ansj"/>  
    </analyzer>  
    <analyzer type="query">  
        <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="query_ansj"/>  
    </analyzer>  
  </fieldType>
```

索引处用的是`index_ansj`，所以它给出了最细粒度的分词结果，比如`鄞州区`给出了`鄞州`和`鄞州区`（因为我导入的词库里两者都有）；而查询用的是`query_ansj`，因此返回最粗粒度的结果。


# 4 通过Solr来更新ANSJ的自定义词库

在上一节中我们预定义了一批行政区划名称库，这些词作为用户自定义词在ANSJ类被静态初始化的时候加载。

我们也希望能供让用户动态添加自定义词，并且持久化到数据库中。一方面，ANSJ本身是支持编程的方式修改词典，另一方面我们看到Solr对外暴露了基于HTTP协议的API接口来修改其配置文件。

所以通过Solr的HTTP API来更新ANSJ自定义词库的方式是可行的。这一节我们会继承Solr的RequestHandlerBase来实现这一功能。

## 4.1 准备存放自定义词库的表

首先我们创建一张表用来存放自定义词库，和上面的area类似：
```sql
create table cssename.user_defined (
    aname varchar(200) primary key,
    nature varchar(10),
    freq int
);
```
## 4.2 修改ANSJ配置文件
我们希望ANSJ在加载的时候，把user_defined和area都作为自定义词进行加载，那么我们修改`ansj_library.properties`配置文件：

```config
dic=jdbc://jdbc:mysql://192.168.0.120:3306/cssename?serverTimeZone=UTC|username|password|select aname as name, nature, freq from cssename.area union select aname as name, nature, freq from cssename.user_defined
```

## 4.3 修改Solr配置文件
接下来我们进入`/server/solr/cssename/conf/`目录，找到solrconfig.xml，在其中添加两个requestHandler：

```xml
  <requestHandler name="/ansjinsert" class="me.jiaqili.ansj5_solr7_plugin.service.AnsjInsert">
  </requestHandler>

  <requestHandler name="/ansjdelete" class="me.jiaqili.ansj5_solr7_plugin.service.AnsjDelete">
  </requestHandler>
```

name属性表示的是服务名称。比如我们的核心名称是`cssename`，requestHandler叫做`ansjinsert`，那么可以通过`http://IP地址:端口号/solr/cssename/ansjinsert`来访问我们的服务。

class表示的是处理这个服务的类。我们现在需要做的就是编写AnsjInsert和AnsjDelete两个类。

## 4.4 实现请求处理类

新建一个Maven项目，然后导入下面的依赖：
```xml
    <!-- https://mvnrepository.com/artifact/org.apache.solr/solr-core -->
	<dependency>
	    <groupId>org.apache.solr</groupId>
	    <artifactId>solr-core</artifactId>
	    <version>7.3.1</version>
	</dependency>
	<!-- https://mvnrepository.com/artifact/org.ansj/ansj_seg -->
	<dependency>
	    <groupId>org.ansj</groupId>
	    <artifactId>ansj_seg</artifactId>
	    <version>5.1.6</version>
	</dependency>
	<!-- https://mvnrepository.com/artifact/org.ansj/ansj_lucene7_plug -->
	<dependency>
	    <groupId>org.ansj</groupId>
	    <artifactId>ansj_lucene7_plug</artifactId>
	    <version>5.1.5</version>
	</dependency>
	<!-- https://mvnrepository.com/artifact/org.nlpcn/nlp-lang -->
	<dependency>
	    <groupId>org.nlpcn</groupId>
	    <artifactId>nlp-lang</artifactId>
	    <version>1.7.7</version>
	</dependency>
	<dependency>  
	    <groupId>jdk.tools</groupId>  
	    <artifactId>jdk.tools</artifactId>  
	    <version>1.8</version>  
	    <scope>system</scope>  
	    <systemPath>C:/Program Files/Java/jdk1.8.0_101/lib/tools.jar</systemPath> 
	</dependency> 
```

然后，定义一些常量：

```java
package me.jiaqili.ansj5_solr7_plugin.util;

public class CommonResponseMessage {

    public static final String CODE_SUCCEEDED = "200";
    public static final String MSG_SUCCEEDED = "OK";
	
    public static final String CODE_BAD_REQUEST = "400";
    public static final String MSG_BAD_REQUEST = "BAD REQUEST";
	
    public static final String CODE_INTERNAL_SERVER_ERROR = "500";
    public static final String MSG_INTERNAL_SERVER_ERROR = "Internal Server Error";
}
```

```java
package me.jiaqili.ansj5_solr7_plugin.util;

public class Constant {

    public static final boolean DEFAULT_IS_FLUSH = true;
    public static final boolean DEFAULT_IS_PRESISTENT = false;
}
```

下面来实现AnsjInsert服务（AnsjDelete类似就不赘述了）：
```java
package me.jiaqili.ansj5_solr7_plugin.service;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

import org.ansj.library.DicLibrary;
import org.ansj.util.MyStaticValue;
import org.apache.solr.common.params.SolrParams;
import org.apache.solr.handler.RequestHandlerBase;
import org.apache.solr.request.SolrQueryRequest;
import org.apache.solr.response.SolrQueryResponse;

import me.jiaqili.ansj5_solr7_plugin.util.CommonResponseMessage;
import me.jiaqili.ansj5_solr7_plugin.util.Constant;

public class AnsjInsert extends RequestHandlerBase{

    // 插入到用户自定义词库的语句
    public static final String SQL = "insert into cssename.user_defined(aname, nature, freq) values (?, ?, ?)";
    
    @Override
    public String getDescription() {

        return "Insert a user defined word into ANSJ's dictionary.";
    }

    @Override
    public void handleRequestBody(SolrQueryRequest req, SolrQueryResponse res) throws Exception {

        try{
            SolrParams params = req.getParams();
            // 获取名称
            String name = params.get("name");
            if( name == null || "".equals(name)){
                throw new IllegalArgumentException("missing argument name");
    
            }
            
            // 获取词性
            String nature = params.get("nature");
            if( nature == null || "".equals(nature) || "null".equals(nature)){
                nature = DicLibrary.DEFAULT_NATURE; // ANSJ的默认词性
            }
            
            // 获取词频
            String freqStr = params.get("freq");
            if( freqStr == null || "".equals(freqStr)){
                freqStr = DicLibrary.DEFAULT_FREQ_STR; // ANSJ的默认词频
            }
            
            
            int freqInt = Integer.valueOf( freqStr);
            if( freqInt <= 0){
                freqInt = DicLibrary.DEFAULT_FREQ;
            }
            
            // 是否立即更新内存
            boolean isFlushBool = Constant.DEFAULT_IS_FLUSH;
            String isFlushStr =  params.get("flush");
            if( isFlushStr != null && "false".equals( isFlushStr.toLowerCase())){
                isFlushBool = false;
            }else if(isFlushStr != null && "true".equals( isFlushStr.toLowerCase())){
                isFlushBool = true;
            }
            
            // 是否持久化
            boolean isPresistentBool = Constant.DEFAULT_IS_PRESISTENT;
            String isPresistentStr =  params.get("flush");
            if( isPresistentStr != null && "false".equals( isPresistentStr.toLowerCase())){
                isPresistentBool = false;
            }else if(isPresistentStr != null && "true".equals( isPresistentStr.toLowerCase())){
                isPresistentBool = true;
            }
            
            // 插入到数据库
            if( isPresistentBool){
                insertIntoDatabase( name, nature, freqInt);
            }
            
            // 插入到ANSJ
            if( isFlushBool){
                DicLibrary.insert(DicLibrary.DEFAULT, name, nature, freqInt);
            }
            
            // 成功结束
            res.add("ResponseCode", CommonResponseMessage.CODE_SUCCEEDED);
            res.add("ResponseMessage", CommonResponseMessage.MSG_SUCCEEDED);

        }catch(IllegalArgumentException  | SQLException e){
            res.add("ResponseCode", CommonResponseMessage.CODE_BAD_REQUEST);
            res.add("ResponseMessage", CommonResponseMessage.MSG_BAD_REQUEST + ": " + e.getMessage());
        }catch(Exception e){
            res.add("ResponseCode", CommonResponseMessage.CODE_INTERNAL_SERVER_ERROR);
            res.add("ResponseMessage", CommonResponseMessage.MSG_INTERNAL_SERVER_ERROR + ": " + e.getMessage());
        }
    }

    private void insertIntoDatabase(String name, String nature, Integer freq) throws SQLException{
        
        String connStr = MyStaticValue.ENV.get("dic"); // 使用ansj_library.properties里面配置的数据源
        
        String[] split = connStr.split("\\|");
        String jdbc = split[0].substring(7); // ANSJ配置开始为“jdbc://链接字符串”，我们需要去掉头部的七个字符。
        String username = split[1];
        String password = split[2];
        
        
        try (Connection conn = DriverManager.getConnection(jdbc, username, password);
                PreparedStatement statement = createPreparedStatement( conn, name, nature, freq)) {

            statement.executeUpdate();
            
        } catch(SQLException e){
            throw e;
        }
    }
    
    private PreparedStatement createPreparedStatement(Connection conn, String name, String nature, Integer freq) throws SQLException{
        
        PreparedStatement pstat = conn.prepareStatement(SQL);
        pstat.setString(1, name);
        pstat.setString(2, nature);
        pstat.setInt(3, freq);
        return pstat;
    }
}
```

最后把这个Maven项目导出成一个Jar包，丢到`./server/solr-webapp/webapp/WEB-INF/lib`目录下，重启solr即可。

## 4.5 测试

我们试一下`普华永道会计师事务所`，下面是添加自定义词前，`普华永道`因为是个专有名词而且ANSJ词库里没有，因此结果不准确：

{{% figure class="center" src="/images/solr-ansj-config/solr-user-defined1.png" alt="自定义词添加前" title="自定义词添加前"  %}}

下面我们在浏览器上访问下面的地址：
```text
http://192.168.0.120:8983/solr/cssename/ansjinsert?name=普华永道&flush=true&presistent=true&freq=1000
```

返回结果显示执行成功：
```json
{
  "responseHeader":{
    "status":0,
    "QTime":859},
  "ResponseCode":"200",
  "ResponseMessage":"OK"}
```

再次对`普华永道会计师事务所`的结果如下：
{{% figure class="center" src="/images/solr-ansj-config/solr-user-defined2.png" alt="自定义词添加后" title="自定义词添加后"  %}}

这里只演示了插入一个自定义词，ANSJ还可以清空、重载用户自定义词库等方法，可以自行翻阅源码。

# 5 配置Solr同义词库

## 5.1 配置同义词

Solr的同义词默认在核心的配置目录下，即`/server/solr/cssename/conf/synonyms.txt`。里面已经给出了Solr的两种配置例子。

1. xxx => yyy 表示xxx映射到yyy，但反过来不行。比如
   `华师大 => 华东师范大学 华南师范大学`
2. aaa,bbb,ccc 表示一组互相可以替换的同义词。比如
   `第二医院,二院` 
   
修改synonyms.txt不需要重启Solr，只要重载核心即可:`http://192.168.0.120:8983/solr/admin/cores?action=RELOAD&core=cssename`。

## 5.2 添加Filter
配置完后，打开schema.xml，找到我们的字段类型text_ansj。在原有基础上，增加一个SynonymGraphFilter。修改完以后如下：

```xml
<fieldType name="text_ansj" class="solr.TextField" positionIncrementGap="100">  
  <analyzer type="index">  
    <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="index_ansj"/>  
    <filter class="solr.SynonymGraphFilterFactory" synonyms="synonyms.txt" 
        format="solr" ignoreCase="false" expand="true" 
        tokenizerFactory="org.ansj.lucene.util.AnsjTokenizerFactory" type="index_ansj"/>
  </analyzer>  
  <analyzer type="query">  
    <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="query_ansj"/>  
    <filter class="solr.SynonymGraphFilterFactory" synonyms="synonyms.txt" 
        format="solr" ignoreCase="false" expand="true" 
        tokenizerFactory="org.ansj.lucene.util.AnsjTokenizerFactory" type="query_ansj"/>
  </analyzer>  
</fieldType>
```

Solr6及以后可以使用SynonymGraphFilterFactory，之前的版本用的是SynonymFilterFactory。以前的版本无法解决多词项同义词问题，比如上面的`第二医院`分词结果有两个词`第二`和`医院`,这种情况下就无法做同义词到`二院`。


## 5.3 测试
处理`宁波第二医院`，截图中的AT表示的是ANSJ的分析结果，SGF表示的是增加了同义词过滤器后的结果。注意SGF中出现了`二院`，而`二院`不是ANSJ的分析结果，并且注意看`二院`的SGF的type是`SYNONYM`，表示它是作为同义词出现在结果里的。

{{% figure class="center" src="/images/solr-ansj-config/solr-synonym1.png" alt="宁波第二医院的同义词分析结果" title="宁波第二医院的同义词分析结果"  %}}


下面是反过来分析`宁波二院`，我们可以看到在SGF的结果里也出现了`第二`和`医院`。

{{% figure class="center" src="/images/solr-ansj-config/solr-synonym1.png" alt="宁波二院的同义词分析结果" title="宁波二院的同义词分析结果"  %}}

最后来看`华师大`，SGF结果里出现了`华南`,`华东`,`师范大学`；但是反过来分析`华东师范大学`，SGF结果里只有`华东`和`师范大学`，不会出现华师大（截图就不放了）。

# 6 通过数据库加载Solr的同义词库

Solr自身通过HTTP协议的一系列API接口来访问和维护同义词、停用词等。如果采用默认的方式对这些词库进行管理，那么不需要做任何修改了。关于如何使用Solr API管理同义词、停用词等，[这里有一篇文章](https://lucidworks.com/2014/03/31/introducing-solrs-restmanager-and-managed-stop-words-and-synonyms/)写的比较详细。

回到本文，我们希望将这些词库持久化到数据库中，但是Solr本身似乎不提供这种模式，因此我们需要做一点扩展。如果用Google搜索这个问题，可以发现已经有人做了这个事情，你可以在[这里](https://developer.s24.com/blog/solr-jdbc-synonyms.html)找到让Solr从数据库中加载同义词的的一个扩展。

我在上面这个插件基础上做一些改动：

1. 没有使用JNDI，而是将数据库连接信息配置到了schema上；
2. 使用了SynonymGraphFilterFactory而不是SynonymFilterFactory，后者在Solr 6以后已经被前者替代。

首先我们需要扩展SynonymGraphFilterFactory:

```java
package me.jiaqili.jdbcsolrplugin.synonym;

import java.io.IOException;
import java.nio.charset.Charset;
import java.util.Map;

import org.apache.lucene.analysis.synonym.SynonymGraphFilterFactory;
import org.apache.lucene.analysis.util.ResourceLoader;
import org.apache.solr.search.SolrIndexSearcher;


public class JdbcSynonymGraphFilterFactory extends SynonymGraphFilterFactory implements SearcherAware {

	private static final Charset UTF8 = Charset.forName("UTF-8");
	
	private final JdbcReader reader;
	

	public JdbcSynonymGraphFilterFactory(Map<String, String> args) {
		this(args, SolrJdbcReader.createFromSolrParams(args, "synonyms"));
	}

	JdbcSynonymGraphFilterFactory(Map<String, String> args, JdbcReader reader) {
	      super(args);

	      this.reader = reader;
	   }
	
	@Override
	public void inform(SolrIndexSearcher searcher) throws IOException {

		try {
			inform(searcher.getCore().getResourceLoader());
		} catch (IOException e) {
			throw new IllegalArgumentException("Failed to notify about new searcher.", e);
		}

	}

	@Override
	public void inform(ResourceLoader loader) throws IOException {

		super.inform(new JdbcResourceLoader(loader, reader, UTF8));
	}
}
```

JdbcSynonymGraphFilterFactory的构造函数将schema中配置的属性`args`传递给静态方法SolrJdbcReader.createFromSolrParams来创建一个SolrJdbcReader。这个SolrJdbcReader负责与数据库建立连接并执行我们配置在schema中的sql来查询同义词。因为我们所继承的SynonymGraphFilterFactory在inform方法中实现从文件中读取同义词并构建同义词表的，因此我们只需要调用父类的inform方法，但是需要给她一个不同的数据来源，这也就是我在上面代码中new了一个JdbcResourceLoader的原因。

下面是JdbcReader的接口和SolrJdbcReader的实现：

```java
package me.jiaqili.jdbcsolrplugin.synonym;

import java.io.IOException;
import java.io.Reader;

/**
 * Reads "lines" of configuration out of JDBC.
 *
 * @author Shopping24 GmbH, Torsten Bøgh Köster (@tboeghk)
 */
public interface JdbcReader {
   /**
    *
    * @return a {@linkplain Reader}, never <code>null</code>
    */
   Reader getReader() throws IOException;
}
```

```java

package me.jiaqili.jdbcsolrplugin.synonym;

import static com.google.common.base.Preconditions.checkNotNull;

import java.io.IOException;
import java.io.Reader;
import java.io.StringReader;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.google.common.base.Joiner;
import com.google.common.base.Preconditions;

/**
 * Get synonyms fron configured database table
 * 
 *
 */
public class SolrJdbcReader implements JdbcReader {

	/**
	 * JDBC connection string
	 */
	private String jdbc;

	/**
	 * database username
	 */
	private String username;

	/**
	 * database password
	 */
	
	private String password;

	/**
	 * sql for fetching synonyms
	 */
	private String sql;

	/**
	 * Construct an reader instance
	 * 
	 * @param jdbc  JDBC connection string
	 * @param username database username
	 * @param password database password
	 * @param sql sql for fetching synonyms
	 */
	public SolrJdbcReader(String jdbc, String username, String password, String sql) {
		this.jdbc = checkNotNull(jdbc);
		this.username = checkNotNull(username);
		this.password = checkNotNull(password);
		this.sql = checkNotNull(sql);
	}

	@Override
	public Reader getReader() throws IOException{

		try (Connection conn = DriverManager.getConnection(jdbc, username, password);
				PreparedStatement statement = conn.prepareCall(sql);
				ResultSet rs = statement.executeQuery()) {

			List<String> content = new ArrayList<String>();
			while(rs.next()){
				
				content.add( rs.getString(1));
			}
			
			return new StringReader( Joiner.on('\n').join(content));
		} catch (SQLException e) {
			throw new IOException(e);
		}
	}

	/**
	 * Create an instance from Solr's parameters
	 * @param args Solr's parameter configured in schema.xml
	 * @param originalParamName
	 * @return an instance of SolrJdbcReader
	 */
	public static SolrJdbcReader createFromSolrParams(Map<String, String> args, String originalParamName) {
		Preconditions.checkNotNull(args);

		args.put(originalParamName, JdbcResourceLoader.DATABASE);

		String jdbc = args.remove("jdbc");
		String username = args.remove("username");
		String password = args.remove("password");
		String sql = args.remove("sql");

		return new SolrJdbcReader(jdbc, username, password, sql);
	}
}
```

createFromSolrParams方法创建了一个SolrJdbcReader，并初始化连接字符串，用户名密码以及查询同义词需要的SQL，这些都配置在schema中。getReader方法连接数据库，并执行查询SQL，最后将结果写入一个StringReader返回。

再来看JdbcResourceLoader，这个是inform方法所需要用来读取数据的类，这边不需要改动，直接用的是原作者的代码。

```java
/**
 * {@link ResourceLoader} which loads a resource from a {@link JdbcReader}.
 * All other operations are delegated to the parent resource loader.
 * 
 * @author Shopping24 GmbH, Torsten Bøgh Köster (@tboeghk)
 */
class JdbcResourceLoader implements ResourceLoader {
   /**
    * Name of database resource.
    */
   static final String DATABASE = "database";

   /**
    * {@link ResourceLoader} to delegate class loading to.
    */
   private ResourceLoader parent;

   /**
    * Database based reader.
    */
   private final JdbcReader reader;

   /**
    * Encoding of database resource.
    */
   private final Charset charset;

   /**
    * Constructor.
    *
    * @param parent
    *           Parent resource loader.
    * @param reader
    *           Database based reader.
    * @param charset
    *           {@link Charset} to encode database resource with, because resources are always input streams.
    */
   public JdbcResourceLoader(ResourceLoader parent, JdbcReader reader, Charset charset) {
      this.parent = checkNotNull(parent);
      this.reader = checkNotNull(reader);
      this.charset = checkNotNull(charset);
   }

   @Override
   public InputStream openResource(String resource) throws IOException {
      if (DATABASE.equals(resource)) {
         return new ReaderInputStream(reader.getReader(), charset);
      }

      return parent.openResource(resource);
   }

   @Override
   public <T> Class<? extends T> findClass(String cname, Class<T> expectedType) {
      return parent.findClass(cname, expectedType);
   }

   @Override
   public <T> T newInstance(String cname, Class<T> expectedType) {
      return parent.newInstance(cname, expectedType);
   }
}
```

最后是一个JdbcSynonymGraphFilter继承的一个接口定义，也是用的是原作者的代码：

```java
/**
 * Interface for event notification, when a new searcher has been created.
 * 
 * @author Shopping24 GmbH, Torsten Bøgh Köster (@tboeghk)
 */
public interface SearcherAware {
   /**
    * Notification that a new searcher has been created.
    * 
    * @param searcher
    *           The new searcher.
    * @throws IOException
    *            In case of any problems.
    */
   void inform(SolrIndexSearcher searcher) throws IOException;
}
```


和上面扩展Solr的requestHandler来实现对ANSJ数据库的维护一样，把这些类放到打一个Jar包丢到`./server/solr-webapp/webapp/WEB-INF/classes`目录下。我们还需要修改一下schema.xml：

```xml
<fieldType name="text_ansj" class="solr.TextField" positionIncrementGap="100">  
  <analyzer type="index">  
    <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="index_ansj"/>  
    <filter class="solr.JdbcSynonymGraphFilterFactory" jdbc="jdbc:mysql://192.168.0.120:3306/cssename?serverTimeZone=UTC"
        username="dbUsername" passowrd="password" sql="select clause from synonyms" synonyms="synonyms.txt" 
        format="solr" ignoreCase="false" expand="true" 
        tokenizerFactory="org.ansj.lucene.util.AnsjTokenizerFactory" type="index_ansj"/>
  </analyzer>  
  <analyzer type="query">  
    <tokenizer class="org.ansj.lucene.util.AnsjTokenizerFactory" type="query_ansj"/>  
    <filter class="solr.JdbcSynonymGraphFilterFactory" jdbc="jdbc:mysql://192.168.0.120:3306/cssename?serverTimeZone=UTC" 
        username="dbUsername" passowrd="password" sql="select clause from synonyms" synonyms="synonyms.txt" 
        format="solr" ignoreCase="false" expand="true" 
        tokenizerFactory="org.ansj.lucene.util.AnsjTokenizerFactory" type="query_ansj"/>
  </analyzer>  
</fieldType>
```

这里配置的sql是`select clause from synonyms`，这个字段里面存储的即为Solr的同义词格式，比如`AAA => BBB CCC`或者`XXX,YYY,ZZZ`。

最后重启一下Solr使它加载我们的Jar包。之后我们可以像管理ANSJ数据库中的自定义词库一样，通过扩展solr的RequestHandler来增加接口来管理数据库中的Solr同义词。对同义词的修改也不需要重启Solr，只需要重载核心即可。



