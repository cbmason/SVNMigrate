#!/bin/bash

# usage: ./load_repos.sh <list of dumpfiles>

while read line
do
	CURREPO=${line/_*//}
	echo "loading $line into $CURREPO"
	svnadmin load --force-uuid $CURREPO < $line
done < $1


