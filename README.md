# Funclib: 高效设计功能多样的酶库

>参考1:  Automated design of efficient and functionally diverse enzyme repertoires
>
>参考2: http://FuncLib.weizmann.ac.il

**作者: 刘源** 

简介: 北京大学化学与分子工程学院-王初课题组特聘博士后



## 零.前言

通常对于酶活性/特异性的改造是集中在活性中心区域的，然而这些突变往往是具有非叠加效应的，因此使用传统的单点突变和后继的多点联合突变的改造思路不再适用。因此Sarel J. Fleishman在2018年提出了Funclib的方法，针对磷酸三酯酶和乙酰辅酶A合成酶进行设计，结果表明改造后酶的反应特异性发生了改变，对于原有的非底物的催化效率提升10-4000倍不等。



## 一、计算原理

蛋白设计的过程中，使用的打分函数不是完美的，在过大的构象空间进行采样往往难以有很高的成功率，遍历采样反而挖出了打分中的漏洞。所以如果能结合一些生信的数据来优化序列空间，对成功设计以及提高计算效率都会有很大帮助。

本文中介绍的Funclib的开发思路是继承PROSS的核心思想，首先利用PSSM信息以及单点突变预测信息，将备选的序列空间大大降低，再进行序列的组合design，比起通常Rosetta中的全序列空间的模拟退火寻找近优解来说，通过穷举法搜索序列空间可以挖掘地更深。Funclib流程只考虑酶底物结合口袋附近的位点，并约束关键的活性侧链以及离子构象，可以将序列采样空间缩小到可以穷举的范围（几万），通过softrepack，repack，rotmin等常用mover结合，可以在几十秒内完成一个突变体的打分。

将可耐受的突变获取作为候选突变类型（如PSSM>=-2, ddG<=5的单点突变），再对所有的位点进行穷举组合（至少3个突变，最多5-6个突变）计算ddG。最后通过再对所有结果进行排序和聚类得到突变体的建议。文章中他们展示了该方法可以成功的扩展若干模式酶的底物选择性。![funclib原理](/Users/kunkun/Library/Mobile Documents/com~apple~CloudDocs/markdown/图片/funclib/funclib原理.png)





## 二、使用方法

以下将介绍如何使用RosettaScript来使用Funclib的方法。

**本文所有的脚本均在github可下载，github地址:https://github.com/guyujun/FunclibLocal。**

**本方法不需要额外处理辅酶分子，所有在pdb中的底物、金属离子均会被保留。**



### 0 确定突变的具体参数

第一步先通过视觉判断，定义酶活中心中的重要残基，可突变残基等。

可通过脚本一键生成所有需要的参数文件:

```shell
python make_flags.py example.pdb 18B,69B,93B 65B,13B
```

- 参数1: exampel.pdb，输入的pdb名称
- 参数2: 酶活中心关键的氨基酸的pdb编号，这些氨基酸不允许侧链发生变化，如18B,69B,93B（根据实际情况填写）
- 参数3: 酶活中心允许突变的氨基酸pdb编号列表，如65B,13B（根据实际情况填写）



并且新建出3个文件夹: refinement、resfiles以及output



### 1 生成PSSM文件

本文通过psiblast生成，也可以使用其他的在线服务器。FuncLib web-server上是通过考虑二级结构的比对，因此PSSM构建更加的精准。

首先通过https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE=Proteins&PROGRAM=blastp&RUN_PSIBLAST=on输入序列进行数据库搜索。

下载匹配到的所有序列, 并将下载的序列进行格式化:

```shell
python gen_pssm.py $blast_fasta $protein_fasta
```

- blast_fasta: 从ncbi-psiblast下载的同源序列结果4
- protein_fasta: 输入文件pdb的fasta序列

运行完毕后产生result.pssm.



### 2 生成主链约束

生成主链的约束，约束每个氨基酸Cα的坐标，生成的限制文件为example.cst。

```shell
sh make_csts.sh example.pdb > bbCA.cst
```



### 3 优化初始结构

运行优化命令: 

```shell
mpirun -np 4 rosetta_scripts.mpi.macosclangrelease @refine.flags -nstruct 100
```

输出的文件结果均在refinement文件夹中。

最终需要获取一个最优化的结构，**并将这个结构重命名为lowest_energy.pdb。**



### 4 单点突变扫描

```shell
mpirun -np 4 rosetta_scripts.mpi.macosclangrelease @filterscan.flags
```

该过程会遍历计算每种突变类型的ddG值，结果会保存在resfiles文件夹的每个resfile中，不同的cutoff存到不同的文件里。可以根据需要修改resfile。



如: res_65B,13B.6, 最后的6就代表ddG小6.0时，特定若干位点上所有的符合条件的突变类型:

```txt
nataa
start
13	B	PIKAA	Y
65	B	PIKAA	AGIST
```

13号位点有1个氨基酸突变类型，65号位点有5种突变类型。



### 4 穷举所有突变

```python
python gen_mutate_jobs.py $level
```

$level: 分为0、0.5、1、1.5、2、2.5、3、3.5、4、4.5、5、5.5、6等若干级别。

$level值与单点突变的ddG值截断值直接对应。选取对应的level值，使得穷举量在10000以内较为合适。

打开job.list，其中记录了每条穷举的突变计算命令，如:

```shell
rosetta_scripts.mpi.macosclangrelease @mutate.flags -out:suffix _0000 -parser:script_vars target0=13B new_res0=TYR target1=65B new_res1=ILE 
```

运行其中的一条命令后，将获得组合突变的pdb结构以及其对应的打分。结果文件均储存在out文件夹中。文件分别为score_0000.sc，以及lowest_energy_0000_0001.pdb。

如需并行计算job.list中所有的命令可使用，



最后通过再对所有结果进行排序和聚类得到突变体的建议。





## 三、结语

Funclib的计算方法是默认不放置目标底物分子的，因此构建出的是一个非特异性的酶序列库。如果催化的小分子目标明确，并且与晶体结构中的底物分子有共同的母核，就可以有针对性地进行设计酶活中心。这种情况可以跑两轮Funclib，第一轮就是为了塞进目标底物，首先通过比对，将新的底物分子放置在酶活中心区域，并执行序列搜索，找到能够兼容新底物的基本口袋形状。将第一轮中能量最低的结构作为第二轮的输入，开始真正设计酶库，最后实验验证筛选。

此外，Funclib也有潜在风险，设计出来的酶库可能口袋会被填上。



最后附上官方的服务器网站: http://FuncLib.weizmann.ac.il. 如果任务量不大，也可以直接排队提交任务，耐心等待即可。