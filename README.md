# Recruitment-case

## Set Up
A python environment is required to perform this assignment. If not yet available please install python via your
preferred way or follow this [tutorial](https://realpython.com/installing-python/).

Once you have set up your (virtual) environment, you'll need to install a few basic packages which are specified in 
`requirement.txt`. Installing the packages can be done by running following pip command: `pip install -r requirements.txt`

## Assignment Notebook
The assignment Jupyter Notebook (`assignment.ipynb`) will be your starting point which contains a first version 
including a naive solution. Once you have set up a running python environment you should be able to open this
notebook and run all cells.

## Data
This repo contains two CSV files and can be found in the `data` directory:
- orders.csv
- assortment.csv

A set of shop orders and a stock allocation is required to run a simulation. To create an allocation you can use the 
assortment dataset. However, a naive solution is already given that uses the assortment.csv to create a stock allocation.
It is up to you to improve this stock allocation.

## Simulation
In the assignment notebook a `simulate` function is imported. You can use this simulate function to run a simulation on 
a set of shop orders to evaluate your stock allocation. All simulation code can be found in `src` directory although this
assignment focuses on improving the stock allocation.