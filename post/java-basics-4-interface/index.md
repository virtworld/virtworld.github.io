# 抽象类和抽象方法

包含抽象方法的类被称做抽象类。如果一个类包含一个或多个抽象方法，它必需被定义为抽象类。

抽象类可以包含具体的数据和具体的方法。抽象类不能实例化，不过可以有一个抽象类的对象变量，但是它只能引用非抽象子类对象。如果从一个抽象类继承，要么实现它所有的抽象方法，要么继承的类也是个抽象类。

我们也可以创建一个没有任何抽象方法的抽象类，比如用于阻止该类的实例化。

抽象类的优点是我们可以明确告诉用户哪些方法需要由子类实现，并且可以很容易地将公共方法沿着层次向上移动；抽象类也有限制，Java不允许多重继承，也就是一个类只能扩展于一个类，而每个类可以扩展自多个接口。

Java不提供多重继承而使用接口来实现类似多重继承的好处在于，避免多重继承的复杂性和低效性。

<!--more-->

# 接口

接口是一个完全抽象的类，它根本没有提供任何实现。它的所有方法只确定了方法名，参数列表和返回类型，没有任何方法体。接口用来实现类与类之间的协议：所有实现了特定接口的类都存在该接口所声明的方法可以被调用。

因为一个类可以实现多个接口，因此一个类可以被向上转型为多个接口类型，从某种意义上讲，这是多重继承的变种。接口可以是public或默认包访问权限的。

接口中可以包含域，但是它的域默认是public static final, 因此必须被初始化，但是接口中的域可以被非常量表达式初始化，比如使用随机函数生成的值。方法默认是public abstract的。

使用接口最终原因是为了能够向上转型为多个基类型，以及由此带来的灵活性。第二个原因和使用抽象类相同，就是防止客户端程序员实例化该对象。如果某事物应该成为一个基类，那么首选应该是接口，特别是不带任何具体方法实现的类，否则再考虑使用抽象类。

Java8增加了新的特性，允许在接口中添加默认方法，默认方法有default修饰符，并包含完整的方法体。

在继承接口中的默认方法时，我们可以

1. 不管哪个默认方法，这个方法和其他继承下来的方法一样可以被调用；
2. 重写默认方法。我们可以重写成抽象方法（没有方法体的方法）或者重写成非抽象方法。Java8还在接口中增加了静态方法，静态方法含有方法体。

在同时存在继承类和接口的情况下，具体的类应该放在前面，然后是接口。如果接口和父类都含有签名相同的方法，那么父类中的方法可以作为接口中的方法的实现，因此不一定要在继承类中再覆盖。比如：

```java
class A{
	public void method(){}
}

interface B {
	void method();
}

class C extends A implements B{
	// 不必定义method 方法
}
```
在类的继承中，一个类只能继承extends自一个类，可以实现implements多个接口。接口本身也可以进行扩展，我们可以让一个接口extends多个接口，这种语言只适用于接口。比如：
```java
interface A{
	int methodA();
}
interface B{
	int methodsB();
}

interface C extends A, B{
	int methodC();
}

class D implements C{
	public int methodA(){return 0;}
	public int methodB(){return 0;}
	public int methodC(){return 0;}
}
```

注意：在组合使用继承类和接口时，如果方法签名相同但是返回值不同会造成冲突报错, 比如：
```java
interface I1 { void f(); }
interface I2 { int f(int i); }
interface I3 { int f(); }

class C1 { public int f() {return 1; } }

// Error: method f differs only on return type.
interface I4 extends I1, I3{}

// Error: method f differs only on return type.
class C2 extends C1 implements I1{}

// OK: two method fs overloaded.
class C3 implements I1, I2{
	public int f( int i ) {return 0;}
	public void f(){}
}

// OK: overloaded f
class C4 extends C1 implements I2{
	public int f(int i){ return 0; }
}

// OK: same method fs(sigantures and return type) in interface and inherited class are fine.
class C5 extends C1 implements I3{
	public int f(){ return 0; }
}
```


# 嵌套接口

首先是接口中嵌套接口。接口中的接口默认就是public的，不能申明为private。如果接口A包含接口B，当我们实现接口A的时候，我们只需要实现A中的所有方法，不需要实现B中的方法。

其次是在类中嵌套接口。类中的接口可以是public，包访问或者private可见性。这里我们要讨论一下定义在类内部的私有接口。私有接口不能在定义它的类的外部被实现。

如果类A包含一个私有接口I和一个实现了I的内部类B，如果A有一个public方法x，x的返回类型是I的引用，x创建了一个B的实例并返回。那么在类A外部，虽然x是public的，但是我们没法使用它，因为我们没法在定义I的类外部使用I。唯一能够使用I的引用的是A的方法。所以实现私有接口的目的是强制定义该接口中指定的方法，同时不添加类型信息（即该实现不能向上转型为该私有接口）。类的外部不能认为该内部类实现了此接口。


# 接口与回调

在某个特定事件发生时采取某个动作（调用某个方法）称为回调。我们需要把这个待事件发生后调用的方法传递给调用者。因为Java是面向对象编程，我们不像C++那样传递函数指针，而是传递一个类的对象，并让这个类实现某个接口，确保它会实现回调方法。比如说计时器，每隔1秒钟调用一个方法。

```java
ActionListener listener = new TimePrinter();
Timer t = new Timer(1000, listener);
```

这里的listener 就是一个实现了某回调方法的对象, 这个回调方法定义在ActionListener 接口中。
```java
class TimePrinter implements ActionListener{
	public void actionPerformed(ActionEvent event){
		System.out.println("1s!");
	}
}
```