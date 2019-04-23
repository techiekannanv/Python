'''This script is used to compare file1 with file2'''


from __future__ import print_function
import argparse

parser = argparse.ArgumentParser(description="Compare file1 with file2 for specific fields")
parser.add_argument('--file1', action='store', dest='file1', required=True)
parser.add_argument('--file2', action='store', dest='file2', required=True)
parser.add_argument('--field1', action='store', dest='field1', required=True,
                    help="fields from file1 need to separate by ':'")
parser.add_argument('--field2', action='store', dest='field2', required=True,
                    help="fields from file2 need to separate by ':'")
argv = parser.parse_args()

