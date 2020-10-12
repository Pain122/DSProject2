# Distributed Systems 

# Project2: Distributed File System

## Authors

Mikhail Olokin: m.olokin@innopolis.univeristy

Nikita Smirnov: n.smirnov@innopolis.university

Pavel Tishkin: p.tishkin@innopolis.university

# Introduction

The problem of data storage was topical, since the creation of computers. The questions of where to store, how to store and how to make an access to the files fast are still actual. In the past, it was necessary to make an efficient system to store user's files, make its processing fast, etc. This problem was solved via Virtual Memory, Hierarchy of Storage and other techniques. Nowadays, Big Companies, such as Google, Netflix, Amazon have come to another issue: how to store Big Data, coming from mobile devices, local stores and  make use of it to enhance the user experience, fasten delivery of the products. This project is done to access the problem of storage of files. The team was asked to implement a Distributed File System, using any programming language.

## How to run it

### How to run Client

To run the client, the user should clone the repository. You should install the requirements: 

```bash
pip install -r requirements.txt
```

Next, you should install command line interface, using pip:

```bash
pip install --editable .
```

Then, write, to list all available commands:

```bash
dfs --help
```

You are free to do anything from here.

We guess, it is our responsibility to handle servers and Name Node

## Architecture of DFS

### Overall structure of the DFS

![Overall Structure](https://imgur.com/oKXADSd.jpg)

If you have some problems with grasping the idea through this diagram, you can always refer to the diagrams presented below. They represent relations between each component of the system.

### Client-Name Node Communications

![Client-Name Node Diagram](https://imgur.com/McucT3g.jpg)

### Client-Server Communications

![Client-Server Diagram](https://imgur.com/flp76XH.jpg)

### Name Node-Server Communications

![Name Node-Server Diagram](https://imgur.com/zjn7etE.jpg)

### Name Node-Database Communications

![Name Node-Database Diagram](https://imgur.com/26DM4W9.jpg)

### Server-Server Communications

![Server-Server Diagram](https://imgur.com/Lic1SOp.jpg)



### Server-Database Communications

![Server-Database Diagram](https://imgur.com/Urm9Q7w.jpg)

## Description of Communication Protocols

It is possible to say that our communication is Transient. If one of the servers dies, the message to it is discarded and sent to the next server. Also, if Name Node dies, client receives an error message and needs to resend their file when server goes up.

Between Servers, Name Node and Clients, there is asynchronous TCP connection which ensures that messages are received.

## Some of the interesting features

Name Node

	- Some tasks may fail due to failure of nodes. They may come back later. It is possible to instantiate the incoming node as the new node, but our system can recover it from its previous state which is stored in the Database. It also keeps track of the pending tasks that were not executed (Probably works, in theory it should; Will be implemented in the next sprint). Here is the diagram of how it should be working:

![Recovery case](https://imgur.com/2rCPyoS.jpg)

Storage 

- As you have already known, it keeps folders only if file lies in these folders (eg. if user decides to store /ex1/ex2/file1.txt, it will create folders ex1, ex2. If user creates folder it will only be the logical folder on the server Database). You may have already asked yourself, what happens if we delete the file? Do folders remain in the system? The answer is no, in case there are no other files in these folders. For instance, let us assume that the system has files /ex1/ex2/file1.txt and /ex1/ex3/file2.txt at time t. If user decides to delete file2.txt at time (t+1), the file and folder ex4 will be deleted from the system. Below you can see the transition diagram:

![Delete Case](https://imgur.com/qIlumbI.jpg)

## Problems during Implementation of DFS

During the execution if the project, our team has faced the following Problems:

### Changes in request/response Models

Our first choice for networking implementation was Flask. But it soon became clear that changes in request/response models require a lot of extra work from each side.

To make our lives easier we decided to rewrite the code using Fast API, which supports python library pydantic that eases the creation of models.

### Delete when Replicate, Move, Copy

Python Fast API supports asynchronous methods, which greatly reduced the complexity of implementation but it brought one serious issue with the work of the system: What if user decides to delete a file, when it is being replicated by primary storage node to secondary storage node?

To solve the problem, we decided to let Server have an access to the remote Database of the name node to query one thing: check if file exists after preforming replicated save to ensure that the file is not deleted during the replication process.

## Work of Each Member of the Team

Smirnov Nikita:

- Name node and Database for operations
- Connection of Database to Server
- Testing

Pavel Tishkin

- Server Functionality (replicate, copy, move, etc.)
- Server Functionality testing
- Report Creation

Mikhail Olokin

- Client to all communications
- Command Line Interfaces
- Docker Containerization

## Link to GitHub repository

https://github.com/Pain122/DSProject2

## Link to Docker Hub images

https://hub.docker.com/sas