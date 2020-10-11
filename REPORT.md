# Distributed Systems 

# Project2: Distributed File System

## Authors

Mikhail Olokin: m.olokin@innopolis.univeristy

Nikita Smirnov: n.smirnov@innopolis.university

Pavel Tishkin: p.tishkin@innopolis.university

# Introduction

The problem of data storage was topical, since the creation of computers. The questions of where to store, how to store and how to make an access to the files fast are still actual. In the past, it was necessary to make an efficient system to store user's files, make its processing fast, etc. This problem was solved via Virtual Memory, Hierarchy of Storage and other techniques. Nowadays, Big Companies, such as Google, Netflix, Amazon have come to another issue: how to store Big Data, coming from mobile devices, local stores and  make use of it to enhance the user experience, fasten delivery of the products. This project is done to access the problem of storage of files. The team was asked to implement a Distributed File System, using any programming language.

## Architecture of DFS



## Problems during Implementation of DFS

During the execution if the project, our team has faced the following Problems:

### Changes in request/response Models

Our first choice for networking implementation was Flask. But it soon became clear that changes in request/response models require a lot of extra work from each side.

To make our lives easier we decided to rewrite the code using Fast API, which supports python library pydantic that eases the creation of models.

### Delete when Replicate, Move, Copy

Python Fast API supports asynchronous methods, which greatly reduced the complexity of implementation but it brought one serious issue with the work of the system: What if user decides to delete a file, when it is being replicated by primary storage node to secondary storage node?

To solve the problem, we decided to let Server have an access to the remote Database of the name node to query one thing: check if file exists after preforming replicated save to ensure that the file is not deleted during the replication process.