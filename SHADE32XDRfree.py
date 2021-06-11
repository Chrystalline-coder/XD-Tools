'''
This proramme imports Hydrgen-ADPs from a SHADE .cif file to a xd.res file,
creating a xd.inp file, performing xdlsm with cycle -5 for all sets in a
XDRFREE bulk as an intermediate step for XDRFREE.
written by Christian Schuermann.
'''

import re, os, fnmatch, glob
from subprocess import Popen,PIPE,STDOUT
from shutil import copy

def run_prog(prog,XDName):
    p = Popen([prog,XDName],stdout=PIPE,stderr=STDOUT,bufsize=1)
    p.wait()
    print 'xdlsm done'

def changemas(mas):
    with open(mas, 'r') as rfile:
        lines = rfile.readlines()
        with open('xd.mas','w') as ofile:
            for line in lines:
                if line.startswith('TITLE'):
                    title = line.split()[1]
                if line.startswith('SELECT  cycle'):
                    items = line.split()
                    items[2] = '-5'
                    ofile.write('  '.join(items) + '\n')
                elif re.match('H\(\S+\)\s+C\(\S+',line):
                    line = re.sub(r'\s+1','   2',line)
                    ofile.write(line)
                else:
                    ofile.write(line)
    return title

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
                if lines[i-1].startswith('H('):
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
    maindir = os.getcwd()
    cif = select('*.cif')
    adp = read_cif(cif)
    number = raw_input('please give xd**.mas/xd**.res number to perform HADP-insertion with: ')
    number = int(number)
    res = 'xd{:>02}.res'.format(number)
    newres = 'xd{:>02}_pre_SHADE-ADP.res'.format(number)
    nextinp = 'xd{:>02}.inp'.format(number+1)
    mas = 'xd{:>02}.mas'.format(number)
    for set in sorted(glob.glob('[0-9][0-9]')):
        print '################ set {:>02} ###############'.format(set)
        os.chdir(maindir + '/' + set)
        copy(res,newres)
        write_2_res(newres,'xd.inp',adp)
        title = changemas(mas)
        run_prog('XDLSM',title)
        write_2_res('xd.res',res,adp)
        copy(res,nextinp)
    


