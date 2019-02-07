# The Complex System of Vulnerabilities to Misinformation

* [Introduction](#introduction)
* [Datasets](#datasets)
  * [Domain Sharing on Twitter](#domain-sharing-on-twitter)
  * [Political Valence](#political-valence)
  * [Misinformation Domains](#misinformation-domains)
* [Set Up Python and Modules](#set-up-python-and-modules)
* [Execute Workflow](#execute-workflow)
* [Contact](#contact)

## Introduction

In this repository, you can find code and instructions for reproducing the plots from *The Complex System of Vulnerabilities to Misinformation* by Filippo Menczer and Dimitar Nikolov.

To start, clone the repo:

```
$ git clone https://github.com/dimitargnikolov/twitter-bias.git
$ cd twitter-bias
```

You should run all subsequent commands from the directory where you clone the repo.

## Datasets

There are three datasets you need to obtain. Before you begin, create a `data` directory at the root of the repo.

```
$ mkdir data/
```

### Domain Sharing on Twitter

This dataset contains a set of domain sharing actions that occurred on Twitter during the month of June 2017. The dataset is accessible at [Zenodo](https://zenodo.org/record/2558687). Download the `domain-shares.json` file from the link and put it into the `data` directory.

### Political Valence

This is a [dataset from Facebook](http://science.sciencemag.org/content/348/6239/1130), which gives political valence scores to several popular news sites. You can request access to the dataset from [Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/LDJ7MS). Once you have access, put the `top500.csv` file into the `data` directory.

### Misinformation Domains

This is a dataset of manually curated sources of misinformation available at [OpenSources.co](http://www.opensources.co). Clone it from Github in your `data` directory.

```
$ git clone https://github.com/BigMcLargeHuge/opensources.git data/opensources
```

## Set Up Python and Modules

Make sure you have [Python 3](https://www.python.org/) installed on your system. Then, set up a `virtualenv` with the required modules at the root of the cloned repository:

```
$ virtualenv -p python3 VENV
$ source VENV/bin/activate
$ pip install -r requirements.txt
```

From now on, any time you want to run the analysis, activate your virtual environment with:

```
$ source VENV/bin/activate
```

## Execute Workflow

The replication code is contained in the `.py` files in the `scripts` directory. You can automate their execution with the provided `Snakemake` file:

```
$ cd workflow
$ snakemake -p
```

The execution will display the actual shell commands being executed, so you can run them individually if you want. You can inspect the `workflow/Snakemake` file to see how the inputs and outputs for each script are specified. At the end of the execution, the generated plots will be in the `data` directory.

## Contact

If you have any questions about running this code or obtaining the data, please open an issue in this repository and we will get back to you as soon as possible.
