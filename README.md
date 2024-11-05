# 华中科技大学数据挖掘课程关联规则挖掘答案一键生成

## 使用说明
项目源码地址：
[https://github.com/DullPinard/DataMining](https://github.com/DullPinard/DataMining)

### 环境准备
安装好 `requirements.txt` 以后运行 `app.py` 出现如下界面：
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/3cde0b7d81ff498aba5ba072a0bc9786.png)
点击 `帮助` 按钮可以获得使用说明。
我们以2024年华中科技大学研究生课程数据挖掘技术考试试题举例：
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/0b5235ed37d2461fbb2d53c0c2c365a6.png)

可以使用微信图像的文字识别功能或其他的文字识别工具识别表格中的信息，准备好数据，把数据按照列合并成一列：
```
Major
Arts
Arts
Arts
Appl_science
Appl_science
Science
Science
Status
Graduate
Graduate
Undergraduate
Graduate
Undergraduate
Graduate
Undergraduate
Age
Old
Old
Young
Young
Young
Old
Young
Gender
Female
Male
Female
Male
Female
Male
Female
Gpa
Good
Exellent
Good
Exellent
Good
Good
Good
Count
80
50
120
140
80
180
120
```

中间有空的空行是无所谓的，然后设置界面中 `统计列关键字` ，一般默认为 `Count` ，表示的是该行对应的数值。点击 `读取数据` 可以读数据，读取成功数据会在右侧按照列显示。
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/82c48d6cd4334e068d9c9ad3bf87b73c.png)
记得检查一下所有的规则名称是否都是正确的。
### 第一问（强关联规则）求取
设置 `最小支持度阈值` 和 `最小置信度阈值` ，然后在右下侧表格设置强关联规则。
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/270b643b97aa4baca102ca5f7673f9c9.png)
可以右键添加，在这个强关联规则表格中设置的是频繁三项集的求取，每个项都是不重复的，因此除了 `Age` 一列也可以设置为 `All` ，效果相同。
点击 `开始计算（强关联规则）` 可以在弹窗中看到所有结果：
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/dc0481299b5549eb817320863a430fd3.png)
这就是第一问的全部结果，如果答题空间够可以把过程全部抄上。

### 第二问（判定树）求取
选择判定树的输出列，以本题 `Gender` 为例，然后点击 `开始计算（判定树）` 即可看到生成结果，全部抄上即可满分。
![在这里插入图片描述](https://i-blog.csdnimg.cn/direct/09d789cc1fab462499f4160f4e51c6aa.png)
