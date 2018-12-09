内部类就是定义在另一个类中的类。使用内部类有以下几个好处：

1. 内部类的方法可以访问其类定义所在作用于的数据，包括私有数据；
2. 内部类可以对同一个包中的其他类隐藏；
3. 如果需要定义一个回调函数但不想编写大量代码时，使用匿名内部类比较方便。

<!--more-->

# 内部类的隐式引用

内部类的对象有一个隐式的引用，它指向创建它的外部类的对象（static内部类没有这种附加指针，后文会讨论）。这使得内部类的对象既可以访问自己的数据域，也可以访问创建它的外围类的对象的数据域。比如以下代码（虽然B类位于A类内部，并不意味着每个A类有一个B类的实例）：
```java
public class A{
	private boolean condition;
	public A(){
		condition = true;
	}

	public class B{
		public void doSomething(){
			if(condition){...}
		}
	}
}
```

这里的condition来自外围类。要获取外围类对象的数据，必需有外围类对象的引用。编译器通过修改所有B类的构造方法，向其中添加一个外围类对象引用作为参数，使内部类获得外围类的引用。
下面的代码解释了这一过程, 其中的outer并不是Java的关键字，只是用来说明这个过程，并且实际上这个引用对我们并不可见：

```java
// B 的默认构造方法被修改为如下
public B(A a){
	outer = a
}

// 在B 被创建的时候， 自动将this 指针传给B 的构造方法
B b = new B(this);
```

# 内部类的可见性

我们可以将B类申明为private，这样只有A类的方法才能构造B对象。注意，只有内部类可以具有private可见性，正常的类要么使public，要么使包可见性。

# 内部类的特殊语法

1. 内部类中使用外围类对象的引用的语法是

	OutClass.this

	比如我们可以把上述例子中的B类的方法doSomething等价地改写成：
	
	```java
	public class A{
		
		private boolean condition;
		
		public A(){
			condition = true;
		}
		
		public class B{
		
			public void doSomething(){
				if(A.this.condition){...} // <--
			}
		}
	}
	```
	
2. 外围类（或其他类）构造内部类的方法的语法是

	outerObject.new InnerClass(construction parameters)
	
	比如我们可以这样构造上述例子中的内部类B：

	```java
	public class A{
		private boolean condition;
		
		public A(){
			condition = true;
			B b = this.new B(); // <--
		}
		
		public class B{
			public void doSomething(){
				if(A.this.condition){...}
			}
		}
	}
	```
	
	首先，内部类对象的外围类引用一定是指向类定义中包裹在内部类外面的外围类的某个实例的，这个引用不可能指向其它不相关类的实例。
	那么，我们看这条语句，这条语句将新构造的b对象的外围类引用设置为创建内部类对象的方法中的this引用，即上述构造对象的语句所在的方法是在外围类中。这种情况下，this是多余的，可以去掉。
	
	然而，当B类是public内部类时，我们可以在其他任何类的方法中创建该内部类，我们只需要将新创建的内部类对象b的外围类引用指向任何一个A的对象。比如在另一个完全不相关的C类的某个方法中，我们先创建了一个A类的对象：
	
	```java
	public Class C{
		public C(){
			A a1 = new A();
		}
	}
	```
	
	然后，我们要创建一个A类的内部类B的对象b1，并且把b1外部类引用设置为a1(如果内部类B为private，那么该语句就会报错)：
	
	```java
	public Class C{
		public C(){
			A a1 = new A();
			A.B b1 = a1.new B();
		}
	}
	```

	这里我们还演示了在外围类作用于之外（C 类中）如何引用内部类：
	
	OuterClass.InnerClass
	
# 内部类的安全性

内部类是一种编译器现象，编译器将内部类翻译成用$符号连接的外部类和内部类名的常规类文件，与虚拟机没有关系。

既然内部类编译后是一种常规的类，它是怎么访问外围类的私有数据的呢？如果内部类访问了外围类私有数据域，外围类就会产生一个可见性为包级别的静态方法，该静态方法接受一个外围类对象作为参数，返回该对象的某私有数据域，这个私有域正是内部类需要用到的域。

理论上，可以通过附加在外围类所在包中的其它类访问外围类的私有数据域。比如，上面的外围类A和内部类B编译后可能产生如下情况：

```java
public class A{
	private boolean condition;
	
	static boolean access$0(A){...};
	
	public class B{
	
		public void doSomething(){
			if(access$0(outer)){...}
		}
	}
}
```

# 局部内部类

如果只在某个方法中使用内部类，可以把内部类定义在该方法内，作为一个局部内部类。局部内部类不能有public或private修饰符，它的作用域被限定在这个局部类的块中。局部类的有以下两个特点:

1. 对外部完全隐藏，即使同一个类的其他方法也不能访问它;
2. 除了可以访问外围类以外，还可以访问局部变量，但是那些局部变量必须被声明为final。

考虑以下这种情况：一个局部内部类引用了一个局部变量。局部代码首先创建该内部类，再将内部类引用传递给外部代码，最后局部代码块结束了。此时局部变量已经不存在了，但是外部代码使用这个传递给它的内部类时就会有问题，因为它引用了一个已经不存在的局部变量。
所以，在局部内部类被创建的时候，如果它引用了局部变量，那么该变量就会作为构造函数的一个隐式的参数传递给它，并以final修饰符的成员变量保存起来。这样就算创建它的局部代码块结束，这个局部类还是可以访问这个局部变量。

声明为final确保了局部类的成员变量初始化后不再改变，使得它和代码块的局部变量保持一致。有时候为了更新局部变量，我们可以用一个只包含一个元素的一维final数组来代替局部变量。比如以下匿名内部类，更新了其外部的方法中的技术变量。

```java
final int[] counter = new int[1];

for(int i = 0; i < dates.length; i++){
	dates[i] = new Date(){
		public int compareTo(Date other){
			count [0]++;
			return super.compareTo(other);
		}
	}
}
```

# 匿名内部类

如果只需要创建一个局部内部类的对象，那就可以使用匿名类了，因为没有必要命名了。如果构造参数的圆括号后面跟一个花括号，那么正在定义的就是匿名内部类。

```java
public class A{
	public void method1(){
		SuperType type = new SuperType(Construction Parameters){
			// inner class methods and data.
		}
	}
}
```

SuperType可以是一个类或接口，新创建的匿名内部类对象就是实现了或继承了这个接口或类。由于构造器名字必须与类名相同，而匿名类没有类名，所以匿名类不能有构造器。

我们将构造器参数传递给父类的构造器，因此在匿名内部类实现接口的时候（即SuperType 为接口的时候）不能有任何构造参数。

双括号初始化：

```java

List<String> b = new ArrayList<String>(){
	{
		add("A"); 
		add("B"); 
	}
};
```
	
外层括号创建了一个ArrayList的匿名子类，内部括号则是一个对象构造快。

使用匿名内部类时，需要小心考虑其父类或父接口的equals的实现，具体参见`Java基础知识系列3： Object类`

匿名内部类还有一个用途：在一个静态方法中获取静态方法所在类的类名（非静态方法调用getClass实际上调用的是this.getClass()，静态方法没有this 引用）。
```java
new Object(){}.getClass().getEnclosingClass().getName();
```

# 静态内部类

如果内部类不需要访问外围类对象的时候，只是想把它隐藏在外围类中时，应该将内部类声明为static，以便取消对外围类的引用。

静态内部类和其他内部类完全一样，除了不能引用外围类对象以外。当在静态方法中构造内部类对象时，必须使用静态内部类。接口中声明的内部类自动为static和public的。