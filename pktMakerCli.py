#!/usr/local/bin/python2.7
# encoding: utf-8
'''
packet tool -- generate the packet

This is a description

It defines classes_and_methods

@author:     dlashyang
        
@copyright:  2013 dlashyang. All rights reserved.
        
@license:    license

@contact:    dlashyang@outlook.com
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

from pktTool import gen_Packets

__all__ = []
__version__ = 0.1
__date__ = '2013-07-13'
__updated__ = '2013-07-28'

DEBUG = 0
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by YangLiu on %s.
  Copyright 2013 YangLiu. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument(dest="pkt_action", help="packet actions", choices=['create', 'delete', 'get', 'set'])
        parser.add_argument(dest="table_id", help="IE. 0x06000104")
        parser.add_argument(dest="values", help="values for setting or creating", nargs="?")
        parser.add_argument("-k", "--index", dest="index", help="Key item(Index) for the table, none for global")
        parser.add_argument("-i", "--item", dest="item_id", help="IE. 0x01")
        parser.add_argument("-v", "--verbose", dest="verbose", action="store_true", help="set verbosity level [default: %(default)s]", default=False)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        
        # Process arguments
        args = parser.parse_args()

        if args.verbose:
            print("Verbose mode on")
            print args

        # Main process
        gen_Packets(args)

        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-v")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = '111_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())