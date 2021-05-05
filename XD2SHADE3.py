# -*- coding: utf-8 -*-
"""
Created on Apr 2017

@author: cschuermann
"""
from __future__ import print_function
import os,re


if __name__ == '__main__':
    #print '''This script is for the preparation of cif-files, compartible to the SHADE3 server from xd_archive.cif. 
	#Please use xdcif to provide the xd_archive.cif In order to convert the SHADE-results back to XD format, please use SHADE2XDpy'''
    xdcif = raw_input('Please give the *.cif from XD [xd_archive.cif]: ') or 'xd_archive.cif'
    shadein = raw_input('Please give the filename for shade [shade_in.cif]: ') or 'shade_in.cif'
    Z = raw_input('Please give the number of Z [2]: ') or '2'
    line = open(xdcif,'r').readlines()
    
    if shadein in os.listdir('.'):
        try:
            os.remove(shadein)
        except: 
            print('there has benn an issue deleting the old file.'
                + 'Please make sure, it is not opened in another process')
    with open(shadein,'w') as ofile:
        copy = False
        for i, actual_line in enumerate(line):
            if actual_line.startswith('data_'):
                copy = True
            if line[i].startswith('#                   CRYSTAL INFORMATION'):
                copy = False
            if line[i].startswith('#                   ATOMIC TYPES, COORDINATES AND THERMAL PARAMETERS'):
                copy = True
            if i < len(line)-2 and line[i+1].startswith('    _atom_site_anharm_GC_C_label'):
                copy = False
            if copy: 
                if i == 0:
                    ofile.write(actual_line)
                    continue
                if actual_line.startswith('data_'):
                    split = actual_line.split()
                    ofile.write(split[0] + '\n_diffrn_ambient_temperature		100(2)\n')
                elif actual_line.startswith('_cell_volume'):
                    ofile.write(actual_line)
                    ofile.write('_cell_formula_units_Z                   ' + Z + '\n')   
                elif line[i-1].startswith('    _atom_site_U_iso_or_equiv'):
                    if not line[i].startswith('    _atom_site_adp_type'):
                        ofile.write('    _atom_site_adp_type\n')
                    ofile.write(actual_line)
                elif line[i].startswith('    _atom_site_symmetry_multiplicity'):
                    if not line[i+1].startswith('    _atom_site_type_symbol'):
                        ofile.write(actual_line)
                        ofile.write('    _atom_site_adp_type\n')
                    else: 
                        ofile.write(actual_line)
                elif re.match('H\(\w+\)(\s\d\.\d+){3}\s+\d\.\d+',line[i]):
                    split = actual_line.split()            
                    ofile.write(" ".join(split[:5]) + ' Uiso ' + " ".join(split[5:]) + ' H \n')
                elif re.match('[A-Z]\(\w+\)(\s\d\.\d+\(\d+\)){3}\s+\d\.\d+\s+\d\s\d',line[i]):
                    atype = re.search('([A-Z])\(\w+\)(\s\d\.\d+\(\d+\)){3}\s+\d\.\d+\s+\d\s\d',line[i]).group(1)
                    split = actual_line.split()
                    ofile.write(" ".join(split[:5]) + ' Uani ' + " ".join(split[5:]) + ' ' + atype + '\n')
                else:
                    ofile.write(actual_line)
                    
    with open(shadein, 'r') as file_obj:
        lines = file_obj.readlines()
    
    with open(shadein, 'w') as file_obj:
        for line in lines:
            match = re.match(r'([a-zA-Z]{1,2})\((\w+)\)(.+)', line)
            if match != None:
                file_obj.write(match.group(1) + match.group(2) + match.group(3) + '\n')
            else:
                file_obj.write(line)
            
            
            
            
    ofile.close()