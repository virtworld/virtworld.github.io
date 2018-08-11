> 本文是面向对象设计的读书笔记。主要包括四部分：面向对象思想的回顾、面向对象设计尝试解决的是什么问题、面向对象设计的原则以及GoF中提到的面向对象的设计模式。主要参考了以下书目：

>1. Design Patterns: Elements of Reusable Object-Oriented Software
2. Head First Design Pattern
3. Agile Software Development: Principles, Patterns, and Practices
4. Thinking in Java, 4th Edition
5. Core Java Volume I - Fundamentals

> 文章最初是我为单位写的Powerpoint格式的培训材料，所以内容将基本上采用bullet point的形式呈现。

# **面向对象编程思想回顾(Java语言)**
## **OO基本要素一：抽象**
1. 抽象既可以是一个过程，也可以是一个实体。抽象作为过程，尝试提取一个事物中关键的细节，同时忽略掉那些不关键的信息；抽象作为实体，是一个具体事物的外部表示。
2. 所有的程序设计都尝试建立起问题空间的问题模型（比如，一项业务）与解空间的机器模型（比如，一段程序）之间的联系，这是一种抽象过程。
3. 在面向对象的设计中，我们把问题空间中和解空间中的元素的表示都称为对象，这是抽象的实体。
4. 我们能够解决问题的复杂性取决于抽象的类型和质量。
5. 抽象有很多层级：当抽象层次提高时，我们得到的是更重要的，更少的信息；相反，当抽象层次降低时，我们将看到更多的细节。

## **OO基本要素二：封装**
1. 封装和抽象一样，可以被看作是一个过程，也可以被看作是一个实体。封装作为一个过程，指的是将一个或多个事物包裹到一个容器里的动作；封装作为一个实体，指的是一个包含有一个或多个事物的包裹。
2. 在面向对象编程中，对象将数据和功能封装在一起，来满足某些特定的请求。这些请求由对象的接口定义（这里的接口指的是暴露给外部调用的方法）；实现这些接口的代码和隐藏的数据构成了对象的实现。
3. 封装将类变成软件的基本构件，提高了内聚性：每个类作为一个服务提供者，可以很好的完成某项任务，但又不做超出其设计范畴的工作。
4. 封装将类的实现和类的使用分开，降低了耦合性：类的设计者可以改变类的内部工作方式（实现）而不影响类的使用者使用类（接口）。为了确保使用者不接触类的实现，Java提供了访问修饰符。

## **抽象 vs 封装**
1. 抽象决定了哪些特定的信息可见，哪些特定的信息被隐藏。
2. 封装指的是将信息包裹起来，来实现特定信息的隐藏和可见。
3. 抽象关注的是事物的外部表示，封装关注的是事物的内部实现。

<!--more-->

## **OO基本要素三：继承**
1. 父类包含其所有子类所共享的特征和行为：子类包含了父类的所有接口，所有可以发送给父类的请求，也可以发送给子类。子类和父类拥有相同的类型；
2. 子类在继承父类的基础上，增加了自身特有的数据和行为：
  1. 增加新的方法和数据。子类和父类的关系被表示为is – like - a；
  2. 改变父类方法的行为（覆盖Overriding）来实现子类和父类行为上的差异。纯粹的只替代不新增的继承，子类和父类的关系被表示为 is – a。
3. 在Unified Modeling Language中，继承关系表示为泛化和实现关系，如下图 
{{% figure class="center" src="/images/oodesign/inheritance-example.png" alt="继承示例" title="继承示例"  %}}


## **组合**
1. 在面向对象的上下文中，我们统称has-a为组合关系；
2. 在UML的定义中，我们将其细分为组合、聚合和关联：
  1. 组合是一种最强的关联关系，整体与部分有相同的生命周期，比如人和心脏的关系；
  2. 聚合是一种相对弱的关联关系，整体与部分有各自的生命周期，比如公司和员工的关系；
  3. 关联关系仅表示一个类知道另一个类的存在，并没有主从关系。可以单向关联（只有一个类知道对方存在），也可以双向关联（双方彼此知道）；可以实现称一对多，多对一或者多对多。
{{% figure class="center" src="/images/oodesign/associate-example.PNG" alt="组合示例" title="组合示例"  %}}

## **继承 vs 组合 vs 代理**
1. 组合通常用在新类希望使用现有类的功能而非它的接口的情况下（即，在新类中嵌入某个private对象，让其实现所需要的功能，但并不暴露被嵌入的类的方法）。这是一种has-a的关系。
2. 继承通常用在使用现有类并开发一个特定版本的情况下，是一种is-a或is-like-a的关系。
3. 用继承来表示行为间的差异，用字段（组合）来表示状态上的变化。
4. 代理介入组合和继承之间：现有类仍旧作为一个字段被新类引用（同组合），但是在新类的接口中暴露了现有类的方法（同继承）：

```java
public class SpaceShip(){
    private SpaceShipController ctl = new SpaceShipController();
    public void back(){
        ctl.back();
    }
    public void forward(){
        ctl.forward();
    }
}
```

5. 虽然OO设计要求代码可复用，但是继承并不是OO中最常用的代码复用技术。最常用的是简单的将数据和方法的封装，或者使用组合来复用现有类（继承和组合一起使用也很常见）。
6. 当有多种方式可以实现功能的时候，应该慎用继承：当由子类向父类向上转型是必要的时候 ，继承才是必要的；如果不需要向上抓你选哪个，可以考虑下是否有必要使用继承[1]。
7. 组合比继承更加的灵活，继承关系在编译时指定，并且Java不支持多重继承；而组合可以运行时指定，允许动态地改变类的行为。在后续许多设计模式中将会很频繁的用到组合关系。

## **重载 vs 重写**
1. 在同一个类中，如果两个方法的方法名相同，参数列表不同（参数个数或者类型不同），无论返回类型是否相同都称为方法重载；
2. 在同一个类中，如果两个方法的方法名和参数列表都相同（即方法签名相同），无论返回类型是否相同，都会造成编译时错误；
3. 如果父类中有重载过的方法，子类也有同名不同参的方法，也属于方法重载，这并不会覆盖父类的方法；
4. 如果要重写父类的方法，那么子类的方法签名需要和被重写的方法相同，返回类型必须为父类的被重写方法的返回类型或者其导出类型（子类不允许有和父类方法签名相同，但是返回类型不同的方法）；
5. 重写父类方法时，访问修饰符的访问范围应该大于或等于父类；异常抛出范围小于或等于父类；
6. 构造方法不能被重写；
7. 如果父类的方法是private，那么就不构成重载或重写，该方法对子类不可见，子类中的方法相当于新的方法。

## **向上转型和向下转型**
1. 在OO原则中，我们经常用到面向接口编程。也就是说，我们不希望编写出依赖特定类的代码，而是用该类的抽象类或者接口等更加一般化的类型表示。这个把某个对象的引用视为对其父类的引用的做法被称为由子类像父类转型，或者叫**向上转型**。
2. 向上转型是将较特定的类型向较通用类型转换的过程。由于子类是父类的一个超集，它可能比父类含有更多的方法，但是至少具备父类的全部方法，因此向上转型总是安全的；
3. 向下转型则相反，如果类型不正确会抛出ClassCastException。这种运行期间的类型检查用的是RTTI（运行时类型识别）。应该尽量少地使用类型转换和instanceof操作。进行向下转换的唯一原因应该是需要使用对象的全部功能。

## **OO基本要素四：多态**
1. 一个子类的对象可以被用在任何需要使用其父类对象的地方，也就是说一个父类变量可以指向多种实际子类的现象称为**多态**。
2. Java中的多态又称为**动态绑定**、**后期绑定**或者**运行时绑定**；
3. **绑定**是指将一个方法调用与一个方法主体关联起来的操作。
4. 与动态绑定相反的是**前期绑定**。非面向对象的编译器和连接器产生的函数调用是前期绑定的：编译器产生对一个具体函数名的调用，运行时将这个调用解析到具体的代码地址。
5. 当我们使用父类的引用来操作子类的时候，我们并不清楚具体要调用的是哪个子类的方法，被执行的代码要在运行时才能确定，编译器只检查被调用的方法是否存在、参数和返回类型是否正确。这就是**运行时绑定**。
6. 即使我们把一个类向上转型为父类，但是通过这个父类的引用调用的方法还是会根据实际的类型表现出特定的行为。
7. 比如说对象o是类C1的实例，C1继承自C2，C2继承自C3，…， Cn-1继承自Cn，那么Cn是最泛化的类型，而C1是最特定的类型。假设我们有一个引用类型为Cn，指向对象o，并且对象o调用了方法p，那么JVM会按照C1, C2, …, Cn的顺序搜索方法p，直到找到第一个方法p为止。
8. 多态通过分离做什么（父类的方法调用）和怎么做（子类的方法调用）来解耦类型间的关系，将接口和实现分离。
9. C++中需要将方法声明为虚函数来支持动态绑定，而Java中除了static方法和final方法外（private方法属于final方法），所有方法都是默认动态绑定的。为了实现动态绑定，对象中必然会储存类型信息。

## **Java中的一些注意点**
### 私有方法不能被覆盖
声明为private的方法不能被覆盖，所以如果子类向上转型为父类，并用父类的引用调用一个private方法的时候，那么即使子类本身也有同名同参方法，调用的还是父类的方法。比如:

```java
public class A{
    private void f(){ System.out.println(“A”);}
    public static void main(String… args){
        A a = new B(); 
        a.f();
    }
}
public class B extends A{
    public void f(){System.out.println(“B”);}
}
```

上面的B类是A的子类，但是B类的方法f并没有覆盖A类的方法f，最终输出结果将是A。

### 只有普通方法访问是多态的，任何域访问都是由编译器解析的，不是多态的。
```java
class Super{
    public int field = 0;
    public int getField(){return field;}
}

class Sub extends Super{
    public int field = 1;
    public int getField(){return field;}
    public int getSuperField(){return super.field;}
}

public class Test{
    public static void main(String… args){
        Super super = new Sub();
        System.out.println(super.field); // 返回0
        System.out.println(super.getField()); // 返回1
    }
}
```

### 如果某个方法是静态的，它的行为就不具有多态性。
```java
class Super {
    public static String staticGet(){ return “Super Static Get”;}
    public static String dynamicGet(){ return “Super Dynamic Get”;}
}

class Sub extends Super {
    public static String staticGet(){ return “Sub Static Get”;}
    public static String dynamicGet(){ return “Sub Dynamic Get”;}
}

public class Test {
    public static void main(String… args)}
        Super super = new Sub();
        System.out.println( super.staticGet()); // 返回Super Static Get
        System.out.println( super.dynamicGet()); // 返回Sub Dynamic Get
    }
}
```

### 子类中覆盖父类的方法可以返回父类被覆盖方法的返回类型的导出类型。
```java
class A {
    public String toString(){ return “A”;}
}

class B extends A {
    public String toString(){ return “B”;}
}

class Base {
    A proc(){ return new A();}
}

class Derived extends Base {

    // 这里可以返回A的导出类型B
    @Override
    B proc(){ return B();}
}
```

# **面向对象设计尝试解决的问题**

## **为什么使用面向对象的设计？**

* 为了最大化代码重用？
* 为了对真实世界的对象进行建模？
* 为了实现关注点分离(Separation of Concern)?
* 为了封装实现的细节？

以上都不正确

## **真实世界的场景**

> 当一个软件刚开发完的时候，一切看上去都是完美的。而当我们开始使用它的时候，会对它进行修改。一个模块开始依赖另一个模块，另一个模块依赖又一个模块。代码会变地越来越多，越来越丑陋，软件就像食物一样开始“腐烂”。对软件的改动变得越来越难，最终它变得无法维护！

* 是什么导致软件的逐渐“腐烂”？ 是因为**依赖**。
* 是什么引入了依赖？`new`操作符, `extends`关键字等等强耦合的操作。
* 问题是？我们不能没有new, 我们也需要使用继承来降低依赖关系

## **面向对象设计的目的**

**依赖管理（解耦）** Dependency Management(Decoupling)

面向对象设计的目标是将系统各个模块组装起来，但是在增加新模块时不需要去修改老的那些。


这是视频是Bob Martin在InfoQ上关于“敏捷设计原则”的[演讲](http://www.infoq.com/presentations/principles-agile-oo-design)。

# **面向对象的设计原则**

* 面向对象的设计模式都是依赖于这些设计原则；
* 每个设计模式的背后都体现了一个或多个的设计原则；
* 在设计遇到两难的时候，我们必需回归到这些原则上来思考；
* 面向对象的设计原则是我们的目标，而设计模式是我们的做法。

## **单一职责原则**
什么是职责？

> 在The Single Responsibility Principle(SRP)中职责的定义为“变动的原因”(A reason for change)

如果你有多个动机去修改一个类，那么这个类就有多个职责。

这可能很难理解，因为我们通常把一组职责放在一起思考，下面来看一个具体的例子。下面是一个Modem（调制解调器或者叫猫）的接口

```java
interface Modem
{
    public void dial(String pno);
    public void hangup();
    public void send(char c);
    public char recv();
}
```

上面这个猫的接口中存在两个职责：第一个是管理连接（dial和hangup）;第二个是数据传输（send和recv）

这两个职责应该被分开，因为
1. 它们没有共同点，而且通常会因为不同的原因被修改；
2. 调用它们的代码通常属于应用的不同部分，而这部分代码也会因为不同的原因被修改。

下面是一个Modem的一个优化后的设计:
{{% figure class="center" src="/images/oodesign/srp-modem.png" alt="单一职责原则Modem示例" title="单一职责原则Modem示例"  %}}

通过拆分猫的接口，我们可以在应用的其他部分将猫的设计分开来对待；虽然我们又在猫的实现中(Modem Implementation)将这两部分职责重新耦合在一起，但是除了初始化猫的代码意外，在使用面向接口编程的原则后，其他代码并不需要依赖于猫的实现。

SRP是最简单的一个面向对象设计原则，但也是最难做正确的一个，因为我们习惯于将职责合并，而不是将它们分开来。找到并且拆分这些职责正是软件设计真正需要做的事情。

最后我们给出单一职责的原则的定义：

> 不应该有超过一个原因去修改一个类。

> THERE SHOULD NEVER BE MORE THAN ONE REASON FOR A CLASS TO CHANGE.

> 或者说找到那些需要修改的部分并把它们封装到一个类中。

> IDENTIFY WHAT IS LIKELY TO CHANGE AND ENCAPSULATE IT IN A SINGLE CLASS.

## **开放关闭原则**
一个典型的不良设计是：对一个模块进行微小的改动引起级联式的依赖模块的修改，这造成：

1. 程序的僵化(Rigidity)：很难对程序作出修改，因为每一个修改都会导致系统中太多的部分需要发生改动；
2. 程序的脆弱(Fragility)：当对程序作出一个改动，系统中另一个看似无关的部分不可预料的崩溃了；
3. 程序的固化(Immobility)：很难在另一个系统中重用某些模块。

开发-关闭原则认为程序的模块应该不允许改变，当需求做出变更时，你通过添加新的代码来扩展现有模块的行为，而不是修改现有模块。

开发-关闭原则的定义为

> 程序实体（类、模块、函数等）应该接受扩展，拒绝修改。

> SOFTWARE ENTITIES (CLASSES, MODULES, FUNCTIONS, ETC.) SHOULD BE OPEN FOR EXTENSION, BUT CLOSED FOR MODIFICATION.

符合开放-关闭的设计原则的模块有以下两个特性：

1. 接受扩展：程序模块的行为可以被扩展。当需求变更，或者有新的需求时，我们可以让模块表现出新的或不同的行为；
2. 拒绝修改：不允许对程序模块的源代码做任何修改。

开发-关闭原则的关键在于抽象。考虑下面的一个例子：

{{% figure class="center" src="/images/oodesign/ocp-1.png" alt="开放关闭原则" title="开放关闭原则" %}}

上图的例子中没有遵循开放-关闭的设计原则：

1. 客户端和服务器端都是具体的类；
2. 当我们希望客户端使用一个不同的服务器端对象的时候，客户端对象必须被修改才能使用新的对象。

下面是修改后的符合开放-关闭原则的例子：
{{% figure class="center" src="/images/oodesign/ocp-2.png" alt="开放关闭原则" title="开放关闭原则" %}}
AbstractClass是一个抽象类，Client使用的是一个抽象类。当我们需要一个新的Server实现的时候，我们只需要扩展AbstractClass来构建一个新的Server，而Client不需要作出变动。

开发-关闭原则引出了很多被普遍接受的面向对象设计规范，比如：

1. 所有类的成员变量都应该是私有的；
2. 不要有全局变量；
3. 运行时类型识别（RTTI）可能是不安全的。
4. ...

开发-关闭原则是面向对象设计的核心。符合这一原则的设计可以带来面向对象技术的优点，包括重用性和可维护性。但是，使用面向对象的程序语言并不能保证设计出符合开放-关闭原则的程序，它需要设计者对程序中会发生变化的部分进行抽象。

## **里氏替换原则**

由Barbara Liskov最初提出的Liskov替换原则，在经过Robert Martin重新表述后定义如下：

> 使用了指向基类的指针或引用的函数，应当能够在不了解该类的导出类的前提下，使用导出类。

> FUNCTIONS THAT USE POINTERS OR REFERENCES TO BASE CLASSES MUST BE ABLE TO USE OBJECTS OF DERIVED CLASSES WITHOUT KNOWING IT.

这个原则似乎很明显，Java的多态或者C++的虚函数本身就允许把指向基类的指针或引用，在调用其方法或函数的时候，调用实际类型的方法或函数。我们来看一个简单的例子:

```java
public class Rectangle {
    
    private double width;
    private double height;
    
    public double getWidth() { 
        return width;
    }
    
    public void setWidth(double width) { 
        this.width = width; 
    }

    public double getHeight() { 
        return height; 
    }

    public void setHeight(double height) { 
        this.height = height; 
    }
}
```

我们系统里如上所示的有一个长方形类。但是现在需求发生了变化，要求增加一个正方形类。很明显，“正方形”是一种特殊的“长方形”。在我们面向对象编程思想中，这是一种is-a的关系，而这种关系我们用继承来表示。
这种思想是很危险的。因为它们带来的问题不可预料，只有当开始敲代码的时候才会被发现。下面我们来讨论这种设计有什么问题：

1. 正方形并不需要height和width两个变量，但它们还是会被继承下来。这明显是一种空间上的浪费，特别是在一些CAD软件里面，一种基本形状可能有几百万个。
2. 假设空间资源不是问题，但是setWidth和setHeight方法会被继承下来，这两个方法显然对于正方形来说是不合适的。这时候应该可以发现这个系统的设计出了问题。当然我们还是可以解决的——在正方形子类里把setWidth和setHeight覆盖掉。

下面是我们的正方形类：
```java
public class Square extends Rectangle {

    @Override
    public void setWidth(double width) {
        super.setWidth( width);
        super.setHeight( width);
    }
    
    @Override
    public void setHeight(double height) {
        super.setWidth( height);
        super.setHeight( height);
    }
}
```

当我们调用Square对象的setWidth或者setHeight时，长和宽都会随之改变：
```java
public static void main(String... args){
	Square s = new Square();
	s.setHeight(10); // 长和宽都设置成了10
	s.setWidth(5); // 长和宽都设置成了5
}
```

并且Java里面一般的方法（非final的，非静态的）调用都是动态绑定的（类似C++里面的虚函数），因此下面的Rectangle的引用实际上调用的是Square的方法：
```java
public class Test {
    public void f (Rectangle r){ 
        r.setWidth(5); 
    }
    
    public static void main(String... args){
        Square s = new Square();
        new Test().f( s ); // 最终调用的是Square的set方法
    }
}
```

到目前为止，这个设计似乎还能够接受。我们可以总结来说这几个对象的设计是正确的，并且自我一致的(self consitent)。但是自我一致的设计并不一定与它们的所有用户保持一致！考虑下面的方法调用：
```java
public class Test {
    public void g (Rectangle r){
    
        r.setWidth(5);
        r.setHeight(4);
        assert (r.getWidth() * r.getHeight() == 20);
    }
    
    public static void main(String... args){
    
        Square s = new Square();
        new Test().g( s );
    }
}
```
方法g按照长方形的参数来设计。如果传进去的是Rectangle，没有问题；但是如果传进去的是Square，assert就会报错。

所以我们这里真正的问题是：编写g方法的程序员做了一个假设，改变长方形的高度的方法不会修改长方形的宽度，那么这个假设是否合乎情理？显然这个假设很合理。
那么将Square传递给任何作出如此假设的程序员所编写的方法都会导致同样的错误。这种错误在没有assert的时候可能还不易被发现。
所以，存在接受基类Rectangle的方法，但不能很好地处理子类Square。
这违反了里氏替换原则。
从上述例子中我们可以总结出：当考虑一个特定的面向对象设计是否合理的时候，我们不能简单地把那个设计单独来看，而是要从使用这个设计的客户程序员的角度来看。

那么在上述例子中，到底哪里出了问题？这个明显的is-a关系的设计从直觉上来看，不应该是很合理的吗？
从数学角度来看，一个正方形是一种长方形，但是一个正方形对象is not a长方形对象：因为正方形对象的行为与长方形对象的行为不一致！
所以，从行为角度来讲，正方形不是一个长方形。而软件设计关注的是行为。
为了保持里氏替换原则，所有子类的行为必须符合类的使用者所认为的其父类的行为。

这里引出了**契约式设计**：

契约式设计要求类的方法申明前置条件和后置条件；
1. 方法执行前，它的前置条件必须被符合;
2. 方法执行后，方法保证它的后置条件符合;
3. 契约式设计和里氏替换规则关系密切;
4. 对于我们Rectangle类的setWidth方法来说，它的后置条件应该为：
```java
assert((this.width == wdith) && (this.height == old.height));
```
契约式设计的提出人Bertrand Meyer对于子类的前置和后置条件制定的规则为：
> 当（在子类中）重新定义一个例程的时候，你只能将前置条件替换为一个更弱的条件，将后置条件替换为一个更强的条件。

> ...when redefining a routine [in a derivative], you may only replace its precondition by a weaker one, and its postcondition by a stronger one.

根据契约式设计的要求，显然Square类的setWidth方法的后置条件的明显要比Rectangle的setWidth的后置条件要宽松，因为它没有要求满足
```java
this.height == old.height
```

当我们通过父类的指针去使用一个子类对象的时候，根据里氏替换原则，使用者只知道父类的前置和后置条件。
因此，子类不能期望它的使用者去遵循比父类更加严格的前置条件。也就是说父类能够接受的前置条件子类必须都能够接受。
同时，子类还必须符合父类的所有后置条件。也就是说子类的行为和输出不能违反父类的限制。
这就是为什么子类的前置条件可以更加宽松，后置条件必须更加严格。
在Java里，这体现在子类的方法覆盖父类方法时，子类的可见性必须大于等于父类被覆盖方法的可见性，而异常抛出范围必须小于等于父类被覆盖方法的异常抛出范围。

## **依赖反转原则**
依赖反转的定义：

> A.上层模块不应该依赖下层模块。所有模块应该依赖于抽象。

> A. HIGH LEVEL MODULES SHOULD NOT DEPEND UPON LOW LEVEL MODULES. BOTH SHOULD DEPEND UPON ABSTRACTIONS.

> B. 抽象不应该依赖于实现。实现应该依赖于抽象。

> B. ABSTRACTIONS SHOULD NOT DEPEND UPON DETAILS. DETAILS SHOULD DEPEND UPON ABSTRACTIONS.


传统的软件设计趋向于上层模块依赖于下层模块，抽象依赖于实现。上层模块依赖下层模块的后果是上层模块包含了业务逻辑，决定了应用的功能；而下层模块一旦变动，就会直接影响到上层模块，并要求这些逻辑发生修改。

一个良好设计的面向对象编程是对于传统软件设计的“反向”，即这里所说的“反转”。使用依赖反转实现复用高级别模块。上层模块复用是框架设计的重点。如果上层模块不依赖于下层模块，复用会很容易。

假设我们要设计一个很简单的程序，将键盘的输入输出到打印机上。一个简单的设计的程序结构图如下所示：
{{% figure class="center" src="/images/oodesign/dip-1.png" alt="依赖反转原则" title="依赖反转原则" width="300px" %}}

上面的设计中有三个模块，Copy模块调用Read Keyboard模块来读取输出，然后Copy调用Write Printer模块输出字符。Read Keyboard和Write Printer是两个下层模块，并且很容被复用。

然而我们的Copy模块却不能被复用于任何不包含键盘和打印机的场景中，而Copy恰恰是这个程序的业务逻辑所在的模块，也是我们最希望能够复用的。

比如，我们还希望将键盘的输入，复制到磁盘文件。我们当然希望复用Copy模块，而事实上，Copy依赖于键盘和打印机，缺一不可，所以不能被复用。
我们也可以往Copy中增加一个if条件来支持新的磁盘文件输出，但是这就违背了开放-关闭原则，最终随着功能的变多，代码将变地不可维护。

这个例子中的问题其实是高层级的模块（Copy模块）依赖于层级的模块（Read Keyboard和Write Printer)；
如果能够找到一个让Copy独立于它所控制的底层级模块的方法，那么我们可以自由地复用这个Copy模块。下图就是一种依赖反转的解决方案。

{{% figure class="center" src="/images/oodesign/dip-2.png" alt="依赖反转原则" title="依赖反转原则" width="300px" %}}

在这个新的设计中，我们的Copy模块有一个抽象的Reader和一个抽象的Writer。Copy不再直接依赖于具体的实现，不管有几个Reader或Writer的实现，我们都不需要修改Copy。

我们再看第二个例子：我们想要设计一个按钮Button对象和一个灯泡Lamp对象，用Button来控制Lamp的开关。一个简单的设计如下所示：

{{% figure class="center" src="/images/oodesign/dip-3.png" alt="依赖反转原则" title="依赖反转原则" width="300px" %}}

在这个设计里，按钮Button直接依赖于灯泡Lamp对象。这意味着Button类必须随着Lamp类的修改而修改，也意味着我们不能用这个Button去控制别的东西（复用）。原因是我们没有将高层的策略(Policy)和底层的模块分离开。

什么是高层的策略？是那些不会随实现细节而发生变化的东西——抽象(Abstraction)。在这个例子中，这个抽象是“检测用户打开/关闭的操作并且将这个操作传递到目标对象”。

用什么机制检测用户的操作？我们不关心。什么是目标对象？我们也不关心。因为这些都是无关紧要的细节。

为了符合依赖反转原则，我们必需把抽象和细节分离开，然后我们把设计中的依赖关系修改为细节依赖于抽象。下面是一个更新后的设计方案：

{{% figure class="center" src="/images/oodesign/dip-4.png" alt="依赖反转原则" title="依赖反转原则" width="300px" %}}

Button对如何检测用户开关的操作一无所知，Button也对需要操控的目标一无所知。这些都由独立地具体实现（ButtonImplementation和Lamp）来控制。

对于前面的设计，我们要求被控制的目标必需是ButtonClient的到处类。但是如果Lamp是由第三方库提供的呢？我们不能修改它们的代码。
这个时候我们可以使用适配器(Adapter)模式。LampAdapter将ButtonClient的开关信号传递给Lamp类。

{{% figure class="center" src="/images/oodesign/dip-5.png" alt="依赖反转原则" title="依赖反转原则" width="300px" %}}

## **接口隔离原则**
先来看一个门禁超时程序的例子。我们有一个Door接口，可以被锁定和解锁，如下：
```java
public interface Door {
	public void lock();
	public void unlock();
	public boolean isDoorOpen();
}
```

现在我们想实现一个TimedDoor类，当门长时间没有关闭的时候，发出警告。为了实现这个需求，我们需要一个Timer：
```java
public class Timer {
	public void register(int timeout, TimerClient client);
}

public interface TimerClient {
	public void timeOut();
}
```

当TimedDoor希望在超时时被通知到，那么它就调用Timer的register方法，注册一个超时通知，当超时发生时，Timer就会调用TimerClient的timeout方法。
为了使TimedDoor可以被Timer通知到，那么它必须实现TimerClient接口。下面是一个常规的实现。
{{% figure class="center" src="/images/oodesign/isp-1.png" alt="接口隔离原则" title="接口隔离原则" width="300px" %}}

这个设计中Door接口必须依赖于TimerClient接口，但是并不是所有的Door的实现都需要Timer来计时。
对于那些不需要TimerClient接口的Door实现来说，它们只能继承下来TimeOut方法，然后不做任何事情。
如果还有其他接口需要添加到Door接口之上时，Door的实现将被迫继承更多的方法。

这里引出了**接口污染**的概念：接口Door被它不需要的TimerClient接口给污染了；因为Door的某一个实现需要，而强制给Door接口增加了父接口。

假设我们要对Timer进行修改，Timer将传递一个timerOutId给TimerClient的timeOut方法，那么看上去和Timer毫无关系的Door接口以及所有Door的实现都被迫需要修改。
这就会导致程序中一个地方的修改，引起毫无关系的另一块代码也需要修改。

接口隔离原则的定义

> 客户端不应该被迫依赖那些它不使用的接口
> CLIENTS SHOULD NOT BE FORCED TO DEPEND UPON INTERFACES THAT THEY DO NOT USE.

当客户端依赖于那些不需要的接口时，这些接口的修改会到导致客户端的修改。
这增加了整个设计的耦合性，我们需要尽可能的将接口分类开。

有两种方法来分离接口。其一是通过委托分离接口(Separation through Delegation)。

{{% figure class="center" src="/images/oodesign/isp-2.png" alt="接口隔离原则" title="接口隔离原则" width="300px" %}}

1. 使用适配器模式，为TimerClient创建一个DoorTimerAdapter。
2. 当TimedDoor需要注册一个超时调用的时候，它创建一个DoorTimerAdapter，并向Timer注册这个适配器；
3. 当Timer调用DoorTimerAdapter的timeOut接口的时候， DoorTimerAdapter再把这个消息委托回给TimedDoor。

另一种方式是通过多重继承分离接口(Separation through Multiple Inheritance)。前面通过委托来实现分离的方法有一个缺点：当我们每次需要注册一个超时调用的时候都需要创建一个适配器。
下面是通过多重继承来实现接口的分离：

{{% figure class="center" src="/images/oodesign/isp-3.png" alt="接口隔离原则" title="接口隔离原则" width="300px" %}}

## **迪米特原则**
迪米特原则的目的是通过尽量减少类之间的关联来降低耦合性，它的定义如下：

> 一个对象的方法只应该调用以下对象的方法：

> 1. 自身对象(this)
2. 自身方法的参数
3. 任何自身创建或者初始化的对象
4. 自身直接引用的对象

> A method of an object should invoke only the methods of the following kinds ofobjects:

> 1. itself
2. its parameters
3. any objects it creates/instantiates
4. its direct component objects

我们先来看一个客户和收银员的程序的例子。收银员需要从客户那里取得钱。首先，我们的客户对象定义如下（省略了set方法）:
```java
public class Customer {
    private String firstName;
    private String lastName;
    private Wallet myWallet;
    
    public String getFirstName(){ 
        return firstName; 
    }
    
    public String getLastName(){ 
        return lastName; 
    }
    
    public Wallet getWallet(){ 
        return myWallet; 
    }
}
```
然后是钱包Wallet的定义
```java
public class Wallet {
	private float value;
	public float getTotalMoney() { return value;}
	public void setTotalMoney(float newValue) {
		value = newValue;
	}
	public void addMoney(float deposit) {
		value += deposit;
	}
	public void subtractMoney(float debit) {
		value -= debit;
	}
}
```
最后，是收银员收钱的代码
```java
payment = 2.00; 
Wallet theWallet = myCustomer.getWallet();
if (theWallet.getTotalMoney() > payment) {
	// 付款成功
	theWallet.subtractMoney(payment);
} else {
	// 付款失败
}
```

客户和收银员的程序存在一些问题。比如，Customer对象允许收银员直接操作Wallet对象。这在实际情况下是不合适的，如果允许其他对象持有Wallet，那么Customer将失去对Wallet的控制，比如下面的代码就可能发生：
```java
myCustomer.setWallet(null);
```
再比如，收银员的代码还需要处理Wallet为空的情况：
```java
Wallet theWallet = myCustomer.getWallet();
if( theWallet == null ) 
    return;
```
Wallet、Customer和收银员耦合在了一起，如果Wallet发生修改，收银员的代码也需要修改，尽管Wallet和它并没有关系。

客户和收银员的程序根据迪米特原则优化后，Customer对象中不返回Wallet对象，但是增加一个付款的方法：
```java
public float getPayment(float bill) {
    if (myWallet != null) {
        if (myWallet.getTotalMoney() > bill) {
            theWallet.subtractMoney(payment);
            return payment;
        }
    }
}
```
收银员不再操作客户的Wallet，而是调用客户付款的方法：
```java
payment = 2.00; // “I want my two dollars!”
paidAmount = myCustomer.getPayment(payment);
if (paidAmount == payment) {
	// 付款成功
} else {
	// 付款失败
}
```
我们在这个例子中做了以下改进：

1. 新的面向对象设计更符合实际情况。收银员不会直接去翻客户的钱包，而是要客户给钱；
2. Wallet类现在可以自由地修改了，并且收银员的代码不再依赖Wallet的实现；
3. getPayment包含了我们的业务逻辑。我们可以按照需要修改getPayment方法，而不用担心存在之前提到的空指针的错误。


哪些场景下可以使用迪米特原则来改善设计？

1. 链式get方法。比如
```java
value = object.getX().getY().getTheValue();
```
2. 许多“临时”引用变量。比如
```java
Wallet tempWallet = person.getWallet();
license = tempWallet.getDriversLicense();
```
3. 导入很多不需要的类。比如
```java
import java.awt.*;
```

哪些设计模式使用了迪米特原则？

1. 包装类的设计模式，比如Adaptor, Proxy, Decorator。迪米特原则在这里把被包装的类隐藏起来，使调用者必须通过包装的类来访问；
2. Façade设计模式。迪米特原则把许多类隐藏在一个API背后；

到目前为止，我们介绍了S.O.L.I.D.(Robert Martin提出来的)面向对象的5个类设计原则:

* S - Single-responsiblity principle
* O - Open-closed principle
* L - Liskov substitution principle
* I - Interface segregation principle
* D - Dependency Inversion Principle 

以及迪米特原则。


## **内聚型、耦合性原则**

### **发布/复用等价原则**

发布/复用等价原则 The Reuse/Release Equivalence Principle (REP) 是一个包内聚性原则：

1. 复用的单元即是发布的单元。The unit of reuse is the unit of release.  
不应该重用某一个类或者某一段代码，而是重用一个完整的发布的包。原始作者仍旧负责维护被重用的模块，这样你的程序能跟上新的特性或补丁的发布。
2. 有效的复用需要对发布进行跟踪。Effective reuse requires tracking of releases from a change control system. 
3. 包是实际上的复用和发布单元。The package is the effective unit of reuse and release.

### **共同封装原则** 
共同封装原则 Common-Closure Principle (CCP)是一个包内聚性原则：

1. 将容易变化的部分隔离出来，单独放到一个包里，不要和那些不需要变化的代码混在一起；
2. 那些耦合性很高的类，属于同一个包；
3. 包不应该有超过一个的原因导致其被修改。

### **共同复用原则**
共同复用原则 Common-Reuse Principle (CRP)是一个包内聚性原则：

1. 那些会被一起复用的类，属于同一个包；
2. 当程序依赖某个包的时候，我们希望包里的类是不可分离的、相互依赖的；
3. 如果重用了包中的一个类，相当于复用了包中的全部的类，所以要经可能减小包的大小。

### **无环依赖原则**
无环依赖原则 Acyclic Dependencies Principle (ADP)是一个包耦合性原则：

1. 不应该存在循环的依赖关系，比如包A依赖于包B，包B依赖于包C，包C又依赖于包A。

### **稳定依赖原则**
稳定依赖原则 Stable-Dependencies Principle (SDP)是一个包耦合性原则：

1. 包会因为使用的环境而发生变化，而包的设计应该支持这种变化；
2. 一个包只能依赖于那些比它自身更加稳定的包。

### **稳定抽象原则**
稳定抽象原则 Stable-Abstractions Principle (SAP)是一个包耦合性原则：

1. 一个稳定包必须是抽象的，因此它的稳定性才不会阻止它被扩展；
2. 一个不稳定的包必须是具体的，因为它的不稳定性允许它里面的具体的代码被修改；
3. 包的稳定性与包的抽象程度成正比。

## **其它原则**
下面这些设计原则或多或少都已经介绍过

1. 组合/聚合复用原则：多用组合，少用继承；
2. 契约式设计：要依赖抽象，不要依赖具体实现；
3. 好莱坞原则：别调用我们，我们会调用你（依赖注入）；
4. KISS原则（Keep it simple and stupid）：设计应该简单，而不是复杂；
5. 高内聚，低耦合：模块内部要做到内聚度高，模块之间要做到耦合度低；
6. DRY原则（Don‘t repeat yourself）：不要有太多重复的代码，尽可能复用；
7. 关注点分离：将一个复杂的问题分离为多个简单的问题，然后逐个解决这些简单的问题；
8. 惯例优于配置：尽量让惯例来减少配置，这样才能提高开发效率，尽量做到“零配置”；
9. ……


# **面向对象的设计模式**

## **基本介绍**
“架构设计”、“设计模式”这些词最初来自于建筑学。
一个叫Christopher Alexander的建筑师写了一本关于建筑模式的书，然后碰巧被一群搞软件的看到了；
{{% figure class="center" src="/images/oodesign/oodp-basics-1.jpg" alt="建筑模式" title="建筑模式" width="100px" %}}

在软件行业中，软件工程师们也希望那些最佳实践被记录，被分享；
那么就借鉴了建筑行业的术语，诞生了软件的“设计模式”。
{{% figure class="center" src="/images/oodesign/oodp-basics-2.jpg" alt="设计模式" title="设计模式" width="500px" %}}

设计模式是

1. 在特定环境中不断重复出现的，从具体形式中提炼出来的一种抽象；
2. 一种经过反复证明有效的最佳实践；
3. 一个富有创造性的用于传达一个经过验证的解决方案的本质的深刻见解；
4. 一种和技术人员交流解决方案的行话；
5. ……

引用简书上一篇[文章(作者gekylin)](https://www.jianshu.com/p/15edb371c0b5)的表述：

* 设计模式（Design pattern）是一套被反复使用、多数人知晓的、经过分类编目的、代码设计经验的总结。使用设计模式是为了可重用代码、让代码更容易被他人理解、保证代码可靠性。 毫无疑问，设计模式于己于他人于系统都是多赢的；设计模式使代码编制真正工程化；设计模式是软件工程的基石脉络，如同大厦的结构一样。
* 而设计原则则是设计模式所遵循的规则，设计模式就是实现了这些原则，从而达到了代码复用、增加可维护性的目的。一个项目中的设计模式，可能是另一个项目中基本的构造模块。


一个设计模式的基本要素：

1. 名称：用于对模式进行概要描述；
2. 问题：用于描述模式解决了什么问题，在什么场景下时候使用模式；
3. 解决方案：描述了构成这个模式的设计的元素、它们之间的协作关系，职责等；
4. 结果：应用模式后的利弊分析。

设计模式按用途分类可分为

* 创建型模式：关注对象创建的过程；
* 结构型模式：关注类和对象如何组合在一起；
* 行为型模式：关注类与对象如何交互，如何分担职责。

按照范围分类

* 类模式：处理的是类与子类之间的关系，它们之间的关系通过继承来建立，因此它们是静态的，在编译时就确定了（虽然绝大部分模式都会用到继承，但那些关注类之间关系的才算是类模式） ；
* 对象模式：处理的是对象的关系，它们可以在运行时发生变化。

{{% figure class="center" src="/images/oodesign/oodp-basics-3.jpg" alt="设计模式分类" title="设计模式分类" width="600px" %}}

下面是GoF中关于设计模式之间的关系图：
{{% figure class="center" src="/images/oodesign/oodp-basics-4.jpg" alt="设计模式之间的关系" title="设计模式之间的关系" width="700px" %}}

我们从以下几个方面来描述一个设计模式：

1. 模式产生的动机 Motivation；
2. 模式定义，包括名称、别名、分类和用途 Definition；
3. 适用场景 Applicability；
4. 模式的结构（通常是UML的设计图） Structure；
5. 模式的各参与方 Participants；
6. 模式中各方的协作关系 Collaborations；
7. 应用模式的结果 Consequences；

## **创建型模式**
### **单例模式**
*Motivation & Definition & Applicability*

> 定义：单例模式就是为了确保一个类只有一个实例，并且提供了一个全局地对那个实例的访问点；

有些类必须至多有一个实例，比如线程池、缓存、日志对象等等，当存在多个对象的时候会出现异常行为。

当要确保类只有一个实例，并且这个实例需要通过一个公共的访问点提供给客户的时候，适用于单例模式。

*Implementation*

单例模式是没有很复杂的结构，它有以下三种实现方式：

1. 主动实例化模式
```java
public class Singleton {
    // 实例在JVM加载类的时候即初始化
    private static Singleton instance = new Singleton();
    // 私有化的构造方法
    private Singleton(){}
    // 全局访问点
    public static Singleton getInstance(){
        return instance;
    }
}
```

2. 被动实例化模式
```java
public class Singleton {
    private static Singleton instance;
    private Singleton(){}
    public static synchronized Singleton getInstance(){
        if( instance == null) instance = new Singleton();
        return instance;
    }
}
```
前面被动实例化模式中，给方法加Synchronized其实没有必要，因为只有在第一次new的时候才需要同步，加上Synchronzied反而会在大量并发的时候造成瓶颈。下面这种方式是一种优化。
```java
public class Singleton {
    private volatile static Singleton instance;
    private Singleton(){}
    public static Singleton getInstance(){
        if( instance == null){
            synchronized ( Singleton.class) {
                if( instance == null) instance = new Singleton();
            }
        }
        return instance;
    }
}
```

3. 注册表模式
```java
public class SingletonRegistry {
    private static Map<String, Object> registry = new HashMap<String, Object>();

    private SingletonRegistry(){}

    public static Object getInstance (String classname) {

        Object singleton = registry.get( classname);

        if( singleton != null) return singleton

        try{ 
            singleton = Class.forName( classname).newInstance();
        } catch (Exception e){
            throw new RuntimeException(e);
        }

        registry.put( classname, singleton);
        return singleton;
    }
}
```

### **简单工厂、工厂方法和抽象工厂模式**
*工厂模式概述*

1. 所有的工厂模式都是用来封装对象的创建的；
2. 简单工厂并不属于GoF中介绍的设计模式之一，但是它也被频繁地使用；
3. 工厂模式帮助我们针对抽象编程，而不是针对接口编程。

*简单工厂 Definition*

> 简单工厂模式：定义了一个工厂类，这个工厂类有一个创建对象的方法。该方法根据传入的参数创建相应的对象，但是将创建对象的逻辑隐藏起来。

*简单工厂 Motivation*

假设要开一个Pizza店，我们有很多种Pizza，需要一个预定Pizza的方法。
```java
public class PizzaStore{
    public Pizza orderPizza ( String type ){
        Pizza pizza;
        
        if( type.equals(“cheese”)){ 
            pizza = new CheesePizza;
        } else if( type.equals(“greek”)){ 
            pizza = new GreekPizza();
        }
        
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
        return pizza;
    }
}
```
这个orderPizza是一个高层的业务逻辑模块，但是它依赖于底层的具体的Pizza类型。显然这是一个不好的设计。一旦Pizza类型增加、减少、修改都会导致orderPizza被改动。

那么按照前面的面向对象的设计原则，我们把会变化的部分封装起来。这就有了一个简单Pizza工厂，所有客户都用这个简单工厂来创建Pizza。
```java
public class SimplePizzaFactory {
    
    public Pizza createPizza( String type ){
        Pizza pizza = null;   
        if( type.equals(“cheese”)){ 
        pizza = new CheesePizza;
    } else if( type.equals(“greek”)){ 
        pizza = new GreekPizza();
    }
        return pizza;
    }
}
```
下面我们来看下这个简单工厂的UML图（Head First Design Pattern）:

{{% figure class="center" src="/images/oodesign/oodp-factory-1.jpg" alt="简单工厂模式UML" title="简单工厂模式UML" width="700px" %}}

现在我们来看一下有了这个简单Pizza工厂后，PizzaStore会变成什么样子：
```java
public class PizzaStore {
    SimplePizzaFactory factory;

    public PizzaStore (SimplePizzaFactory factory){
        this.factory = factory;
    }

    public Pizza orderPizza( String type ){
        Pizza pizza = factory.createPizza(type); // <-- 变化在这里
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
        return pizza;
    }
}
```

*简单工厂 Consequences*

在新的PizzaStore类中，我们不再有new关键字————创建Pizza的过程被委托给了SimplePizzaFactory的createPizza方法，PizzaStore不再关心Pizza是如何被创建的，它只知道我要一个XXX类型的pizza，然后简单工厂返回了一个XXX类型的pizza；

* 优点1：实现与接口的分离。客户端不再依赖具体产品的实现，而是依赖产品的抽象接口。一旦产品发生增加、修改、删除，客户端都不需要做改动；
* 优点2：所有创建对象的内部逻辑都对客户端隐藏；
* 缺点1：简单工厂模式其实违反了开发-关闭原则。当我们需要新赠、修改、删除具体的产品的时候，虽然我们将所有的修改封装在了一个类中（只需要修改一个地方），但是还是会发生修改。一个好的设计应该是对扩展开放、对修改关闭，因此这个设计模式在这方面有问题。
* 缺点2：还违反了依赖反转原则。依赖反转原则说上层模块不应该依赖下层模块，这里简单工厂依赖于具体的产品。

*工厂方法 Definition*

> 工厂方法模式：定义了一个创建对象的接口，但由子类来决定要实例化的类是哪一个（客户端选择了哪个子类，即选择了要实例化的产品）。工厂方法让类把实例化推迟到子类；

*工厂方法 Motivation*

鉴于简单工厂的上述缺点，我们重新设计Pizza类的构造过程。我们将Pizza的创建重新放回到PizzaStore类中，并将PizzaStore变成抽象类: 原本是由PizzaStore完成全部具体产品类的实例化，现在改成由它的子类来负责。
 
```java
public abstract class PizzaStore {
    public final Pizza orderPizza(String type){
        Pizza pizza = createPizza(type);
        pizza.prepare();
        pizza.bake();
        pizza.cut();
        pizza.box();
        return pizza;
    }

    protected abstract Pizza createPizza(String type); // 这个就是工厂方法
}
```

然后我们让PizzaStore的子类，具体的某个PizzaStore来决定创建Pizza的种类:
```java
public class NYPizzaStore extends PizzaStore {
    @Override
    protected Pizza createPizza(String item){
        if( item.equals(“cheese”)){
            return new NYStyleCheesePizza();
        }else if( item.equals(“clam”)){
            return new NYStyleClamPizza();
        }else{
            return null;
        }
    }
}

public class SHPizzaStore extends PizzaStore {
    @Override
    protected Pizza createPizza(String item){
        if( item.equals(“cheese”)){
            return new SHStyleCheesePizza();
        }else if( item.equals(“clam”)){
            return new SHStyleClamPizza();
        }else{
            return null;
        }
    }
}
```

createPizza是工厂方法，它是抽象的，有具体的子类来实现。工厂方法用来处理对象的创建，并将行为封装在子类中。工厂方法可以有多个参数，也可以没有参数。工厂方法将客户代码（即orderPizza方法）与实际创建具体产品的代码分开。

工厂方法返回的产品Pizza通常也是抽象的（可以有默认实现），一般由工厂方法的实现来决定具体的产品。

下面我们来看一下产品类Pizza，以及一个具体实现。

```java
public abstract class Pizza {
    String name;
    abstract void prepare();
    abstract void bake();
    abstract void cut();
    abstract void box();
}

public class NYStyleCheesePizza extends Pizza {
    public NYStyleCheesePizza(){ name = “NY Style Cheese Pizza”;}

    void cut prepare() { 
        System.out.println(“Preparing NYStyleCheesePizza…”);
    }

    // 其他方法
}
```

最后我们来看一下怎么使用这些类来预定Pizza。


```java
public static void main(String[] args){
    PizzaStore nystore = new NYPizzaStore(); 
    PizzaStore shstore = new SHPizzaStore();

    Pizza pizza = nystore.orderPizza(“cheese”);
    pizza = shstore.orderPizza(“cheese”);
}

```

工厂方法模式通过让子类决定该创建对象是什么，来达到将对象创建的过程封装的目的。
在我们的例子中PizzaStore是抽象创建者类，它定义了一个抽象的工厂方法（createPizza），让子类实现此方法制造产品，抽象创建者不需要知道制造了哪种具体的产品。
NYPizzaStore和SHPizzaStore是具体创建者类，它们通过覆盖抽象工厂方法来实现创建自己特定的Pizza。
Pizza是抽象产品类，而NYStyleCheesePizza, NYStyleClamPizza, SHStyleCheesePizza, SHStyleClamPizza是具体的产品类。

抽象工厂方法产生了两个平行的类层级结构，一个是创建者，一个是产品。

*工厂方法 Structure & Participants*

{{% figure class="center" src="/images/oodesign/oodp-factory-2.jpg" alt="工厂方法模式UML" title="工厂方法模式UML" width="700px" %}}

1. Product: 工厂生成的产品。定义了一个Creator创建的对象的的接口，这个工厂方法也可以接受参数，根据参数生产对象。
2. ConcreteProduct：具体的产品，实现了Product接口。
3. Creator：申明了一个工厂方法，返回一个Product类型，让子类实现此方法来制造产品；同时也可以定义一个默认的工厂方法实现，返回一个默认产品。
4. ConcreteCreator: 创建并返回一个具体的产品。

*工厂方法 Applicability*

1. 类不能预料它需要创建哪种类型的对象；
2. 类想要它的子类决定创建的什么对象；
3. 类将创建对象的职责委托给一些子类中的一个，并且希望集中化管理这个委托的情况。

*工厂方法 Implementation*

1. Creator可以将工厂方法定义为抽象方法，或者提供一个默认的实现；
2. 工厂方法可以是参数化的，即允许通过传入的值决定创建的具体的产品，也可以是非参数化的。

*工厂方法 Consequences*

1. 优点1：相比简单工厂，工厂方法将抽象与实现分离，使设计更加灵活。代码仅处理Product接口，可以与任何用户定义的ConcreteProduct一起使用。比如，如果我们要增加一个新的Pizza产品的时候，我们完全不用修改原始代码，只要增加一个新的PizzaFactory和一个新的Pizza就可以，这遵循了开放关闭原则；
2. 优点2：相比简单工厂使用条件判断语句来决定到底使用哪个具体产品，工厂方法使得写测试代码更加方便；
3. 优点3：工厂方法可以提供一个默认的构造过程，而子类可以更加灵活方便的在此基础上构建特定的产品；
4. 缺点1：为了创建一个ConcreteProduct，用户需要去创建一个ConcreteCreator。

*抽象工厂 Definition*

> 抽象工厂模式：定义了一个接口用于创建相关的或相依赖的对象，而不需要明确指定具体类。

*抽象工厂 Applicability*

1. 简单工厂和工厂方法是创建一类产品的模式，抽象工厂一般用来创建一组相关的产品。它提供了一组工厂，每个工厂创建一组特定的相关产品。所以抽象工厂又被称为工厂的工厂。
2. 抽象工厂允许客户使用抽象的接口来创建一组想关的产品，而不需要知道实际生产出来的产品是什么，使客户从具体的产品解耦。
3. 下面是GoF给出的抽象工厂的适用性：
  1. 一个系统要独立于它的产品的创建、组合和表示时；
  2. 一个系统要由多个产品系列中的一个来配置时；
  3. 当一组相关的产品对象被设计用来一起使用的时候，并且你希望保证这一点；
  4. 当你提供一个产品类库，而只想展示他们的接口而不是实现的时候。


*抽象工厂 Motivation*
我们继续Pizza的例子。现在Pizza上面需要添加很多调料，每一个PizzaStore需要生产自己的一组调料，而每一种风味的Pizza通常需要的调料可能也不一样。下面我定义一个抽象工厂来确定生成调料的工厂的接口：
```java
public interface PizzaIngredientFactory{
    public Sauce createSauce();
    public Cheese createCheese;
    public Clams createClam();
}
```
我们也可以把这个接口改写成抽象类，然后提供一部分默认的调料生产方法。

下面我们为SHPizzaStore来编写一个调料生产工厂：
```java
public class SHPizzaIngredientFactory implements PizzaIngredientFactory {
    public Sauce createSauce(){
        return new KetchupSauce();
    }

    // 其他调料创建方法
}
```

下面我们来更新一下Pizza类，将调料添加到Pizza中
```java
public abstract class Pizza {
    String name;
    Sauce sauce;
    Cheese cheese;
    Clams clam;

    abstract void prepare();
    abstract void bake();
    abstract void cut();
    abstract void box();
}
```

接下来我们做一个CheesePizza
```java
public class CheesePizza extends Pizza{
    PizzaIngredientFactory ingredientFactory;

    public CheesePizza(PizzaIngredientFactory ingredientFactory){
        this. ingredientFactory = ingredientFactory;
    }

    void prepare(){
        // 添加调料
        sauce = ingredientFactory.createSauce();
        cheese = ingredientFactory.createCheese();
        // 我们不需要clam
    }

    // 其他Pizza制作步骤的方法
}
```

接下来我们做一个ClamPizza
```java
public class NYPizzaStore extends PizzaStore{
    PizzaIngredientFactory ingredientFactory;

    public CheesePizza(PizzaIngredientFactory ingredientFactory){
        this. ingredientFactory = ingredientFactory;
    }

    void prepare(){
        // 添加调料
        sauce = ingredientFactory.createSauce();
        cheese = ingredientFactory.createCheese();
        clam = ingredientFactory.createClam();
    }

    // 其他Pizza制作步骤的方法
}
```

最后我们还需要修改一下PizzaStore的类。
```java
public class SHPizzaStore extends PizzaStore{
    protected Pizza createPizza(String item){
        Pizza pizza = null;
        PizzaIngredientFactory ingredientFactory = new     
            SHPizzaIngredientFactory();

        if( item.equals(“cheese”)){
            pizza = new CheesePizza(ingredientFactory);

        }else if ( item.equals(“clam”)){
            pizza = new ClamPizza(ingredientFactory);
        }
        return pizza;
    }
}
```

*抽象工厂 Structure*

{{% figure class="center" src="/images/oodesign/oodp-factory-3.jpg" alt="抽象工厂模式UML" title="抽象工厂模式UML" width="700px" %}}

*抽象工厂 Participants*

1. AbstractFactory：声明一个创建抽象产品对象的操作的接口；
2. ConcreteFactory: 实现创建具体产品对象的操作；
3. AbstractProduct：为一类产品对象声明一个接口；
4. Product：定义一个被具体工厂创建的产品对象；实现抽象产品接口。
5. Client： 仅适用AbstractFactory和AbstractProduct类声明的接口

*抽象工厂 Collaborations*

1. 抽象工厂类模式一般用工厂方法来实现某个产品的创建，也可以用原型模式来实现；
2. 一个具体的工厂经常实现为单例模式；
3. 抽象工厂将产品对象的创建推迟到了具体工厂的子类里。

*抽象工厂 Consequences*

1. 缺点1：难以支持新的产品。如果要在抽象产品工厂中，增加一个新的产品，那么它的所有子类必须也要添加。
2. 优点1：将客户与具体的产品类解耦。工厂封装了创建产品对象的责任和过程，客户通过抽象接口操作产品对象。具体产品的类名也不会出现在客户代码中；
3. 优点2：很容易替换产品系列，只需要将具体工厂替换成另一个具体工厂即可；
4. 优点3：有利于产品的一致性。一个工厂创建出来的产品是一套相关的产品，使用工厂模式，有利于保持产品的一致性。

*三种工厂模式的回顾*

1. 所有工厂都是用来封装对象的创建；
2. 所有工厂都通过减少应用程序和具体类之间的依赖来促进解耦；
3. 工厂方法模式使用继承，把对象的创建委托给子类，子类实现工厂方法来创建对象；
4. 抽象工厂模式使用对象组合，对象的创建被实现在工厂接口所暴露出来的方法中；
5. 工厂方法允许将类的实例化延迟到子类中进行；
6. 抽象工厂创建相关的对象的家族，而不需要依赖它们的具体类。

*工厂方法和抽象工厂对比*

{{% figure class="center" src="/images/oodesign/oodp-factory-4.jpg" alt="工厂方法模式" title="工厂方法模式" width="700px" %}}
{{% figure class="center" src="/images/oodesign/oodp-factory-5.jpg" alt="抽象工厂模式" title="抽象工厂模式" width="700px" %}}


### **生成器模式**
*Motivation*

假设我们要组装一台PC主机，组装的过程有安装主板，安装CPU，安装内存，安装机械硬盘，安装电源，可选的组件有显卡，无线网卡，固态硬盘等。

组装电脑的过程是一步一步的，并且并不是每一台电脑都安装所有的组件，因此我们希望这个电脑对象的构建过程是可以被精细化控制，并且作为客户我们并不想知道组装电脑的具体过程。我们使用Builder（生成器）模式来演示这个过程。

首先我们有一个Computer接口用于定义了一台电脑，简单起见，假设一台电脑只有主板、CPU和内存：
```java
public class Computer {
    public String cpu;
    public String motherboard;
    public String memory;
}
```

们再定义一个构建Computer的生成器的接口IComputerBuilder
```java
public interface IComputerBuilder(){    void setMemory();
    void setCPU();
    void setMotherboard();
    Computer getComputer();
}
```

我们想组装一台高配的电脑，这个组装过程定义在ComputerBuilderA这个类中：
```java
public class ComputerBuilderA implements IComputerBuilder {
    private Computer computer;
    
    public void setMemory(){ computer.memory = “32GB”; }
    public void setCPU(){ computer.cpu = “Intel i7”; }
    public void setMotherboard(){ computer.motherboard = “Asus Z370”; }
    
    public Computer getComputer(){
        return computer;
    }
}
```

我们想组装一台低配的电脑，这个组装过程定义在ComputerBuilderB这个类中：
```java
public class ComputerBuilderB implements IComputerBuilder {
    private Computer computer;
    
    public void setMemory(){ computer.memory = “2GB”; }
    public void setCPU(){ computer.cpu = “Intel i3”; }
    public void setMotherboard(){ computer.motherboard = “Asus B360”; }
    
    public Computer getComputer(){
        return computer;
    }
}
```

我们再设计一个类用来专门负责电脑的组装过程：
```java
public class ComputerBuilderDirector {
    IComputerBuilder builder;
    public ComputerBuilderDirector(IComputerBuilder builder) {
        this.builder = builder;
    }

    public Computer construct(){
        builder.setMotherboard();
        builder.setCPU;
        builder.setMemory();
        Computer computer = builder.getComputer();
        return computer;
    }
}
```

最后我们再来看一下如何使用这些类的：
```java
public static void main(String… args){
    IComputerBuilder builder = new ComputerBuilderA();
    Computer c = new ComputerBuilderDirector( builder).construct();
}
```

*Definition*

> 将一个复杂对象的构建与它的表示相分离，使得同样的构建过程可以创建不同的表示

*Applicability*

当创建复杂对象的算法应独立于该对象的组成部分以及它们的装配方式时，或者当构造过程必须允许被构造的对象有不同的表示时：
用简单的话说：当我们需要通过一步一步的构造过程来构造一系列复杂的，但是相似的对象时，或者说，当我们需要将许多小的部件通过一系列相类似的步骤构造成一个复杂的对象时，Builder模式适用。

*Structure & Participants*
{{% figure class="center" src="/images/oodesign/oodp-builder-1.png" alt="生成器模式UML" title="生成器模式UML" width="700px" %}}

Builder: 定义一个抽象的接口用于创建产品对象的一部分；
ConcreteBuilder: 实现Builder接口以构造和装配该产品的各个部分；定义和跟踪表示的创建；并提供一个接口用于取回创建的产品。
Director: 通过Builder接口来构建一个对象；
Product: 表示一个需要构建的复杂对象。ConcreteBuilder创建该产品的内部表示，并定义它的装配过程；包括定义组成部件的类，也包括将这些部件装配成最终产品的接口。

*Collaborations*

1. 客户端创建一个Director对象，并将客户端想要构建的对象的Builder注入到这个Director对象中；
2. 当有产品的一部分需要被创建的时候（即客户端调用Director的Construct方法时），Director通知Builder需要创建的部分；
3. Builder处理构造产品一部分的请求，并把构造的这部分添加到整个产品中去；
4. 客户端从Builder中获取构造好的产品。

{{% figure class="center" src="/images/oodesign/oodp-builder-2.png" alt="生成器模式交互图" title="生成器模式交互图" width="500px" %}}

*Consequences*

1. 允许Builder改变产品的内部表示，将产品的内部表示、结构和组装方式对客户端隐藏；
2. 将构建产品的代码和产品表示的代码分离开，产品的实现可以被替换；
3. 允许对产品的构建过程进行更加精细化的控制（由Director一步步地控制）；
4. Builder模式适合与构造复杂的对象，并且这个过程是可以被拆分成多步骤的，如果构造过程很简单，使用Builder模式可能将引入不必要的复杂性；
5. 相比工厂模式，使用Builder模式生成对象的的客户需要更多的领域知识。

*Implementation*

通常Builder类是一个抽象类，为每一个组件的构建定义了一个抽象方法，由子类来具体实现该组件的构造过程。

### **原型模式**

*Definition*

> 原型模式通过克隆（复制）已有对象来创建新的对象，如果新的对象和原有对象相近，并且对象创建开销很大的话，可以采用原型模式来创建对象；

*Applicability*

1. 当一个系统应该独立于它的产品的创建、组装和表示，并且符合以下任一条件时，使用原型模式：
2. 当要实例化的类是在运行时制定，比如动态加载；
3. 为了避免创建一个和产品类层次（hierarchy）平行的工厂类层次时；
4. 当一个类的实例只能有几个不同状态组合中的一种时，建立相应数目的原型并克隆它们可能比每次用合适的状态手工实例化更加方便。

*Structure & Participants*

{{% figure class="center" src="/images/oodesign/oodp-prototype-1.png" alt="原型模式UML" title="原型模式UML" width="600px" %}}

1. Prototype: 声明一个克隆自己的接口；
2. ConcretePrototype: 实现一个克隆自己的操作；
3. Client: 让一个原型克隆自身来创建新的对象。

*Collaborations*

客户端通过要求原型克隆自己来创建新的对象

*Consequences*

1. 优点1：减少子类的构造。相比工厂方法构造一个和产品层级平行的Creator层次，原型模型不需要构建这么多Creator；
2. 缺点1：每一个原型的子类都必须实现Clone接口，当有些对象不支持拷贝或者有循环引用的时候可能会有问题。



## **结构型模式**

### **装饰器模式**

*Motivation*

Kebab是一种中东美食，在欧洲的街边也很常见。它主要是各种烤肉，然后根据顾客要求加入很多不同的佐料，西红柿片，黄瓜片，洋葱、蔬菜等等，最后浇上顾客制定酱料，比如番茄酱、烧烤酱等等，然后放在两片很大的面饼里面。有点类似Subway。笔者至今还时常想念那个味道；

假如我们要在食堂里开一家Kebab店，需要开发一个自助订餐系统。一种简单但是很笨重的设计方法是用继承，将Kebab定义为一个接口类，然后让不同风味的Kebab继承它。

但是，Kebab的特点的是客户定制化程度很高，如果我们对每一种客户定制的Kebab都设计一个具体的类的话，这种组合会多的很可怕：比如一个烧烤味的带有西红柿和洋葱的鸡肉Kebab：TomatoOnionBBQChickenKebab

使用继承的设计还有一个缺点：不够灵活。所有的组合都是在编译时确定的，一旦需要一个新的组合就需要增加代码。

装饰器模式非常适合这个场景。

*Applicability*

1. 动态地、透明地为对象增加责任，而同时不影响其他对象；
2. 责任可以被撤回；
3. 当作为子类继承不现实的情况下：通常是有很多独立的扩展（不同的佐料和酱料），使用继承会造成子类数量指数级的增长（组合不同的佐料和酱料）。

*Motivation(Continued)*

回到Kebab的场景，我们来看下装饰器模式是如何解决这个问题的。假设我们需要为一份Kebab计算价钱，其中每一种佐料、酱料都需要统计。我们先定义一个烤肉抽象类：
```java
public abstract class Kebab {
    public abstract double cost();
}
```

然后我们开始为各种烤肉编写代码
```java
public class ChickenKebab extends Kebab {
    public double cost() { return 3.49;}
}

public class DonerKebab extends Kebab {
    public double cost() { return 2.49;}
}
```

现在我们为各种佐料、酱料编写代码，首先编写一个调料的抽象类，继承Kebab抽象类，它除了继承了cost方法外，什么都没有：
```java
public abstract class CondimentDecorator extends Kebab {}
```

然后，我们开始编写各种佐料、酱料，我们以西红柿为例：
```java
public class Tomato extends CondimentDecorator {
   Kebab kebab;
   public Tomato ( Kebab kebab ){ this.kebab = kebab;}

   @Override
   public double cost (){
       return 0.20 + kebab.cost(); // 西红柿是如何计算价钱的
   }
}
```

我们再编写一个BBQ的类：
```java
public class BBQ extends CondimentDecorator {
   Kebab kebab;
   public BBQ ( Kebab kebab ){ this.kebab = kebab;}

   @Override
   public double cost (){
       return 0.1 + kebab.cost(); // 西红柿是如何计算价钱的
   }
}
```

使用同样的方法入门定义了Cucumber，Ketchup等佐料、调料。让我们来看下一份Kebab是怎么做出来的。
```java
public static void main(String… args){
    Kebab kebab = new DonerKebab();
    kebab = new Tomato( kebab);
    kebab = new BBQ( kebab);
}
```

在计算这份Kebab的加强的时候，kebab.cost()会最先进入外层BBQ的cost方法，也就是0.10 + kebab.cost()，然后进入Tomato的cost()，最后进入DonerKebab的cost：
`0.10 + 0.20 + 2.49 = 2.79`

这个设计有点像俄罗斯娃娃一样，一层套一层；而不管套几层，都长地一样：
{{% figure class="center" src="/images/oodesign/oodp-decorator-1.jpg" alt="俄罗斯娃娃" title="俄罗斯娃娃" width="600px" %}}

*Definition*

> 装饰器模式动态地将职责加到对象上面。相对于使用子类来扩展功能，装饰器提供了一个更加灵活的替代方案；

策略模式称为Decorator Pattern，又称Wrapper；

装饰器和被装饰对象有相同的超类型，可以用多个包装器包装对象；

因为超类型相同，因此任何使用原始对象的地方，都可以使用装饰过的对象；

装饰器可以在所委托的被装饰对象的行为前和/或后加上自己的行为；

对象可以在任何时候被装饰，所以可以在运行时动态地、不限量地使用你喜欢的装饰器来装饰对象;

装饰器模式vs策略模式：装饰器模式通过修改对象的外表来修改它的行为，而策略模式通过通过修改对象的内在。如果Component类本身非常地重，那么策略模式可能会更合适。

*Structure & Participants*
{{% figure class="center" src="/images/oodesign/oodp-decorator-2.jpg" alt="装饰器UML" title="装饰器UML" width="600px" %}}

1. Component 定义了一个装饰器和ConcreteComponent都通用的接口；
2. Decorator 维护了一个指向Component的引用并且定义了一个符合Component定义的接口；
3. ConcreteComponent 向Component添加职责；

*Collaborations*

装饰器将方法收到的请求转发给Component，它可以在转发前或之后根据实际需要进行额外的操作。

Consequences
优点1：相对于静态继承来说更加灵活。职责可以在运行时动态地添加到对象上面，也可以动态地移除；
优点2：避免类数量爆炸。可以根据需要添加职责类，而不用把所有可能的组合在设计的时候全部考虑到；
缺点1：会有很多小对象；
缺点2：装饰器和被装饰对象不是完全一致的。所以你在使用装饰器的时候不能以来对象的类型。

#### **Java I/O**

Java IO包里面的很多类其实都是装饰器，我们来看一下它的关系图：

{{% figure class="center" src="/images/oodesign/oodp-decorator-3.jpg" alt="Java IO" title="Java IO" width="600px" %}}


### **适配器模式**

*Motivation*

假设我们设计了一个鸭子的抽象接口，和一个鸭子的实例，如下:
```java
public interface Duck {
    public void quack();
    public void fly();
}

public class MallardDuck implements Duck {
    @Override
    public void quack() { System.out.println(“Quack”); }

    @Override
    public void fly() { System.out.pritln(“I’m flying”);}
}
```

我们也设计了一个火鸡的抽象接口，和一个火鸡的实例，如下:
```java
public interface Turkey {
    public void gobble(); // 火鸡不会呱呱叫，只会发出咯咯的叫声
    public void fly(); // 火鸡飞不远
}

public class WildTurkey implements Turkey {
    @Override
    public void gobble() { System.out.println(“Gooble”); }

    @Override
    public void fly() { System.out.pritln(“I’m flying”);}
}
```

现在因为某些原因，我们想通过Duck的接口调用WildTurkey类的实例。这时候我们需要一个适配器。Duck是客户想要看到的接口类型，但是我们只有WildTurkey，那么Turkey是被适配的接口类型，我们的适配器需要将Turkey接口转换成Duck接口。
```java
public class TurkeyAdapter implements Duck {
    Turkey turkey;

    public TurkeyAdapter (Turkey turkey){this.turkey = turkey;}

    @Override
    public void quack(){ turkey.gobble(); }

    @Override
    public void fly(){
        for( int i = 0; i < 5; i++) turkey.fly(); 
    }
}
```

最后我们要通过Duck接口使用WildTurkey了。
```
public static void main(){
    Duck duck = new TurkeyAdapter( new WildTurkey());
    duck.quack();
    duck.fly();
}
```
这里客户main方法和被适配者WildTurkey是解耦的（WildTurkey可以通过外部注入）。

1. 客户通过目标接口（Duck）调用适配器（TurkeyAdapter）的方法对适配器发出请求；
2. 适配器使用被适配者接口把请求转换成被适配者的一个或多个接口调用；
3. 客户接收到调用的结果，但并不知道适配器做了转换。

*Definition*

> 将一个类的接口转换成客户期望的另一个接口，将原本接口不兼容的类可以放在一起工作。

适配器模式(Addapter)也叫Wrapper模式。

*Structure & Participants*

有两种适配器模式，一种是我们鸭子的例子中见到的，对象层面的适配，通过将被适配者组合到适配器中达到目的；另一种是类层面的视频日，通过多重继承来实现。

{{% figure class="center" src="/images/oodesign/oodp-adapter-1.jpg" alt="适配器模式UML" title="适配器模式UML" width="600px" %}}

1. Target: 定义一个客户使用的特定领域的接口（客户期望的类型）；
2. Client：调用Target接口的对象；
3. Adaptee：定义一个需要被适配的接口；
4. Adapter：对Adaptee的接口与Target的接口进行适配。

*Collaborations*

Client调用Adapter实例进行操作，而Adapter又调用Adaptee来实现这个操作。

*Applicability*

1. 当需要使用一个已经存在的类，但是它的接口不符合要求的时候；
2. 当需要创建一个可以复用的类，该类可以与其它不相关的类或不可预见的类（接口可能不一定兼容的类）系统工作；
3. （仅针对对象层面的适配器）当想要使用一些已经存在的子类，但是又不想逐个匹配它们的接口，对象层面的适配器可以适配它们的父类接口，然后也就可以使用子类了。

*Consequences*

1. 类层面的适配器：
  * 优点1：Adapter可以重定义Adaptee的行为，因为我们采取的是继承的方式；
  * 优点2：仅仅增加了一个对象，不需要额外的指针间接得到被适配者；
  * 缺点1：我们无法适配Adaptee的子类；

2. 对象层面的适配器：
  * 优点1：允许一个Adapter和多个Adaptee——即Adaptee本身以及它的所有子类同时工作；Adapter也可以一次给所有Adaptee添加功能；
  * 缺点1：重定义被适配者的行为比较困难。这需要继承Adaptee，然后覆盖Adaptee的方法，然后让Adatper引用该子类。

*适配器模式 vs 装饰模式*

1. 装饰器表示有新的责任或行为要添加到现有类中；
2. 适配器的首要作用是转换接口。

*Java中的适配器例子*

1. 遗留集合类型像Vector，Stack，Hashtable都实现了一个elements()方法。该方法返回一个Enumeration接口；
  * Enumeration有两个方法：hasMoreElements()和nextElement()。

2. 新的集合使用Iterator来替代Enumeration;
  * Iterator有三个方法：hasNext()，next()和remove()。

3. 为了适配新老接口，我们设计了一个EnumerationAdapter:
  * EnumerationAdapter继承Iterator接口，实现hasNext()，next()和remove()方法；
  * EnumerationAdapter持有一个指向Enumeration接口的引用， hasNext()和next()方法将直接被转换为对hasMoreElements()和nextElement()的调用；
  * remove()将抛出UnsuooprtedOperationException();


### **外观模式**

*Motivation*

我们简单地描述一下Head First里面的例子：假设我们有一个家庭影院。其中，投影仪，播放机，音响等等都是一个个对象。当我们想看电影的时候，我们依次调用

1. 投影仪的打开方法；
2. 播放机的开始播放方法；
3. 音响的打开方法；

当我们像结束放映的时候，我们又要调用一系列的方法。

为了简化这个过程，我们可以有一个遥控器类，一旦调用遥控器的打开方法，它会自动执行投影仪、播放机、音响等等相应的启动方法。
这个遥控器扮演的就是外观的角色，它将子系统（投影仪、播放机、音响）的接口统一并且简化。但是如果你想单独调用音响的方法（比如提高音量），遥控器（外观）也不会阻止你这么做。

*Definition*

> 外观模式提供了一个统一的接口，用来访问子系统中的一群接口。外观定义了一个高层的接口，让子系统共容易使用。

外观模式创建了一个简化而统一的接口用来包装系统中一个或多个复杂的类，让客户和子系统之间避免耦合；

外观没有屏蔽子系统的接口，当用户想要使用复杂的接口的时候仍旧可以绕过外观使用子系统的接口。

*适配器模式 vs 外观模式*

适配器模式将一个或多个接口变成客户所希望的一个接口，适配器的意图是转换接口。虽然很多例子中，适配器只是一对一的适配，事实上一个适配器可以统一多个被适配者；

外观模式针对一个或多个拥有复杂接口的类提供简化的接口，外观模式的意图是提供子系统的一个简化接口。虽然很多例子中，外观模式处理的是多个复杂的类，事实上外观模式也可以用于简化一个类。

*Applicability*

1. 当你需要为一个复杂的子系统提供一个简单的接口的时候，Façade模式可以提供一个简单的默认视图，这一视图对大多数用户来说已经足够，而需要更多定制化的用户可以绕过façade层；
2. 当客户程序与抽象类的实现类之间存在很大依赖的时候，引入façade模式将这个子系统与客户以及其它子系统分离开，提供子系统的独立性和可移植性；
3. 当需要构建一个层次结构的子系统的时候，使用façade模式定义子系统中每层的入口点；如果子系统之间是相互依赖的，可以让它们仅通过façade进行通讯，从而简化它们之间的依赖关系。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-facade-1.png" alt="外观模式UML" title="外观模式UML" width="500px" %}}

*Participants*

1. Façade：知道哪些子系统类负责处理请求，将客户的请求转发给适当的子系统对象；
2. Subsystem classes：实现子系统的功能，处理由façade对象分发的请求。子系统类没有façade的信息（即没有指向façade的指针）。

*Collaborations*

1. 使用façade的客户不必直接访问子系统类；
2. 客户程序将请求发送给façade，然后façade转发给适当的子系统对象处理。Façade需要将它的接口转换成子系统接口。

*Consequences*

1. 优点1：对客户屏蔽了子系统组建，减少了客户处理的对象的数目，使得系统使用起来更加方便；
2. 优点2：实现了子系统与客户之间的松耦合关系。子系统内部的功能组建往往是紧耦合的，松耦合的客户与子系统关系使得子系统组建变化不会影响到客户。同时，也有助于建立层次结构系统，以及对对象之间的依赖分层。
3. 优点3：如果需要，façade模式并不限制使用子系统类。


### **代理模式**

*Definition*

>为另一个对象提供一个替身或占位符以控制对这个对象的访问；

使用代理模式创建一个代表，让代表控制某对象的访问，比如：

  1. 远程代理控制客户访问远程对象；
  2. 虚拟代理控制访问创建开销大的对象；
  3. 保护代理基于权限控制对资源的访问。

*Structure*

下面是代理模式的一般结构：
{{% figure class="center" src="/images/oodesign/oodp-proxy-1.png" alt="代理模式UML" title="代理模式UML" width="500px" %}}

运行时代理的结构图：
{{% figure class="center" src="/images/oodesign/oodp-proxy-2.png" alt="运行时代理的结构图" title="运行时代理的结构图" width="500px" %}}

*Participants*

1. Proxy: 
  * 维护一个指向被代理的对象的引用，如果RealSubject和Subject接口相同，Proxy会引用Subject；
  * 提供一个和Subject接口完全相同的接口，这样Proxy可以替代RealSubject；
  * 控制对RealSubject的访问，同时也可能负责创建和删除RealSubject；
  * 以下功能取决是哪种代理模式：
      - 远程代理负责对请求及其参数进行编码，并通过网络发送编码的请求；
      - 虚拟代理可以缓存实体的附件信息，以便延迟对它的访问；
      - 保护代理检查调用者是否有权限访问被代理的对象。
2. Subject: 定义一个RealSubject和Proxy通用的接口，使得Proxy可以任何地方替代RealSubject；
3. RealSubject：定义Proxy代表的真正实体。RealSubject是实际处理业务逻辑的类。

*Collaborations*

根据不同的代理模式，代理在恰当的时候将请求转发给真正的实体处理。

*Applicability*

1. 如果简单地对对象的引用不足以满足需求的时候，需要一个更加通用而复杂的对象来代替这个引用的时候可以考虑使用代理模式。下面是代理模式适用的几种常见场景：
2. 远程代理提供不同地址空间的对象的一个本地表示，比如Java RMI；
3. 虚拟代理按需创建对象（延迟开销较大的对象的创建）；
4. 保护代理控制对原始对象的访问，特别是当对象需要有不同的访问权限时。

*Consequences*

1. 代理模式在客户和对象之间引入了一个额外的一层，将客户对Subject的方法调用拦截下来。这层有很多种用途，取决于代理的种类：
  - 远程代理向调用方隐藏了被调用的对象实际上在另一个地址空间这个事实；
  - 虚拟代理可以进行性能优化；
  - 保护代理可以在对象被访问的时候做一些额外的事情；
  - 写时复制延迟（大）对象的复制，直到对象被修改的时候才真正复制；
  - 防火墙代理控制网络资源的访问，保护被代理的资源免于恶意客户侵害；
  - 智能引用代理在访问时做额外的动作，比如计算一个对象被引用的次数；
  - 缓存代理为开销大的计算结果提供缓存，允许多个用户共享结果；
  - ……

2. 代理的缺点是会增加设计中类的数目。


*代理 vs 适配器 vs 装饰器*

1. 代理的目的是控制对对象的访问，而装饰器是为了增加对象的行为；
2. 代理和适配器都是挡在其他对象的前面，并负责将请求转发给它们；而适配器会改变对象适配的接口，代理则实现相同的接口。


#### **Java的动态代理**

{{% figure class="center" src="/images/oodesign/oodp-proxy-3.png" alt="Java动态代理" title="Java动态代理" width="700px" %}}

需要被代理的对象是图中的RealSubject，它实现一个或多个接口（图中的Subject）；

在Java的动态代理里面，代理类Proxy是由Java自身的代码创建的，不需要去编写。而且，动态代理里的Proxy类是在运行时才将它创建出来的。程序开始执行时，还没有Proxy类，它是根据需要提供的接口集创建的。

这个自动创建的Proxy类会实现被代理的RealSubject的所有接口（图中的Subject），并且将接口方法的调用请求都转发给实现了InvocationHandler接口的类；
这个实现了InvocationHandler的类是需要我们去编写的，同时我们需要告诉JRE如何去创建Proxy类。

下面我们来看一个例子。在接下来要演示的代码中，我们特意加上了包名，用来区分哪些代码是我们写的，哪些是Java自身的代码。

我们的场景是转账：将一笔钱从一个账户转到另一个账户。我们首先定义这个转账的接口和方法。这里的ITransaction接口相当于结构图中的Subject接口：

```java
package me.jiaqili.oodesign.proxy;

public interface ITransaction {
    void doTransaction(String from, String to, BigDecimal amount);
}
```

然后我们实现这个接口来做真正的转账动作（我们的目的是演示Java动态代理，因此转账的动作被简化成了打印一行转账信息的代码），这里的Transaction相当于结构图中的RealSubject：

```java
package me.jiaqili.oodesign.proxy;

public class Transaction implements ITransaction {

    @Override
    public void doTransaction(String from, String to, BigDecimal amount) {
        System.out.println("Transfer $" + amount + " from " + from + " to " + to + ".");
    }
}
```

在没有使用代理的情况下，转账的方法调用过程如下：

```java
package me.jiaqili.oodesign.proxy;

public class Test1 {

    public static void main(String[] args) {

        Transaction realTransaction = new Transaction();

        // 1. Transcation without Proxy
        ITransaction transaction = realTransaction;
        transaction.doTransaction("Alice", "Bob", BigDecimal.valueOf(1000.00));

    }
}
```
输出`Transfer $1000.0 from Alice to Bob.`

如果我们想在转账之前做一些检查，比如看一下收款人是不是在黑名单里面。如果收款人是黑名单客户，则拒绝付款。我们可以使用代理模式来控制对转账方法的访问。
```java
package me.jiaqili.oodesign.proxy;

public class RestrictedPartiesFilterInvocationHandler implements InvocationHandler {
    private Set<String> restrictedParties; // 黑名单客户名单
    private ITransaction transaction;      // 被代理对象的引用

    public RestrictedPartiesFilterInvocationHandler( ITransaction transaction, Set<String>     
                                                     restrictedParties){

        this.transaction = transaction;
        this.restrictedParties = restrictedParties;
    }

    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 处理代理业务逻辑…
    }
}
```

RestrictedPartiesFilterInvocationHandler类里面invoke方法：
```java
@Override
public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {

    try{
        if( method.getName().equals( "doTransaction") 
            && restrictedParties.contains( (String)args[1])){

            // if the method is doTransaction and the beneficiary is in the blocked list...
            System.out.println("Beneficiary *" + (String)args[1] + "* is restricted from " +
                               "receving fundings.");
        }else{
            // otherwise, forward request to the real subject 
            return method.invoke(transaction, args);
        }
    } catch(InvocationTargetException e){

        // if the method throws exception, it will go here.
        e.printStackTrace();
    }

    // return null for other method invocation 
    return null;
}
```

Proxy会继承Itransaction接口，而它的doTrasaction方法会调用Handler的invoke方法。调用时会将自身的引用、调用的方法和参数列表传递给invoke。

我们首先判断方法是不是我们需要过滤的doTransaction方法，然后判断黑名单里面是不是包含收款人（即doTransaction的第二个参数）。
如果复合条件，我们打印出拒绝转账的消息；否则我们将方法调用请求正常转发给Transaction对象；

接下来我们来看一下Proxy对象是如何被创建的，以及如何使用Proxy对象来代替Transaction对象。

```java
package me.jiaqili.oodesign.proxy;

public class Test1 {

    public static void main(String[] args) {

        Transaction realTranscation = new Transaction(); // 创建一个被代理的类的对象

        // 1. Transcation without Proxy 不使用代理，直接调用
        ITranscation transcation = realTranscation; 
        transcation.doTranscation("Alice", "Bob", BigDecimal.valueOf(1000.00));

        // 2. Transcation with a restriced parties filtering proxy 使用代理
        Set<String> restrictedParties = new HashSet<String>(); // 创建一个黑名单集合
        restrictedParties.add(“Bob”); // 将Bob添加到黑名单

        // 这里创建了一个Proxy类，然后转型为Itranscation接口
        ITranscation transcation2 = (ITranscation) Proxy.newProxyInstance( 
               realTranscation.getClass().getClassLoader(), 
               realTranscation.getClass().getInterfaces(), 
               new RestrictedPartiesFilterInvocationHandler(realTranscation, restrictedParties));

        // 做两笔转账
        transcation2.doTranscation("Alice", "Bob", BigDecimal.valueOf(500000.00));
        transcation2.doTranscation("Alice", "Cat", BigDecimal.valueOf(2000.00));
    }
}
```
上面代码的输出：
```text
Transfer $1000.0 from Alice to Bob.
Beneficiary *Bob* is restricted from receving fundings.
Transfer $2000.0 from Alice to Cat.
```

第一笔转账没有使用代理，Alice向Bob转账$1,000；

第二笔转账使用代理，Alice向Bob转账$50,000。但是因为Bob在黑名单里面，代理拦截了这笔转账；

第三笔转账也使用了代理，Alice向Cat转账$2,000。Cat不在黑名单里面，交易正常进行。

下面将介绍Java是如何动态生成Proxy类的。在上面的测试代码中，我们并没有编写Proxy类的代码，而是调用了一个方法：
```java
ITranscation transcation2 = (ITranscation) Proxy.newProxyInstance( 
               realTranscation.getClass().getClassLoader(), 
               realTranscation.getClass().getInterfaces(), 
               new RestrictedPartiesFilterInvocationHandler(realTranscation, restrictedParties));
```

这里的Proxy是java.lang.reflect包里的类，它的newProxyInstance方法接收三个参数：

1. 类加载器：用来定义代理类的类加载器。我们使用了被代理类的类加载器；
2. 接口数组：代理类需要实现的所有接口。我们使用了被代理类实现的全部接口；
3. 代理方法处理器：拦截被代理类的方法调用后会被这个处理器处理。

newProxyInstance返回由传入的类加载器定义的，实现了传入的接口的，并且和传入的handler一起协作的代理类实例。
下面我们看下newProxyInstance的源码。

```java
package java.lang.reflect;

public class Proxy implements java.io.Serializable {
    public static Object newProxyInstance(ClassLoader loader, Class<?>[] interfaces,    
            InvocationHandler h) throws IllegalArgumentException {
    
        // 进行一些校验
    
        // 查找或生成制定的代理类
        Class<?> cl = getProxyClass0(loader, intfs); 
    
        try {
            // 进行一些校验
    
            final Constructor<?> cons = cl.getConstructor(constructorParams);
            
            // 进行一些权限处理
    
            // 构造代理类实例，传入代理处理器作为参数
            return cons.newInstance(new Object[]{h});
    
        } catch (……){…}
    }
}
```

这里的核心是getProxyClass0这个方法，它会生成代理类的代码。
```java
package java.lang.reflect;

public class Proxy implements java.io.Serializable {
    
    private static final WeakCache<ClassLoader, Class<?>[], Class<?>>
            proxyClassCache = new WeakCache<>(new KeyFactory(), new ProxyClassFactory());

    private static Class<?> getProxyClass0(ClassLoader loader, Class<?>... interfaces) {
        if (interfaces.length > 65535) {
            throw new IllegalArgumentException("interface limit exceeded");
        }

        // If the proxy class defined by the given loader implementing
        // the given interfaces exists, this will simply return the cached copy;
        // otherwise, it will create the proxy class via the ProxyClassFactory
        return proxyClassCache.get(loader, interfaces);
    }
}
```

getProxyClass0方法也是在Proxy这个类里面，它很简单，检查了一下需要实现的接口数量，然后从proxyClassCache对象中获取代理类。

proxyClassCache是一个WeakCache实例，是一个缓存。 proxyClassCache.get方法会从缓存中查找：如果同一个类加载器实现相同的接口的代理类已经创建过了，那么就直接返回这个类；否则get方法会创建这个类。

proxyClassCache的构造器参数中传入了两个参数，第二个参数PrxoyClassFactory是和动态构建代理类有关的类工厂。

proxyClassCache的get方法这里不详细展开了，但是它会调用ProxyClassFactory对象的apply方法，并将类加载器和接口数组作为参数传给它。下面我们看一下ProxyClassFactory，它是Proxy类的一个内部类：

```java
package java.lang.reflect;

public class Proxy implements java.io.Serializable {
    
    private static final class ProxyClassFactory implements 
                  BiFunction<ClassLoader, Class<?>[], Class<?>> {

        // 所有代理类的通用前缀
        private static final String proxyClassNamePrefix = "$Proxy";

        // 用于生成唯一代理类名的下一个数字
        private static final AtomicLong nextUniqueNumber = new AtomicLong();

        @Override
        public Class<?> apply(ClassLoader loader, Class<?>[] interfaces) {

            // 根据类加载器和需要实现的接口生成代理类
            // ……
        }
    }
}
```

继续深入ProxyClassFactory对象的apply方法:
```java
Map<Class<?>, Boolean> interfaceSet = new IdentityHashMap<>(interfaces.length);
for (Class<?> intf : interfaces) {
    // 1. 校验intf是否可以由传入的类加载器加载;
    // 2. 校验intf是否是一个接口；
    // 3. 校验intf在数组中是否重复;
}

String proxyPkg = null; // 生成的代理类的包名
int accessFlags = Modifier.PUBLIC | Modifier.FINAL; // 生成的代理类的访问修饰符

for (Class<?> intf : interfaces) { // 如果有非public的接口，那么这些接口需要在同一个包内，这里进行检查
    int flags = intf.getModifiers(); // 遍历获取接口的访问修饰符
    if (!Modifier.isPublic(flags)) { // 如果修饰符不是public的
        accessFlags = Modifier.FINAL; // 将生成类的访问修饰从public final改成final
        String name = intf.getName();
        int n = name.lastIndexOf('.');
        String pkg = ((n == -1) ? “” : name.substring(0, n + 1)); // 获取接口所在包名
        if (proxyPkg == null) {    // 如果包名还没指定，指定为这个非public接口所在包的包名
            proxyPkg = pkg;      
        } else if (!pkg.equals(proxyPkg)) { // 如果包名已指定（说明有另一个非public的接口），并且两者不一致
            throw new IllegalArgumentException( // 抛出异常
                "non-public interfaces from different packages");
        }
    }
}

if (proxyPkg == null) {
    // 如果包名仍旧为空，即没有找到非public的接口，那么使用默认的包名com.sun.proxy
    proxyPkg = ReflectUtil.PROXY_PACKAGE + ".";
}

// 设置生成的代理类的全限定名，例如：com.sun.proxy.$Proxy0
long num = nextUniqueNumber.getAndIncrement();
String proxyName = proxyPkg + proxyClassNamePrefix + num;

// 使用ProxyGenerator生成字节码
byte[] proxyClassFile = ProxyGenerator.generateProxyClass(proxyName, interfaces, accessFlags);

// 加载生成的代理类，这里defineClass0是一个native方法
try {
    return defineClass0(loader, proxyName, proxyClassFile, 0, proxyClassFile.length);
} catch (ClassFormatError e) {
    throw new IllegalArgumentException(e.toString());
}

```

继续深入ProxyGenerator来看下一下字节码是怎么生成的。注意这个类在sun包里，sun包里的类并不属于Java平台的代码，也不保证长期支持。

```java
package sun.misc;

public class ProxyGenerator {

    public static byte[] generateProxyClass(final String name, 
                                Class<?>[] interfaces, int accessFlags){
        
        ProxyGenerator gen = new ProxyGenerator(name, interfaces, accessFlags);
        // 调用generateClassFile()方法生成字节码
        final byte[] classFile = gen.generateClassFile();
		
        return classFile;
    }
    
    private byte[] generateClassFile() {
        // 生成字节码的逻辑
    }
}
```

继续深入ProxyGenerator的generateClassFile方法。

```java
// 1. 组装ProxyMethod对象
// 组装hashCode, equals和toString方法
addProxyMethod(hashCodeMethod, Object.class);
addProxyMethod(equalsMethod, Object.class);
addProxyMethod(toStringMethod, Object.class);

// 添加所有接口的所有方法
for (Class<?> intf : interfaces) {
    for (Method m : intf.getMethods()) {
        addProxyMethod(m, intf);
    }
}

// 做一些校验

// 2. 组装FieldInfo和MethodInfo对象
// 首先添加构造器
methods.add(generateConstructor());

// 处理所有代理方法
for (List<ProxyMethod> sigmethods : proxyMethods.values()) {
    for (ProxyMethod pm : sigmethods) {

         // 添加代理类的静态字段
        fields.add(new FieldInfo(pm.methodFieldName, "Ljava/lang/reflect/Method;",
                   ACC_PRIVATE | ACC_STATIC));

        // 添加代理类的代理方法
        methods.add(pm.generateMethod());
    }
}

// 添加代理类的静态初始化方法
methods.add(generateStaticInitializer());

// 做一些校验

// 3 写入class文件
ByteArrayOutputStream bout = new ByteArrayOutputStream();
DataOutputStream dout = new DataOutputStream(bout);
try {
    dout.writeInt(0xCAFEBABE); // 写入魔数
    dout.writeShort(CLASSFILE_MINOR_VERSION); // 写入次版本号
    dout.writeShort(CLASSFILE_MAJOR_VERSION); // 写入主版本号
    cp.write(dout); // 写入常量池
    dout.writeShort(accessFlags); // 写入访问修饰符
    dout.writeShort(cp.getClass(dotToSlash(className))); // 写入类引用
    dout.writeShort(cp.getClass(superclassName)); // 写入父类引用
    dout.writeShort(interfaces.length); // 写入接口计数
    for (Class<?> intf : interfaces) { // 写入所有接口
        dout.writeShort(cp.getClass( dotToSlash(intf.getName())));
    }
    dout.writeShort(fields.size()); // 写入字段计数
    for (FieldInfo f : fields) { // 写入所有字段
        f.write(dout);
    }
    dout.writeShort(methods.size()); // 写入方法计数
    for (MethodInfo m : methods) { // 写入所有方法
        m.write(dout);
    }
    dout.writeShort(0); // 写入属性计数（代理为0）
} catch (IOException e) {
    throw new InternalError("unexpected I/O Exception", e);
}
return bout.toByteArray();

```

ProxyGenerator的generateClassFile方法，根据class文件的格式以及需要继承的接口和handler类生成class字节码。

class是java代码编译后的字节码，字节码的格式介绍已经超出了本文的范畴。可以参考Java虚拟机规范中的定义。
最后我们看一下动态生成的代理类。

```java
package com.sun.proxy;

public final class $Proxy0 extends Proxy implements ITranscation{
    private static Method m1; private static Method m3;
    private static Method m2; private static Method m0;
	
    public $Proxy0(InvocationHandler paramInvocationHandler) {
        super(paramInvocationHandler);
    }
	
    public final void doTranscation(String paramString1, 
                                    String paramString2, BigDecimal paramBigDecimal) {
        this.h.invoke(this, m3, new Object[] { paramString1, paramString2, paramBigDecimal });
    }
  
    // hashCode, toString, equals等方法省略

    static {
        m1 = Class.forName("java.lang.Object").getMethod("equals", new Class[] 
                     { Class.forName("java.lang.Object") });
        m3 = Class.forName("me.jiaqili.oodesign.proxy.ITranscation").getMethod(
                     "doTranscation", new Class[] { Class.forName("java.lang.String"),      
                     Class.forName("java.lang.String"), Class.forName("java.math.BigDecimal") });
        m2 = Class.forName("java.lang.Object").getMethod("toString", new Class[0]);
        m0 = Class.forName("java.lang.Object").getMethod("hashCode", new Class[0]);
    }
}
```

#### **Java的RMI**

RMI是Java中远程代理的一种实现；

可以由本地方法调用另一台虚拟机上的对象。

*略*


### **Flyweight模式**

*Motivation*

在有些场景下，我们有非常多的重复的对象，比如围棋的棋子。如果我们为每一个对象new一个实例出来，会造成非常大的内存开销。
这些对象有一些内部的状态，比如围棋棋子的颜色；也有一些外部状态，比如棋子的位置；
内部的状态独立于这个对象使用的场景，可以被共享，比如不管棋子放在哪里，黑色的棋子还是黑色的棋子；
外部的状态不能被共享，比如一个放在左上角的棋子和一个放在右下角的棋子，它们的位置不同。

享元模式（flyweight模式）的目的是重用这些内部状态一致的对象。下面我们来看下围棋这个例子的代码。代码来自[这里](https://blog.csdn.net/u013292493/article/details/51649278)。

```java
/**
 * FlyWeight抽象享元类
 */
public interface ChessFlyWeight {
    void setColor(String c);
    String getColor();
    void display(Coordinate c)
}

/**
 * ConcreteFlyWeight具体享元类
 */
class ConcreteChess implements ChessFlyWeight {
    private String color;

    public ConcreteChess(String color) {
        super();
        this.color = color;
    }

    @Override
    public void setColor(String c) { this.color = c;}

    @Override
    public String getColor() { return color; }
    
    @Override
    public void display(Coordinate c) {
        System.out.println(“棋子颜色：” + color);
        System.out.println(“棋子位置：” + c.getX() + ”,” + c.getY());
    }
}

/**
 * 外部状态UnSharedConcreteFlyWeight非共享享元类
 */
public class Coordinate {
    private int x,y;

    public Coordinate(int x, int y) {
        super();
        this.x = x;
        this.y = y;
    }

    public int getX() { return x;}

    public void setX(int x) { this.x = x;}

    public int getY() { return y; }

    public void setY(int y) { this.y = y; }
}

/**
 * 享元工厂类
 */
public class ChessFlyWeightFactory {
    //享元池
    private static Map<String, ChessFlyWeight> map = new HashMap<String, ChessFlyWeight>();

    public static ChessFlyWeight getChess(String color) {
        if(map.get(color)!=null){
            return map.get(color);
        }else{
            ChessFlyWeight cfw = new ConcreteChess(color);
            map.put(color, cfw);
            return cfw;
        }
    }
}

// 享元的使用
public class Client {
    public static void main(String[] args) {
        ChessFlyWeight chess1 = ChessFlyWeightFactory.getChess("黑色");
        ChessFlyWeight chess2 = ChessFlyWeightFactory.getChess("黑色");
        System.out.println(chess1);
        System.out.println(chess2);

        chess1.display(new Coordinate(10,10));
        chess2.display(new Coordinate(20,20));  
    }
}

```

*Definition*

> 运用共享技术有效地支持大量的细粒度对象的重用（让类的一个实例提供许多“虚拟实例”）；

Flyweight是一个共享对象，它可以同时在多个场景（context）中使用。每个场景中flyweight作为一个独立对象，和非共享的对象没有区别。Flyweight不能对它被使用的场景做出任何假设。

Flyweight的内部状态（intrinsic state）储存在flyweight对象的内部，它与flyweight所在的场景独立；而外部状态（extrinsic state）依赖于场景并随场景而变，因此外部状态不能被共享。客户端对象负责传递flyweight需要的外部状态。

*Applicability*

当以下情况*都*符合时适用flyweight模式：

1. 应用程序使用大量的对象；
2. 由于使用大量对象造成很大的储存开销；
3. 大部分对象的状态可以被变为外部状态；
4. 如果外部状态被移出，可以用相对较少的共享对象取代很多组对象；
5. 应用程序不依赖于对象的identity，因为理论上不同的两个对象，在实现上用的是同一个共享对象。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-flyweight-1.png" alt="Flyweight模式UML" title="Flyweight模式UML" width="700px" %}}

*Collaborations*

1. 客户端不应该直接实例化ConcreteFlyweight，而是通过FlyweightFactory来获取，这能确保ConcreteFlyweight能被正确地共享；
2. Flyweight正常使用所需的状态要么是内部的要么是外部的，内部状态存储在flyweight对象内部，外部状态存储在客户端对象汇总，客户端调用flyweight操作的时候将外部状态传递给它。

*Participants*

1. Flyweight：声明一个接口，通过这个接口flyweight可以接收并作用于外部状态；
2. ConcreteFlyweight：实现flyweight的接口，同时增加intrinsic状态。一个Concreteflyweight必须可以被共享，任何它储存的状态必须是intrinsic；
3. UnsharedConcreteFlyweight：并不是所有的Flyweight的子类都必须被共享——flyweight模式并不强制要求共享。
4. FlyweightFactory：创建并管理flyweight对象；确保flyweight对象被正确的共享：当客户端请求一个flyweight对象的时候，FlyweightFactory会返回一个已经存在的实例或者当不存在的时候创建一个新的实例返回。

*Consequences*

1. 缺点1：如果原来外部状态是存储在对象内部的，那么使用Flyweight模式以后，传输、查找、计算外部状态都将产生额外的开销；
2. 优点1：节省空间。通过共享减少内部状态的储存数量，通过将外部状态改外计算的方式而不是存储的方式来降低外部状态占用的空间。

### **桥接模式**

*Motivation*

当一个抽象有好几个实现的时候，通常的做法是使用继承。但是继承将实现和抽象永久绑定了，这使得对抽象或实现独立地修改、扩展和重用变得比较困难；

考虑下面一个场景（来自GoF）。假设我们定义一个GUI窗口对象Window，然后我们针对IBM Presentation Manager平台和*nix平台分别定义了两种实现，PMWindows和Xwindow，并使他们都继承Window接口；

当我们需要扩展抽象的Window接口的时候，比如我们新增一个IconWindow抽象接口扩展自Window。这意味着我们需要再实现两个不同平台的针对这个新抽象接口的实现类，这使得扩展变得非常麻烦。如下图所示：

{{% figure class="center" src="/images/oodesign/oodp-bridge-1.png" alt="Bridge模式例子" title="Bridge模式例子" width="700px" %}}

桥接模式通过将Window这个抽象层级和实现类的抽象层级分开来解决这个问题：Window、IconWindow等有一个类层级；而实现类也有一个平行的层级，继承自WindowImp，如下所示:

{{% figure class="center" src="/images/oodesign/oodp-bridge-2.png" alt="Bridge模式例子" title="Bridge模式例子" width="700px" %}}

所有Window子类的操作都调用的是WindowImp接口提供的方法, Window以及所有继承自Window的类都有一个指向WindowImp的引用。这将window抽象从许多平台特有的实现中解耦。

Window和WindowImp之间的关系称为桥接，因为它连接了抽象和实现，同时允许WindowImp和Window独立地发生变化。

*Applicability*

1. 当不希望抽象和实现之间有固定的绑定关系的时候，比如在运行时选择或更换实现；
2. 抽象和实现都应该可以通过继承来扩展。桥接模式使得不同的抽象和实现可以组合，并让实现和抽象独立地发展；
3. 对一个抽象的实现部分修改不应该对客户产生影响。

*Definition*

> 桥接模式将抽象部分和实现部分分离，但又允许抽象的类层级和实现的类层级一起工作，允许抽象和实现独立地变化。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-bridge-3.png" alt="Bridge模式UML" title="Bridge模式UML" width="700px" %}}

*Participants*

1. Abstraction: 定义抽象类接口，维护一个指向Implementor类型对象的引用；
2. RefinedAbstraction: 扩展Abstraction定义的接口；
3. Implementor：给实现类定义一个接口。这个接口不一定要和Abstraction定义的接口一致，事实上Implementor和Abstraction可以有相当大的差别。通常，Implementor的接口提供更加底层的操作，而Abstraction接口定义了基于这些底层操作的更高层级的操作；
4. ConcreteImplementor: 实现Implementor定义的接口并定义它的具体实现。

*Collaborations*

Abstraction将client的亲贵转发给它的Implementor对象。

*Consequences*

1. 优点1：分离接口及其实现部分。抽象类的实现可以在运行时配置，而不是将抽象和实现固定地绑定在一起。这也有助于分层，实现更好地结构化的系统，系统高层只需要知道Abstraction和Implementor即可；
2. 优点2：提高扩展性。可以独立地对Abstraction和Implementor层次结构进行扩展；
3. 优点3：对客户隐藏实现细节。

*Implementation*

1. 在只有一个实现类的时候没有必要创建一个Implementor，Abstraction可以直接对应一个ConcreteImplementor；
2. 何时何地何种方法来创建ConcreteImplementor？
  - 如果Abstraction知道所有可能的ConcreteImplementor，那么可以在其构造器中，用参数传入的方式确定实例化哪一个类；
  - 也可以让Abstraction实例化一个默认的ConcreteImplementor，然后根据运行时的需要更换；
  - 或者引入一个工厂对象（抽象工厂模式），该工厂对象的职责就是封装系统平台曾的细节——它知道应该为所在平台创建正确的ConcreteImplementor对象。


### **组合模式**

*Motivation*

在一个图形界面软件中，有许多基本组件，比如文本框、按钮、分隔栏等等。这些组件通常会组合在一起形成一个更复杂的组件，称为容器。

实际上用户通常认为基本组件和容器都是一样的，如果把两者分别对待，会使程序变地更加复杂；

Composite(组合)模式使用了递归的方式使得用户不必区别对待容器和基本组件。

比如下面的例子中，抽象类Graphic可以是Line, Rectangle, Text或者容器Picture；而Picture又是由Graphic组合而成的。

{{% figure class="center" src="/images/oodesign/oodp-composite-1.png" alt="Composite模式例子" title="Composite模式例子" width="700px" %}}

这个Graphic是个抽象类，它既可以代表基本组件也可以代表容器。这个是组合模式的关键。

Graphic既声明一些基本组件使用的方法，比如Draw()，也申明一些容器共用的方法，比如管理它们的子节点的方法。

基本组件会实现Draw这类的方法，而它们没有子节点，因它们不执行容器类的方法；

容器类的方法会把Draw这类的基本组件方法传递给它的子节点。

{{% figure class="center" src="/images/oodesign/oodp-composite-2.png" alt="Composite模式例子" title="Composite模式例子" width="500px" %}}

*Definition*

> 将对象组合成树形结构以表示“部分-整体”的层次结构。Composite使得用户对单个对象和组合对象的使用具有一致性。

*Applicability*

1. 想表示对象的部分-整体的层次结构；
2. 希望用户忽略组合对象与单个对象的不同，用户将统一地使用组合结构中的所有对象。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-composite-3.png" alt="Composite模式例子" title="Composite模式例子" width="500px" %}}

一个典型的组合模式如下：

{{% figure class="center" src="/images/oodesign/oodp-composite-4.png" alt="Composite模式例子" title="Composite模式例子" width="500px" %}}

*Participants*

1. Client: 通过Component接口操纵组合部件的对象；
2. Component: 为组合模式中的对象申明接口，申明共有接口（可以实现其默认行为），并申明用于访问和管理Component的子组件的接口，也可以申明一个接口用户访问父部件；
3. Leaf：表示组合中的叶节点；
4. Composite：存储子部件（子部件是一个Component），并定义那些有子部件的部件的行为；

*Collaborations*

用户直接用Component接口与组合模式中的对象进行交互，如果接收者是一个叶节点，那么它直接处理请求；如果是一个Composite节点，它通常会把请求发送给它的子部件，在转发请求的之前和/或之后可能执行一些额外的操作。

*Consequences*

1. 优点1：定义了一个包含基本对象和组合对象的类层次结构。这个组合过程可以不断地递归。只要任何用到基本对象的地方，就可以使用组合对象；
2. 优点2：简化了客户端代码。客户不需要知道它交互的是一个组合对象还是一个基本对象，和对象的交互是一致的；
3. 优点3：使增加新的类型更加容易。新赠的类型都实现Component接口，因此与已有代码可以很好的整合到一起；
4. 缺点1：可以使设计过度地通用化。无法限制Composite里面用到哪些Component。



## **行为型模式**

### **策略模式**

*Motivation*

现在我们有一群鸭子类（如下图），它们能叫（quack），能游泳（swim），能被展示（display），现在新的需求来了，鸭子们要能飞。
看上去只要Duck类里面加一个fly()方法就可以了。

{{% figure class="center" src="/images/oodesign/oodp-strategy-1.png" alt="策略模式例子" title="策略模式例子" width="500px" %}}

那么问题来了。RubberDuck是一只橡皮鸭，它会叫（有发声器），会游泳（浮在水上），但它不会飞。让所有子类都有这些行为（继承）是不恰当的。

那么能不能把fly()放到一个接口里，然后让需要的鸭子去实现它呢？接口很难实现代码复用。即使我们提供了接口里fly()的默认实现，但是当不同的鸭子需要有自己的fly()实现的时候，必须完全重新写fly()方法。

fly()方法和Duck()类其实没有直接联系，fly()会根据不同的Duck子类而发生变化。fly()其实是一组方法，根据实际的Duck子类来选择特定的fly()。

根据前面提到的内聚性原则，我们应该把会变化的代码分离开来，单独封装，现在我们来设计一个FlyBehaviour的接口来单独封装fly()方法。

{{% figure class="center" src="/images/oodesign/oodp-strategy-2.png" alt="策略模式例子" title="策略模式例子" width="500px" %}}

经过重新设计后的Duck和Fly的领域模型如下

{{% figure class="center" src="/images/oodesign/oodp-strategy-3.png" alt="策略模式例子" title="策略模式例子" width="700px" %}}

*Definition*

> 策略模式：将一组算法，分别封装起来，让他们的实现可互相替换。策略模式解耦具体的算法和使用算法的客户类；

策略模式是一种行为型模式；策略模式称为Strategy Pattern，又称Policy Pattern；

在策略模式中，我们使用了很多设计原则：

1. 多用组合，少用继承：很明显，继承无法解决这个场景的问题；组合运行我们在运行时改变行为，使设计更有弹性；
2. 针对接口编程，而不是针对实现：Duck持有一个FlyBehavior的引用，但它不知道到底用哪一种fly的实现，这由具体的Duck类在运行时决定；
3. 封装变化：将fly这块会变化的代码，单独提取出来和Duck独立。

*Structure & Participants*

{{% figure class="center" src="/images/oodesign/oodp-strategy-4.png" alt="策略模式UML" title="策略模式UML" width="500px" %}}

1. Strategy定义了一个对于所有被支持的算法的通用的接口。
2. ConcreteStrategy实现一个符合Strategy接口的具体算法。
3. Context有一个指向Strategy的引用，这个引用被初始化为一个ConcreteStrategy；Context可以有一个接口来允许Strategy来访问它的数据。

*Collaborations*

1. Context将它收到的请求中涉及算法的部分，委托给Strategy来处理。创建Context的代码通常会传递一个ConcreteStrategy给Context；之后外部代码只需要和Context打交道而不再理会Strategy。
2. Context和Strategy的交互方式有两种：
  - Context调用Strategy的时候将所有后者需要的数据作为参数传递过去；
  - Context可以讲它自己作为参数传递给Strategy，让Strategy来回调。
  
*Applicability*

1. 许多相关的类仅仅是行为上有差异的时候，策略模式提供了用多种行为中的一种行为来配置一个类的方法；
2. 同一个算法有多个版本的时候，策略模式可以将多个算法变种抽象起来形成统一的对外接口；
3. 当一个算法需要使用的数据不应该被它的调用方知道的时候，策略模式可以避免暴露复杂的、特定于算法的数据结构；
4. 当一个类定义了多种行为，并且这些行为在这个类中以多个条件语句的形式存在的时候，使用策略模式将想关条件分支移入它们各自的Strategy类中。

*Consequence*

1. 优点1：消除了条件语句。通过条件语句来选择算法的代码，通常可以重构成策略模式；
2. 优点2：提供相同行为的不同实现。比如算法结果一致，但是不同的实现可能做出了不同的时间/空间的权衡，客户可以根据需要选择具体实现；
3. 优点3：封装了一系列相关算法。Strategy的接口定义了一系列可供重用的算法或行为，继承Strategy有助于提取这些算法中的公共功能；
4. 优点4：隔离了易变的代码。Strategy可以独立于Context修改；
5. 缺点1：客户必须了解不同的Strategy实现之间的区别；
6. 缺点2：增加了对象的数目；
7. 缺点3：Context和Strategy之间额外的通信开销，并不是所有Strategy实现都会用到通过接口传递过去的所有参数。


### **观察者模式**

*Definition*

>观察者模式定义了对象之间的一对多依赖，当一个对象状态改变的时候，它的所有依赖着都会收到通知并自动更新。

观察者模式是一种行为型模式；观察者模式称为Observer Pattern，又称Publish-Subscribe模式；

因为观察者模式是一个非常常见的设计模式，这里不再给出Motivation了，直接来看结构图。

*Structure & Participants*

{{% figure class="center" src="/images/oodesign/oodp-observer-1.png" alt="观察者模式UML" title="观察者模式UML" width="500px" %}}

1. Subject提供一个接口，用于附加观察者和解除观察者；
2. Observer定义一个Update接口，当Subject发生变化的时候通过该方法通知；
3. ConcreteSubject记录了一个状态值，当状态值发生变化时调用Nofify通知观察者；
4. ConcreteObserver保存一个指向ConcreteSubject的引用，并且存储一个和Subject保持一致的状态值，实现Update方法使这个状态值在接到通知后仍旧与Subject保持一致。

*Collaborations*

ConcreteSubject当一个变化发生并且“可能”导致其状态发生变化时，通知所有的观察者；

当ConcreteObserver接到上述通知后，它可以进一步查询ConcreteSubject的状态信息，然后以此来同步自身的状态。

{{% figure class="center" src="/images/oodesign/oodp-observer-2.png" alt="观察者模式交互图" title="观察者模式交互图" width="500px" %}}

如上图所示，aConcreteObserver是引起Subject状态发生变化的对象，但是它并没有更新自身的状态，直到aConcreteSubject调用Notify方法时才更新。

Applicability
当改变一个对象会导致需要改变其它对象，而你不知道到底有多少对象需要被修改时；
当一个对象需要去通知其它对象，但是这个对象不需要知道其它对象是什么的时候（你不希望这些对象耦合）；
当一个抽象存在两部分，一个部分依赖于另一部分的时候。把它们分别分装起来，然后可以分别被修改或复用。


Consequence
优点1：Subject只知道它有一个Observer组成的列表，并且每一个Observer都符合一个共有的简单的接口的定义；因此Subject和Observer之间的耦合是抽象的、最小的。
优点2：支持广播通信的方式。Subject只负责通知它的Observer，而Observer决定如何处理或者忽略该通知。
优点3：独立复用Observer、Subject。
缺点1：不可预料的更新。Observer并不知道Subject中的其它Observer，因此它们并不清楚引起Subject改变会带来什么样的后果。一个看似无害的对Subject的修改，可能造成Observer们级联式的update，并且可能最终产生有害的update。归根到底，我们并不清楚是什么造成了状态的变更。

#### **Java内置的观察者模式**

实现Observer接口的类可以通过继承了Observable的类的addObserver方法添加到Observable的观察者列表中；

Java的观察者模式增加了setChanged方法。当notifyObservers被调用的时候，会首先检查changed变量是不是为true，是则通知观察者更新，并将changed置为false；否则不会采取任何操作。

```java
setChanged(){ 
    changed = true;
}

notifyObservers(){ 
    notifyObservers(null);
}

notifyObservers(Object arg){

    if( changed){
        for every observer on the list {
            call update(this, arg);        }
        changed = false;
    }
}
```

{{% figure class="center" src="/images/oodesign/oodp-observer-3.png" alt="Java的观察者模式" title="Java的观察者模式" width="200px" %}}

changed这个标记允许对通知Observer的情况进行更加有弹性的控制：并不是Observable一发生变化就通知Observer，只有当changed被设置的时候才会通知观察者；

notifyObservers有两个版本，一个是将数据Object传递给了Observer，这是一种推的模式；还有一种只传递自身的引用，让Observer来查询Observable的数据，这是一种拉的操作。注意不要依赖观察者被通知的顺序。

Java的内置的观察模式有两个缺点：

1. 缺点1：由于Observable是一个类，而不是接口，所以限制了它被复用的场景；
2. 缺点2：同时Observable的setChanged是一个protected方法，因此Observable的实例没法被组合到其他类中引用，破坏了“多用组合，少用继承”的原则；


### **访问者模式**

*Definition*

> 表示一个作用于某对象结构中个元素的操作，它使你可以在不改变个元素的类的前提下定义作用于这类的新操作。

*Applicability*

1. 一个对象结构中包含很多类对象，它们有不同的接口，而想对这些对象实施一些依赖于其具体类的操作；
2. 需要对一个对象结构中的对象进行很多不同的并且而不相关的操作，而要避免让这些操作“污染”这些对象的类；
3. 定义对象结构的类很少改变，但经常需要在此结构上定义新的操作。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-visitor-1.png" alt="访问者模式" title="访问者模式" width="600px" %}}

*Participants*

访问者模式有两个类层次：一个对应于接受操作的元素（Element层次），一个对应于定义对元素的操作的访问者（Visitor层次）。给访问者增加一个新的子类即可创建一个新的操作。

1. ObjectStructure：它能够枚举所有Element元素，提供一个高层的接口以允许访问者访问它的元素；
2. Visitor：为对象结构中的每一个类申明一个visit操作；
3. ConcreteVisitor：实现Visitor的操作；
4. Element：定义一个Accept操作，它以一个访问者为参数；
5. ConcreteElement：实现Accepte操作。


*Collaborations*

1. 一个使用Visitor模式的客户必须创建一个ConcreteVisitor对象，然后遍历对象结构ObjectSture，并用该访问者访问每一个元素；
2. 当一个元素被访问时，它调用对应于它的类的visitor操作。该元素可以将自身作为这个操作的一个参数以便访问者访问它的状态。

{{% figure class="center" src="/images/oodesign/oodp-visitor-2.png" alt="访问者模式交互图" title="访问者模式交互图" width="600px" %}}

*Consequences*

1. 优点1：访问者模式使得易于增加新的操作。只要增加一个新的访问者就可以在一个对象结构上定义一个新的操作。而如果每个功能都分散在多个类上的化，定义新的操作时必需修改每一个类；
2. 优点2：访问者计中相关操作并分离无关操作。相关的行为不是分布在定义对象结构的各个类上，而是计中在一个访问者中。无关的行为被分别放在它们各自的访问者子类中；
3. 缺点1：增加新的ConcreteElement变地很困难。每添加一个新的ConcreteElement都要在Visitor抽象类中增加一个访问操作，并且每一个ConcreteVisitor都要实现该操作。在使用访问者模式前需要考虑系统哪个部分会经常变化，如果是对象结构中的各个类，那么不适用访问者模式，可以直接在类中定义相关的操作；如果是作用于这些类上的算法，则可以适用于访问者模式；
4. 缺点2：访问者模式要求元素提供接口访问其内部状态，这可能会破坏它的封装性。

下面我们看一个具体的例子:

我们有一个账本Account(相当于一个对象结构)，账本里面有很多交易Transaction（相当于Element）。交易的种类不会变化，只有两种，分别是收入交易IncomeTransaction（相当于一种ConcreteElement）和支出交易PaymentTransaction（也是一种ConcreteElement）；

这个系统有多个用户User（相当于Visitor），每个用户都想按照自己的业务骆逻辑来使用账本。比如，我们有一个审计用户AuditUser（相当于ConcreteVisitor），它只关心交易中是否涉及黑名单客户；再比如，一个人力资源用户HrUser（相当于ConcreteVisitor），它关心的是每个月发给员工的薪水有多少。

下面我们看具体代码：
```java
public interface Transaction {
    void accept(User visitor);
}

public class IncomeTransaction implements Transaction {

    private String from;
    private String to;
    private BigDecimal amount;

    // 构造函数 和 get/set函数省略

    @Override
    public void accept(User visitor){
        visitor.process( this);
    }
}
```

Transaction接口定义了处理每一个对象结构中的类的方法accept，每一个对象结构中的类都是实现了Transaction接口的类，都需要实现这个accept，accept方法会调用visitor的process方法。
上面给出了IncomeTransaction的实现，PaymentTransaction类似，就不赘述。

```java
public interface User {

    void process(IncomeTransaction tran);
    void process(PaymentTransaction tran);
}
```

User是Visitor类层次的顶层接口。每一个Visitor都实现User。每个ConcreteElement都在User里面有一个对应的处理方法，下面我们实现以下AuditUser和HrUser。

```java
public class AuditUser implements User{

    private Set<String> restrictedParties;
    private List<String> hitList; // 省略 getHitList方法

    public AuditUser(Set<String> restrictedParties){
        thid.restrictedPartries = restrictedParties;
    }

    @Override
    private void process(IncomeTransaction tran){
        if( restrictedParties.contains( tran.getFrom())){
            hitList.add( tran.getFrom());
        }
        if( restrictedParties.contains( tran.getTo())){
            hitList.add( tran.getTo());
        }
    }

    @Override
    private void process(PaymentTransaction tran){
        if( restrictedParties.contains( tran.getFrom())){
            hitList.add( tran.getFrom());
        }
        if( restrictedParties.contains( tran.getTo())){
            hitList.add( tran.getTo());
        }
    }
}

public class HrUser implements User{

    private Set<String> employees; 
    private BigDecimal totalAmount = BigDecimal.ZERO; // 省略get方法

    public HrUser( Set<String> employees){
        this.employees = employees;
    }
    
    @Override
    private void process(IncomeTransaction tran){
        // HR不关心公司收入的钱，这里什么都不做。
    }

    @Override
    private void process(PaymentTransaction tran){
        if( employees.contains( tran.getTo())){ // 仅计算支付给员工的钱
            totalAmount = totalAmount.add( tran.getAmount());
        }
    }
}

public class Account {
    // 交易列表
    private List<Transaction> transactions = new ArrayList<Transaction>();

    public void addTransaction( Transaction transaction){
        transactions.add( transaction);
    }

    public void visit(User visitor){
        for(Transaction tran : transactions){
            tran.accept( visitor);
        }
    }
}
```

Account是一个对象结构，它存有对所有Transaction的引用，它也提供一个高层的方法visit，对所有Transaction进行遍历。

### **模板方法模式**

*Motivation*

我们通过Head First里面的一个例子来了解下模板方法是怎么产生的。假设我们有两个类分别用来准备咖啡和茶，类的实现如下：
```java
public class Coffee {
    void prepareRecipe(){
        // 准备咖啡依次涉及四个步骤（方法）。具体方法省略。
        boilWater();        // 1. 准备开水
        brewCoffeeGrinds(); // 2. 用沸水冲泡咖啡
        pourInCup();        // 3. 倒入杯子
        addSugarAndMilk();  // 4. 假如糖和牛奶
    }
}

public class Tea {
    void prepareRecipe(){
        // 准备茶依次涉及四个步骤（方法）。具体方法省略。
        boilWater();   // 1. 准备开水
        steepTeaBag(); // 2. 用沸水浸泡茶叶
        pourInCup();   // 3. 倒入杯子
        addLemon();    // 4. 添加柠檬
    }
}
```

准备咖啡和茶的第一步和第三部是一样的，我们可以提取一个抽象类出来。抽象类实现公共的方法（子类可以选择覆盖或者不覆盖），并将非公共的方法作为抽象方法，由子类去实现。
```java
public abstract class Beverage {
    
    final void prepare(){ // 模板方法定义为final不允许子类覆盖
        boilWater();      // 1. 准备开水
        brew();           // 2. 冲泡
        pourInCup();      // 3. 倒入杯子
        addCondiments();  // 4. 添加调料
    }

    abstract void brew();          // 抽象方法：冲泡方法由子类实现，而且必需实现
    
    void addCondiments(){};        // 钩子方法：添加调料方法子类可以选择实现或不实现，默认为空。

    final void boilWater(){ 
        System.out.println(“Boiling water…”); // 具体方法：默认的烧水方法，且不让子类覆盖
    }

    void pourInCup(){ 
        System.out.println(“Pouring into cup…”)； // 具体方法：默认的倒入杯子的方法，允许子类覆盖
    }
}
```

重新设计一下咖啡和茶的类：
```java
public Coffee extends Beverage {
    
    @Override
    public void brew() { System.out.println(“Dripping Coffee through filter.”); }

    @Override
    public void addCondiments(){System.out.println(“Adding sugar and milk.”);}
}

public Tea extends Beverage {
    
    @Override
    public void brew() { System.out.println(“Steeping the tea.”); }

    @Override
    public void addCondiments(){System.out.println(“Adding lemon.”);}
}
```

抽象类中的prepare即为模板方法，它被声明为final，表示子类不能覆盖它。prepare中调用了抽象类中的几种类型的方法，分别代表模板中的各种步骤：

- 抽象方法：子类必需提供实现；
- 空的具体方法（即钩子方法）：这是模板中可选的步骤，子类可以不提供实现，也可以提供它定制的实现，也可以让子类对模板中已经发生的步骤或将要发生的步骤做出响应。
- 具体方法：这是模板中的默认实现，如果不希望子类覆盖，可以声明为final；子类可以直接继承该方法，不做修改，也可以修改非final的默认方法。

*Definition*

> 模板方法模式在一个方法中定义一个算法的骨架，而将一些步骤延迟到子类中。模板方法使得子类可以在不改变算法结构的情况下，重新定义算法的某些步骤。

这个模式创建了一个算法模板，模板就是一个方法。这个方法定义了一组步骤，任何步骤都可以是抽象的，由子类负责实现。这确保算法结构不变，同时由子类提供部分实现。

*Applicability*

1. 一次性实现算法的不变部分，并将可变的行为留给子类来实现；
2. 各自类中公共的行为应被提取出来并几种到一个公共父类中以避免代码重复；
3. 控制子类的扩展。通过钩子方法等扩展点进行控制。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-template-1.png" alt="模板方法模式UML" title="模板方法模式UML" width="600px" %}}

*Participants*

1. AbstractClass: 定义抽象的步骤（基本操作），由子类来实现其中的一部分操作；定义一个模板方法（一个算法骨架），该方法调用各个步骤；
2. ConcreteClass: 实现抽象类中定义的各个步骤。

*Collaborations*

ConcreteClass依赖AbstractClass来实现算法中不变的步骤。

*Consequences*

1. 模板方法是一种代码复用的基本技术。模板方法拥有整个算法结构，并保护这个结构免受继承类的修改；同时，算法集中在一个地方便于修改；
2. 需要权衡模板方法中步骤的粒度。如果粒度太细，需要子类实现的方法太多；如果粒度太粗，又缺少弹性；
3. 模板方法实践了面向对象原则中的“好莱坞原则”，即“不要调用我们，我们会调用你”。底层组件将自己挂钩到系统上，但是高层组件会决定什么时候和怎样使用这些底层组件。

*模板方法模式 vs 策略模式*

1. 策略模式定义一个算法家族，这些算法实现一个公共接口，可以互相替换；
2. 模板方法定义一个算法大纲，由子类来定义其中一些步骤；
3. 策略模式使用组合，可以在运行时更换算法，更加有弹性；
4. 模板方法使用继承，将重复代码都提取到抽象类中，对整个算法有更好的控制。

### **状态模式**

*Motivation*

我们使用Head First中的例子来作为引子。这个场景是一个售卖糖果的机器。它的状态和状态间转换图如下所示：

{{% figure class="center" src="/images/oodesign/oodp-state-1.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

糖果机有四种状态：没有硬币、有硬币、售完、售出。

{{% figure class="center" src="/images/oodesign/oodp-state-2.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

下面我们用一些变量来代表这些状态：

{{% figure class="center" src="/images/oodesign/oodp-state-3.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

糖果机有四种行为，每种行为都会导致状态转换：插入硬币、弹出硬币、转动手柄、出售。

{{% figure class="center" src="/images/oodesign/oodp-state-4.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

我们需要为糖果机的这四种行为编写四个方法，每种方法有需要根据糖果机当前的状态做出正确的动作。比如下面是插入硬币的方法：

{{% figure class="center" src="/images/oodesign/oodp-state-5.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

糖果机类的框架如下：

{{% figure class="center" src="/images/oodesign/oodp-state-6.png" alt="状态模式例子" title="状态模式例子" width="300px" %}}

现在需求变更了：需要增加一个新的状态。我们先不管这个状态是什么有，但是要把一个新的状态放入到已有的状态转换图中，意味着要修改糖果机类：

1. 增加一个状态变量；
2. 每一个原有的方法都需要增加一个条件分支来处理新增加的状态；
3. 可能还需要增加新的方法来处理新增加的动作。

修改的代码数量可能随着状态的增加而不断增加。
为了解决这个问题，我们重新设计了老的糖果机。我们把所有的状态及其行为封装在一个单独的类中：

{{% figure class="center" src="/images/oodesign/oodp-state-7.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

我们来看其中一个状态类的实现：

{{% figure class="center" src="/images/oodesign/oodp-state-8.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

然后我们把糖果机中状态的表示由数值变量改为对象引用：

{{% figure class="center" src="/images/oodesign/oodp-state-9.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

最后我们来看下完整的糖果机。糖果机将每个动作都委托给了状态对象来处理：

{{% figure class="center" src="/images/oodesign/oodp-state-10.png" alt="状态模式例子" title="状态模式例子" width="600px" %}}

*Definition*

> 状态模式允许对象在内部状态改变时改变它的行为，对象看起来好像修改了它的类。

这个模式将状态封装为独立的类，并将动作委托到代表当前状态的对象（将行为局部化），因此行为会随着内部状态的改变而改变；

这个模式使用组合，通过引用不同的状态对象来造成对象看起来修改了类的假象；

*Applicability*

1. 当一个对象的行为取决于它的状态，且必需在运行时根据状态改变它的行为；
2. 一个操作中含有庞大的多分支条件语句，且这些分支依赖于该对象的状态。这个状态通常用一个或多个枚举常量表示。通常有多个操作包含这一相同的条件结构。State模式将每一个条件分支放入一个独立的类中。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-state-11.png" alt="状态模式UML" title="状态模式UML" width="600px" %}}

*Participants*

1. Context：维护一个ConcreteState的引用，这个引用就是Context当前状态；
2. State：定义一个接口以封装与Context的一个特定状态相关的行为；
3. ConcreteState: 每一个子类都实现一个与Context的一个状态相关的行为

*Collaborations*

1. Context将与状态相关的请求委托给当前的ConcreteState对象处理；
2. Context可将自身作为一个参数传递给处理该请求的状态对象；
3. 客户可以使用一个状态对象来配置一个Context，配置后客户不再需要直接与状态对象打交道了；
4. Context和ConcreteState都可以决定哪个状态是另外哪一个的后继者，以及何种条件下进行状态转换：当状态转换是固定的时候，适合放在Context中；如果状态转换是动态的，通常放在状态类中，这也会使状态对象之间产生依赖。

*Consequences*

1. 优点1：State对象可以被共享。如果State本省没有实例变量（状态完全由它们的类型决定，状态对象没有内部状态，只有行为），那么各个Context对象可以共享一个State对象；
2. 优点2：使状态转换显示化。如果不将状态封装到一个State对象里面，而是采用一些变量，并赋一些数值来表示状态的时候，状态转换是不明确的，也可能是不原子的。State对象的引入保证对象转换是原子操作（只需要重新保定一个不同的State对象，而无须为多个变量赋值），因此Context内部状态保证一致；
3. 优点3：将与特定状态相关的行为局部化，将不同状态的行为分割开来。所有与一个特定状态相关的行为都放入了一个对象中，通过定义新的子类可以很容易地增加新的状态和转换。
4. 缺点1：类的数目可能大幅增加。


*状态模式 vs 策略模式*

1. 状态模式和策略模式它们的结构图是一样的，但是它们的目的不一样；
2. 状态模式将一群行为封装在一个对象中。Context可以委托到任意一个状态对象中的任意一个。当前状态在状态对象集合中不断改变，以反映出Context内部的状态，而Context的行为也会随之改变。但是Context的客户基本上对于状态对象不了解；
3. 在策略模式中，客户通常需要显示地指定Context所要组合的策略对象是哪一个。虽然策略模式也是使用组合来使策略的指定具有弹性，但对于一个Context来说通常只有一个最适当的策略对象；
4. 一般来说我们把策略模式想成是除了继承之外的一种弹性替代方案；因为继承将对象的行为进行前期绑定，策略模式则可以通过组合来后期绑定；
5. 而我们把状态模式想成是不用在Context中放置很多条件判断的替代方案。可以在Context内简单地改变状态对象来改变context的行为。

### **命令模式**

*Motivation*

使用Head First里面的例子：我们有一个遥控器对象来控制许多第三方厂商提供的类，比如电视机、电风扇等。遥控器里面有很多对按钮，每对按钮分别表示开和关。
遥控器还提供一个撤销按钮，无论前面按了什么，撤销按钮都会undo前面的功能。第三方类暴露不同的接口，比如电视机有开、关方法，电风扇有关闭、快速、慢速方法等。

那么如何设计一个遥控器，使得它能够适配所有的第三方类，同时也能在新赠新的类的时候，不需要修改遥控器本身呢？（即解耦请求发出方和请求被执行方）

我们希望遥控器不依赖于具体的产品，而遥控器发出的命令可能会随着产品的变化而变化。那么我们将遥控器发出的请求都封装成一个对象——命令对象，让命令对象负责和产品交互。下面是命令对象的的接口，所有命令对象皆实现此接口:
```java
public interface Command {
    public void execute();
    public void undo();
}
```

我们来实现两个开、关灯的命令对象：
```java
public class LightOnCommand implements Command {
    Light light;
    public LightOnCommand(Light light) { this.light = light;}
    public void execute(){ light.on();}
    public void undo(){ light.off();}}

public class LightOffCommand implements Command {
    Light light;
    public LightOnCommand(Light light) { this.light = light;}
    public void execute(){ light.off();}
    public void undo(){ light.on();}}
```

电灯的undo操控相对简单，因为毕竟只有开、关两个动作。

电风扇有多个状态，关闭、快速、中速、慢速，那么我们需要在命令对象里面保留历史操作记录来支持撤销。我们下面演示单步撤销，当然也可以用一个数组来保存所有的操作历史，来支持多步撤销。

{{% figure class="center" src="/images/oodesign/oodp-command-1.png" alt="命令模式例子" title="命令模式例子" width="600px" %}}

最后还有一个空命令对象。遥控器在初始化的时候可能没有设定某一对按钮控制的具体产品，这时候有两种处理方法，一种实在遥控器中加入条件判断，另一种更优雅的做法是创建一个空命令对象，然后将遥控器的按钮动作默认指向这个空命令对象：

{{% figure class="center" src="/images/oodesign/oodp-command-2.png" alt="命令模式例子" title="命令模式例子" width="400px" %}}

现在我们可以来实现遥控器了。首先我们需要两个数组分别保存开、关命令按钮对，然后需要加入一个undo按钮，并初始化这些按钮到空命令对象：

{{% figure class="center" src="/images/oodesign/oodp-command-3.png" alt="命令模式例子" title="命令模式例子" width="500px" %}}

然后是按钮方法：

{{% figure class="center" src="/images/oodesign/oodp-command-4.png" alt="命令模式例子" title="命令模式例子" width="500px" %}}

现在当增加一个新的产品的时候，我们不需要修改遥控器类，只需要增加一个新的产品命令对象即可。
作为命令模式的扩展，我们可以将一组命令合并起来设计一个“宏命令”：

{{% figure class="center" src="/images/oodesign/oodp-command-5.png" alt="命令模式例子" title="命令模式例子" width="500px" %}}

*Definition*

> 命令模式将请求封装成对象，以便使用不同的请求、队列或者日志来参数化其它对象。命令模式也支持可撤销的操作；

命令模式将发出请求的对象和执行请求的对象解耦，被解耦的两者之间通过一个命令对象进行沟通。

命令模式将命令接收者和一个或一组动作封装进一个命令对象中，只对外暴露一个execute接口。调用者通过调用execute方法来发出请求，接收者的动作执行这个请求。

命令模式支持撤销操作，也支持用来实现队列处理、日志系统，也可以实现宏命令来将一组命令打包在一起执行。

*Applicability*

1. 需要在不同的时刻指定、队列化或者执行某些指令。一个命令对象可以和请求有不同的生存期。可以支持异步地执行命令。比如说我们可以支持生产者-消费者模式，一些线程往队列里添加命令对象，而另一些线程则负责获取一个对象，执行它，然后再获取下一个对象；
2. 支持取消操作，可以在Command执行execute方法的时候将状态保存起来，增加一个undo方法来进行回退；
3. 支持修改日志，可以在Command接口中增加一个load和一个store方法，将所有操作都存储下来用于恢复；
4. 用基于原语操作的高层操作来构建系统。这种结构在支持事务的信息系统中很常见。一个事务封装了对数据的一系列修改的动作。命令模式提供了对事务建模的一种方式。命令对象都有通用的接口，允许使用相同的方式进行调用。同时命令模式也可以使增加新的事务变地非常方便。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-command-6.png" alt="命令模式UML" title="命令模式UML" width="500px" %}}


*Participants*

1. Command：申明一个用于执行操作的接口execute()；
2. ConcreteCommand: 将一个Receiver和一组动作绑定到一起；通过调用Receiver上响应的操作来实现execute()接口；
3. Client：创建一个ConcreteCommand并且设定它的Receiver
4. Invoker: 要求Command执行某一请求；
5. Receiver：知道如何执行某一请求的操作。


*Collaborations*

下图显示了各个对象之间的交互过程，以及Command和Invoker是如何解耦的。

{{% figure class="center" src="/images/oodesign/oodp-command-7.png" alt="命令模式交互图" title="命令模式交互图" width="500px" %}}



1. Client创建一个ConcreteCommand对象，然后设定它的Receiver;
2. Invoke对象保存了一个ConcreteCommand对象，以便在需要的时候调用；
3. Invoke通过调用execute方法将请求发送给命令对象。当命令对象是支持撤销的时候，它会在调用execute之前储存它的状态；
4. ConcreteCommand对象最后调用receiver上的操作来执行请求。

*Consequences*

1. 命令模式将发出命令的一方和执行命令的一方解耦；
2. Command对象是First-class object，意味着它们可以被像其它类一样操作和扩展；
3. 可以将Command组合起来形成一个复合Command，比如前面提到的MacroCommand；
4. 添加新的Command非常容易。

### **责任链模式**

*Motivation*

我们使用GoF中的例子。在一个图形用户界面系统中，用户希望点击系统的任意部分来获取帮助。所提供的帮助依赖于点击的是哪一部分及其上下文。例如对话框中的按钮可能和主界面上的按钮不同。

如果对话框中的按钮没有帮助信息，那么使用它的外层容器，比如对话框本身的帮助信息。

因此我们需要按照帮助信息的普遍性，从最特定的帮助信息到最普遍的帮助信息，来排序。如下图所示，当打印按钮可以显示帮助信息的时候，它就自己处理，当它没有相关帮助信息的时候，就将帮助请求委托给打印对话框。然后一次类推，直到最外层的（即最普遍的）组件处理。

{{% figure class="center" src="/images/oodesign/oodp-cor-1.png" alt="责任链模式例子" title="责任链模式例子" width="500px" %}}

在刚才的例子中，aPrintButton转发给aPrintDialog，最后转发给anApplication。如下图所示：

{{% figure class="center" src="/images/oodesign/oodp-cor-2.png" alt="责任链模式例子" title="责任链模式例子" width="500px" %}}

事实上每个对象都可以选择处理请求、忽略请求或转发请求；提交请求的而客户并不直接和最终处理请求的对象打交道。

每个处理请求的类都要实现通用的处理请求的方法，以及一致的访问链上后继者的方法。如下图所示，每个组件，不论是Application还是Widget都实现了HelpHandler接口，并且每个类的handleHelp方法都尝试处理请求，如果不能处理请求就转交给父类处理：

{{% figure class="center" src="/images/oodesign/oodp-cor-3.png" alt="责任链模式例子" title="责任链模式例子" width="500px" %}}

*Definition*

> 使多个对象都有机会处理请求，从而避免请求的发送者和接收者之间的耦合关系。责任链模式将这些希望处理请求的对象链接成一条链，并沿着这条链传递请求，直到有一个对象处理请求为止。

*Applicability*

1. 当有多个对象可以处理请求时，应该由哪个对象处理需要在运行时自动确定；
2. 希望在不明确处理者的前提下，向多个对象中的而一个提交请求；
3. 当可以处理请求的对象集应该被动态指定的时候。

*Structure* 

{{% figure class="center" src="/images/oodesign/oodp-cor-4.png" alt="责任链模式UML" title="责任链模式UML" width="500px" %}}

*Participants*

1. Handler: 定义一个处理请求的接口；实现继承链；
2. ConcreteHandler: 处理自身所负责的请求，将不能处理的交给它的后继者；
3. Client：向责任链中的一个ConcreteHandler发起请求。

*Collaborations*

当一个Client发起一个请求的时候，请求随着责任链传递，直到一个ConcreteHandler负责处理它。

*Consequences*

1. 解耦。责任链模式使得对象无需知道哪个对象会处理它的请求。它只需要知道它的请求会被正确处理。请求者和执行者都不知道对方，并且责任链中的一个对象不需要知道整个责任链的结构；
2. 增强了给对象指派职责的灵活性。可以在运行时动态添加处理一个请求的对象，或者修改责任链。可以将这种动态的灵活性与静态的继承责任对象的技巧相结合；
3. 不保证请求一定被处理。因为请求没有显示的接收者。当责任链结束但是没有对象处理请求时，或者责任链构造不正确的时候，可能会无法正确处理请求。


### **中介者模式**

*Motivation*

考虑一个图形用户界面（GoF例子）。界面上有很多组件，比如下拉框，文本框，复选框、列表和按钮。
下拉框的选择会触发文本框内容的变化和按钮是否可用，复选框的选择会触发下拉框列表的变化等等。
界面上的各个组件互相依赖。在最糟糕的情况下，每一个对象都需要与其他全部对象进行交互。

我们可以将这些交互的行为封装在一个单独的称为中介者Mediator的对象中。中介者负责控制和协调一组对象之间的交互。
中介者对象使得所有的组件不需要显示地调用别的组件，每个组件只需要知道中介者，减少了互相的引用。

比如我们可以设计一个如下的类结构模式：aFontDialogDirector作为列表，按钮等组件的中介者：

{{% figure class="center" src="/images/oodesign/oodp-mediator-1.png" alt="中介者模式例子" title="中介者模式例子" width="500px" %}}

对象之间的交互如下所示：
{{% figure class="center" src="/images/oodesign/oodp-mediator-2.png" alt="中介者模式例子" title="中介者模式例子" width="500px" %}}

1. 列表框通知中介者它发生了变化；
2. 中介者获取列表框的内容；
3. 中介者将获取到的内容发送给一个EntryField组件。

*Definition*

> 用一个对象来封装一系列对象的交互。中介对象使得各个对象不需要显示地互相引用，从而减少它们的耦合，而且可以独立地改变它们的交互。

*Applicability*

1. 一组对象以定义良好但是复杂的方式进行通信。产生的相互依赖关系混乱且难以解耦；
2. 一个对象引用其它很多对象，并且直接与这些对象通信，导致难以复用该对象；
3. 想要定制一个分布在多个类中的行为，而又不想生成太多的子类。


*Structure*

{{% figure class="center" src="/images/oodesign/oodp-mediator-3.png" alt="中介者模式UML" title="中介者模式UML" width="500px" %}}

一个典型的中介者模式的类图如下：

{{% figure class="center" src="/images/oodesign/oodp-mediator-4.png" alt="中介者模式例子" title="中介者模式例子" width="500px" %}}

*Participants*

1. Mediator:中介者定义一个接口与各Colleague对象通信；
2. ConcreteMediator: 了解并维护它的各个Colleague，通过协调各个Colleague对象实现协作行为
3. Colleague class:每一个Colleague对象知道它的中介者对象，并且在需要与其它Colleague对象通信的时候与中介者通信。

*Collaborations*

Colleague向中介者对象发送和接受请求。中介者在各个Colleague之间恰当地转发请求以实现写作行为。

*Consequences*

1. 减少了子类的生成。中介者将原本分布于多个对象间的行为集中到一起，改变这些行为只需要继承中介者类就可以。这样Colleague类可以被重用；
2. 将各个Colleague解耦。可以独立改变和复用各个Colleague和Mediator；
3. 简化对象协议。使用Mediator和Colleague之间一对多的交互协议来代替原来一大堆Colleague之间多对多的协议。一对多的关系更容易理解、维护和扩展；
4. 将对象间如何协作进行了抽象。将对象本身的行为和它们之间交互的行为区分开，将后者作为一个独立的概念封装在一个对象中。有助于理清一个系统中对象的交互；
5. 使控制集中化。将交互的复杂性改为了中介者的复杂性。中介者本身可能会变地复杂难以维护。

*Implementation*

忽略抽象的Mediator类。如果Colleague只需要和一个Mediator交互，那么就没有不要提供抽象Mediator类。Colleague-Mediator通信方式：

1. 使用观察者模式将Mediator实现为一个Observer，Colleague实现为Subject。当事件发生时向Mediator发送通知。Mediator向其它Colleague传递事件带来的影响；
2. 或者在Mediator中定义一个通知接口，Colleague在需要通信时直接调用该接口。

### **迭代器模式**

*Definition*

> 提供一种顺序地访问一个聚合对象内的元素并且不暴露该聚合对象底层结构的方法。

*Applicability*

1. 用来访问一个聚合对象的内容而无须暴露它的内部表示；
2. 支持对聚合对象的多种遍历；
3. 为遍历不同的聚合结构提供一个统一的接口。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-iterator-1.png" alt="迭代器模式UML" title="迭代器模式UML" width="500px" %}}

*Participants*

1. Iterator: 定义遍历元素的接口；
2. ConcreteIterator: 实现迭代器接口，对聚合遍历时跟踪位置；
3. Aggregate: 定义创建相应迭代器的接口；
4. ConcreteAggregate: 实现创建迭代器的接口，该接口放回一个ConcreteIterator对象。

*Collaborations*

1. ConcreteIterator跟踪聚合中的当前对象，并能够计算出待遍历的后继对象。

*Consequences*

1. 支持以不同的方式遍历一个集合，只需要自定义迭代器子类即可
2. 简化了聚合的接口。聚合本身无须类似的遍历接口；
3. 可以同时进行多个遍历，每个迭代器保留自身的状态。

*Implementation*

1. 由谁控制迭代？由客户控制迭代时，客户必需主动推进遍历的步伐，显示地向迭代器请求下一个元素，这称为外部迭代器；由迭代器控制迭代时，客户只需要提交一个待执行的操作，而迭代器将对集合的每一个元素实施给操作，这称为内部迭代器；
2. 谁定义遍历算法？可能由聚合类自身控制，迭代器只是储存了一个遍历的状态，这种迭代器称为游标(cursor)；也可能由迭代器自己控制遍历算法，这样可以方便指定不同的遍历算法，以及在不同的集合上复用遍历算法，但是可能不方便访问集合私有域；
3. 迭代器的健壮性如何？当遍历时修改集合内容时可能会带来问题。比如Java在集合上遍历的时候，如果出现并发修改，可能会抛出ConcurrentModificationException；
4. 迭代器有哪些操作？基本的迭代器操作有first, next, hasNext等…

### **备忘录模式**

*Definition*

> 在不破坏封装性的前提下，捕获一个对象的内部状态，并在对象之外保存该对象。之后可以将对象恢复到保存时的状态。

*Applicability*

1. 当一个对象需要恢复到它以前的某个时刻的状态，该对象的需要保存一份它的（一部分）状态的快照；
2. 当提供一个接口来访问对象的内部状态会破坏对象的封装性的时候。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-memento-1.png" alt="备忘录模式UML" title="备忘录模式UML" width="500px" %}}

*Participants*

1. Originator: 创建备忘录用来记录它当前内部状态；使用备忘录来恢复某一时刻的状态 ；
2. Memento: 
  - 存储Originator内部状态，由Originator决定哪些状态存储到Memento；
  - 防止除Originator以外的对象访问备忘录。通过两个接口实现：
3. Caretaker只能看到窄接口，它只能将备忘录传递给其他对象；
4. Originator可以看到宽接口，允许它读取备忘录里面全部数据。理想情况下，只允许生成本Memento的Originator对象访问。
5. Caretaker：负责保存备忘录，但不能对备忘录内容进行操作或检查。

*Collaborations*

1. Caretaker向Originator请求一个备忘录，Originator新建一个Mememto对象，将自身的状态保存其中；
2. Caretaker持有一段时间的Mememto对象然后传递回Originator，如下图：

{{% figure class="center" src="/images/oodesign/oodp-memento-2.png" alt="备忘录模式交互图" title="备忘录模式交互图" width="500px" %}}

*Consequences*

1. 保持封装边界。备忘录模式可以避免暴露一些只应由Originator管理却又必须储存在Originator以外的信息；
2. 简化了Originator。备忘录模式允许客户管理Originator的状态，使得客户在工作结束时无需通知Originator；
3. 在一些语言中可能难以保证只有Originator可以访问备忘录；
4. 使用备忘录可能代价很高。如果Originator在生成备忘录的时候需要存储大量信息，或者非常频繁地生成备忘录，可能会导致很大的开销。如果生成备忘录和恢复开销很大，这个模式可能不适用；
5. Caretaker复杂删除它所维护的备忘录，但是它不知道备忘录中有多少状态。因此可能会产生很多存储开销。

下面是一个例子：

```java
public class Originator3 {

    String state;

    public Originator3(String state) { this.state = state; }

    public String toString() { return "State: " + state;}

    public void setState(String state) { this.state = state;}

    public Memento save() {
        return new Memento(state);
    }

    public void restore(Object refMemento) {
        Memento memento = (Memento) refMemento;
       this.state = memento.state;
    }

    private class Memento {
        String state;
        public Memento(String state) {
            this.state = state;
        }
    }
}

public class Caretaker {

    Object mememto;

    public void saveState(Originator originator) {
        mememto = originator.save();
    }

    public void restoreState(Originator originator) {
        originator.restore(mememto);
    }
}

public class MementoDemo {
    public static void main(String[] args) {

    Caretaker3 caretaker = new Caretaker3();
    Originator3 originator = new Originator3("1");
    System.out.println("初始状态：" + originator);

    originator.setState("2");
    System.out.println("状态修改" + originator);

    caretaker.saveState(originator);
    System.out.println("保存状态" + originator);

    originator.setState("3");
    System.out.println("状态修改" + originator);

    caretaker.restoreState(originator);
    System.out.println("恢复状态" + originator);
    }
}
```

输出结果如下：
```text
初始状态：State: 1
状态修改State: 2
保存状态State: 2
状态修改State: 3
恢复状态State: 2
```
### **解释器模式**

*Definition*

> 给定一个语言，定义它的语法表示，并定义一个解释器来解释这个语言中的句子。

*Applicability*

1. 当有一个语言需要解释执行，并且可以把给语言的句子表示为一个抽象语法树（AST）时，同时满足以下条件：
2. 语法比较简单。复杂的语法可能更适用于parser generator, 它们可以在不构建AST的前提下解释表达式，这样可以节省空间以及时间；
3. 效率不是首要考虑的因素。

*Structure*

{{% figure class="center" src="/images/oodesign/oodp-interpret-1.png" alt="解释器模式UML" title="解释器模式UML" width="500px" %}}

*Participants*

1. AbstarctExpression: 申明一个语法树中所有节点所共享的抽象的解释操作；
2. TerminalExpression: 实现语法中终止性符号的解释操作，每个终止性符号都需要一个实例；
3. NonterminalExpression: 每条语法规则都需要一个此类；
4. Context:包含解释器之外的全局信息；
5. Client: 构建语法所定义的某个特定语句的AST。AST由TerminalExpression以及NonterminalExpression组成；以及调用解释操作。

*Collaborations*

1. Client构建一个由TerminalExpression和NonterminalExpression组成的抽象语法树(AST)，然后初始化上下文并调用解释操作；
2. 每一个NonterminalExpression节点的解释由子表达式节点的解释定义；
3. TerminalExpression节点的解释操作定义了递归的base case；
4. 每一个节点的解释操作用上下文来存储和访问解释器的状态。

*Consequences*

1. 扩展和改变语法比较简单；
2. 实现语法也较为简单；
3. 复杂语法不易维护。



