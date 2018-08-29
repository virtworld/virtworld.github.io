# 容器的接口与实现分离

Java的集合类库设计将接口与实现分离。以队列为例，我们可以有以下接口：
```java
interface Queue <E>{
	void add(E element);
	E remove();
	int size();
}
```

这个接口只是定义了一个队列的实现所必需包含的方法，但没有说明具体应该如何实现。队列的常见实现方式有

1. 循环数组比如ArrayDeque; 
2. 链表，比如LinkedList。

一旦我们构造了一个集合，我们就不需要知道它究竟用了哪一种实现，因为它们都遵守了接口的协议。通常我们将实例化的某集合保存到一个接口的引用中，如下所示：
```java
Queue <Customer> custQueue = new LinkedList <Customer>();
```

这样做的目的是，一旦我们想修改某数据结构的实现，我们只要在上述构造的地方（new 语句中）修改即可。另外，还有一组Abstract开头的类。和接口不同的是，集合中的抽象类一般是给类库实现者设计的，比如如果要实现自己的队列类，可以扩展AbstractQueue类，这要比实现Queue 接口中所有的方法轻松地多。

<!--more-->

# Collection接口和Iterable接口

集合中的实现大多扩展自Collection或者Map，而Collection又扩展自Iterable，它们都是泛型接口。

```java
public interface Collection <E>{
	boolean add(E element);
	Iterator <E> iterator();
	int size();
	boolean isEmpty();
	boolean contains(Object obj);
	boolean containsAll(Collection <?> c);
	boolean equal(Object other);
	boolean addAll(Collection <? extends E> from);
	boolean remove(Object obj);
	boolean removeAll(Collection <?> c);
	void clear();
	boolean retailAll(Collection <?> c);
	Object[] toArray();
	<T> T[] toArray(T[] arrayToFill);
}
```

从第三个开始，这些方法都是些集合类的实用方法，因此所有实现Collection接口的类都必需实现它们。但是每一个实现了Collection的接口都去实现一遍这些通用方法，对于类的设计者来说很不方便，因此有了一个抽象的AbstractCollection类，这个类并没有实现size、iterator 等方法，但是实现了诸如contains等的通用方法。

接下来我们来分析一下add和iterator方法。Collection的add方法用来向集合中添加元素，如果添加元素后集合发生了改变就返回true，否则返回false。iterator方法返回一个实现了Iterator接口的迭代器，这个迭代器可以遍历集合中的元素。
```java
public interface Iterator <E>{
	E next();
	boolean hasNext();
	void remove();
}
```
我们可以使用下面的一些方法来利用迭代器遍历集合：
```java
Collection <String > c = ...;
Iterator <String > iter = c.iterator();
while( iter.hasNext()){
	String element = iter.next();
	// do something ...
}
```
或者使用`for...each`块来遍历，`for...each`可以和任何实现了Iterable接口的对象一起使用，而我们知道Collection是Iterable的子接口，所以所有Collection的子类都是可以用for...each 来遍历的：
```java
for(String elem : c){
	// do something ...
}
```
Iterable 接口只有一个方法：
```java
public interface Iterable <E>{
	Iterator <E> iterator();
}
```

我们认为迭代器是在两个元素之间：调用next的时候，迭代器就越过下一个元素，并返回刚越过的那个元素的引用，类似于InputStream.read一样，从流中消耗掉并返回这个字节。

如果想要删除指定位置上的元素，也需要先越过该元素，才能删除它。方法next和remove具有互相依赖性，在remove之前没有调用next将报错：
```java
iter.next();
iter.remove();
```

# 容器框架
Collection和Map是容器中两个最基本的接口。如下图所示：

{{% figure class="center" src="/images/java-10-container/ContainerInterfaces.PNG" alt="容器接口" title="容器接口" %}}

使用add(Value)向Collection中插入，使用put(Key, Map)向Map中插入。对于Collection可以通过迭代器来获取它里面的值，对于Map可以用get(Key)获取其中的值。

List是Collection的子接口，而且是个有序集合，所以除了使用迭代器来获取元素外，还可以

1. 使用get(int)配合指定索引的位置来获取元素；
2. 使用remove(int)配合指定索引的位置来移除元素。

List的实现可以用LinkedList和ArrayList，但是前者不能提供高效的随机访问get函数。因此，我们引入了一个标记接口RandomAccess，这个接口没有任何方法，只是用来检测特定的集合是否支持高效的随机访问。

ListIterator作为Iterator的子接口，除了和Iterato 一样可以通过nex 和remove来获取和删除元素，还添加了一个add(E)的方法，可以把元素添加到迭代器所在位置之前。

如果两个List里面所有元素相同，并且它们的顺序相同，那么这两个Lis 等价，并且它们的hashCode会相同；

Set不允许添加重复的元素，如果两个Set中的所有元素相同，不管位置，那么这两个Set等价，并且它们的hashCode会相同。

SortedMap和SortedSet可以返回一个比较器对象，并且可以返回Map或者Set的子集视图。NavigatableSet和NavigatableMap实现了可以在有序集和映射表中查找和遍历的方法，比如大于某个指定键的键值对等。TreeSet和TreeMap分别实现了这两个接口。

下图显示了抽象类和它们的实现：

{{% figure class="center" src="/images/java-10-container/ContainerClasses.PNG" alt="容器类" title="容器类" %}}

下面是一些遗留下来的容器类：

{{% figure class="center" src="/images/java-10-container/ContainerLegacyInterfaces.PNG" alt="遗留容器" title="遗留接口" %}}

Java容器全图：

{{% figure class="center" src="/images/java-10-container/CollectionCheatSheet.PNG" alt="Java容器全图" title="Java容器全图" %}}

# 视图

视图views是实现了集合接口或映射表接口的对象，但是没有在上图中列出。比如Map的keySet方法返回的是一个实现了Set接口的类对象，这个类的方法对原Map进行操作。这种容器称为视图。

在Collection和Map接口中有些方法在文档中被称为Optional。因为有些实现了这些接口的视图一般都有一些限制，比如只能读，不能改变大小，只能删除而不能插入等。如果尝试了视图不支持的操作，就会抛出UnsupportedOperationException异常。

从实现角度来讲，这些视图继承了相应的接口，但是对于它们不想要实现的方法，直接抛出了该异常。这个设计打破了OOP的原则，既然继承了接口，却不实现其方法；它本身的用意是减少框架中接口的数量。通常我们不应该在自己的面向对象设计中使用这种方式。

1. 轻量级的包装器视图
	```java
	Integer[] a = new Integer [20];
	List<Integer> aList = Arrays.asList(a);
	```
	aList是一个实现了List接口的视图，使用它的get和set方法将直接修改底层数组，但是当尝试改变视图的大小时，会抛出UnsupportedOperationException。
	
	另外下面的方法返回了一个实现了List的不可修改视图，包含n个anObject对象的引用。
	```java
	Collections.nCopies(n, anObject);
	```
	还有返回单个元素的视图比如：
	```
	Collections.singleton(anObject); // 返回Set 视图
	Collections.singletonMap(anObject); // 返回Map 视图
	Collections.singletonList(anObject); // 返回List 视图
	```
	
2. 不可修改视图
	```java
	List<String> strings = new LinkedList<>();
	List<String> umStrings = Collections.unmodifiableList(strings);
	//...
	Collections.unmodifiableCollection
	Collections.unmodifiableSet
	Collections.unmodifiableSortedSet
	Collections.unmodifiableMap
	Collections.unmodifiableSortedMap
	```
	不可修改视图并不是容器本身不能修改。可以使用原始的容器的引用对元素进行修改。另外，因为不可修改视图实现了某特定的接口，因此上例中只能调用List接口中的方法，而LinkedList特有的方法则不可调用。
	
3. 下面介绍一下同步视图。为了让多个线程安全的访问某个容器，我们可以把容器转换为同步视图，比如：
	```java
	Map <String , Employee > map = Collections.synchronizedMap(new HashMap <String , Employee >());
	```
	
4. 然后是检查视图。检查视图用来对泛型类型发生问题时提供调试支持，目的是使错误在正确的位置得以报告。比如下面错误的添加了一个Date对象到String的List，这个错误知道Date对象被获取并被强制类型转换前不会被发现：
	```java
	ArrayList <String > strings = new ArrayList <String >();
	ArrayList rawList = strings; // get warning only , not an error , for compatibility with legacy code
	rawList.add(new Date()); // now strings contains a Date object!
	```
	使用检查视图，可以在添加Date 对象的时候报错：
	```
	ArrayList rawList = safeStrings;
	rawList.add(new Date()); // Checked list throws a ClassCastException
	```
	当然检查视图受限于虚拟机的运行时检查，比如类型`ArrayList<Pair<String>`对象中插入`Pair<Date>`对象就没法检查到了。
	
	这里的unmodifiableCollection、synchronizedCollection和checkedCollection的equals方法没有调用底层集合的equals方法，而是继承了Object的equals 方法，因此只能检测两个对象是否是同一个对象。
	
	然后unmodifiableSet和unmodifiableList调用的确是底层的hashCode 和equals 方法。

5. 子范围视图。比如下面返回的是一个list的第10到第19 个元素：
	```java
	List group2 = staff.subList(10, 20);
	```
	对这个子List 的操作将直接反映到原始List。另外还有如下子范围视图：
	```java
	SortedSet <E> subSet(E from , E to)
	SortedSet <E> headSet(E to)
	SortedSet <E> tailSet(E from)
	SortedMap <K, V> subMap(K from , K to)
	SortedMap <K, V> headMap(K to)
	SortedMap <K, V> tailMap(K from)
	NavigableSet <E> subSet(E from , boolean fromInclusive , E to, boolean toInclusive)
	NavigableSet <E> headSet(E to, boolean toInclusive)
	NavigableSet <E> tailSet(E from , boolean fromInclusive)
	```
	
# 集合和数组之间的转换
1. 将数组转换为集合
```java
String[] values = . . .;
HashSet<String > staff = new HashSet<String>(Arrays.asList(values));
```

2. 将集合转换为数组。首先可以转换为一个Object 数组，但是这将丢失实际的类型信息：
```java
Object[] values = staff.toArray();
String[] values = (String[]) staff.toArray(); // Error!
```
或者你可以将需要填充的数组传递给转换方法：
```java
String[] values = staff.toArray(new String [0]);// 将创建一个新的数组values ， 类型为String [];
staff.toArray(new String[staff.size()]); // 如果参数足够常， 将不创建新的数组， 而是将元素填充其中。
```

# 具体的集合
我们会在此介绍java.util中的一些集合（图中的上面部分），这里仅仅介绍这些集合的特性，源码级的分析我会另写文章。另外，concurrent包中的集合也会另外在并发相关的文章中介绍。

## 链表和数组集LinkedList和ArrayList

### Array和链表各有优势

链表适合在中间位置插入和删除元素，而ArrayList适合随机访问。后者封装了一个动态再分配的对象数组。除非插入和删除操作非常频繁造成很大开销，否则简易使用ArrayList。

Java中，所有的链表都是双向链表。

### 链表中添加和删除元素

LinkedList实现了Collection接口，它的add方法将元素添加到链表的末尾。如果需要在中间添加元素，就要用到迭代器了，因为迭代器描述的是集合中的位置。

因为LinkedList是有序集合，它有一个listIterator(int) 方法可以返回一个ListIterator迭代器，这个迭代器指向索引为n的元素的前面的位置，也就是说此时调用next()与调用list.get(n)将返回同一个元素：
```java
interface ListIterator <E> extends Iterator <E>{
	void add(E element);
	...
}
```

和前面Collection接口的add方法不同：Collection的add方法通过返回true表示实际上集合被修改了，false表示add方法之后集合没有被修改；

ListIterator的add方法不返回任何类型，它默认总会修改集合。除了和Iterator接口一样，有hasNext和next方法外，ListIterator接口还增加了previous和hasPrevious方法，用于反向遍历链表。

而nextIndex返回下一次调用next方法时返回的元素的整数索引，previousIndex返回下一次调用previous方法时返回元素的整数索引：

```java
interface ListIterator <E> extends Iterator <E>{
	void add(E element);
	...
	boolean hasPrevious();
	E previous();
	boolean hasNext();
	E next();
	int previousIndex();
	int nextIndex();
}
```

我们之前说过迭代器永远位于两个元素之间（或者在最前面的一个元素之前或者最后的一个元素之后），ListIterator的add方法将在迭代器当前位置之前添加一个新的对象，不管最后一次调用的是next还是previous；而ListIterator的remove 则会将最近越过的一个元素删除，这依赖于最近调用的是next还是previous。所以说add方法只依赖于迭代器的位置，而remove方法还依赖于迭代器的状态：

```java
List <String > a = new LinkedList <String >();
a.add("A");
a.add("B");
a.add("C");
a.add("D");
ListIterator <String > it = a.listIterator();
it.next();
it.add("X");
it.add("Y");
it.previous();
it.add("P");
it.add("Q");
System.out.print(a); // 输出[A, X, P, Q, Y, B, C, D]
it = a.listIterator(); // 重置迭代器
it.next();
it.next();
it.remove();
System.out.print(a); // 输出[A, P, Q, Y, B, C, D]
it = a.listIterator(); // 重置迭代器
it.next();
it.next();
it.previous();
it.remove();
System.out.print(a); // 输出[A, Q, Y, B, C, D]
```

### 链表中修改和带来的问题

set方法用一个新的元素替换调用next或者previous返回的上一个元素。set造成的修改，不属于链表的结构性修改。当一个迭代器发现它的集合发生非它本身造成的结构性修改的时候，它会抛出ConcurrentModificationException。

集合可以跟踪结构性修改的次数，而每一个迭代器维护一个独立的计数值。在每个迭代器方法的开始处检查自己的修改计数和集合的修改计数是否一致，不一致则抛出该异常。为避免该异常，我们应该遵守以下规则：可以给一个容器附加多个迭代器，但是这些迭代器只能读取，另外再单独附加一个既能读又能写的迭代器。

## 散列集HashSet

散列集的优点是当你想快速查看某个元素却不知道它的位置时，能够快速找到它。这里链表和数组都需要进行遍历才能找到该元素。它的缺点是元素的顺序是不定的。

散列集依靠保存键的hashCode：散列集为每一个对象的实例域产生一个整数，再通过某种计算将这些值计算出该对象的散列码，这样具有不同数据域的对象将具有不同的散列码。自己实现的hashCode方法应该与equals方法兼容，即如果a.equals(b)返回true，则a与b具有相同的散列码。


Java 7 及之前的散列集HashSet的实现：HashSet 本质上是一个链表数组。每个链表被称为桶，数组的每个元素储存了指向每个桶的引用。要想从散列表中找出某个对象或者放入某个对象，就要先计算它的散列码，然后与桶的个数（即数组的大小）取余，所得的结果就是保存这个元素的桶的索引。比如某个对象的散列码是76268，并且有128 个桶，那么该对象保存再108号桶中，因为76268除以128余108。

如果桶中存在其它元素，那么就会发生散列冲突(hash collision)，这时我们对于这个桶的链表中的所有元素进行比较，直到找到我们要找的元素。如果是要取出某个对象，则返回找到的对象；如果是要放入某个元素，则更新那个元素。

通常将桶的数目设置为预计元素个数的75%到150%。有观点认为，为防止键的聚集，应该将桶的数目设置为素数，但是Java的实现使用的是2的幂，默认是16。当然一般来讲，我们并不知道需要存储多少个元素，如果散列表太满就会影响性能，这时候就需要再散列(rehashing)，也就是创建一个桶数更多的表，并将全部元素插入到这个新的散列表中。

负载因子(load factor) 决定何时对散列表进行再散列，默认的值是0.75，也就是说表中超过75% 的桶都填入了元素则使用双倍的桶的数目进行再散列。


## 树集TreeSet

树集和散列集很像，但是它是一个有序集合，在对树集进行遍历时，自动按照排序后的顺序呈现。排序是用树结构完成的（红黑树），每添加一个元素，都会被放置在正确的排序位置上。将一个元素添加到树中要比添加到散列集中慢，但是速度仍旧在同一个数量级上，相比于将元素添加到链表或者数组的正确位置上仍旧快很多。

如果树中包含n个元素，查找一个元素的位置平均需要log2n次比较。

TreeSet对元素的排序依赖于元素实现了Comparable接口。Comparable接口带有一个返回int类型的compareTo方法：
```java
public interface Comparable <T>{
	int compareTo(T other);
}
```
如果a与b相等，则a.compareTo(b)返回0；如果排序后a位于b前，则返回负值；否则返回正值。我们也可以不要求对象实现Comparable接口，这时我们需要传递一个Comparator对象给TreeSet构造器，告诉它如何比较元素：
```java
public interface Comparator <T>{
	int compare(T a, T b);
}
```
与Comparable接口一样，如果a位于b前，返回负值；a与b相等，则返回0；否则返回正值。举例：
```java
class ItemComparator implements Comparator <Item >{
	public int compare(Item a, Item b){
		String descrA = a.getDescription();
		String descrB = b.getDescription();
		return descrA.compareTo(descrB);
	}
}

ItemComparator comp = new ItemComparator();
SortedSet <Item > sortedByDescription = new TreeSet <>(comp);
```
或者我们可以将这个比较器实现为匿名类：
```java
SortedSet <Item > sortedByDescription = new TreeSet <>( new
	Comparator <Item >(){
		public int compare(Item a, Item b){
			String descrA = a.getDescription();
			String descrB = b.getDescription();
			return descrA.compareTo(descrB);
		}
	}
);
```

虽然使用树集的开销并不比使用散列集的开销大很多，但是在不需要对数据进行排序的时候，就没有必要付出这些额外的开销。而且对于某些数据来说，可能因为比较器的比较很复杂等原因，排序的开销会大很多。所以不需要排序时应该使用散列集。


## 队列、双端队列(ArrayDeque 和LinkedList)和优先级队列(PriorityQueue)

双端队列即可以在头部和尾部同时添加或删除元素的队列，不支持在中间添加元素。Java中实现了Deque接口的即为双端队列，ArrayDeque和LinkedList类都实现了该接口。

优先级队列是一个底层用堆来实现的数据结构。堆是一个可以自我调整的二叉树，执行添加和删除操作时可以将最小的元素移动到根，而不必花时间对元素进行排序。因此优先级队列总是按照排序的顺序进行检索：每次调用remove时，总会获得队列中最小的元素，并且因为底层是用堆实现的原因，并不需要对这些元素进行排序。

和TreeSet 一样，一个优先级队列中保存的对象，要么实现了Comparable接口，要么在优先级队列的构造器中提供比较器对象。优先级队列的典型应用是任务调度，任务以无序的形式插入到队列，但是每次都是调用优先级最高的任务。


## 映射表HashMap

映射表实现了Map接口，用来存放键值对。Java 中有两个常用的实现：HashMap和TreeMap。

HashMap对键进行散列，TreeMap用键的整体顺序对元素进行排序，并将其组织成搜索树。

散列映射表比树映射表稍快，如果不需要按照顺序访问键，则应该选择散列映射表。

get方法在没有找到给定的键的信息时会返回null，而put方法在找到已经存在的键值对时，会用新的值取代已经存在的值。

可以获得映射表的视图，这是实现了Collection接口或者其子接口的一组对象，比如：

```java
Set<K> keySet()
Colletion<V> values
Set<Map.Entry <K, V>> entrySet()
```

这里的keySet并不是一个HashSet或者TreeSet，而是实现了Set接口的某个其它的类，Set是Collcetion的子接口。

获取这些视图后我们可以迭代遍历映射表中所有的键值对：

```java
for( Map.Entry <String , Employee > entry : staff.entrySet()){
	String key = entry.getKey();
	Employee value = entry.getValue();
	//...
}
```

如果调用键集的迭代器的remove方法，实际上将从映射表中删除键以及对应的值；但是键集不支持add或者addAll方法。值集values和键值对Entry也有同样的限制。

## 弱散列映射表WeakHashMap

当对键的唯一引用来自散列表条目时，WeakHashMap将与垃圾回收器协同工作一起删除键值对。

WeakHashMap使用弱引用保存键，弱引用将引用（即键）保存到另一个对象中。如果某个对象只能由弱引用来引用，垃圾回收器仍旧回收它，但要将这个引用放入队列中。

WeakHashMap将周期性地检查队列，以便找出新添加的弱引用。进入队列的弱引用表示这个键不会再被使用，因此WeakHashMap将删除键值对。

## 链接散列集LinkedHashSet 和链接散列映射表LinkedHashMap

LinkedHashSet和LinkedHashMap分别扩展自HashSet和HashMap，并分别实现了Set和Map接口，同时它们又有LinkedList的特性，它们记住插入元素的顺序，用于按顺序遍历。

其中LinkedHashMap的构造器中包含一个参数用来指定访问顺序是插入顺序还是访问顺序，访问顺序是从最不常访问的元素到最近访问的元素排序，可以用来实现LRU缓存。

访问顺序的LinkedHashMap在调用get和put时候，受影响条目会从当前位置删除，并插入到链表的尾部。

LinkedHashSet和LinkedHashMap需要额外的空间来为每个元素储存指针，但是整体性能上和HashMap和HashSet接近。

## 枚举集EnumSet和枚举映射表EnumMap

因为枚举类型的实例个数有限，因此内部用位序列实现。如果对应的值在集合中，则相应的位被置为1。

EnumSet没有公共的构造器，需要使用静态工厂方法来构造这个集:
```java
enum Weekday {Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday};

EnumSet<Weekday> always = EnumSet.allOf(Weekday.class);
EnumSet<Weekday> never = EnumSet.noneOf(Weekday.class);
EnumSet<Weekday> workday = EnumSet.range(Weekday.Monday , Weekday.Friday);
EnumSet<Weekday> mwf = EnumSet.of(Weekday.Monday , Weekday.Wednesday , Weekday.Friday);
```
EnumMap是一个键类型为枚举类型的映射表，需要在构造器中指定键类型：

```java
EnumMap<Weekday, Employee> personInCharge = new EnumMap<>(Weekday.class);
```

## 标识散列映射表IdentityHashMap

该映射表的散列值使用System.identityHashCode来计算，这是Object.hashCode根据对象的内存地址来计算散列码时使用的方式。因此在对象比较的时候，IdentityHashMap使用的时==，而不使用equals。

也就是说不同的键对象，即使内容相同，也被视为不同的对象。这在实现对象遍历算法时非常由用。

# 容器中的常用算法
## 排序

Collections的sort方法可以用来对实现了List接口的集合进行排序。它假定元素实现了Comparable接口，或者可以把一个Comparator作为第二个参数传递给sort方法。

该方法直接把所有元素都转入到一个数组中，并使用一种归并排序的变体对数组进行排序，然后再将排序后的序列复制回列表。它虽然比快速排序慢一点，但是它具有稳定性，即不需要交换相同的元素。

sort方法接受的列表必须是可修改的，但不必是可以改变大小的。这里，如果列表支持set方法则是可修改的，支持add和remove方法则是可变大小的。

## 二分查找

Collections中的binarySearch方法要求集合实现了List接口，并且必须是排好序的。如果返回的数值i大于0，则标识匹配对象的索引，即list.get(i)将获得该元素；如果返回负值，则标识没有匹配的元素。

但是可以利用这个返回值，计算出应该在哪里插入元素。插入的位置是-i-1，即
```java
if(i < 0) list.add(-1 - 1, element);
```

只有采用随机访问，二分查找才有性能上的意义，如果为binarySearch方法提供一个链表，它将自动变为线性查找。

# 遗留的集合

## Hashtable

同HashMap类型类似，但是Hashtable是同步的，如果对同步性有要求可以考虑使用ConcurrentHashMap，如果对遗留集合的兼容性有要求才考虑使用Hashtable。

## Bitset

Bitset存量一个位序列，它将位包装在字节里，比使用Boolean对象的ArrayList要高效。
```java
bitset.get(i); // 如果第i 位被设置为开， 则返回true，否则返回false
bitset.set(i); // 将第i 位设置位开
bitset.clear(i); // 将第i 位设置位关
```
## Stack
Stack已经可以完全被LinkedList替代了。因为Stack 扩展自Vector，它可以进行insert和remove操作。