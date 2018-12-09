本章不是对Java语言语法的总结，而是摘录了一些容易容易出错、遗忘或混淆的基础知识点。

# 操作符

1. 前缀递增++a，为先计算后生成值；后缀递增a++，为生成值后递增；
2. 对于对象，==操作符比较的是引用；对于基本类型，==比较的是值。要比较对象的实际内容应该使用equals，详见`Java基础知识系列3： Object类`。
3. 布尔值不能被赋值给int类型；在应该是用String的地方使用了布尔值，它们会被转换为恰当的文本形式，比如false；
4. 直接常量后面加上后缀表示其类型，比如L表示long，D表示double，F表示float；
5. 八进制用0开头，后面跟0-7的数字；十六进制用0x开头，后面跟0-F；
6. 布尔类型可以进行的运算很有限，不能进行加减，但是可以进行位运算，可以执行按位与(&)、或(|)、异或(^)，但是不能执行按位非(~);
7. 移位操作符只能用来处理整数类型，<<左移操作符按操作符右边的位数将操作符左边的操作数向左移动，低位补0；>>有符号右移操作符，符合为正则高位插0，符号为负则高位插1；>>>无符号右移操作符，无论符号如何，高位补0。如果对char, byte, short 等类型进行移位操作，它们会先被转换为int；
8. Java允许我们把任何基本类型转换为任何基本类型，但是布尔类型除外，它不能进行任何类型转换；
9. float和double转换为整型时，小数部分被舍弃，如果需要四舍五入，则需要用Math.round方法；

<!--more-->

# 执行流程控制

本节仅给出不太常见的Label的用法。在Java中唯一需要使用Label的原因是:跳出多层嵌套循环。比如：
```java
label1:
for(int i = 0; i < n; i++){
	for(int j = 0; j < m; j++){
		break label1;
		continue label1;
	}
}
```

这里的break label1 将中断并跳出标签所指的循环，continue 会到达标签位置，并重新进入下一个循环（i被+1）。


# 大数值
java.math包中的BigInteger和BigDecimal可以处理任意长度的数字序列的值。比如，我们这样初始化：

```java
BigInteger bi = BigInteger.valueOf (100);
BigInteger bi2 = BigInteger.valueOf (100);
BigInteger bi2 = bi.add(bi2);
```

我们只能用它们的add，multiply等方法，不能使用+, x等操作符。不要使用new BigDecimal(10.5)这种初始化方式。


# 包装器

像Integer, Double, Floar等类型称为包装器，它们都有一个对应的基本类型。包装器类的对象是不可变的，一旦构建了包装器就不能改变它的值；包装器还是final的，所以不能定义它们的子类。

因为使用包装器比直接使用基本类型效率低，所以在用它们构建ArrayList等对象时，应该构造小型对象。

字符串转换成整型，可以使用Integer.parseInt("100")。

当将一个Integer赋值给int时，我们称为自动拆箱；反之为自动装箱。自动装箱和拆箱是编译器行为，在编译时自动插入所需要的代码，虚拟机只是执行这些字节码。

Java规范要求：boolean, byte, char<=127, -128到127之间的short和int被包装到固定的对象中。因此以下代码是成立的：

```java
Integer a = 100;
Integer b = 100;
if(a == b)...
```

但是如果将a和b都换成128，上述判断不会成立。

# 方法参数

按值调用表示方法接收的是调用者提供的值；按引用调用表示方法接收的是调用者提供的变量地址。Java总是安值调用。

<!--一个方法可以修改传递的引用所对应的变量值，而不能修改传递值调用所对应的变量值。-->

Java的方法参数有两种类型：

1. 基本类型，传递的是基本类型的一份拷贝；
2. 对象引用，传递是对象引用的一份拷贝。

注意：
1. 一个方法不能修改一个基本数据类型的参数，它修改的只是一份拷贝。
2. 一个方法可以改变一个对象参数的状态，可以通过对象引用操作实际对象。
3. 一个方法不能让对象参数引用一个新的对象，因为它修改的只是引用的一份拷贝。

可变参数Object...等价于Object[], 我们可以将一个数组传递给一个可变参数，也可以接收null，可变参数必需位于方法的最后一个参数。

# String
本节给出String使用中的一些注意点：

1. String是immutable的，传递String时和传递其它对象一样，传递的是一份引用的拷贝；
2. String的不可变的优点是，常量字符串可以被共享，Java设计者认为共享带来的高效率胜过拼接带来的低效率；
3. 用于String的+和+=是Java中仅有的两个重载过的操作符，而Java程序员不能重载操作符；
4. 当重复使用+或+=时，编译器可能自动引用StringBuilder，但是这种优化最好还是在代码中体现，一来显示创建StringBuilder可以指定其大小，二来编译后的代码更简单。如果使用循环来构
建一个String，那么最好使用StringBuilder；
5. StringBuffer是线程安全的，它的很多方法都是synchronized的，所以开销会更大一点。
6. Substring(a, b) 方法的第二个参数是不想复制的第一个位置，这样计算字串长度时候就比较简单，就是b-a；

# Array

## 数组的优点

1. 数组是效率最高的存储和随机访问对象引用序列的方法，但是代价是大小固定，另一种折中的方式是使用ArrayList，它可以自动扩容，但是性能不及数组；
2. 数组可以用来持有具体类型的对象，在泛型还没有引入到Java之前，这种可以在编译期执行的类型检查是一种优势，当然现在有了泛型以后，像List这种容器也可以进行类型检查；
3. 数组可以持有基本类型，但是随着自动包装机制的出现，容器也可以处理基本类型了。

## 数组的创建和使用

数组的标识只是一个引用，指向堆中创建的一个数组对象，这个对象用以保存指向其他对象的引用。数组存在唯一的只读成员length，length保存了数组的大小而不是实际保存元素的数量。

[]是访问数组元素的唯一方式。对象数组保存的是引用，所有引用被自动初始化为null；

基本类型数组直接保存的是基本类型的值，数值型的会被自动初始化为0，boolean型的会被自动初始化为false，char型的会被自动初始化为(char)0。

返回一个数组和返回任何一个其他对象（本质上是引用）一样。以下是几种创建和初始化一维数组的方法：

```java
// 第一种： 创建再赋值
int[] c = new int[5];
for(int i = 0; i < 5; i++){
	c[i] = i;
}

// 第二种： 聚合初始化
MyClass[] m = {
	new MyClass(), new MyClass()
};

// 第三种
MyClass[] n = new MyClass []{
	new MyClass(), new MyClass()
};
```

以下是创建和初始化二维数组的方法，注意自动包装机制同样适用于数组，另外Arrays.deepToString(arr)可以用来打印多维数组：

```java
// 第一种： 直接初始化
Integer [][] a = {
	{1, 2, 3},
	{2, 3, 4},
};

// 第二种： 创建后再初始化
Random rand = new Random (47);
int [][][] a = new int[rand.nextInt (7)][][];
for(int i = 0; i < a.length; i++){
	a[i] = new int[rand.nextInt (5)][];
	for(int j = 0; j < a[i].length; j++){
		a[i][j] = new int[rand.nextInt (5)];
	}
}

System.out.println(Arrays.deepToString(a));
```
第二种初始化方式中产生的多维数组是一个粗糙数组，即每个向量可以拥有任意长度。

另外，我们可以有长度为0的数组，比如new int[0]，这和null不同。

## 泛型与数组
除非被证明存在性能问题，否则应该优先考虑容器而不是数组。使用泛型和数组一起工作的时候要特比小心。

## Arrays的实用方法

1. Arrays.fill()用一个值填充整个数组，如果是对象，就是用同一个对象的引用进行填充。
	```java
	int a2[] = new int[10];
	Arrays.fill(a2, 20); // 用20 填充整个a2 数组
	```
	
2. sort()用于对数组排序: 对于基本类型使用快速排序，对于对象类型使用稳定归并排序；

3. equals()用于比较两个数组的元素是否相同，deepEquals()用于多维数组: 
    1. 元素个数必须相同；
    2. 对应位置的元素也相同；相当于对每个位置的元素调用equals方法，对于基本类型相当于调用其包装器类的equals；
	
4. binarySearch(a, r)在已经排序好的数组中进行二分查找，其中a是数组，r是目标。如果数组包含重复元素，则无法保证找到的是哪一个副本。

	它的返回值为：index of the search key, if it is containedin the array; otherwise, (-(insertion point) - 1). 
	The insertion point is defined as the point at which the key would be inserted into the array: the index of the first element greater than the key, 
	or a.length if all elements in the array are less than the specified key. 
	Note that this guarantees that the return value will be >= 0 if and only if the key is found.

5. Arrays.asList()这个方法的签名如下：
	
	```java
	public static <T> List <T> asList(T... a)
	```
	
	它返回一个底层是数组的List，修改这个List将直接影响数组里的数据；
	
6. System.arraycopy()。参数依次是原数组标识符，原数组起始拷贝的偏移量，目标数组表示符，目标数组起始拷贝的偏移量，拷贝元素个数。它比for循环要高效，但是它不会自动包装和拆包，并且它执行的是浅复制。
	
7. newArray = Arrays.copyOf(oldArray, oldArray.length)这个方法也用来拷贝数组中的元素，第一个参数是源数组，第二个参数是新数组的长度。如果新数组过长，多余的元素将被置0或false；如果新数组过短，则只拷贝前面的元素。

8. Comparable接口的compareTo方法：实现了此接口的类需要实现一个compareTo方法，这个方法接受此类的一个其它对象作为参数，与自身比较，按照预定义的顺序如果该对象比参数中的对象小则返回负数，相等则返回0，否则返回正数，典型的实现如下：
	
	```java
	public class CompType implements Comparable <CompType > {
		
		public int value;
		
		public CompType(int value){
			this.value = value;
		}
		
		public int compareTo(CompType other){
			return value - other.value;
		}
	}
	```
	
	Comparator 接口的compare 方法，典型的实现如下：
	
	```java
	public class CompTypeComparator implements Comparator <CompType > {
		
		public int compare(CompType o1, CompType o2){
			return o1.value - o2.value;
		}
	}
	```

# 命令行参数数组

启动java 程序时的命令行参数。比如java MyApp -msg Hello，那么args[0] 为-msg，arg[1] 为Hello。
