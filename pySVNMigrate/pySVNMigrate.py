#!/usr/bin/env python3
################################################################################
#
# pySVNMigrate.py
#
# Author: Chris Mason
#
# Description: Functions to assist in migrating SVN repos from server to server
#
################################################################################

import os
import sys
import re
import subprocess

def _swap_pairs_in_external(external):
	pathpairs = list(external.splitlines())
	retval = ''
	for pair in pathpairs:
		retval += pair.split()[1] + ' ' + pair.split()[0] + '\n'
	return retval


def modify_externals(repo, oldbase, newbase):
	""" Takes a path to a repo and searches it for externals, changing any 
	svn:externals found that contain oldbase into newbase.  
	Also switches any svn:externals that are using the old SVN format 
	where file and URL are swapped into using the new one. """

	#check out repo 
	fixedrepo = re.sub('^file://', '', str(repo + "_fixed"))
	retval = subprocess.call(["svn", "checkout", "--ignore-externals", repo, fixedrepo])
	if retval != 0:
		print("Checkout Failed :( ")
		return retval

	#get list of externals
	myexternals = subprocess.check_output(["svn", "propget", "-R", "svn:externals", fixedrepo]).decode()

	#parse list
	myexternals = list(filter(None, re.split("\n\n+", myexternals)))
	myextdict = []
	for pairing in myexternals:
		myextdict.append(re.split(' - ', pairing))
	myextdict = dict(myextdict)

	#make the externals path changes
	for key in myextdict:
		#check format, swap URL / file positions if old bad format
		if re.match('\A\S+ [./^]', myextdict[key]) or re.match('\A\S+ \S+://', myextdict[key]):
			myextdict[key] = _swap_pairs_in_external(myextdict[key])
		myextdict[key] = myextdict[key].replace(oldbase, newbase)
		retval = subprocess.call(["svn", "propset", "svn:externals", myextdict[key], key])
		if retval != 0:
			print("svn propset failed :(")
			return retval
	return 0


if __name__ == "__main__":
	modify_externals(sys.argv[1], sys.argv[2], sys.argv[3])

