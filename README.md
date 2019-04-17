# Net2Text

This repository contains the code to generate the datasets used in the
NSDI'18 submission of the [Net2Text project](https://net2text.ethz.ch).

## Generating a Dataset

The script [examples/generator/example_generator.py](examples/generator/example_generator.py)
allows you to generate all the forwarding paths and flows for a given
number of prefixes and egresses.

The output consists of two files:

1. A dump of all paths (aggregated forwarding tables): ndb_dump.out
2. The topology: ndb_topo.out
3. A config file containing all settings for Net2Text

### Running the Script

```bash
$ python example_generator.py <graph_file> <output_path> [--automatically] [--debug]
```

#### Arguments

* __graph_file__ name of the file containing the graph in graphml format (e.g., from [TopologyZoo](http://www.topology-zoo.org/dataset.html)
* __output_path__ path to the directory where the output should be stored
* __-a/--automatically__ automatically generate names and pick egresses, if it is not specified, you have to provide
for each node in the graph the name and pick the egress routers manually.
* __-d/--debug__ enable debug output

__Note:__ to limit the number of prefixes used in the dataset, just
edit line 72 in `example_generator.py`.

### Helper Scripts

* `example_test.py` - check basic information of a generated example
(e.g., number of nodes, prefixes, prefixes per destination) and compute
the score of different summaries.

## Loading a Dataset

Use the scrip `load_example.py` to load a dataset from the generated files.

### Running the Script

```bash
$ python load_example.py <path>
```

#### Arguments

* __path__ path to the directory containing the generated files.


## Example using ATT NA

### Generating the Dataset

```bash
$ cd examples/generator
$ python example_generator.py ../att_na/AttMpls.graphml ../att_na -a
```

Now, you should have all the files in the directory `examples/att_na_X`
where X is the number of prefixes specified in line 72 of the generator
script.

### Loading the Dataset

```bash
$ cd ../..
$ python load_example.py examples/att_na_1000
```
