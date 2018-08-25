# 泛型概述

泛型的代码意味着它可以被很多不同类型的对象所重用，比如ArrayList<T>可以用来保存任意特定类型。
	
我们知道原生类型，保存的是Object类型（在擦除小节会讲到），当用get方法获取元素时候，需要进行强制类型转换。

但是泛型提供了类型参数(即类型参数化的概念)，它希望通过解耦类或方法与所使用的类型之间的约束来使类或方法实现最广泛的表达能力。这里的T可以用来指示元素类型，比如
```java
ArrayList <String > files = new ArrayList <>();
```

当调用get的时候不再需要强制类型转换，因为编译器自动插入了合适的强制类型转换，它直接返回正确的类型，比如

```java
String filename = files.get(0);
```
# 泛型类

一个泛型类是具有一个或多个类型变量的类。类型变量使用大写形式，通常比较短，一般用E表示集合的元素类型，用K和V表示关键字与值的类型，T、U 和S表示任意类型。以下是一个泛型类的示例：

```java
public class Pair <T> {
	private T first;
	private T second;
	public Pair() { first = null; second = null;}
	public Pair(T first , T second) { this.first = first; this.second = second;}
	public T getFirst() { return first;}
	public T getSecond() { return second;}
	public void setFirst(T newValue) { first = newValue;}
	public void setSecond(T newValue) { second = newValue;}
}
```

<!--more-->

# 泛型方法

带有类型参数的方法称为泛型方法，泛型方法可以在普通方法中也可以在泛型类中。定义泛型方法时，如果类型参数没有被申明，我们必需先申明；如果在泛型类定义中申明过的，比如上面的例子，就不用申明了。

申明类型参数必须在返回值前修饰符后面加<T>，来声明这是一个泛型方法，持有一个泛型T。比如

```java	
public ArrayAlg{
	public static <T> getMiddle(T... a){
		return a[a.length / 2];
	}
}
```

在调用一个泛型方法时候，在方法名前的尖括号中放入具体的类型，比如

```java
String middle = ArrayAlg.<String>getMiddle("A", "B", "C");
```

大多数情况下<String>可以省略，因为编译器可以推断除类型。但是有时候编译器会警告，比如

```java	
double middle = ArrayAlg.getMiddle(1.0, 2);
```

因为参数分别自动包装成了Double和Integer类型，这时候编译器把getMiddle类型自动推断为它们共有的父类，产生了`Number & Comparable<?>` 类型。这个时候我们可以把类型都改写为double类型，或者加\<Double\>明确我们使用的是double类型。


# 类型变量的限定（边界）

`<T extends BoundingType>` 表示T 应该是绑定类型的子类型(subtype)。这里的T和BoundingType都可以是类或者接口。

一个类型变量或通配符（后文会讲）可以有多个限定。比如`<T extends Comparable & Serializable>`。我们用`&`来分割限定类型，用逗号来分割类型变量。限定中至多有一个类，如果用一个类作为限定，那么它必须是限定列表中的第一个。

# 泛型的擦除Erasure

在泛型代码的内部，无法获得任何有关泛型参数类型的信息。比如List<String>和List<Integer>的类型都是List。Java的泛型是用擦除来实现的，也就是说当使用泛型的时候，任何具体的类型都被擦除成了原生类型。
	
原生类型用第一个限定的类型变量来替换，如果没有给定限定就用Object来替换。比如前文的`Pair<T>`类，将会被擦除成它的原生类型：

```java
public class Pair {
	private Object first;
	private Object second;
	public Pair() { first = null; second = null;}
	public Pair(Object first , Object second) { this.first = first; this.second = second;}
	public Object getFirst() { return first;}
	public Object getSecond() { return second;}
	public void setFirst(Object newValue) { first = newValue;}
	public void setSecond(Object newValue) { second = newValue;}
}
```

Pair是无限定类型，因此类型变量T被擦除成了Object；对于有限定类型，比如`<T extends Comparable & Serializable>`它会被擦除成Comparable。

为了提高效率，我们将tagging（标签）类接口，即没有方法的接口，放在边界列表的末尾。

当调用泛型方法时，编译器会插入恰当的强制类型转换。比如使用者会认为Pair的getFirst方法会返回类型T，但是因为擦除它的实际返回类型使Object，这时编译器会自动地插入强制类型转换，将返回的Object转换为T类型。所以从使用者角度来看，他得到的仍旧是T类型的对象。当存取一个泛型域的时候，编译器也会插入恰当的强制类型转换。

# 桥方法Bridge Method

桥方法是合成方法，有几种常见的情况虚拟机会产生桥方法。我们先来讨论一种和泛型有关的桥方法：当擦除后基类方法的参数类型和实际被调用方法的参数类型不同的时候，虚拟机会合成桥方法。比如

```java
public class SampleTwo {

	public static class A<T> {
		public T getT(T args) {
			return args;
		}
	}
	
	public static class B extends A <String > {
		
		public String getT(String args) {
			return args;
		}
	}
}
```

类B被擦除后，存在两个getT方法，一个是带有String参数且返回String类型的getT，另一个是从类A继承下来但是被擦除了类型参数的getT即带有Object参数，返回Object类型）。编译后的结果如下:

```java
public class SampleTwo$B extends SampleTwo$A{
	public SampleTwo$B();
	...
	public java.lang.String getT(java.lang.String);
		Code:
		0: aload_1
		1: areturn
	
	public java.lang.Object getT(java.lang.Object);
		Code:
		0: aload_0
		1: aload_1
		2: checkcast #2; //class java/lang/String
		5: invokevirtual #3; //Method getT:(Ljava/lang/String;)Ljava/lang/String;
		8: areturn
}
```

这表示编译器将继承下来的getT方法变成了一个桥方法，其内部做了类型检查，并调用了另一个定义在B中的getT方法。类似如下:

```java
public static class B extends A<String > {
	public String getT(String args) {
		return args;
	}
	
	// bridge method
	public Object getT(Object args) {
		return getT( (String) args);
	}
}
```

正常情况下当一个类中定义了或者继承了多个重名但是不同参的方法，虚拟机会调用那个最合适的方法，即如果有一个getT(Object)和一个getT(String)方法，那么带有字符串的调用会调用后者，其它情况会调用前者。但是在此例擦除生成的桥方法中，如果使用非String的参数调用就会报错。

桥方法的第二个应用场景是协变返回类型。协变返回类型同样会出现在泛型方法中，也可以出现在普通方法中。如果方法的参数类型不是类型化参数T，而是空的呢？

我们就会有一个类B中定义的getT()返回String，一个继承自基类A但是被擦除的getT()返回Object。

```java
public class SampleOne {
	
	public static class A<T> {
		public T getT() {
			return null;
		}
	}

	public static class B extends A<String > {
		public String getT() {
			return null;
		}
	}
}

擦除后，它们的代码变成下面的样子:

```java
public class SampleOne {
	public static class A {
		public Object getT() {
			return null;
		}
	}
	
	public static class B extends A {
		public String getT() {
			return null;
		}
	}
}
```

编译后的结果如下:

```java
public class SampleOne$B extends SampleOne$A {
	public SampleOne$B();
	...
	public java.lang.String getT();
		Code:
		0: aconst_null
		1: areturn
	public java.lang.Object getT();
		Code:
		0: aload_0
		1: invokevirtual #2; // Call to Method getT:()Ljava/lang/String;
		4: areturn
}
```

可见继承在基类A的方法getT实际上调用了B类自己定义的返回String的getT方法。Java语言定义不允许写出这样的代码，因为Java语言规定方法签名由方法名和参数共同决定，显然在Java语言规范上这两个无参getT是同一个方法，但是JVM的方法签名定义不同，它不仅考虑方法名和参数，还要考虑返回类型，因此编译器仍旧正常生成桥方法，并且JVM可以正常处理。

第三个使用桥方法的场景是增加继承类的继承方法的可见性。考虑下面的代码:
```java
public class SampleFour {
	static class A {
		public void foo() {
		}
	}
	
	public static class C extends A {
	}
	
	public static class D extends A {
		public void foo() {
		}
	}
}
```

类C的可见性是public，但是它的父类A并只是包可见性。因此在继承A的时候，编译器会插入一个foo的桥方法，来调用A的foo方法，以增强C方法中foo的可见性；类D就没有桥方法，因为D自己的foo方法重写了基类的方法。

对于擦除我们需要记住以下几点:

1. 虚拟机中没有泛型，只有普通类和方法；
2. 所有的类型参数都用它们的限定类型替换；
3. 桥方法被合成来保持多态；
4. 为保持类型安全性，必要时插入强制类型转换。


# 擦除带来的限制

## 不能用基本类型来实例化类型参数

没有`Pair<double>`这种用法，只有`Pair<Double>`。因为擦除之后，Pair类含有Object类型的域，Object不能存储double值。

## 运行时类型检查只适用于原始类型

1. 可以做`if(a instanceof Pair)...`，但是写`if(p instanceof Pair<Integer>)...` 或者`if(p instanceof Pair<T>)...`就会报错。
2. 使用instanceof或者涉及泛型类型的强制类型转换表达式都会看到编译器警告，比如`Pair <String> b = (Pair <String>) a`
3. getClass()返回的是原始类型。比如

	```java
	Pair <String> a = ...;
	Pair <Integer> b = ...;
	if( a.getClass() == b.getClass()){
		// 等价
	}
	```
	
## 不能在静态域或方法中引用类型变量

因为我们可能会希望根据泛型类型来获取或产生某种对象，但是实际上在擦除以后所有的泛型类型都变为了限定类型，从而无法达到我们的目的。比如：

```java
public class Singleton <T> {
	public static T t;  // 报错
	public static T getInstance () { // 报错
		if(t == null) {
			// ... construct a new instance of T
		}
		return t;
	}
}
```

## 不能创建参数化类型的数组

因为正常情况下，不管数组是否被向上转型成，数组都会记住创建它时的类型。但是，在运行时泛型类型是不存在的，也就是说在数组看来Pair<String>和Pair<Integer>是一样的，都是Pair，也就可以绕过数组的类型检查了，尽管往一个Pair<String>的数组里放入一个Pair<Integer>还是会导致类型错误。
	
因此不允许创建参数化类型的数组。比如，以下语句是会报错的：
```java
Pair<String>[] table = new Pair <String>[10];
```

因为擦除之后Pair<String>[]类型的table变成了Pair[]类型，我们可以把它转为Object[]:
```java
Object[] obj = table;
```
obj知道它的元素类型是Pair[]，因此如果你尝试往里面放一个Double肯定会报错，但是放Pair<Double>就会绕过数组的检查，但是在使用时仍旧会导致类型错误。
	
虽然不能创建参数化类型的数组，但是可以申明参数化类型的变量。比如可以申明Pair<String>[]，但是不能用new Pair<String>[10] 初始化它。可以用无限定通配符数组来初始化，然后进行强制类型转换。比如：
```java
Pair <String>[] table = (Pair <String>[]) new Pair <?>[10];
```

这样做的结果是不安全的，因为我们可以在table中储存非Pair<String>的类型，比如Pair<Employee>。
	
当我们在调用getFirst时候就会尝试把Employee转换为String，从而触发ClassCastException。正确的方法是使用ArrayList来保存参数化类型的数组。

## 可变参数和参数化类型

让我们考虑下面的代码：

```java
public static <T> void addAll(Collection <T> coll , T... ts){
	for( t:ts ) coll.add(t);
}
```

ts实际上时一个T类型的数组，即T[]。一般情况下当T是一个对象的时候，我们只是循环将ts中的元素添加到coll 中。但是如果T是一个参数化的类型呢，比如Pair<String>，那么ts不就是Pair<String>[]吗？是不是回到了前面一个问题。
	
但是，对于可变参数列表的参数化类型调用，只会得到警告不会报错。可以使用
```java
@SuppressWarnings("Unchecked");
```
或者
```java
@SafeVarargs
```

来抑制警告。对于只需要读取参数数组的所有方法都可以使用后者的标记。滥用这个标记会由潜在风险，比如我们可以用下列方法创建一个参数化类型的数组并传递给其它方法使用：

```java
@SafeVarargs
static <E> E[] array(E... array){
	return array;
}
```

当E是参数化类型的时候，上一节所说的风险就发生了：我们产生了一个参数化类型的数组，它不受数组类型检查的约束。

## 不能实例化类型变量

不能使用new T(), 或者T.class，因为类型擦除会把这里的T 都变成限定类型。也不能构造泛型数组，比如new T[2]，因为擦除这样构造出来的是Object[2]。比如下面的写法：

```java
public class ArrayList <E>{
	private E[] elements;
	
	public ArrayList(){
		elements = (E[]) new Object [10];
	}
}
```
这里的强制类型转换(E[]) 其实是假的，因为类型擦除其实使它变成了(Object[])。编译器会给处警告：

```text
Type safety: Unchecked cast from Object[] to E[]
```

我们可以

1. 通过显示传递参数类型，通过反射调用Class.newInstance方法来构造泛型对象。比如：
	```java
	public static <T> Pair <T> makePair(Class <T> cl){
		try{
			return new Pair <>(cl.newInstance(), cl.newInstance());
		}catch(Exception ex){
			return null;
		}
	}
	```

2. 通过反射获取类型后直接实例化，但是会得到Unchecked cast警告。比如：

	```java
	public static <T> T getA(T... args) throws InstantiationException , IllegalAccessException{
		System.out.println(args.getClass().getName());
		T a = (T)args.getClass().getComponentType().newInstance();
		return a;
	}
	
	public static <T> T getB(T args) throws InstantiationException , IllegalAccessException{
		System.out.println(args.getClass().getName());
		T a = (T)args.getClass().newInstance();
		return a;
	}
	
	// 创建泛型数组
	public static <T> T[] getC(T args) throws InstantiationException , IllegalAccessException{
		System.out.println(args.getClass().getName());
		T[] a = (T[])Array.newInstance(args.getClass(), 2);
		return a;
	}
	```

## 不能抛出或者捕获泛型类的实例

1. 不能抛出，也不能捕获泛型类的对象，即不能throw new T，有不能catch(T e)...；
2. 可以在方法签名中申明抛出异常类对象，即throws T；
3. 在边界限制中可以用Throwable，比如`<T extends Throwable>`，但是泛型类不能扩展Throwable，比如`Problem<T> extends Exception`；
4. 正常情况下，必需对所有已检查(checked)的异常提供一个异常处理器，但是利用泛型可以消除这个限制。比如下面的代码：
	
	```java
	public abstract class Block{
		
		public abstract void body() throws Exception;
		
		public Thread toThread(){
			return new Thread(){
				public void run(){
					try{
						body();
					} catch( Throwable t){
						Block.<RuntimeException>throwAs(t); // 编译器会认为t是一个未检查异常
					}
				}
			}
		}
		
		@SuppressWarning("unchecked")
		public static <T extends Throwable> void throwAs(Throwable e) throws T{
			throw (T)e;
		}
	}
	```
	注意这里Body是一个抽象的会抛出Exception的方法，由具体实现的类来实现此方法，但是我们的run方法是没有异常声明的，因此正常情况下所以已检查异常要么必需处理调，要么像Exception章节中所说的，把它们包装到未检查异常中抛出。
	
	但是这里我们通过泛型，没有做这种包装，只是直接抛出异常，而编译器认为我们抛出的是未检查异常。


## 擦除引起的冲突

1. 比如考虑下面的类
	```java
	public class Pair <T>{
		public boolean equals(T value){
			return first.equals(value) && second.equals(value);
		}
	}
	```
	如果有一个Pair<String>，那么它会有一个从Object继承下来的`boolean equals(Object)`和一个自身的equals方法`boolean equals(String)`。
	
	但是String会被擦除成Object，所以我们有了两个完全相同的方法。因此必需重命名引发错误的方法。

2. 为了避免与合成的桥方法产生冲突，必需强制限制一个类或类型变量不能同时成为两个接口类型的子类，而这两个接口是同一接口的不同参数化。比如下面的第二个类定义是非法的：

	```java
	class Calendar implements Camparable<Calendar>{...}
	class GregorianCalendar extends Calendar implements Comparable<GregorianCalendar> {...}
	```
	
	第二个方法的接口中实现了两次Comparable，但是参数不同。因为Comparable<X>会合成以下桥方法：
	
	```java
	public int compareTo(Object other) {return compareTo( (X)other);}
	```
	
	不能有两个一模一样的桥方法。


# 泛型类型的继承

假设Manager是Employee的子类型，因为擦除，ArrayList<Manager>和ArrayList<Employee>没有继承关系，ArrayList<Manager>不是ArrayList<Employee>的子类型。
	
但是，ArrayList<Manager>和ArrayList<Employee>同时又分别是List<Manager>和List<Employee>的子类型；

ArrayList<Manager>和ArrayList<Employee>都是ArrayList<? extends Employee>的子类型；

ArrayList<Manager>和ArrayList<Employee>又都是ArrayList<? super Manager>的子类型。

ArrayList<? extends Employee>和ArrayList<? super Manager>是ArrayList的子类型，也是List的子类型。即永远可以将参数化类型转换为原始类型。但是转换为原始类型以后，调用set方法设置一个不正确的类型，只会得到一个编译时警告，但是在运行时会报ClassCastException，比如
```java
Pair <Manager > man = new Pair <>(ceo , cfo);
Pair raw = man;
raw.setFirst(new File (...));
```

这和Java数组很像，我们将Manager[]向上转型给Employee[]，但是在往实际类型是Manager但是引用类型是Employee的数组里添加一个低级别雇员的时候就会报ArrayStoreException。


# 通配符类型

Java的泛型通配符有三种情况：

1. 上边界限定的通配符`<? extends Employee>`; 
2. 下边界限定的通配符`<? super Employee>`; 
3. 无限定的通配符`<?>`。

## 上边界限定的通配符

`List<? extends Employee>`表示的是某种特定的Employee类型的列表，这个特定的类型可以被向上转型为Employee。

**注意**：它可以是Employee本身或者任何Employee的导出类，Employee是它的上边界。

但是，这里的**特定**表示该List只能持有一种类型，它不能同时持有Manager，又持有LowlyEmployee。

这里我们说List<Employee>和List<Manager>都是`List<? extends Employee>`的子类型，`List<? extends Employee>`又是List的子类型（注意List<Manager>不是List<Employee>的子类型）。
	
**限制**：虽然`List<? extends Employee>`表示某种特定的Employee或其子类型，但是我们并不知道它具体是什么类型。

假设这种未知类型是T。如果我们想要添加一个People类的对象p到这个List，编译器会不允许，因为p是Employee的基类的对象，它可能不具有Employee的某些特性，因此添加p是不安全的；

如果我们想要添加一个Manager类的对象m到这个List，编译器也不会允许，因为类型T可能会是LowlyEmployee，它和Manager类没有继承关系，添加m同样会是不安全的。编译器只会允许添加能够被安全地向上转型到T的对象，而编译器并不知道T的确切类型，所以它不允许添加任何对象到这个List，除了null以外。

相反，编译器允许将T赋值给任何Employee或其基类，因为T的类型`? extends Employee`保证了其上边界为Employee，那么它可以被安全的向上转型为Employee本身或任何其基类，但因为擦除，这也是我们所唯一知道的了（我们不确定它到底是Employee 的什么子类）。

因此对于上边界限定的通配符`<? extends Employee>`，我们可以从它获取(get)，但不能写入(set)，除了null。

**应用**：如上所述，在`List<? extends Employee>` 中我们不能调用add 方法，但是我们可以调用contains，indexof等方法。这是泛型类的设计者在编写泛型类时决定的。请看这些方法的参数：
```java
public boolean add(E e)
public boolean contains(Object o)
public int indexOf(Object o)
```
那些可以被安全调用的方法的参数为Object，而那些需要考虑实际类型的则被设置为泛型类型。当我们用`<? extends Employee>`作为参数类型调用add时，编译器不知道确切的类型所以它不接受任何类型。

在编写我们自己的泛型类时要考虑这些情况，一般来讲获取类型的方法参数可以是Object，它不需要考虑上边界限定的通配符，修改用的方法参数应该是泛型的。


## 下边界限定的通配符

`List<? super CompanyAEmployee>`表示的是某种特定的Employee或其基类的列表。同样它只能表示一种类型，这种类型肯定是Employee或这是它的基类。这里我们说`List<? super CompanyAEmployee>`是List<Object>的父类，但是`List<?>`和`List`的子类。
	
**限制**：我们可以向这个`List`添加任何CompantAEmployee或者其子类，比如CompanyAManager，因为这些类都可以被安全地向上转型为CompanyAEmployee；

但是我们不能添加CompanyBManager，因为CompantBManager和CompanyAEmployee没有任何继承关系。也不能添加Employee（假设其为CompantAEmployee的基类）。

然而，从该List中get出来的对象只能被赋值给Object，因为编译器除了知道它是CompanyAEmployee的基类以外，并不知道它具体的类型。

Core Java中对此的总结是，带有上边界限定的通配符可以从泛型对象读取，带有下边界限定的通配符可以从泛型对象写入。

## 复杂的通配符

比如`<T extends Comparable<? super T>>`，表示的是一个实现了Comparable<? super T> 接口的类型T，这个接口的类型可以是T或者其基类。这么写主要增加通配符的适用范围，比如有以下两个方法：
```java
public static <T extends Comparable <T>> void sort1(List <T> list){
	Collections.sort(list)
}

public static <T extends Comparable <? super T>> void sort2(List <T> list){
	Collections.sort(list)
}
```

并且有两个类的定义：

```java
class A imeplements Comaparble <A>{
	@Override
	public int compareTo(A other){
	//...
	}
}
class B extends A{}
```

如果我们有一个`List<B>`，我们可以用它调用sort2，但是不能调用sort1，因为`List<B> implements Comaprable<A>`对于sort1而言，需要B和A是一致的，而sort2只需要A是B的父类。


## 无边界限定的通配符

还有一种无限定通配符`<?>`, 它的get类型方法只能被赋值给Object引用，set类方法（除了null 外）不能被调用。

对于某些不需要实际类型的操作(即方法体的逻辑与泛型无关) 时，我们可以使用无限定通配符，比如：

```java
public static boolean containsNull(List <?> list){
	return list.contains(null);
}
```

因为擦除会将`<?>` 擦除到`<Object>`, 所以无边界限定的通配符和原生类型很像，但是它表示开发者希望使用泛型而不是原生类型，只不过在当前情况下，泛型参数可以持有任意特定类型。

`List`表示的是持有任何`Object`类型的原生`List`，而`List<?>`表示的是具有特定类型的非原生`List`，只是我们不知道那种类型是什么。下面我们来看一个原生类型和无边界限定通配符的区别：

```java
// 我们可以调用原生类型的set 方法， 但是会有警告；
// 因为任何对象被传递原生类型的set ， 都会被向上转型为Object ；
// 因此使用了原生类型就放弃了编译器检查。
Pair raw = new Pair();
raw.setFirst(new Main());
// 将原生类型指向无边界限定通配符的类型， 同样只有警告
Pair<?> unbounded = new Pair<Integer>();
raw = unbounded;
raw.setFirst(new Main());
// 这里就会报错了， 我们没法调用无边界限定通配符的set方法
// 报错：The method setFirst(capture#3-of ?) in the type Pair <capture#3-of ?> is not applicable for the arguments (Main)
unbounded.setFirst(new Main());
```

总结来说，原生类型可以持有任意类型，它们都会被向上转型为`Object`类型；`<?>`则只能是特定类型，但是它又不知道具体是什么类型，所以干脆什么都不接受。


## 捕获转换

通配符不是类型变量，不能在代码中用`?`作为一种类型，但是当我们需要使用某个`?`变量（比如交换元素，需要临时保存时），我们需要将`?`捕获。比如
```java
public static void swap ( Pair<?> p ){
    swapHelper(p);
}

public static <T> void  swapHelper(Pair<T> p){
    T t = p.getFirst();
    p.setFirst(p.getSecond());
    p.setSecond(t);
}
```
这里`swapHelper`的`T`捕获了通配符，它虽然不知道这是哪种类型的通配符，但是它是个明确的类型。

通配符捕获只有在编译器能够确信通配符表达的是单个、确定的类型时才是有效的。比如`ArrayList<Pair<T>>`不能捕获`ArrayList<Pair<?>>`，因为这个List可以保存两个`Pair<?>`，而这里的?表示不同类型。