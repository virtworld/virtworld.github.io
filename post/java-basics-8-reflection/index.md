# 反射概述

反射表示程序能够在运行时检查和修改自身结构和行为的能力。Java运行时为所有的对象维护一个运行时类型标志，这些被保存在Class对象中。Java的反射机制，可以让我们获取这些信息，分析类的能力，查看对象，调用任意方法等。

# Class 类

一个Class对象表示的是一个特定类型，注意这里不一定是指类的类型。我们可以使用多种方法来获取Class对象。

1. Object类中的`getClass()`方法动态获取类型。因为所有的对象都继承自Object类，因此所有的对象上都可以调用getClass() 来获得其类型信息；
2. 静态的`Class.forName(String)`方法。适用于将类名保存在字符串中，并可以在运行中改变的情况。因为参数必需是有效的类名，所以必需搭配一个已检查异常处理器使用；
3. T.class来静态的获取类型。比如`Date.class`，`Double[].class`，`int.class`。

我们可以使用==来判断两个对象的类型是否一致：

```java
if( e.getClass() == Employee.class)
```

我们可以使用Class对象上的newInstance()方法来快速创建一个类的实例。newInstance()方法调用类的默认构造器，如果没有默认构造器则会抛出异常。比如：

```java
e.getClass().newInstance();
```

<!--more-->

# 利用反射分析类的能力

下面程序可以帮助我们在运行时获取类的信息：

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.Scanner;

public class ReflectionTest
{
   public static void main(String[] args)
   {
      // read class name from command line args or user input
      String name;
      if (args.length > 0) name = args[0];
      else
      {
         Scanner in = new Scanner(System.in);
         System.out.println("Enter class name (e.g. java.util.Date): ");
         name = in.next();
      }

      try
      {
         // print class name and superclass name (if != Object)
         Class cl = Class.forName(name);
         Class supercl = cl.getSuperclass();
         String modifiers = Modifier.toString(cl.getModifiers());
         if (modifiers.length() > 0) System.out.print(modifiers + " ");
         System.out.print("class " + name);
         if (supercl != null && supercl != Object.class) System.out.print(" extends "
               + supercl.getName());

         System.out.print("\n{\n");
         printConstructors(cl);
         System.out.println();
         printMethods(cl);
         System.out.println();
         printFields(cl);
         System.out.println("}");
      }
      catch (ClassNotFoundException e)
      {
         e.printStackTrace();
      }
      System.exit(0);
   }

   /**
    * Prints all constructors of a class
    * @param cl a class
    */
   public static void printConstructors(Class cl)
   {
      Constructor[] constructors = cl.getDeclaredConstructors();

      for (Constructor c : constructors)
      {
         String name = c.getName();
         System.out.print("   ");
         String modifiers = Modifier.toString(c.getModifiers());
         if (modifiers.length() > 0) System.out.print(modifiers + " ");         
         System.out.print(name + "(");

         // print parameter types
         Class[] paramTypes = c.getParameterTypes();
         for (int j = 0; j < paramTypes.length; j++)
         {
            if (j > 0) System.out.print(", ");
            System.out.print(paramTypes[j].getName());
         }
         System.out.println(");");
      }
   }

   /**
    * Prints all methods of a class
    * @param cl a class
    */
   public static void printMethods(Class cl)
   {
      Method[] methods = cl.getDeclaredMethods();

      for (Method m : methods)
      {
         Class retType = m.getReturnType();
         String name = m.getName();

         System.out.print("   ");
         // print modifiers, return type and method name
         String modifiers = Modifier.toString(m.getModifiers());
         if (modifiers.length() > 0) System.out.print(modifiers + " ");         
         System.out.print(retType.getName() + " " + name + "(");

         // print parameter types
         Class[] paramTypes = m.getParameterTypes();
         for (int j = 0; j < paramTypes.length; j++)
         {
            if (j > 0) System.out.print(", ");
            System.out.print(paramTypes[j].getName());
         }
         System.out.println(");");
      }
   }

   /**
    * Prints all fields of a class
    * @param cl a class
    */
   public static void printFields(Class cl)
   {
      Field[] fields = cl.getDeclaredFields();

      for (Field f : fields)
      {
         Class type = f.getType();
         String name = f.getName();
         System.out.print("   ");
         String modifiers = Modifier.toString(f.getModifiers());
         if (modifiers.length() > 0) System.out.print(modifiers + " ");         
         System.out.println(type.getName() + " " + name + ";");
      }
   }
}
```

比如运行参数为java.lang.Object，会输出以下内容：

```text
public class java.lang.Object
{
   public java.lang.Object();

   protected void finalize();
   public final void wait();
   public final void wait(long, int);
   public final native void wait(long);
   public boolean equals(java.lang.Object);
   public java.lang.String toString();
   public native int hashCode();
   public final native java.lang.Class getClass();
   protected native java.lang.Object clone();
   public final native void notify();
   public final native void notifyAll();
   private static native void registerNatives();

}
```

# 在运行时使用反射分析对象

在上一节中我们查看了一个类的域、构造方法和其它方法。下面我们将操作对象，来获取它各个字段的值：

```java
Employee harry = new Employee("Harry Hacker", 35000, 10, 1, 1989);
Class cl = harry.getClass();
Field f = cl.getDeclaredField("name");
Object v = f.get(harry); // 返回String 对象， 值是Harry Hacker
```

首先，这段代码有一个访问上的问题。因为name其实是一个私有域，只有类自身的方法能够访问私有域。因此，上述代码会抛出IllegalAccessException异常。反射的默认行为受限于Java的访问控制。如果一个程序不受安全管理器的控制，则可以覆盖访问控制。我们只需要调用Field，Method，Constructor的setAccessible方法即可。setAccessible方法是AccessibleObject类的一个方法，该类是Field，Method，Constructor的父类。

```java
f.setAccessible(true);
```

其次，因为get方法返回的是一个Object，如果域是一个基本类型，会被自动打包成其包装类型，比如Double，Integer 等。最后，可以通过`f.set(harry, "Harry2")`来修改对象的f的域。

# 使用反射编写泛型数组

我们可以使用反射来扩展任意类型的数组，这里不仅仅指对象数组，还包括基本类型的数组：

```java
import java.lang.reflect.Array;

public static Object copyof(Object a, int newLength){
	Class cl = a.getClass();
	if( !cl.isArray()) return null; // 如果传进来的不是一个数组， 就不能处理。
	
	Class componentType = cl.getComponentType(); // 获取数组的元素类型。
	int length = Array.getLength(a); // 　获取原数组的长度。
	Object newArray = Array.newInstance( componentType , newLength); // 创建类型为componengType ， 长度为newLength 的数组。
	System.arraycopy( a, 0, newArray , 0, Math.min( length , newLength));
}
```

参数类型申明为Object而不是Object[]是考虑到基本类型数组，它们可以被转型为Object但是不能转型为对象数组。


# 使用反射调用任何方法
Method类中有一个invoke方法可以用来调用包装在当前Method对象中的方法。它的签名如下：

```java
Object invoke(Object obj , Object... args)
```

第一参数用来指定在哪个对象像调用这个方法，如果是静态方法那么第一个参数可以为null。后面的参数即为该方法的参数。比如假设m1 是Employee的getName方法，那么如下代码将会调用harry对象上的该方法：

```java
String name = (String) m1.invoke(harry);
```

如果返回的是基本类型，将被包装成其包装类型。