'''
This proramme imports Hydrgen-ADPs from a SHADE .cif file to a xd.res file,
creating a xd.inp file, performing xdlsm with cycle -5 for all sets in a
XDRFREE bulk as an intermediate step for XDRFREE.
written by Christian Schuermann.
'''

import re, os, fnmatch

def read_cif(cif):
    inlist = []
    adp ={}    
    with open(cif,'r') as rfile:
        lines = rfile.readlines()
        for i in range(len(lines)):
            if lines[i].startswith(' _atom_site_aniso_label'):
                while not lines[i].startswith(' H'):
                    if lines[i].startswith(' _atom_site_aniso_U'):
                        inlist.append(re.sub('\D',"",lines[i]))
                    i = i+1
                while lines[i].startswith(' H'):
                    line = lines[i].split()
                    adp[re.sub('[()]','',line[0])] =  [line[j] for j in [inlist.index('11')+1,inlist.index('22')+1,inlist.index('33')+1,inlist.index('12')+1,inlist.index('13')+1,inlist.index('23')+1]]
                    i +=1
            if lines[i].startswith('loop_'):
                rfile.close()
    return adp

def write_2_res(res,out,adp):
    with open(res,'r') as rfile:
        with open(out,'w') as ofile:
            lines = rfile.readlines()
            for i in range(len(lines)):
                if lines[i].startswith('H('):
                    lines[i] = re.sub(r' 1 ', ' 2 ', lines[i], count = 1)
                    ofile.write(lines[i])
                elif lines[i-1].startswith('H('):
                    atom = re.sub('[()]','',lines[i-1].split()[0])
                    try:
                        for j in adp[atom]:
                            ofile.write('{: >10}'.format(j))
                        ofile.write('\n')
#                        print atom + ' ADPs transfered'
                    except:
                        print 'Waring {} not cif'.format(atom)
                        pass
                else:
                    ofile.write(lines[i])
    print 'HADPs copied'

def select(key):
    list = []
    for file in os.listdir('.'):
        if fnmatch.fnmatch(file, key):
            list.append(file)
            list.sort()
    count = 1
    for entry in list:
        print [count], entry
        count = count+1
    selected_file = raw_input('Select ' + key +' : [1] ') or '1'
    selected_file = list[int(selected_file)-1]
    return selected_file

    
if __name__ == "__main__":
    cif = select('*.cif')
    res = select('*.res')
    out = raw_input('Please give a name to the output file [xd_shade.inp]: ') or 'xd_shade.inp'
    adp = read_cif(cif)
    write_2_res(res,out,adp)
    


