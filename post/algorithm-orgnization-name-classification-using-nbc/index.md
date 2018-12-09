> 本文介绍使用朴素贝叶斯分类器将机构按照其名称分类为不同的行业的方法。

## **为什么要对机构名称进行分类？**

机构名称是指单位名称或者组织机构的名称，比如`浙江大学`、`深圳市腾讯计算机系统有限公司`、`杭州市法院`等等；行业分类根据实际业务需求变化而变化，一个相对标准的行业分类是国家统计局公布的《国民经济行业分类》，但是本文使用了一套自己定义的行业分类。

首先，为什么要进行行业分类？机构所属的行业其实是机构的一个属性，将机构信息标准化的过程中当然也需要将其行业信息标准化。通常的做法是让用户在填写的时候选择机构的行业类型，但是自动化的行业分类也有很多用处

1. 改善用户体验。因为行业可能有很多层级，比如《国民经济行业分类》就有四级行业分类，如果能在用户选择前提供一个系统推荐的分类，则可以减少用户的操作；
2. 填补行业分类缺失。可能因为多种原因，比如用户自己不清楚、用户不想填写或者前端未强制要求用户填写等，造成行业分类信息缺失，自动化分类可以作为一个补充。

但是使用机构名称来做行业分类也有很多问题，比如从有些名称里面根本看不出行业信息。比如，如果没有名称以外的认知，光看`腾讯`两个字是看不出来这家机构是做什么的，而`深圳市腾讯计算机系统有限公司`则可以猜出个大概。那么为什么还要通过单位名称进行行业分类？

1. 首先是简单。分类函数仅需要一个机构名称的输入，就可以输出结果。
2. 其次是对于标准企业名称是有效的。标准的企业名称是由`行政区划 + 字号 + 行业 + 组织形式`，也就是说如果企业名称是标准的，那么行业信息是很容易识别的；不标准的企业名称，比如简称，则是机构信息标准化中的另一个问题。

<!--more-->

## **朴素贝叶斯分类器**

贝叶斯分类器为条件概率模型，依赖于1. 特征项的概率`P(F)`，在我们的场景中即为词语在机构名称中出现的概率，名称中的词语可以通过分词器来获取（有很多开源的分词器可以选择）；2. 分类的概率`P(C)`，即各个行业分类出现的概率；3. 分类下特征下出现的概率`P(F|C)`，即在某一个行业分类下某词语出现的概率。

$$ P(C_i|F_1,F_2,...,F_n) = \frac{P(F_1,F_2,...,F_n|C_i)P(C_i)}{P(F_1,F_2,...,F_n)} $$

使用朴素贝叶斯的假设，即假设各个特征相对于其它特征项条件独立。并且我们知道分母和分类没有关系，是个常量，因此在实际计算概率大小的时候可以忽略：

$$ P(C_i|F_1,F_2,...,F_n) \propto \prod_k^n P(F_k|C_i)P(C_i) $$

## **训练模型**

我们需要一个训练集，训练集中的每条记录为机构名称和最低一级的行业分类。我们迭代处理每一条记录，分别计算以下统计信息：

```java
// 1. 训练集中各分类计数（各行业的出现次数）
Map<String, Integer> classCount = new HashMap<String, Integer>();
// 2. 训练集中各特征项计数（各词语的出现次数）
Map<String, Integer> featureCount = new HashMap<String, Integer>();
// 3. 训练集中每个分类下特征技术（各行业下各词语的出现次数）
Map<String, HashMap<String, Integer>> condFeatureCount 
    = new HashMap<String, HashMap<String, Integer>>();

// 4. 分类总数（行业总数）- 计数包括重复出现的行业
int totalClassCount = 0; 		
// 5. 特征总数（词语总数）- 计数包括重复出现的特征
int totalFeatureCount = 0; 
// 6. 每个分类中特征总数（各行业下词语总数）- 计数包括重复出现的分类下特征
Map<String, Integer> totalFeatureInClassCount = new HashMap<>(); 

// 处理训练集
while( rs.next()){
			
	String name = rs.getString(1); // 机构名称
	String icode = rs.getString(2); // 行业分类代码

    // 处理每一条记录
    ...
}
```

下面我们看下处理每一条记录的代码，也就是如何计算上述几个统计数据。

```java
// 1. 递增训练集中各分类计数，icode为行业分类代码
Integer classCountValue = classCount.get(icode);
if(classCountValue == null){
    classCount.put(icode, 1);
}else{
    classCount.put(icode, classCountValue + 1); 
}

// 4. 递增所有分类总数计数（包括重复出现的）
totalClassCount++;

// 将机构名称分词			
List<Term> words = ToAnalysis.parse(name).getTerms();
for (Term word : words) {
	// 处理每一个词语（特征）		
    
    // 如果词语不存在，跳过
    if( "".equals( word.getName().trim()) ){
        continue;
	}

    // 取词语名称				
	String wordName = word.getName();

	// 2. 递增训练集中各特征计数
	Integer featureCountValue = featureCount.get(wordName);
	if(featureCountValue == null){
		featureCount.put(wordName, 1);
	}else{
		featureCount.put(wordName, featureCountValue + 1); 
	}

    // 5. 递增所有特征总数计数（包括重复出现的）
    totalFeatureCount++;

	// 3. 递增训练集中各分类下各特征计数
	HashMap<String, Integer> condFeatureCountValue = condFeatureCount.get(icode);
	if(condFeatureCountValue == null){
		condFeatureCountValue = new HashMap<String, Integer>();
	}
				
	Integer condFeatureCountValueInt = condFeatureCountValue.get(wordName);
	if(condFeatureCountValueInt == null){
		condFeatureCountValue.put(wordName, 1);
	}else{
		condFeatureCountValue.put(wordName, condFeatureCountValueInt + 1); 
	}
				
	condFeatureCount.put(icode, condFeatureCountValue);

     // 6. 递增每个分类中所有特征总数计数（包括重复出现的）
	Integer totalFeatureInClassCountValue = totalFeatureInClassCount.get(icode);
	if( totalFeatureInClassCountValue == null){
		totalFeatureInClassCount.put(icode, 1);
	}else{
		totalFeatureInClassCount.put(icode, totalFeatureInClassCountValue + 1);
	}

}
```

处理完训练集后，上述收集的六类数据会被存放于数据库的一张表中，如下所示：

| Class | Feature | Count | Total |
| :--   | :----   |----:  | ----:  |
|       | 有限公司 | 64,408 | 1,227,170 |
|       | 上海    | 8,186 | 1,227,170 |
|       | 小学    | 6,699 | 1,227,170 |
| ...   | ... | ... | ... |

上面这些Class为空的记录上述第2和第5类数据，表示某个特征（比如`有限公司`）出现次数（64408次）和总特征计数（1227170次）。
下面这部分Class不为空，而Feature为空的则记录的是第1和第4类数据，表示某个行业（比如`批发制造业`）出现的次数（23741次）和总训练记录数（223,617条）。

| Class | Feature | Count | Total |
| :--   | :----   |----:  | ----:  |
| 制造维修业      |  | 23,741 | 223,617 |
| 批发零售业      |     | 20,042 | 223,617 |
| 党政机关      |     | 17,896 | 223,617 |
| ...   | ... | ... | ... |

最后是Class和Feature都不为空的第3类和第6类数据，下面也举几个例子：

| Class | Feature | Count | Total |
| :--   | :----   |----:  | ----:  |
| 学校教育行业      |  小学 | 3,528 | 46,659 |
| 商业贸易行业      | 贸易    | 3,268 | 63,933 |
| 建筑及周边行业      | 装饰    | 1,465 | 22,559 |
| ...   | ... | ... | ... |

最后根据上述这个这些数据，我们构成我们的朴素贝叶斯模型。具体加载数据到下面这些Map里的代码就不展示了，比较直接。

```java
public class NaiveBayesianModel {

    /**
	 * The probabilities map of P(F_i|C_j)s
	 */
	public Map<String, Map<String, BigDecimal>> condFeatureProb = new HashMap<>();

	/**
	 * The probabilities map of P(F_i)
	 */
	public Map<String, BigDecimal> featureProb = new HashMap<>();

	/**
	 * The probabilities map if P(C_j)
	 */
	public Map<String, BigDecimal> classProb = new HashMap<>();

	/**
	 * The minimum values of P(F_i). This is used in the formula when the
	 * feature cannot be found in the featureProb map. The value will
     * be updated during initialization. 
	 */
	public BigDecimal minFeatureProb = BigDecimal.ONE;

	/**
	 * The minimum value of P(C_j). Used when no value found in classProb.
     * The value will be updated during initialization.
	 */
	public BigDecimal minClassProb = BigDecimal.ONE;

	/**
	 * The minimum value of P(F_i|C_j). Used when no value found in
	 * condFeatureProb. The value will be updated during initialization.
	 */
	public BigDecimal minCondFeatureProb = BigDecimal.ONE;
}
```

## **结果**
下面是几个比较容易区分的例子：


1. 【招商银行南京市分行】的行业类型为：

  - 第 1猜测为：银行及银行业, 可信度为：70.76%
  - 第 2猜测为：金融, 可信度为：29.20%

2. 【杭州市公安局西湖分局文新派出所星洲社区警务室】的行业类型为：

  - 第 1猜测为：行政机关、公务员, 可信度为：99.26%
  - 第 2猜测为：事业单位, 可信度为：0.69%

下面再展示几个容易误判的例子：

1. 【一点点奶茶（宁波大学店）】的行业类型为：

  - 第 1猜测为：旅馆和餐饮业, 可信度为：68.19%
  - 第 2猜测为：广告中介或咨询服务业, 可信度为：10.35%

2. 【浙江大学附属第一医院】的行业类型为：

  - 第 1猜测为：公立医院, 可信度为：99.61%
  - 第 2猜测为：事业单位, 可信度为：0.21%

下面再展示一个假的组织名称的识别结果：

1. 【偷税漏税股份有限公司】的行业类型为：

  - 第 1猜测为：机械及原料加工业, 可信度为：14.58%
  - 第 2猜测为：金融, 可信度为：13.72%