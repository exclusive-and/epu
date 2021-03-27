# EPU: A Minimalist Educational Computer

A lot of people ask me how they can learn programming, improve their programming skills, or develop greater intuition about computers.
Well here you go: a CPU I've designed specifically to trim everything excess (compilers, operating systems, pipelining, superscalar execution, multithreading - everything).
With EPU, it's just you and the processor.

The instruction set with only 10 instructions offers a vast simplification over other assemblers out there.
Even RISC architectures like RISC-V and ARM have complicated assembly languages with dozens of instructions.
EPU has only a handful, with no fancy annotation, in hopes that this simplified form makes assembly accessible to learners.

I like assembly programming as an introduction to programming because, as I've noted, it gets you up close and personal with the computer.
To write any program in assembly language, you need to think like a computer: step by step.
This closeness to the machine encourages the development of intuition about phrasing programs as sequences of computations.
That intuition is indispensible to a good programmer.

# Components

## EPU

A very simple CPU built in the digital logic simulation software Logisim.

## EASM (WIP)

A hand-written assembler written in Python to compile programs written in human-readable assembly language to machine code that EPU can understand.

# Requirements

## EPU

 - Logisim Evolution version 3.3.0  (https://github.com/reds-heig/logisim-evolution/releases/tag/v3.3.0)

## EASM

 - Python 3.6 or later (https://www.python.org/downloads/)
 
# Notes

I'll be working on a nice guide to writing programs and assembling them with EASM, which will be uploaded here once the assembler is in a working state.
I'll also be putting together a guide on how to use EPU in Logisim, including loading compiled programs, simulating the processor's execution, and inspecting the different components to see how code actually gets executed.
This is all a work in progress.

# Collaboration and Contribution

If you have experience with CPU design, assembly, or Logisim, I welcome any contributions to this project.
If you do contribute, make sure to keep it simple: this is all educational, and needs to be accessible to people with only minimal experience with computers.

# Issues

Github has an issues section - if you find an issue, spot a bug, have any suggestions, please open an issue and describe the details and I'll get around to it.

# Licensing

I haven't decided on a license yet.
I hope this gets spread far and wide, so I want to choose a license that's as open and as accessible as possible.
Current front-runner is the BSD-2 license; if you know any better ones please open an issue and title it something containing "License Suggestion".

# Acknowledgements

Any contributors will have their names added to this section.

 - exclusive-and : Project author, main EPU designer and maintainer, lead EASM designer and maintainer
 - LordDecapo : because I love him
 - and you <3
 


