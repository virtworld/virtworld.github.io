<!-- 
.. title: G53COM Computability 可计算性 复习笔记
.. slug: g53com-computability-revision-notes
.. date: 2014/06/01 20:54:42
.. tags: Computability
.. link: 
.. description: 
.. type: text
-->

*内容基于 G53COM 1314 年度的课件，讲师为 [Dr Andrew Parkes](http://www.cs.nott.ac.uk/~ajp/)*  
*这篇文章**并非**标准答案. 任何定义，解释和示例可能是不准确的或者错误的。请参考您自己的笔记和课件。*  
*因为原始的笔记是用英语写的，有些术语也不清楚中文叫什么，就不翻译了。*

# 1. 定义

## 问题分类

* **NC** is a set of problem that can be solved in polylog time using polynomial a number of processors.
* **DTIME(f(n))** is a set of problem that can be solved using some DTM in time f(n).
* **P = U<sub>k</sub> DTIME(n<sup>k</sup>)** is a set of problem that can be solved using a DTM in any polynomial time.
* **P-hard**: if a problem X is said to be P-hard iff all problems within P can be reduced to X using polylog time on a polynomial number of processors.
* **P-complete**: if a problem X is said to be P-complete iff it is in P and it is P-hard.
* **NTIME(f(n))** is a set of problem that can be solved using some NDTM in time f(n).
* **NP = U<sub>k</sub> NTIME(n<sup>k</sup>)** is a set of problem that can be solved using some NDTM in any polynomial time. A language is accepted by a NDTM is a set of strings that there exists one or more than one execution path of NDTM that gives yes.
* **Reduction from X to Y**: convert any instance of X to some instance of Y.
* **NP-hard**: if a problem X is said to be NP-hard iff any problem in NP can be reduced to X in polynomial time.
* **NP-complete**: if a problem X is sad to be NP-complete iff it’s in NP and it’s NP-hard.
* **DSPACE(f(n))** is a set of problem that can be solved using some DTM with space f(n).
* **PSPACE = U<sub>k</sub> DSPACE(n<sup>k</sup>)** is a set of problem that can be solved by a DTM using polynomial space.
* **PSPACE-hard**: if a problem X is said to be PSPACE-hard iff any problem in PSPACE can be reduced to X within polynomial time.
* **PSPACE-complete**: if a problem is PSPACE-complete if it is in PSPACE and it is PSPACE-hard.
* **NSPACE(f(n))** is a set of problem that can be solved using some NTDM with space f(n).
* **NPSPACE = U<sub>k</sub> NSPACE(n<sup>k</sup>)** is a set of problem that can be solved using a NTDM with polynomial space.

## 关系

**NC ⊆ P ⊆ NP ⊆ PSPACE = NPSPACE**

* **P ⊆ PSPACE**, because a poly time TM cannot use more than polyspace (space can be reuse, but time cannot). 
* **NP ⊆ PSPACE**, a NDTM can be seen as an execution tree with polynomial height, any one execution path has a length of at most polynomial time. We can solve NP problem in PSAPCE by using DFS to explore the tree of possible executions due to non-determinism. Hence NP in PSPACE. 
* **Savitch’s theorem**: NSPACE(f(n)) ⊆ DSPACE(f(n)<sup>2</sup>)  
* **Prove PSPACE = NPSPACE**  
      NSPACE(f(n)) ⊆ DSPACE(f(n)<sup>2</sup>) by Savitch  
      NPSPACE = U<sub>k</sub> NSPACE(n<sup>k</sup>) by def.  
      => NPSPACE ⊆ U<sub>k</sub>DSPACE(n<sup>k</sup>)  
      => NPSPACE ⊆ PSPACE  
      It is trivial that PSPACE ⊆ NPSPACE.  
      Hence, NPSPACE = PSPACE  

# 2. 图灵机，列举和可解决性
## Deterministic Turing Machine. 
Turing machine is a model of computation that consists of a 7-tuples  
<table>
    <tr><td>Q</td><td>A finite set of states</td></tr>
    <tr><td>Γ</td><td>A finite set of tape alphabet</td></tr>
    <tr><td>q0 ∈ Q</td><td>An initial state</td></tr>
    <tr><td>F ⊆ Q</td><td>A set if final states</td></tr>
    <tr><td>b ∈ Q</td><td>A blank symbol</td></tr>
    <tr><td>Σ ⊆ Γ \ b</td><td>A set of input symbols</td></tr>
    <tr><td>δ: Q \ F x Γ -> Q x Γ  x {L, R, N}</td><td>A Transition function that takes a state (not final one) and a tape symbol, returns a new state, a new tape symbol and movement which is left, right or stay.</td></tr>
</table>
A TM is deterministic if and only if the action for any current state q and any symbol that can occur when the machine is in state q is unique. An action is 5-tuples: (current state, current tape symbol, new state, new state and direction of move)  

## Universal Tuning Machine
**Motivation and concept** For every new problem, we need a TM to solve, but general purpose computer can execute any program that stored on hard disk. A Universal Turning Machine acts as an interpreter that takes e(M) and executes it on input s.  
**Construct and work.** UTM uses fixed states, alphabet and transitions. The program M encodes the set of tuples of an arbitrary TM with arbitrary states and program. The input of the target TM is also stored on tape as s. UTM runs on e(M)&s, keeps track of simulated head of M and its real head, keeps track of current state of target TM.

## Non-Deterministic Turing Machine. 
Non-deterministic Turing Machine is a Turning Machine that has more than one possible transition for a given state and a tape symbol. This means for more than one execution path. An NDTM M is said to accept a string s if and only if there is some execution path that leads to halting with yes. Usage: It is the vital concept to the NP definition.  
Simulate NDTM with DTM: Breadth First Search or iterative deepening on NDTM

## REC and RE
A language L is decided by a Turing Machine M if and only if:  

* s in L implies M is guaranteed to halt with yes.  
* s not in L implies M is guaranteed to halt with no.

If a Turning Machine is existed with such property, then L is **Recursive Language (REC)**.  
A Language L is accepted by a Turing Machine M if and only if:  

* s in L implies M is guaranteed to halt with yes.  
* s not in L implies M either halt with no or it never halt.  

If a Turning Machine is existed with such property, then L is **Recursive Enumerable (RE).**  

## Enumerate strings of a language
Enumerating strings of language L means explicitly produce the elements of L and put it into a list (print it). This requires only the strings that belongs to L are printed, and all strings in L are eventually printed.

## Give and explain a method to enumerate the strings of a REC
The method is generate and test. Generate all string s in the REC, test each s by a TM and print out those given a ‘yes’.
```
Repeat
    Generate a string w
    Check if w belongs to L by a TM. If yes, print w; if no, ignore w.
```

## Give and explain a method to enumerate the strings of a RE
The idea is still generate and test but run each test on a separate thread. The number of thread is unbounded but always finite, any element of L will be printed out in finite time, because the ‘yes’ is guaranteed to halt.  
```
Assume TM1 accepts language L;
    A TM2 generate new string s, and start a new thread for each one that runs TM1 on string1;
    Run each thread for some number of steps. 
        If one thread halt, print yes; If not halt, just carry on.
```

## Halting problem and its importance
Given a TM M and an input string x, let e(M) be the encoding of M. Does there exist an effective procedure (computable function) for deciding, for every pair (e(M), x) that does M halt for x?

It is equivalent to ask whether the language L = {e(M)&s | M halts for s} is recursive (it is RE)?

The proof of the unsolvability of many problems relies on the unsolvability of Halting problem.

## Halting theorem: The Halting problem for Turing machine is unsolvable.
Assume the Halting problem is solvable, then there exists a Turing machine H that decides the Halting problem. If H can solve the Halting problem for input e(M)&x, H should be able to solve the Halting problem for input e(M)&e(M).

Let H’ be a Turing machine that takes e(M) and makes a copies to obtain e(M)&e(M). Then the H’ execute H with the input e(M)&e(M), but in the case that M halts (that is H halts with yes), H’ loops forever.

If the input of H’ is e(H’), then 

* If H’ halts for e(H’), then H answers yes and H’ loops for ever.
* If H’ does not halts for e(H’), then H answers no and H’ halts.

Both give a contradiction. Neither H nor H’ exists, hence Halting problem is unsolvable.

Note1: Halting theorem says for any fixed reasoning system, there are instances on which it fails. But NOT says, there are instances for which all reasoning systems fail.

Note2: [WRONG] For any TM M and input, there does not exist a TM H decides whether M halts.
For a single pair of TM and input, there are always a TM that gives either yes or no, but we don’t know which one.

## The general structure/technique of the prove: Self-reference with a twist.
In the uncountability of real number, we take the entries of diagonal and twist it by adding one to each entries. 

In the barber paradox, the problem is the self-reference with negation in defining the set of people shaved by the barber.

## Decision Problems and Reduction
Decision problem can be states as a question of some formal system with yes/no answer.

If the decision problem is solvable, then there exist a TM that for every instance of the problem, it halts with output yes or no.

pi reduced to pi’ = An algorithm to solve pi’ can be directly used to solve pi. 

* If pi reduced to pi’ and pi’ is solvable then pi is solvable.
* If pi reduced to pi’ and pi is unsolvable then pi’ is unsolvable.

## Empty word halting problem
Give a TM M. Does M halt on epsilon? 

Proof: (1) show eHP reduced to HP. (2) Assume eHP is solvable. (3) HP is solvable -> contradiction.

Assume an instance of HP, M and x; an instance of eHP, M’ and empty string e. M’ first write x onto its tape to simulate M. (eHP reduce to HP). If we can show M’ halts on e, then M halts. This is a contradiction to Halting theorem. Therefore, eHP is unsolvable.

# 3. NP-hardness and Reductions
## Polynomial time reduction and how reduction are used to show problems are in NP-complete
Given any instance of a problem class X.

Computer an instance f(x) in problem class Y with the conversion done in polynomial time and the answer preserved, i.e., ans(x) = yes if fans(f(x)) = yes.

To show NP-complete, we need to show NP-hard. If a problem is said to be NP-hard iff all problems in NP can be reduced to it in polytime.

## Decision Problems

* [SAT](http://en.wikipedia.org/wiki/Boolean_satisfiability_problem)
* [k-SAT](http://en.wikipedia.org/wiki/Boolean_satisfiability_problem#3-satisfiability)
* [MONOTONE-k-SAT]
* [KNAPSACK]
* [BIN PACKING]
* [HAMILTONIAN CYCLE]
* [TSP(D)]
* [CIRCUIT SAT]
* [SUBSET SUM](http://en.wikipedia.org/wiki/Subset_sum_problem)
* [NUMBER PARTITION]
* [GRAPH COLOURING]
* [INDEPENDENT SET]
* [CLIQUE]
* [VERTEX COVER]

## Prove SAT is HP-hard(informal, read more on [Cook-Levin Theorem](http://en.wikipedia.org/wiki/Cook%E2%80%93Levin_theorem))
If SAT is NP-hard, then every problem in NP can be reduced to SAT in polynomial time. 

According to the definition of NP problem, this means:  
Given an input s of size n, an arbitrary NDTM M that run in polynomial time p(n).

We need to convert the NDTM and input into a SAT formula in polynomial time, such that the NDTM has an accepting computation if and only if the SAT formula has a satisfying assignment.

1.  Using variables in the form of function of time t to describe states

    * x(i, t) = 1 iff the machine in state i at time t  
    * y(i, k, t) = 1 iff the tape element i has value k at time t  
    * z(i, t) = 1 iff the head is at position i at time t  

    If all values of these variables are given, then the execution sequence of NDTM is given.

2.  The transition to reach state at time t + 1 only depends on state at time t and a non-determinism choice w(c, t) meaning choice c at time t.
These could be expressed using polynomial size clauses. 

The NDTM is converted into a polysize SAT formula containing variables describing the states as a function of time and allowing the need of non-determinism. The SAT formula has a satisfying formula iff there is some sequence of states of the NDTM that lead to acceptance.
 

*(未完待续...)*