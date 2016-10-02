A small Python library for reading and writing Korg Volca FM/DX7 SysEx files.

(Work in progress.)

*Examples*

The examples assume a large corpus of example patches in the corpus/ directory. You can download suitable data from https://homepages.abdn.ac.uk/mth192/pages/html/dx7.html

1. examples/uniform.py
    Generates a bank of random 32 patches, each with parameters distributed uniformly over the allowed range.

2. examples/statistics.py
    Generates a bank of random 32 patches, each with parameters distributed independently with the probability distributions determined by the marginal distributions of parameters in the corpus.

3. examples/markov.py
    Generates a bank of 32 patches by walking backwards from carriers to modulators assuming that for each parameter type, the values along the walk form a Markov chain whose staistics come from the corpus. (For now, in the case when a modulator modulates more than one operator, the choice of predecessor for the modulator depends on the order in which the operators are walked.)
