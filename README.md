# Agent simulation for historical linguistics
This program simulates interaction between agents (language speakers) of Old Norse,
with probabilities extracted from an Old Norse corpus. Intrusive Middle Low German
agents can be added, to simulate language contact


## Run agent simulation
To run an agent simulation, issue the following command:

```
python agents.py --lm_icelandic <ICELANDIC_PICKLE>
```

### Pickle
`<ICELANDIC_PICKLE>` is the pickle containing Icelandic/Old Norse (the basis language) language model probabilities. Pre-generated pickles are available in the `pickles` folder, the next section describes how to generate those from a corpus.

You could use `pickles/lm-icelandic-merged.p/` as pickle for the language model with most construction and function types. Pickles ending in `-order` add word order as feature. Pickles ending in `-fmerged` reduce the number of constructions and functions, `-fmerged-dropdetails` further reduces the number of categories by not taking into account the details of a construction (preposition form or noun ending).

### Settings
Several settings can be changed via command line options, such as the number of iterations and the number of agents. `python agents.py --help` shows the available options. The standard values for the command line arguments are listed in the source code, at the top of `agents.py`.

### Intruders
To add (Middle Low German) intruders, use the `--lm_intruders <INTRUDERS_PICKLE>` flag. `<INTRUDERS_PICKLE>` is the pickle file containing the pickle of the intruders. File names follow the same pattern as the Icelandic (basis language) pickles. The number of intruders, number of intruder batches and the intervals between the batches can be set using command line arguments. Issue

### Plots
Plots of the distribution *p(construction)* are generated and stored in the `plots/` folder. Plots of the conditional distributions *p(construction|function)* are stored per function in the `plots/<FUNCTION>/` folder.

## Generate language model pickles from corpus
It is possible to generate the language model pickles from corpora. The Icelandic language model is generated from two sources: the Saga corpus, for constructions/functions which can be automatically processed, and a qualitative, manually-annotated file which contains manual annotations for constructions/functions from the Saga corpus which could not be automatically detected. The Middle Low German language model only depends on a manually annotated input file.

Follow the following steps:
 - Download the [Saga corpus](http://malfong.is/index.php?lang=en&pg=fornritin). Extract the contents of the .zip archive in a directory under the Agent simulation working directory, for example `Saga`
 - Issue the following command, to generate all language model pickles (with coarse- and fine-grained categories):

```
python counts.py --saga_input_dir Saga --qual_icelandic corpus/20170103-qualitative-icelandic.csv --qual_intruders corpus/20170103-qualitative-mlg.csv
```

`--saga_input_dir` should be the place where the Saga corpus was downloaded. An `--output_dir` can also be specified, this is `pickles` by default.

# Authors
Simulation code written by Peter Dekker (firstname AT firstnamelastname DOT eu), with contributions on corpus extraction by Myrthe Bil. The manual annotations of Icelandic and Middle Low German data were performed by Justin Case.
