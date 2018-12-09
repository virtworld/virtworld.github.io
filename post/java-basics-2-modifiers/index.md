# final数据、方法和类

## final数据

对基本类型使用final修饰词时，该基本类型在初始化后不能被修改；对对象引用使用final修饰词时，该引用被初始化后不能指向其他对象，但是所指向的对象本身仍旧是可变的。比如final数组引用，这个引用只能指向同一个数组，但是数组本身的元素却是可变的。

如果某个域被定义为final，则必须在定义处或者构造器中对其进行初始化。final只表示一旦被初始化，其值将不会改变，但不是说在编译期就能知道其值：我们可以使用随机函数初始化它。

一个既是static又是final 的变量只占据一段不能改变的内存：static表示只有一份，final表示常量。final数据一般出现在不可变的基本类型域或者不可变类的域，对于可变的类，使用final修饰某实例域容易造成混乱。

<!--more-->

## final方法与final类

子类不能覆盖父类的final方法，确保方法在继承后的行为保持不变。final类不能被继承，因此final类中的所有方法都隐式地被指定为final，但是这不影响final类中的域。

private方法隐式地表示为final方法，因为子类无法覆盖它。如果父类中有一个private方法A，并且子类也有一个签名相同的方法B，这并不是覆盖。覆盖只有在某方法是类的接口定义的一部分时才会出现，即能将一个对象向上转型为它的基本类型并调用相同的方法。如果某方法为private，则它不是类接口定义的一部分。继承类中签名相同的类并不是覆盖了父类的方法，只是生产了一个新的方法。

如果一个方法没有被覆盖并且很短，编译器就能对其优化成内联调用。比如getName()方法可以修改为对name域的引用。因此早起的Java中，为了避免动态绑定带来的开销，可能会使用final修饰方法。但是最新的即时编译器能够检测出一个很短、被频繁调用并且没有被真正覆盖的类，并对其进行内联。如果虚拟机之后又加载了一个覆盖了此方法的类，优化器会取消内联。所以在使用final时不需要考虑效率问题，应该交给JVM来处理。

# static域与static方法

静态域在一个类的所有实例中只有一个，所有对象共享这个域，常用于静态常量。静态方法没有this指针，不能操作对象的方法，但是可以访问自身类中的静态域。

在以下几种情况应考虑使用静态方法：

1. 方法不需要访问对象状态，所有的参数都通过显示参数提供，比如Math.sqrt;
2. 方法只需要访问类的静态域;
3. 作为工厂方法代替构造器来构建对象。这有两个特点，一是可以有多个不同名字的工厂方法来构建不同的对象，而类的构造器只能有一个和类相同的名字；二是，工厂方法不一定构建的是该类的对象，而类构造器必定构建的是该类的对象。

# Package

使用package和import的原因是确保类名的唯一性，将单一的全局名字空间分割开，同时提供便捷的访问，类似于c++的namespace和using指令。

在使用package的时候，就隐含地指定了目录结构。使用以下方法导入包中的类：

```java
import java.util.Date;
import java.util.*;
```

后者导入java.util包中所有的类，我们只能用\*来导入一个包中所有的类，但是不能用\*来导入所有的包。比如import java.\*就是不可以的。如果用\*导入的两个包都包含同一个类，在程序使用这个类的时
候就会报编译错误。这时候可以增加一个特定的 import 语句来解决这个问题比如：

```java
import java.sql.*;
import java.util.*;
import java.sql.Date;
```

上面的导入方式将使程序中的Date默认使用的是java.sql.Date。如果两个Date都要使用，那么就要用完整的名字来使用了java.util.Date或者java.sql.Date。

import还可以导入静态方法和域。静态方式导入类：

```java
import static java.lang.System.*;
```

这样我们就不必写System.out.println("xxx")而是可以直接写out.println("xxx")了。我们还可以导入特定的静态方法和域，比如我们想导入System中的域out：

```java
import static java.lang.System.out;
```


# 访问权限修饰符

一般我们将所有的域指定为private，除了该类的成员外，其他类都无法访问。

包权限是默认权限，如果没有加修饰符，那么默认类本身和该类所在的包中的所有类都能访问。相同目录下的所有不具有明确package声明的文件都被认为是该目录下默认包的一部分。

protected提供了包访问权限，并且对于所有继承的类也提供了访问权限。

public则给所有的类都提供了访问权限，也称为接口访问权限。

每一个编译单元（文件）都只能有一个public类，该类的名称必须与文件名相匹配，但是一个文件可以没有任何public类，这时可以随意命名文件。

类不可以是private或者protected的，除非它们是内部类。如果不希望任何人访问该类，可以把所有构造器指定为private。

访问权限控制通常被称为是**具体实现的隐藏**。把数据和方法包装进类中，加上这个具体实现的隐藏，被称为**封装**。封装的结果是带有特征和行为的数据类型。控制访问权限实现了：

1. 设定了客户端程序员可使用和不可使用的边界，清晰地区分哪些是客户端程序员需要知道的接口，哪些是他们不需要关心的实现；
2. 接口与实现的分离。类库设计者可以更改类的内部工作方式。

**警告**：父类中的protected方法只能被同一个包中的类或其子类访问。假设类A和类B在同一个包中，B有一个protected的方法b。

1. 如果类C继承类B，不管C是不是也在同一个包中，A总能访问C类的对象的方法b，因为A和B在同一个包中；
2. 如果类C继承类B，并且C和A、B不在同一个包中，则C类的对象仍能调用自身继承下来的b方法；如果此时有另一个类D同样继承了B，不论D在不在A、B所在包内，C都不能访问D类的b方法；
3. 如果类C不在A、B所在的包中，并且C类和B类没有继承关系，则C的对象不能调用B的对象的方法b，也不能调用任何继承了B的类的方法b。

下面有一个例子。

```java
package PackageA;
public class Base {
	protected void M(){}
}

package PackageA;
public class Ext3 extends Base {}

package PackageB;
import PackageA.Base;
public class Ext2 extends Base {}

package PackageA;
public class Ext4 extends Base{

	public Ext4(){
		Base ext1 = new PackageB.Ext1();
		Base ext2 = new PackageB.Ext2();
		Base ext3 = new PackageA.Ext3();
		ext3.M(); // OK to call M(), because Ext4 is in the same class with Base.
		ext1.M(); // OK to call M(), because Ext4 is in the same class with Base.
		ext2.M(); // OK to call M(), because Ext4 is in the same class with Base.
		this.M(); // OK to call M(), because Ext4 is in the same class with Base.
	}
}

package PackageB;
public class Ext1 extends PackageA.Base {

	public Ext1(){
		this.M(); // OK to call the object's own inherited method.
		PackageA.Base ext2 = new PackageB.Ext2();
		PackageA.Base ext3 = new PackageA.Ext3();
		//ext2.M(); ERROR. M is not in the package A, can only call its own inherted method.
		//ext3.M(); ERROR. M is not in the package A, can only call its own inherted method.
	}
}
```