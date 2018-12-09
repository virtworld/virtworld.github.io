这是一个简单的枚举类型的定义。枚举类型是一个类，除了不能被继承以外，它的行为和一个类相近，关键字enum只是为了告诉编译器在生成相应的类的时候采用的一些编译行为。比如

```java
public enum Size {SMALL , MEDIUM , LARGE}
```

上面的枚举类有三个实例，而枚举类的实例是常量，因此都大写。使用枚举常量时要创建它的一个实例：

```java
Size size = Size.SMALL;
```

enum 经常与switch 配合使用:

```java
Size size;
// do something to get size;
switch(size){
	case SMALL:
	// do something;
	case MEDIUM:
	// do something;
	case LARGE:
	// do something;
}
```

<!--more-->

# 常用方法

所有的枚举类型都继承自Enum类，因此有一些方法被继承了下来。下面是Enum类的一些常用方法：

1. 枚举类实例的toString方法。
	```java
    Size s = Size.SMALL; 
	s.toString(); 
	```
	将返回字符串SMALL。

2. 枚举类实例的ordinal方法。返回声明中枚举常量的位置。

	```java
	Size s = Size.SMALL; s.ordinal(); 
	```
	返回0。

3. Enum的静态方法valueOf。和toString相反，通过枚举常量名字获取枚举实例。

	```java
	Size s = Enum.valueOf(Size.class, "SMALL");
	```
	返回一个SMALL的枚举常量。

4. 枚举类静态方法valueOf。和toString相反，通过枚举常量名字获取枚举实例。

	```java
	Size x = Size.valueOf("LARGE");
	```

	返回一个LARGE的枚举常量。和需要两个参数的valueOf不同，此方法并不是继承自Enum，而是由编译器直接添加到枚举类的静态方法。如果将枚举类向上转型为Enum将无法使用此方法。

5. 枚举类静态的values方法。返回全部枚举常量的数组。

	```java
	Size[] values = Size.values()
	```

	返回一个包含SAMLL, MEDIUM, LARGE的数组。此方法也是编译器直接添加到枚举类中的静态方法，并非继承自Enum 类，所以向上转型为Enum后同样无法使用。
	Class类中有一个getEnumConstants方法也可以达到values的效果。

	```java
	Enum e = (Enum) Size.SMALL; 
	Enum all2[] = e.getClass().getEnumConstants();
	```

6. ==。我们可以用==直接比较两个实例常量，编译器提供了equals和hashCode方法。另外Enum类实现了Comparable接口，所以它具有compareTo方法。因为所有枚举类型继承自Enum，而且Java并不支持多重继承，所以我们不能extend一个枚举类型，但我们可以让它implement其它接口。

# 添加方法

因为枚举类型是类，所以和其他类一样，我们也可以向枚举类型中添加方法，包括main方法。如果我们在Enum类中添加了方法，我们必须把枚举常量的定义放在最前面，并且在其后面加一个分号，如下：

```java
public enum Size{
	
	SMALL("The␣size␣is␣small."),
	MEDIUM("The␣size␣is␣medium."),
	LARGE("The␣size␣is␣large.");
	
	// your method / data definition starts here..
	private String description;
	
	private Size(String description){
		this.description = description;
	}
	
	public String getDescription(){
		return description;
	}

	@Override
	public String toString(){
		return name() + ":␣" + description;
	}
}
```

如上所示，我们在枚举类型Size中增加了一个构造器，这里的构造器声明为private，但是即使不写成private，构造器也不能被外部代码调用。另外我们还覆盖了toString方法。name()返回和toString相同。

# 随机选取枚举实例

经常我们需要随机的选取一个枚举类型中的实例，下面这个公共方法可以支持对任意枚举类型的随机选择：

```java
public class RandomEnumGen {
	
	private static Random rand = new Random (49);
	
	public static <T extends Enum <T>> T random(Class <T> ec){
		return random(ec.getEnumConstants());
	}

	public static <T> T random(T[] values){
		return values[rand.nextInt(values.length)];
	}
}
```

# 枚举的枚举

如果想要嵌套枚举，比如我们想要对一些城市进行分组，可以用接口将枚举实例分组：

```java
public enum Provinces {
	
	ZHEJIANG(Province.Zhejiang.class),
	JIANGSU(Province.Jiangsu.class),
	GUANGZHOU(Province.Guanzhou.class);
	
	private Province[] values;
	
	private Provinces(Class <? extends Province > province){
		values = province.getEnumConstants();
	}

	private interface Province{
		enum Zhejiang implements Province{
			HANGZHOU , NINGBO
		}

		enum Jiangsu implements Province{
			NANJING , SUZHOU
		}
		
		enum Guanzhou implements Province{
			GUANGDONG , SHENZHEN
		}
	}

	public Province randomSelection(){
		return RandomEnumGen.random(values);
	}

	public static void main(String[] args){
		// Get all provinces
		Provinces[] provinces = Provinces.values();
		for(Provinces province : provinces){
			// Get all cities in the province
			Province[] cities = province.values;
			System.out.print(province + "province has:");
			
			for(Province city: cities){
				System.out.print(city + "");
			}
			System.out.println();
		}
	}
}
```

输出如下：

```text
ZHEJIANG province has:HANGZHOU, NINGBO,
JIANGSU province has:NANJING, SUZHOU,
GUANGZHOU province has:GUANGDONG, SHENZHEN,
```

# 

EnumSet和EnumMap分别实现了Set和Map接口，是专门用于存放Enum类及其子类的容器。EnumSet的常见用法：

```java
public class EnumSetTest {

	private enum CITY {NINGBO, HANGZHOU, WENZHOU};
	
	public static void main(String[] args){
		EnumSet<CITY> esetAll = EnumSet.allOf(CITY.class);
		printEnumSet(esetAll, "allOf");
		EnumSet<CITY> esetNone = EnumSet.noneOf(CITY.class);
		printEnumSet(esetNone, "noneOf");
		EnumSet<CITY> esetOf = EnumSet.of(CITY.NINGBO, CITY.HANGZHOU);
		printEnumSet(esetOf, "of TWO");
		esetOf.add(CITY.WENZHOU);
		printEnumSet(esetOf, "add ONE");
		esetOf.removeAll(EnumSet.of(CITY.HANGZHOU, CITY.WENZHOU));
		printEnumSet(esetOf, "remove TWO");
	}
	
	public static <E extends Enum<E>> void printEnumSet(EnumSet<E> eset, String title){
		
		System.out.print(title + ": ");
		for(E e : eset){
			System.out.print(e.toString() + ", ");
		}
		System.out.print("\n");
	}
}
```

上述代码输出：

```text
allOf: NINGBO, HANGZHOU, WENZHOU, 
noneOf: 
of TWO: NINGBO, HANGZHOU, 
add ONE: NINGBO, HANGZHOU, WENZHOU, 
remove TWO: NINGBO, 
```

EnumSet的底层是用一个long来表示的。一个long有64 位，如果是一个长度小于等于64的枚举类，那么EnumSet会使用一个它的子类RegularEnumSet来实现，这个RegularEnumSet就是用一个long和位移操作符来表示哪些位上的Enum实例是存在的。如果长度大于64位，EnumSet会用一个JumboEnumSet的子类来实现，它的底层是一个long数组。具体可以阅读源码。

```java
EnumMap <Provinces, String> emap = new EnumMap <Provinces, String>(Provinces.class);
System.out.println(emap.size());
emap.put(Provinces.ZHEJIANG, "EAST");
emap.put(Provinces.GUANGZHOU, "SOUTH");
emap.put(Provinces.JIANGSU, "NORTH");
System.out.println(emap.size());
```

输出0和3。EnumMap中的size值是在put和remove时候手动维护的，并不是它底层数据结构的大小。事实上当我们创建一个空的EnumMap的时候，所有的Key都已经存在了，只不过Value是null罢了。详见源码。

# 枚举常量相关的方法

在自定义的Enum类的实例可以有自己的方法，这样每个实例都有不同的行为。常见的用法是：

1. 在自定义的Enum的类中添加一个abstract方法，然后所有的该类的实例都实现该方法；
2. 覆盖enum 类中的方法；

```java
public enum EnumTest1 {

	A{
		public String sayName(){
			return "My name is A";
		}
	},
	B{
		public String sayName(){
			return "My name is B";
		}
		public String f(){
			return "Overridden behaviour";
		}
	};
	
	public abstract String sayName();
	
	public String f(){
		return "default behaviour";
	}
	
	public static void main(String[] args){
		EnumTest1 et = EnumTest1.A;
		System.out.print(et.sayName() + ": ");
		System.out.println(et.f());
		et = EnumTest1.B;
		System.out.print(et.sayName() + ": ");
		System.out.println(et.f());
	}
}
```

输出：
```text
My name is A: default behaviour
My name is B: Overridden behaviour
```