# JDBC 设计理念

JDBC提供了Java API和一个驱动管理器。第三方数据库驱动程序向驱动管理器注册，应用程序通过API与驱动管理器进行通讯，然后驱动管理器通过特定的驱动程序与数据库通讯。此结构图如下：

{{% figure class="center" src="/images/java-12-database/jdbc-design.PNG" alt="JDBC设计理念" title="JDBC设计理念"  %}}

JDBC 实现了以下两个目标：

1. 数据库供应商可以优化底层驱动而不影响实际的应用程序；
2. 程序员可以在Java 程序里访问数据库。

JDBC驱动程序类型：

1. 将JDBC翻译成ODBC，用ODBC与数据库通讯（较早版本的Java驱动程序：JDBC/ODBC桥）；
2. 由Java程序和本地代码共同组成，与数据库客户端API 进行通讯（客户端需要安装Java 类库和平台相关代码）；
3. 纯Java客户端类库，将数据库请求通过与具体数据库无关的协议发送给数据库服务器，服务器端再翻译成数据库相关的协议（平台相关代码只在服务器端）；
4. 纯Java 类库，将JDBC 请求直接翻译成数据库相关的协议。

JDBC典型用法：

1. 传统的C/S 模式：服务器端部署数据库，客户端部署应用程序，即

    {{% figure class="center" src="/images/java-12-database/jdbc-cs.PNG" alt="C/S模式" title="C/S模式"  %}}
    
2. 三层应用模式：

    {{% figure class="center" src="/images/java-12-database/jdbc-layers.PNG" alt="三层应用模式" title="三层应用模式"  %}}

<!--more-->

# 链接到数据库
1. 加载数据库驱动程序JAR文件：

    ```text
    Windows: java -classpath .;driverPath
    ```
    
    ```text
    Linux: java -classpath .:driverPath
    ```

2. 注册驱动器类: 遵循JDBC4的驱动程序必需包括自动注册机制。如果驱动程序JAR中包含METAINF/services/java.sql.Driver，则它会自动注册驱动器类。有两种手动注册驱动器的方法：
    
    1. Java程序中使用反射：
    
        ```java
        Class.forName("org.postgresql.Driver");
        ```
    2. 设置jdbc.drivers 属性：
    
        ```java
        System.setProperty(”jdbc.drivers”, ”org.postgresql.Driver”)
        ```
        或者
        ```java
        java -Djdbc.driver=org.postgresql.Driver ProgramName
        ```
        
3. 数据库URL：jdbc:subprotocol:xxx。这里subprotocol 选择用于链接到数据库的具体驱动程序，而xxx是和驱动程序相关的，比如以下两个例子:

    ```java
    // 链接字符串
    String url1 = "jdbc:postgresql:someDBName";
    String url1 = "jdbc:postgresql :// localhost :1527/ someDBName";
    ```
    
4. 获取数据库链接：

    ```java
    String username = 'username';
    String password = 'password';
    // Connection 对象用来执行SQL 语句
    Connection conn = DriverManager.getConnection(url , username , password);
    ```
    
# 执行SQL 语句
1. 准备SQL语句。如果数据库查询或更新逻辑比较复杂，尽量用SQL语句写，而不是通过JAVA语言去处理，比如迭代多个结果集，多次查询等。如果SQL语句中不含参数，按下面sql1的写法即可；不然应该用sql2的写法用问号替代参数（之后再赋值）。如果SQL语句需要换行，特别小
心换行时不要把两个单词间的空格省略调。另外，写在String中的SQL语句不需要分号结尾。

    ```java
    String sql1 = "UPDATE Books SET Price = 50.0 " +
                "WHERE Title = 'Hello World'";
    String sql2 = "UPDATE Books SET Price = ? WHERE Title = ?";
    String sql3 = "SELECT * FROM Books WHERE Id = 1";
    String sql4 = "SELECT * FROM Books WHERE Id = ?";
    ```

    SQL 转义主要发生在以下几种情况，使用方式比如

    ```sql
    SELECT * FROM User WHERE Logindate = {d '2017-02-02'}
    ```
    
    1. 日期和事件字面量。用d、t、ts分别表示DATE、TIME、TIMESTAMP，e.g., `{d '2017-02-02'}`，`{t '23:59:59'}`，`{ts '2017-02-02 23:59:59.999'}`；
	2. 标量函数，即仅返回一个值的函数，比如`{fn left(?, 20)}`；
	3. 存储过程。调用存储过程用call，如果没有参数就不需要加括号，用等号来获取返回值。`{call PROC1(?)}`，`{call PROC2}`，`{call ? = PROC3(3)}`；
	4. 外链接。由于并非所有的数据库对于外链接都使用标准的写法，因此需要使用转义。比如`SELECT * FROM {oj Books LEFT OUTER JOIN Publishers ON Books.Publisher_Id = Publisher.Publisher_Id}`；
	5. 特殊字符。下划线和百分号在SQL的LIKE字句中有特殊含义，如果需要用到它们的字面意思就需要转义。比如下面的例子试图匹配所有包含下划线的字符串。`...WHERE ? LIKE %!_% {escape '!'}`。
	
2. 创建Statement或者PreparedStatment。

    ```java
    // 使用Statement 处理不带参数的SQL 。
    Statement stat = conn.createStatement();
    // 使用PreparedStatement 处理带参数的SQL ， 给参数赋值时， 1 代表第一个问号， 以此类推。
    PreparedStatement pstat = conn.prepareStatement(sql2);
    pstat.setDouble(1, 50.0);
    pstat.setString(2, "Hello␣World");
    // 如果要再次使用pstat ， 必需重新使用set 方法设置新值或调用clearParameters ， 否则值不变。
    ```

    PreparedStatement是Statment接口的子接口，和Statement相比有以下三个优势：

    1. 提高处理速度，多次执行的语句会被数据库缓存可以提高执行速度；
    2. 避免SQL注入攻击。因为PreparedStatement是预编译的，再程序执行时执行计划已经被数据库缓存，并进行参数化的查询，如果传入敏感字符，数据库也只是当一个参数的属性来处理，而不是SQL语句来执行；
    3. 使非标准的Java对象更容易赋值给SQL语句，比如Date, BigDecimal。pstat.setObject(x, obj)将Java对象映射到SQL类型然后写入数据库。

3. 执行SQL 语句。

    ```java
    // 执行SELECT 语句
    ResultSet rs = stat.executeQuery(sql3);
    ResultSet prs = pstat.executeQuery();
    // 执行DDL 或者其他DML 语句， 返回受影响的行数
    int updateCount = stat.executeUpdate(sql1);
    int pUpdateCount = pstat.executeUpdate();
    // 执行任意SQL 语句， 可能返回多个结果集和/ 或更新计数( 执行存储过程时) 。
    // 如果第一个执行结果是结果集， 那么返回true ； 否则返回false 。
    boolean isResultSet = stat.execute(sql1);
    boolean pIsResultSet = pstat.execute();
    ```
    
4. 处理返回结果。
    
    1. 查询语句。如果是通过executeQuery执行的查询语句，它会返回一个ResultSet；如果是execute执行的查询语句，如果结果是一个ResultSet，它会返回true，然后我们通过在stat或pstat对象上调用getResultSet来获取上一条查询语句的结果集。如果上一条语句未返回结果集，那么在stat 或pstat上执行getResultSet 会返回null。

        当我们获得ResultSet 以后，我们可以用以下方式迭代处理每一行的记录：
        
        ```java
        while(rs.next()){
            String title = rs.getString(1);
            double price = rs.getDouble("Price");
        }
        ```
    
        ResultSet的迭代器默认被放在第一行之前，所以必需调用next()把它移动到第一行。当next()方法将迭代器移动到最后一行之后的时候，它返回false。有两种方法访问每一行结果集里面的数据，
        
        1. 按列序号访问：传递一个列序号，第一列对应参数1，而不是0；
        2. 按列名访问：传递一个列名，这个列名是指结果集中的列名，不一定等价于数据库中的列名（比如你可以在查询时指定别名）。
        
        使用按序号访问效率更高。一个Connection可以有多个Statment，一个Statment也可以有多个不相关的命令和查询，但是一个Statment最多只能有一个打开的结果集，需要同时分析多个结果，必需创建多个Statment。
    

    2. 更新语句。如果是通过executeUpdate来执行的更新语句，它会返回更新计数。如果是execute执行的更新语句，如果结果不是一个结果集，它返回的是false，然后我们通用在stat或pstat对象上调用getUpdateCount获取上一条更新语句的更新计数，如果上一条语句未更新数据库，那么在stat或pstat上条用getUpdateCount 会返回-1。
    
        大多数数据库支持对行自动计数支持，插入语句执行后获取自动生成键方法如下：
        
        ```java
        stmt.executeUpdate(insertStmt , Statement.RETURN_GENERATED_KEYS);
        ResultSet rs = stmt.getGeneratedKeys();
        if(rs.next()){
            int key = rs.getInt(1);
        }
        ```
        
    3. 处理多结果。execute执行某些存储过程后会返回多个结果集。可以调用getMoreResults来处理更多结果，如下：
    
        ```java
        boolean isResult = stat.execute(cmd);
        boolean done = false;
        while(!done){
            if(isResult){
                ResultSet result = stat.getResultSet();
                // 处理结果集
            }else{
                int updateCount = stat.getUpdateCount();
                if(updateCount() >= 0){
                    // 处理更新语句的结果
                }else{
                    done = true; // 没有更多结果了
                }
            }
            
            if(!done){
                isResult = stat.getMoreResults();
            }
        }
        ```

5. 处理LOB 类型。二进制大对象称为BLOB，字符型大对象称为CLOB。

    读取LOB对象，需要执行SELECT语句后，通过getBlob或getClob方法获取。然后对于BLOB对象通过调用getBytes或者getInputStream方式获取二进制数据；对于CLOB对象通过getSubString或getCharacterStream的方法获取里面的字符数据。
    
    ```java
    if(rs.next()){
        Blob b = rs.getBlob (1);
        Image img = ImageIO.read(b.getBinaryStream());
    }
    ```

    往数据库里写入LOB 对象，需要准备一个输出流，写出数据，然后把该对象保存到数据库：
    
    ```java
    Blob b = connection.createBlob();
    int offset = 0;
    OutputStream os = coverBlob.setBinaryStream(offset);
    ImageIO.write(b, "PNG", out);
    PreparedStatement pstat = conn.prepareStatement("INSERT␣INTO␣Cover␣VALUES␣(?)");
    pstat.set(1, b);
    pstat.executeUpdate();
    ```
    
6. 关闭资源。使用完成ResultSet、Statement或Connection对象后应立即调用close方法关闭，这些对象占用大量数据库服务器上的资源。

    如果Statment对象上有打开的的结果集，调用close方法将关闭该结果集；调用Connection方法上的Close也会关闭该链接的所有语句。但是关闭不代表释放资源，建议手动显示地按照ResultSet，Statment和Connection的顺序关闭。
    
# 可滚动、可更新的结果集和行集

```java
Statement stmt = conn.createStatement(type, concurrency);
PreparedStatemnt pstmt = conn.prepareStatment(sql, type, concurrency);
```

其中type 可以为以下三个值中的一个：

| 值    | 含义  |
| :---  | :---  |
| ResultSet.TYPE_FORWARD_ONLY | 结果集不能滚动（默认）|
| ResultSet.TYPE_SCROOL_INSENSITIVE | 结果集可以滚动，但对数据库变化不敏感 |
| ResultSet.TYPE_SCROOL_SENSITIVE | 结果集可以滚动，并对数据库变化敏感 |

concurrency可以为以下两个值中的一个：

| 值 | 含义 |
| :-- | :-- |
| ResultSet.CONCUR_READ_ONLY | 结果集不能用于更新数据库（默认） |
| ResultSet.CONCUR_UPDATABLE | 结果集可用于更新数据库 |


在使用上述语句获取可滚动或可更新的结果集之前，先要通过DatabaseMetaData接口的supportResultSetType和supportResultSetCurrency方法来确定特定驱动程序支持哪些结果集类型和并发模式。

另外，就算数据库支持特定的可滚动、可更新结果集。某些特定的，比如多个表的链接查询时，查询就不一定能返回可更新的结果集。

当executeQuery返回功能较少的结果集时，它会添加一个SQLWarning到链接对象中。这时通过ResultSet的getType和getCurrency来确定结果集实际支持的模式。

结果集滚动的一些方法：

1. 向前滚动一行：`if(rs.next())...`如果游标位于最后一行之后，返回false。
2. 向后滚动一行：`if(rs.previous())...`如果游标位于第一行之前，返回false。
3. 向前或向后多行：`rs.relative(n)`如果n 为正数，游标向前移动；负数则向后移动；0则不移动。如果移动后游标位于一个实际的行上，游标移动成功并返回true；如果移动后游标位于最后一行之后或第一行之前，该方法返回false，游标不移动。
4. 移动到指定行上：`rs.absolute(n)`可以用过`rs.getRow()`获取当前行号，第一行为1；0表示不在任何行上，要么在第一行之前，要么在最后一行之后。
5. 移动到最前面、最后面：first(), last(), beforeFirst(), afterLast()。

结果集更新的几种情况：

1. 修改现有的行。

    ```java
    rs.updateDouble(1, 1.25);
    rs.updateString("Title", "Hello␣World");
    rs.updateRow();// 写入到数据库
    ```
    这里的序号是指结果集中的列的序号。修改完所有的字段后，需要调用updateRow把结果刷新到数据库，如果需要撤销则调用cancelRowUpdates()。

2. 添加一条新的记录。
    
    ```java
    rs.moveToInsertRow();
    rs.updateString("Title", "Hello␣Wolrd");
    rs.updateDouble("Price", 1.2);
    rs.insertRow();// 写入到数据库
    rs.moveToCurrentRow();// 将游标移动到moveToInsertRow () 之前的位置。
    ```
    
    注意：无法控制在结果集和数据库中新增数据的位置。

3. 删除游标所指的行。

    ```java
    rs.deleteRow();// 写入到数据库
    ```

除非是交互式程序，否则可更新的结果集一般是没有必要的。通常SQL的UPDATE语句执行效率更高。

# 元数据

如果预先知道数据库里的表、字段等相关信息，那么数据库的结构、表信息等元数据就不会很有用了。而数据库工具开发人员相反并不知道数据库里的信息，所以元数据就会很有用。通过JDBC的API可以获取到三类元数据。

1. 预备语句的元数据，ParameterMetaData。

    ```java
    ParameterMetaData pmd = pstat.getParameterMetaData ();
    ```
    
2. 结果集的元数据，ResultSetMetaData。用于获取结果集的每一列名称，类型和字段宽度。

    ```java
    ResultMetaData meta = rs.getMetaData();
    for(int i = 1; i <= meta.getColumnCount(); i++){
        String columnName = meta.getColumnLabel(i);
        int columnWidth = meta.getColumnDisplaySize(i);
        // ...
    }
    ```
    
3. 数据库的元数据，DatabaseMetaData。比如获取数据库的所有表名：

    ```java
    ResultSet rs = meta.getTables(null , null , null , new String[]("TABLE"));
    while(rs.next()){
        System.out.println(rs.getString (3));
    }
    ```

# 事务

我们可以将一组语句构建成一个事务(transaction)，当所有语句全部顺利执行后，事务被提交(commit)；如果某个语句遇到错误，那么事务被回滚（rollback）。其目的是确保数据库的完整性。

默认情况下，数据库链接处于自动提交模式(autocommit mode)。每个SQL语句一旦被执行便被提交给数据库。所以在使用事务时，我们需要关闭自动提交，然后当所有语句执行完成后手动提交。

```java
try{
    conn.setAutoCommit(false);
    stat.executeUpdate(sql1);
    stat.executeUpdate(sql2);
    stat.executeUpdate(sql3);
    // ...
    conn.commit;
}catch(SQLException e){
    // ...
    conn.rollback();
}finally{
    // cleanup
}
```

某些驱动支持保存点来更细粒度地控制回滚操作，回滚到一个保存点意味着事务开头到保存点间的语句没有受影响。

```java
stat.executeUpdate(sql1);
Savepoint svpt = conn.setSavepoint();
stat.executeUpdate(sql2);
if(...) conn.rollback(svpt);
...
conn.commit();
```

用DatabaseMetaData接口中的supportsBatchUpdates方法可以知道数据库是否支持批量更新。处于同一批中的可以是INSERT,UDPATE,DELETE,CREATE,DROP等，但是SELECT会抛出异常。

```java
boolean autoCommit = conn.getAutoCommit();
Connection conn = ...;
Statement stmt = conn.createStatement();
// PreparedStatement pstmt = conn.prepareStatement("INSERT INTO Books VALUES(?, ?)");
try {
    conn.setAutoCommit(false);
    stmt.addBatch("insert into ...");
    stmt.addBatch("insert into ...");
    // pstmt.setString(1, "xxxx");
    // pstmt.setString(2, "yyyy");
    // pstmt.addBatch();
    // pstmt.setString(1, "aaaa");
    // pstmt.setString(2, "bbbb");
    // pstmt.addBatch();
    // int[] executeBatch() throws SQLException 将一批命令提交给数据库来执行，
    // 如果全部命令执行成功， 则返回更新计数组成的数组。
    stmt.executeBatch();
    // pstmt.executeBatch();
    conn.commit();
    conn.setAutoCommit(autoCommit);
} catch (SQLException e) {
    e.printStackTrace();
    try {
        if (!conn.isClosed()) {
            conn.rollback();
            conn.setAutoCommit(true);
        }
    } catch (SQLException e1) {
        e1.printStackTrace();
    }
} finally {
    // Close all resources.
}
```