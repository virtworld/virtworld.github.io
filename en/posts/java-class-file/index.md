<!-- 
.. title: Java Class 文件
.. slug: java-class-file
.. date: 2015-12-28 10:57:42 UTC
.. tags: Java,JVM
.. category: 
.. link: 
.. description: 
.. type: text
-->

## 1 Class概述
1. Class文件是一个以8位字节为基础单位的二进制流，多字节储存按照Big-endian的方式（既高位字节在地址低位，低位字节在地址高位）；
2. 每个Class对应一个类或接口，而类或者接口不一定以文件的形式存在磁盘上；
3. Class文件储存的数据只有两种类型：无符号数和表
    1. 无符号数：u1, u2, u4和 u8分别表示1个，2个，4个和8个字节;
    2. 表(Table)：由多个无符号数或表组成的复合数据类型。

## 2 内部名称表示
1. **全限定名**(Fully Qualified Name)是JVM中的绝对名称，比如java.lang.Object；**非全限定名**(Unqualified Name)是当前环境，比如类，中的相对名称，比如Object；
2. 类或接口的名称都用**全限定名称**来表示；
3. 全限定名称用CONSTANT_Utf8_info表（见下文）的结构来表示；
4. 类在Class文中中的表示：比如java.lang.Object被表示为“java/lang/Object;”其中“;”为了表示名称结束；
5. 方法名，字段名，局部变量名都使用**非全限定名称**来储存，比如inc；
6. 方法名，字段名，局部变量名不能包含"."、";"、"["、"/"和Unicode，另外方法除了类初始化方法<clinit>和实例初始化方法<init>以外不能使用"<"、">"；

## 3 描述符(Descriptor)和签名(Signature)
1. 描述符描述字段的数据类型，方法的参数列表（数量，类型和顺序）以及返回值；
2. 签名描述字段、方法和类型定义中泛型信息的字符串；
3. 描述符字符含义:

	<table>
	  <tr>
	    <td>B</td>
	    <td>byte</td>
	    <td>C</td>
	    <td>char</td>
	  </tr>
	  <tr>
	    <td>D</td>
	    <td>double</td>
	    <td>F</td>
	    <td>float</td>
	  </tr>
	  <tr>
	    <td>I</td>
	    <td>int</td>
	    <td>J</td>
	    <td>long</td>
	  </tr>
	  <tr>
	    <td>S</td>
	    <td>short</td>
	    <td>Z</td>
	    <td>boolean</td>
	  </tr>
	  <tr>
	    <td>L classname &nbsp;&nbsp;</td>
	    <td>reference 一个名为&lt;Classname&gt;的实例 &nbsp;&nbsp;</td>
	    <td>[ &nbsp;&nbsp;</td>
	    <td>reference 一个一维数组</td>
	  </tr>
	</table>

4. 字段描述符，比如int的实例描述符是"I"；java.lang.Object的实例描述符是"Ljava/lang/Object;"；double的三维数组的描述符为"[[[D"；
5. 方法描述符，先参数后返回值，参数按顺序在圆括号内，比如Object mymethod(char[][] c, int i, double d, Thread t)的描述符为“([[CIDLjava/lang/Thread;)Ljava/lang/Object;”
6. 签名属于Java语言规范，不属于虚拟机的部分，包括泛型类型，方法描述，参数化类型描述，用于实现反射和跟踪调试（见JVS7-4.3.4）

## 4 Class文件结构

<table>
  <tr>
    <th>类型</th>
    <th>名称</th>
    <th>数量</th>
  </tr>
  <tr>
    <td>u4</td>
    <td>magic</td>
    <td>1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>minor_version</td>
    <td>1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>major_version</td>
    <td>1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>constant_pool_count</td>
    <td>1</td>
  </tr>
  <tr>
    <td>cp_info</td>
    <td>constant_pool</td>
    <td>constant_pool_count - 1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>access_flag</td>
    <td>1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>this_class</td>
    <td>1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>super_class</td>
    <td>1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>interfaces_count</td>
    <td>1</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>interfaces</td>
    <td>interfaces_count</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>fields_count</td>
    <td>1</td>
  </tr>
  <tr>
    <td>field_info</td>
    <td>fields</td>
    <td>fields_count</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>methods_count</td>
    <td>1</td>
  </tr>
  <tr>
    <td>method_info</td>
    <td>methods</td>
    <td>methods_count</td>
  </tr>
  <tr>
    <td>u2</td>
    <td>attributes_count</td>
    <td>1</td>
  </tr>
  <tr>
    <td>attribute_info</td>
    <td>attributes</td>
    <td>attributes_count</td>
  </tr>
</table>

1. magic 魔数
    决定这个文件是不是Class文件，永远是0xCAFEBABE
2. minor_version & major_version 次版本号和主版本号
3. constant_pool_count 常量池计数器
    从1开始，比如计数器为20，则常量池有效索引为1 - 19
4. constant_pool 常量池
    1. 是一个长度为 constant_pool_count - 1的表的数组，每一项都是一个表；
    2. 所有的表的第一个字节为tag，表明它是何种类型的表；
    3. 共有14种不同的表，用来保存字面量和符号引用（类/接口的全限定名，字段/方法的名称和描述符）
	
		<table>
		  <tr>
			<th>常量表</th>
			<th>项目名称</th>
			<th>类型       </th>
			<th>内容</th>
		  </tr>
		  <tr>
			<td>CONSTANT_Utf8_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>1</td>
		  </tr>
		  <tr>
			<td></td>
			<td>length</td>
			<td>u2</td>
			<td>第三项占用的字节数</td>
		  </tr>
		  <tr>
			<td></td>
			<td>bytes</td>
			<td>u1</td>
			<td>长度为length的UTF8编码的字符串</td>
		  </tr>
		  <tr>
			<td>CONSTANT_Integer_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>3</td>
		  </tr>
		  <tr>
			<td></td>
			<td>bytes</td>
			<td>u4</td>
			<td>高位在前储存的int值</td>
		  </tr>
		  <tr>
			<td>CONSTANT_Float_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>4</td>
		  </tr>
		  <tr>
			<td></td>
			<td>bytes</td>
			<td>u4</td>
			<td>高位在前储存的float值</td>
		  </tr>
		  <tr>
			<td>CONSTANT_Long_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>5</td>
		  </tr>
		  <tr>
			<td></td>
			<td>bytes</td>
			<td>u8</td>
			<td>高位在前储存的long值</td>
		  </tr>
		  <tr>
			<td>CONSTANT_Double_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>6</td>
		  </tr>
		  <tr>
			<td></td>
			<td>bytes</td>
			<td>u8</td>
			<td>高位在前储存的double值</td>
		  </tr>
		  <tr>
			<td>CONSTANT_Class_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>7</td>
		  </tr>
		  <tr>
			<td></td>
			<td>index</td>
			<td>u2</td>
			<td>对常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Utf8_info的表，表</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>示一个类或接口的全限定名。</td>
		  </tr>
		  <tr>
			<td>CONSTANT_String_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>8</td>
		  </tr>
		  <tr>
			<td></td>
			<td>index</td>
			<td>u2</td>
			<td>对常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Utf8_info的表。</td>
		  </tr>
		  <tr>
			<td>CONSTANT_Fieldref_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>9</td>
		  </tr>
		  <tr>
			<td></td>
			<td>class_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Class_info的表。</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>当前字段是该类或接口的成员。</td>
		  </tr>
		  <tr>
			<td></td>
			<td>name_and_type_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_NameAndType_info</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>的表。表示当前字段的名字和描述符。</td>
		  </tr>
		  <tr>
			<td>CONSTANT_Methodref_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>10</td>
		  </tr>
		  <tr>
			<td></td>
			<td>class_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Class_info的表。</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>该项的类型必须是类。当前字段是该类的成员。</td>
		  </tr>
		  <tr>
			<td></td>
			<td>name_and_type_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_NameAndType_info</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>的表。表示当前方法的名字和描述符。</td>
		  </tr>
		  <tr>
			<td>CONSTANT_InterfaceMethodref_info &nbsp;&nbsp;&nbsp;</td>
			<td>tag</td>
			<td>u1</td>
			<td>11</td>
		  </tr>
		  <tr>
			<td></td>
			<td>class_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Class_info的表。</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>该项的类型必须是接口。当前字段是</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>该接口的成员。</td>
		  </tr>
		  <tr>
			<td></td>
			<td>name_and_type_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_NameAndType_info</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>的表。表示当前方法的名字和描述符。</td>
		  </tr>
		  <tr>
			<td>CONSTANT_NameAndType_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>12</td>
		  </tr>
		  <tr>
			<td></td>
			<td>index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Utf8_info的表。</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>表示一个字段或方法的非限定名，或表示</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>特殊的方法名&lt;init&gt;</td>
		  </tr>
		  <tr>
			<td></td>
			<td>index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Utf8_info的表。表示</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>一个字段或一个方法的描述符。</td>
		  </tr>
		  <tr>
			<td>CONSTANT_MethodHandle_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>15</td>
		  </tr>
		  <tr>
			<td></td>
			<td>reference_kind</td>
			<td>u1</td>
			<td>1-9,决定方法句柄类型</td>
		  </tr>
		  <tr>
			<td></td>
			<td>reference_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引</td>
		  </tr>
		  <tr>
			<td>CONSTANT_MethodType_info</td>
			<td>tag</td>
			<td>u1</td>
			<td>16</td>
		  </tr>
		  <tr>
			<td></td>
			<td>descriptor_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_Utf8_info的表。表示</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>方法的描述符。</td>
		  </tr>
		  <tr>
			<td>CONSTANT_InvokeDynamic</td>
			<td>tag</td>
			<td>u1</td>
			<td>18</td>
		  </tr>
		  <tr>
			<td></td>
			<td>bootstrap_method_attr_ &nbsp;&nbsp;</td>
			<td>u2</td>
			<td>对当前Class文件中引导方法表的</td>
		  </tr>
		  <tr>
			<td></td>
			<td>index</td>
			<td></td>
			<td>bootstrap_methods[]数组的有效索引。</td>
		  </tr>
		  <tr>
			<td></td>
			<td>name_and_type_index</td>
			<td>u2</td>
			<td>常量池的一个有效索引，常量池在该索引的</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>位置必须是一个CONSTANT_NameAndType_info</td>
		  </tr>
		  <tr>
			<td></td>
			<td></td>
			<td></td>
			<td>的表。表示当前方法的名字和描述符。</td>
		  </tr>
		</table>

    5. access_flags 访问标志
	    是一种掩码标志，共有16个标志位可用，当前定义了8个。
		
		<table>
		  <tr>
			<td>ACC_PUBLIC</td>
			<td>0x0001</td>
			<td>是否为public</td>
		  </tr>
		  <tr>
			<td>ACC_FINAL</td>
			<td>0x0010</td>
			<td>是否为final，只能是类</td>
		  </tr>
		  <tr>
			<td>ACC_SUPER</td>
			<td>0x0020</td>
			<td>都为真</td>
		  </tr>
		  <tr>
			<td>ACC_INTERFACE</td>
			<td>0x0200</td>
			<td>表示这是一个接口</td>
		  </tr>
		  <tr>
			<td>ACC_ABSTRACT</td>
			<td>0x0400</td>
			<td>表示是否是abstract，对于抽象类和接口来说为真</td>
		  </tr>
		  <tr>
			<td>ACC_SYNTHETIC</td>
			<td>0x1000</td>
			<td>表示这个类由非用户代码产生</td>
		  </tr>
		  <tr>
			<td>ACC_ANNOTATION&nbsp;&nbsp;&nbsp;&nbsp;</td>
			<td>0X2000&nbsp;&nbsp;</td>
			<td>表示这是一个注解</td>
		  </tr>
		  <tr>
			<td>ACC_ENUM</td>
			<td>0x4000</td>
			<td>表示这是一个枚举</td>
		  </tr>
		</table>

    6. this_class 类索引
        常量池里的一个有效索引，指向一个CONSTANT_Class_info的表，通过该表，确定类的全限定名。
    7. super_class 父类索引
        为0（父类为Object）或为一个指向CONSTANT_Class_info的表的有效索引。
    8. interfaces_count 接口计数器
        当前类或接口的直接父类计数
    9. interfaces 接口索引集合
        1. 每个成员都是一个指向CONSTANT_Class_info的表的有效索引
        2. 按照源代码implements旁边从左到右的顺序
    10. fields_count 字段表计数器
    11. fields 字段表集合
        1. 用于描述接口或类中定义的变量，包括类级变量和实例级变量，但不包括方法内部的变量，也不包括继承来的。
        2. 有可能包括代码中没有的字段，比如内部类为了访问外部类，添加指向外部类实例的字段。
        3. 结构：
            1. u2 access_flags; 
            2. u2 name_index; 
            3. u2 descriptor_index; 
            4. u2 attributes_count; 
            5. attribute_info attributes[attributes_count];
        4. 第一个访问标志，类似于类的访问标志，表示他是public,private,protected,static或者final之类
        5. 第二个是指向常量池的一个CONSTANT_Utf8_info，表示字段的非全限定名
        6. 第三个是指向常量池的一个CONSTANT_Utf8_info，表示字段的描述符
        7. 第四个是属性表计数器
        8. 第五个是属性表集合，用于描述0至多个字段的额外信息
    12. methods_count 方法表计数器
    13. methods 方法表集合
        结构与字段表类似，属性表code中保存代码
    14. attributes_count 属性表计数器
    15. attributes 属性表集合
        1. 通用格式如下
            1. u2 attribute_name_index; 
            2. u4 attribute_length; 
            3. u1 info[attribute_length];
        2. 共有21种，没有顺序要求，比如方法体中的字节码储存在code属性内。
		
		
