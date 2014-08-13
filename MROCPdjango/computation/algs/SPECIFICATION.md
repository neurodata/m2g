Collaboration specification for code contribution to MROCP
===========================================================

This document specifies standards to ensure code contributed to the repository is integrated with ease into the pipeline and attributed to all graphs produced in [graphML](http://graphml.graphdrawing.org/) format. Any derivative work by others that uses your algorithm must in turn cite you as you specify as shown in the `Code Spec` section.

Simply create a folder within this directory that includes your file(s). **NOTE**: If your code is licensed with a license incompatible with the [Apache version 2.0 license](http://www.apache.org/licenses/LICENSE-2.0) then your code cannot be included in MROCP. Once you complete **and test** your algorithm please submit a [pull request](https://help.github.com/articles/using-pull-requests). <br>

**NOTE:** The [graphML](http://graphml.graphdrawing.org/) format will only accepte attributes of type:
(a) string e.g. "val1"
(b) numerical e.g 1, 3.32, 4E-2
(c) boolean e.g True, False
(d) lists/vectors of type *a, b, c* 

No other formats are permitted.

An example of an algorithm written in `C++` is provided in the `example_alg` directory. Please see this example if confused about any of the instructioins provided below.

Code Spec
=========

Document the file
-----------------
1. Provide:
  - A brief description of the algorithm. 
  - A description of any external libraries (including version numbers) necessary to run your code placed in a `Dependencies` comment block. **NOTE:** *The fewer dependencies required, the faster your algorithm can be incorporated.*
  - A citation block containing who to cite if anyone uses the result of your algorithm. 

2. Document each function giving:
  - A description of its functionality.
  - A list of input args (and types if untyped language).
  - A description of returned values (and types if untyped language).
3. Format your code in as readable as manner as possible. For example:
  - Good code formatting:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.c}
  main(int riguing,char**acters)
  {
    int mod1 = 4796;
    int mod2 = 275;
    puts(1[acters-~!(*(int*)1[acters] % mod1 % mod2 % riguing)]);
  } 
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  - Not so good code:
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.c}
  main(int riguing,char**acters){puts(1[acters-~!(*(int*)1[acters]%4796%275%riguing)]);} 
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Submission checklist
--------------------
4. Your file must accept at least one argument (the graph file name) a an error (correct usage) message if the incorrect number (or format/type) of arguments are provided. For languages like `python` and `R` the `argparse` package is suitable for this purpose.

5. A `Makefile` for compiled languages that includes a `clean` rule.

FAQ
===
Q: What languages are accepted?
A: We accept all languages. *Caveat:* We do prefer, languages like `python`, `java, `C/C++`, `R` as they are ubiquitous and free.

Q: My code is written in a framework like FlashGraph, PowerGraph, Giraph -- can I still contribute?
A: Yes, we do accept common no-cost parallel code.

