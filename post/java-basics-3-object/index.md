Java中每个类都是继承自Object，如果一个类没有显示地指明父类，Object就是它的父类。除了基本类型外，对象、对象数组、基本类型数组都是继承自Object类。本文主要介绍Object的方法。

# equals方法

Object的equals方法使用两个对象的地址是否相同来判断对象是否等价。如果子类没有覆盖equals
方法，那么它也将如此判断，但很多时候我们希望通过对象的状态，即私有数据域中的数据，来判断两个对象是否相同。

Java语言规范要求equals方法具有以下方面特性：

- **自反性**。对于任何非空的x，x.equals(x)返回true;
- **对称性**。对于任何引用x和y。当且仅当x.equals(y)返回true，y.equals(x)也应该返回true;
- **传递性**。对于任何引用x、y 和z。如果x.equals(y)返回true，y.equals(z)返回true，那么x.equals(z)也应该返回true;
- **一致性**。如果x和y引用的对象没有发生变化，反复调用x.equals(y)应该返回一样的结果;
- 对于任何非空引用x。x.equals(null) 应该返回false。

<!--more-->

下面以Employee及其子类Manager为例，展示`equals`方法的重写方法：

```java
class Employee{

    private String id;
    private String name;
    private double salary;

    @Override
    public boolean equals(Object other){

        // 地址都相同的， 说明两个引用肯定指向同一个对象
        if( this == other) return true;

        // 如果参数对象为空， 返回false
        if( other == null) return false;

        // 如果类信息不匹配， 返回false
        if( getClass() != other.getClass()) return false;

        // 到这一步， 我们已经知道other 是一个非空的Employee 对象了
        Employee otherEmployee = (Employee)other;

        // 测试两个对象的域是否等价， 对象测试使用Objects.equals(a, b) 方法：
        // 如果两个参数都为null 返回true ， 如果其中一个为null 返回false ，
        // 如果都不为null ， 则调用a.equals(b)
        return Objects.equals(name , otherEmployee.name)
               && salary == otherEmployee.salary
               && Objects.equals(id, otherEmployee.id);
    }
}

class Manager extends Employee{

    private double bonus; // 经理有年终奖

    @Override
    public boolean equals(Object other){

        // 首先调用父类的equals方法，如果相等再判断子类的数据域。
        if( !super.equals( other)) return false;

        // 父类已经检查过， 两个对象类信息相同， 即都是Manager
        Manager otherManager = (Manager)other;

        return bonus == otherManager.bonus;
    }
}
```

上述的代码中，我们比较两个对象的类型是否一致的时候使用了`getClass()`方法，另一种方法是使用`instanceof`来比较：

```java
if( !(other instanceof Employee)) return false
```

这两种方法都有自己的缺点：

1. 使用`instanceof`的方式会违反上面的对称性。
当执行manager.equals(employee)的时候，由于Manger是Employee的子类，上述的代码不会返回false；
但是反过来执行employee.equals(manager)的时候，上述代码一定返回false。

2. 而使用`getClass()`的方式在匿名内部类中会返回false。因为匿名内部类的每个自动生成的类名都不相同。比如下面一个例子，我们创建了a和b两个继承ArrayList的匿名内部类。

    ```java
    public class Test20180601 {

        public static void main(String[] args) {
            
            List<String> c = new ArrayList<String>();
            c.add("A");
            c.add("B");
            
            List<String> a = new ArrayList<String>(){

                private static final long serialVersionUID = 1L;

                {
                    add("A"); 
                    add("B"); 
                }
            };
            
            List<String> b = new ArrayList<String>(){

                private static final long serialVersionUID = 1L;

                {
                    add("A"); 
                    add("B"); 
                }
            };
            
            System.out.println(a.getClass().getName());
            System.out.println(b.getClass().getName());
            System.out.println(c.getClass().getName());
            System.out.println(a.equals(b));
            System.out.println(a.equals(c));
            System.out.println(b.equals(c));
        }
    }
    ```

    上述代码会输出
    ```text
    Test20180601$1
    Test20180601$2
    java.util.ArrayList
    true
    true
    true
    ```

    可见a和b的类型不相同，它们与父类ArrayList也不是一个类型。因此采用`getClass`的equals计算在此场景下会返回false。
    
    但是我们看到a、b和c的互相equals结果都是true，这是因为我们没有重写a和b的equals方法，它们用了ArrayList的equals方法，而ArrayList同样没有重写，最终用的是AbstractList里面的equals方法，它的代码如下：

    ```java
    public boolean equals( Object c ){

        if( o == this) return true;
        if( !( o instaceof List)) return false;

        ListIterator<E> e1 = listIterator();
        ListIterator<E> e2 = ((List<?>) o).listIterator();
        while( e1.hasNext() && e2.hasNext()){
            E o1 = e1.next();
            Object o2 = e2.next();
            if( !( o1 == null ? o2 == null : o1.equals( o2))) return false;
        }

        return !( e1.hasNex() || e2.hasNext());
    }
    ```
    
    所以只要a、b和c都是继承自List，并且内部元素一样，它们都是“相等的”。我们会在内部类章节中再详细讨论内部类的问题。

那么应该用哪种方式来比较类型呢？如果对于Employee及其所有派生类的比较仅仅基于Employee类中的私有域，比如我们只通过id来比
较，那么我们可以使用instanceof来实现，比如上面ArrayList的例子。同时，可以把Employee的equals申明为final，防止子类覆盖（ArrayList没有采取这种做法）。
如果相反，我们比较两个对象时候需要考虑派生类的私有域，那么instanceof就是一种不合适的实现方式，而应该使用getClass()。

通过上述例子，我们总结出equals的编写步骤：

1. 给参数取名为other的一个Object对象，之后需要转换为当前对象的类。
2. 比较两个变量this和other是否引用了同一个对象。
3. 检测other是否null，null 则返回false（使用instanceof可以不加此检查，因为`null instanceof Class`返回false）。
4. 比较this和other是否同属一个类。如果equals语义在每个子类中有所改变，就使用getClass()来判断，如果每个子类中都使用同一的语义，就是用instanceof来检测。
5. 将other转换为当前类类型变量。
6. 对所有需要比较的域进行比较。基本数据类型用==，使用Objects.equals比较对象域。
7. 如果子类中重新定义了equals，就要在其中包含调用了super.equals(other)。

对于数组类型的域，可以使用`Arrays.equals(type[] a, type[] b)`方法来检测。该方法首先检测两个数组长
度是否相同，再检测对应位置上的元素是否也相同。

# hasCode方法

所有对象都继承了Object类的hashCode方法。每个对象都有一个默认的散列码，其值为对象的内存地址。

为了使用Hash类容器，比如HashMap，必须重新定义自己创建的类的hashCode和equals方法。
虽然hashCode的设计需要让对象产生的散列码尽可能均匀分布，尽可能执行速度快，但是不同的对象的hashCode有可能会返回同样的结果，
但是equals方法总是能够严格地区分两个不同的对象。

HashMap判断对象是否已经存在时，先是使用对象的hash值来找到对象的位置，然后对于同一个位置的所有元
素，调用equals找出是否存在完全一致的对象。如果hashCode没有重写，两个逻辑上相同的对象可能就
会因为内存地址不同而被放到不同的位置作为不同的对象来对待；如果equals没有被重写，两个逻辑上相同的对象可能会被
当作两个不同对象处理。因此，equals和hashCode的定义必须一致，如果x.equals(y)返回true，那么
x.hashCode()必须与y.hashCode()具有相同的值。

`Thinking in Java`中给出的一种hashCode重写的指导方案：

1. 给初始的int类型的结果变量result赋一个非零素数常量，比如17；
2. 对对象内每一个需要考虑的私有域（和equals一样）f，计算出一个int类型的散列值c，计算方法如下：

    ```text
    boolean                 c = ( f ? 0 : 1)
    byte, char, short, int  c = ( int ) f
    long                    c = ( int )( f ^ (f >> 32))
    float                   c = Float.floatToIntBits( f )
    double                  long l = Double.doubleToLongBits( f ) 
                            c = ( int )( l ^ ( l >> 32 ) )
    Object                  c = f.hashCode()
    数组                    Arrays.hashCode(type[] a)
    ```
3. 合并计算得到的散列码 result = result * 37 + c;
4. 返回result。

比如Employee类的hashCode可以写成

```java
@Override
public int hashCode(){
    int result = 11;
    result = result * 17 + name.hashCode();
    result = result * 17 + new Integer(id).hashCode();
    result = result * 17 + new Double(salary).hashCode();
    return result;
}
```

在Java7中可以做如下改进：首先空对象的hashCode处理：
```java
@Override
Public int hashCode(){
    Int result = 11;
    result = result * 17 + Objects.hashCode(name);
    result = result * 17 + new Integer(id).hashCode();
    result = result * 17 + new Double(salary).hashCode();
    return result;
}
```

其次可以简化：

```java
@Override
Public int hashCode(){
    Return Objects.hash(id, name , salary);
}
```

这个方法等价于调用Arrays.hashCode()，把所有要处理的元素都放到一个数组里，计算hash 值。

# toString方法

Object类的toString默认打印对象的类名和散列码。比如
```java
System.out.println( new Object() ); 
```
可能会给出java.lang.Object@c17164。

当需要用到x对象的toString方法的时候，建议使用x + ""的方式，这样即使x为空或者x为基本类型都能处理。

自定义的类为了能够正确的打印出对象的内容，而不是其内存地址，需要重写Object类的toString()方法的实现。比如下面是Employee的实现：
```java
public String toString(){
    return getClass().getName() + “ [name= ” + name + “ ,salary= ” + salary + “ ,id= ” + id + “ ] ” ;
}
```

如果父类包含了getClass().getName()，子类在重写的时候只需要调用父类的toString 并加上自己需要打印的域就可以了：
```java
public String toString(){
    return super.toString() + “ [bonus= ” + bonus + “ ] ” ;
}
```

数组也继承了toString 方法，调用一下数组的toString 方法，比如
```java
int[] nums = 1, 2, 3; 
System.out.println( nums ); 
```
可能会打印出[I@1a46e30，这里[表示数组，I表示数组元素的类型是int。

如果要打印数组里面的元素，可以使用Arrays.toString(type[]) 来打印：
```java
int[] nums = {1, 2, 3};
System.out.println( Arrays.toString( nums));
```
上述代码会打印出[1, 2, 3]。

如果是多维数组，可以调用Arrays.deepToString() 方法:
```java
int[][] nums = {
    {1, 2, 3},
    {4, 5, 6}, 
    {7, 8, 9}
};
		
System.out.println( Arrays.deepToString( nums));
```
输出[[1, 2, 3], [4, 5, 6], [7, 8, 9]]。

# clone方法

clone方法在Object类里被申明为了protected，即只有Object所在包中的类，或者Object的子类可
以调用。但是注意，一个Object的子类不能调用别的Object子类的clone方法。换句话说，只有类自
己的代码中才能够克隆自己。

默认的clone方法是浅拷贝，即拷贝基本数据类型和引用，但是引用的对象仍旧只有一个。如果有私有
域引用了一个对象A，那么新克隆的对象和原对象都会引用A。只有在这个共享的对象A是不可变的情
况下，这么做才不会有问题，否则就应该使用深拷贝。

对于每一个对象，我们都要考虑以下三种情况：

1. 是否不应该使用 clone。（默认选择）
2. 默认的 clone 方法能否满足要求。（浅拷贝）
3. 默认的 clone 方法能否通过调用可变子对象的 clone 得到修补。（深拷贝）

对于后两者，我们都需要：

1. 实现Cloneable 接口。这是为了如果该类自身作为其它类的私有域参与到克隆中时，没有实现Cloneable
接口的类会导致Clone抛出异常。
2. 重写Clone，修改Clone修饰符为public。

这里 Clonebale 接口和 clone 方法并没有关系，接口并没有申明要实现该方法，这里接口只是一个标记，
如果一个对象需要克隆但是没有实现 Cloneable 接口就会产生一个已检查异常。


下面是 Employee 类的 clone 方法实现：
```java
// 提升可见性，其它类可以调用Employee的clone方法
@Override
public Employee clone() throws CloneNotSupportedException{
	// 调用Object的clone方法进行浅拷贝
	Employee cloned = (Employee)super.clone();
	// 深拷贝对象
	cloned.hireDat = (Date)hireDay.clone();
}
```

对于final的类，我们可以使用try...catch来处理异常，非final类还是抛出异常比较好。