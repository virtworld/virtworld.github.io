# 变量的初始化

方法内的局部变量，必需显示初始化后才能使用，使用未初始化变量会导致编译器报错；类成员变量或静态域未初始化就会被赋初始值，比如对象会是null，boolean是false，int是0等。

给类成员变量赋值可以在该变量定义的地方进行。不初始化类变量不是一种好的习惯。

# 初始化顺序

当首次调用类的静态方法（包括main方法）或静态域时，或者首次创建对象（其实创建对象所调用的构造器也是静态方法）的时候，JVM会查找类的路径，并加载类对应的.class文件，然后创建一个Class对象。

如果在加载该Class文件的时候发现这个类有父类，那么加载器也会去加载它父类的Class，直到所有Class文件都被加载完。

在加载每个Class对象的时候，会对每个类进行静态初始化，这个静态初始化只执行一次，也就是在类第一次被引用的时候执行。

<!--more-->

静态初始化包括类中定义的static域，static代码块。这个初始化和类的加载顺序一样，从根类开始，然后到它的继承类，因为有些类的静态初始化可能依赖其父类的静态初始化。

无论这些static域或代码块定义在类的什么位置，它们都会被按顺序执行。这个顺序时按照代码在类中的先后顺序执行。比如下面的代码按照t1, t2, t3 的顺序执行：

```java
class A{
	static T t1 = new T();
	static {
		T t2 = new T();
	}
	static T t3 = new T();
}
```

如果没有创建新的对象，那么初始化到这里就结束了，否则需要继续进行。如果创建了新的对象，那么首先从根类开始到最外层的导出类，在堆上分配内存。这块内存储存空间会被清零，这里就会自动地把类对象中的所有数据类型设置成了默认值：基本类型为0，boolean为false，对象为null。

当所有的内存分配和清零工作完成后，才开始执行对象成员变量初始化和对象初始化代码块。比如下面代码所示：

```java
class A{
	private int id;
	private String name;
	private Date dob = new Date();
	
	{
		id = 0;
		name = "Alex";
	}
}
```

首先执行的是根类的对象成员初始化。对象的成员的初始化顺序和静态初始化一样，按照代码定义在类中的先后顺序，因此不要在前面申明的变量中读取后面申明的域，这会造成循环引用。如果在成员对象初始化中引用了一个另一个未加载的类的静态域或静态方法，那么那个类及其父类会被类加载器按照我们之前说的方法进行加载。当根类的成员初始化结束后，就会执行根类的构造器中的代码。

如果在父类的构造器中调用了一个动态绑定的方法，而这个方法将会在子类中被覆盖，并且这个方法使用了子类的某个成员变量，那么这个时候子类的成员变量可能还没有被正确的初始化，也就是说都是0值。这种构造器内的多态行为要特别小心，最好在构造器中避免调用其它方法。在构造器中唯一能被安全调用的方法是父类本身的final或者private方法，因为这些方法不能被覆盖。

当根类的构造器中的代码执行完后，JVM就会开始初始化其导出类的成员、调用导出类的构造器，直到最外层的导出类被初始化。

这里构造器的调用可以在导出类中用super语句来指定，或者自动调用父类的默认构造器。如果使用super语句，那么它必需是构造器的第一条语句。如果即没有使用super语句，父类又没有默认构造器那么就会报错。这里的super和this一样，都有两个用途: 第一是调用隐式参数，第二是调用该类或其父类的其它构造器。super并不是一个对象引用，不能将super赋值给另一个变量。

以下测试可以反映出一部分初始化顺序：

```java
class SubC1{
	static{
		System.out.println("Static␣SubC1");
	}
	public SubC1(){
		System.out.println("SubC1");
	}
}

class SubC2{
	static{
		System.out.println("Static␣SubC2");
	}
	public SubC2(){
		System.out.println("SubC2");
	}
}

class SubD1{
	static{
		System.out.println("Static␣SubD1");
	}
	public SubD1(){
		System.out.println("SubD1");
	}
}

class SubD2{
	static{
		System.out.println("Static␣SubD2");
	}
	public SubD2(){
		System.out.println("SubD2");
	}
}

class SubA{
	static{
		System.out.println("Static␣SubA");
	}
	public SubA(){
		System.out.println("SubA");
	}
}

class C{
	static{
		System.out.println("Static␣C");
	}
	
	private SubC2 c2 = new SubC2();
	private SubC1 c1 = new SubC1();
	
	public C(){
		System.out.println("C");
	}
}

class D extends C{
	static{
		System.out.println("Static␣D");
	}

	private SubD2 d2 = new SubD2();
	private SubD1 d1 = new SubD1();
	
	public D(){
		System.out.println("D");
	}
}

public class A extends D{

	static{
		System.out.println("Static␣A1");
	}

	private SubA a = new SubA();

	public A(){
		System.out.println("A");
	}
	
	public static void main(String[] args){
		new A();
	}
	
	static{
		System.out.println("Static␣A2");
	}
}
```

该测试的输出是：
```text
Static C
Static D
Static A1
Static A2
Static SubC2
SubC2
Static SubC1
SubC1
C
Static SubD2
SubD2
Static SubD1
SubD1
D
Static SubA
SubA
A
```

一般来讲，JVM 垃圾回收器会处理清理工作，但当需要手动释放资源等情况时需要编写代码进行清理。

资源的释放顺序一般和创建的顺序相反，先创建的最后释放。比如创建数据库资源时，一般是先创建Connection，然后是PreparedStatement，最后获取查询结果ResultSet。那么释放顺序就是反过来的ResultSet，PreparedStatement，最后是Connection。如果有父类需要清理，那么先执行自身（子类）的清理工作，然后调用父类的清理方法。

# 数组初始化

数组的定义方式可以是int[] a 或int a[]，建议使用前者。

每个数组都有一个固定的成员变量length，保存了数组的长度。

数组变量被赋值给另一个数组变量时，只是复制了这个数组的一个引用。

有三种数组的初始化方式：

1. 在数组定义的地方初始化。int[] a = {1,2,3};
2. 使用new，并指定数组大小，但不赋值。Integer[] a = new Integer[4]; 这创建的是一个长度为4的引用数组（因为Integer是对象而不是基本类型）。但是所有的元素没有被初始化，数组元素中的基本数据类型会被初始化为默认值，对象引用会被初始化为null。
3. 使用new，不指定大小，但是赋初始值。Integer a = new Integer[]{new Integer(1), new Integer(2),3}。

# 重载，this关键字和可变参数列表

重载：方法名相同，但是形参不同的方法被称为方法重载。方法名和参数类型被称为签名。返回类型不是签名的一部分，同一个类中不能存在两个名字和参数类型相同，返回类型却不同的方法。

this有两种用法。其一、this 关键字只能在非静态的方法内部使用，表示的是对`调用方法的那个对象`引用，所以通过this可以调用`调用方法的对象`的域和方法。其二、this 带有参数列表表示的构造方
法。只有在构造方法中才能用this调用其它构造方法，而且这个调用必需放在构造方法的第一行，而且只能调用一次。

可变参数列表，比如：
```java
void method(Integer... args){}
void method(Double... args){}
```

可变参数列表可以接受一个对应数据类型的数组作为参数，比如method(new Integer(){1, 2})，也可以接受多个对应数据类型的参数，比如method(new Integer(1), new Integer(2))，也可以接受空参数，比如method()。然而在这个例子中，空参数会造成歧义，两个method 到底调用哪一个是不定的，因此会报错。

更多关于初始化顺序以及清理机制，详见JVM相关笔记。