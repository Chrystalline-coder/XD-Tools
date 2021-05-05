from re import match,compile,escape,IGNORECASE
from os import devnull,path,mkdir,getcwd,chdir
from shutil import copy
from subprocess import call
from glob import glob
from zipfile import ZipFile
FNULL = open(devnull,'w')

#############################
####### Definitions #########
#############################
def XDPDF(atom):
  with open('xd.mas','r') as ofile:
    lines = ofile.readlines()
  wfile = open('xd.mas','w')

  replace = {'SELECT':'SELECT atom {} scale 1.0 orth\n'.format(atom),'GRID':'GRID 3-points *cryst\n','CUMORD':'CUMORD second third fourth\n'.replace(' ',' *',int(AtomTable[atom][0])-1)}
  active = False
  for line in lines:
    if 'MODULE XDPDF' in line:
      active = True
    if 'END XDPDF' in line:
      active = False
    if len(line.split()) > 0:
      if line.split()[0].strip('!') in replace and active:
        key = [key for key in replace if key in line and not replace[key] == None]
        wfile.write(replace.pop(key[0]))
      else:
        wfile.write(line)
  wfile.close()

def FIND_TABLE(lines,findtable,tablehead,endtable,offset,name,params):
  container = {}
  for num,line in enumerate(lines):
    if match(findtable,line) > 0: # find the Table head first
      start = num + offset
      end   = num + offset
      break

  for line in lines[start-offset:]:
    if match(tablehead,line) > 0:
      key    = [num for num,val in enumerate(line.split()) if val in name][0]
      values = [num for num,val in enumerate(line.split()) if val in params]
      break

  while not match(endtable,lines[end]): # find the next line with 'endtable'
    end += 1

  for line in lines[start:end]:
    col = line.split()
    if len(col) >= max(values):
      container[col[key]] = [col[x] for x in values]
    else:
      continue

  return container

########################
#######  Main  #########
########################

XDName = 'LEUCHTER'
# possible keys: ['X','Y','Z','U','GC3','GC4','M','D','Q','O','H']
to_check = ['GC3','GC4']
logname = 'XDcheckGC'
XDcheckGC_dir = 'checkpdf'

worknum = False
for file in sorted(glob('xd[0-9]*[0-9]*.res')):
  worknum = file.split('\\')[-1][2:4]
if not worknum:
  print 'no suitable files found!'
  raise SystemExit
worknum = '{:>02}'.format(raw_input('xd[{}]? '.format(worknum)) or worknum)

if worknum.upper() == 'NONE':
  worknum = ''
  with open('xd_lsm.out','r') as open_file:
    read_lsm = open_file.readlines()
else:
  try:# zipped
    zip = ZipFile('xd{:>02}.zip'.format(worknum),'r')
    with zip.open('xd{:>02}_lsm.out'.format(worknum)) as open_file:
      read_lsm = open_file.readlines()
  except IOError:# not zipped
    with open('xd{:>02}_lsm.out'.format(worknum),'r') as open_file:
      read_lsm = open_file.readlines()

logfile = '/'.join([XDcheckGC_dir,'xd{}_{}.lst'.format(worknum,logname)])
table = '/'.join([XDcheckGC_dir,'xd{}_{}_GC-Parameter.tsv'.format(worknum,logname)])
pdf_table = '/'.join([XDcheckGC_dir,'xd{}_{}_PDF.tsv'.format(worknum,logname)])

# find Atoms
findtable = compile('\s*ATOM\s+ATOM0\s+AX1\s+ATOM1\s+ATOM2\s+AX2\s+R/L\s+TP\s+TBL\s+KAP\s+LMX\s+SITESYM\s+CHEMCON\s*',IGNORECASE)
tablehead = findtable
endtable  = compile('\s*DUM\d+\s*|\s*END\s+ATOM\s*')
offset    = 1
name      = ['ATOM']
params    = ['TP']
AtomTable = FIND_TABLE(read_lsm,findtable,tablehead,endtable,offset,name,params)

# find parameter
tablehead = compile('\s*PARAMETER\s+OLD\s+SHIFT\s+NEW\s+SU\s+VAR\s+S/E\s*',IGNORECASE)
endtable  = '---'         # table ends here
offset    = 6             # table begins after offset number of lines from tofind
name      = ['PARAMETER'] # column entry used as dict key
params    = ['NEW','SU']  # which values in the table are to be saved

ParameterDict = {}
for atom in AtomTable:
  findtable = compile('\s*ATOM\s+#\s+(\d+)\s+<<<\s+({})\s+>>>\s*'.format(escape(atom)),IGNORECASE)
  ParameterDict[atom] = FIND_TABLE(read_lsm,findtable,tablehead,endtable,offset,name,params)

check_dict = {
          'X':'X',
          'Y':'Y',
          'Z':'Z',
          'U':'U[1-3][1-3]',
        'GC3':'C[1-3][1-3][1-3]',
        'GC4':'D[1-3][1-3][1-3][1-3]',
          'M':'M[0-1]',
          'D':'D[0-1][+-]*',
          'Q':'Q[0-2][+-]*',
          'O':'O[0-3][+-]*',
          'H':'H[0-4][+-]*'
             }

if not path.isdir(XDcheckGC_dir):
  mkdir(XDcheckGC_dir)
with open(logfile,'w') as log:
  print >> log, 'XDcheckGC: a script to check Gram-Charlier parameters\n'

sigma = 3.0
CheckParams = {}
with open(logfile,'a') as log:
    print >> log, '{:^6} {:^4} {:^4} {:^4}'.format('atom','par','sig','insig')
with open(table, 'w') as tab:
    tab.write(
    '\t'.join(['atom','par','sig','insig','C111/sig','C222/sig','C333/sig','C112/sig','C122/sig','C113/sig','C133/sig','C223/sig','C233/sig','C123/sig','D1111/sig','D2222/sig','D3333/sig','D1112/sig','D1222/sig','D1113/sig','D1333/sig','D2223/sig','D2333/sig','D1122/sig','D1133/sig','D2233/sig','D1123/sig','D1223/sig','D1233/sig'])+'\n')

gc3list = ['C111','C222','C333','C112','C122','C113','C133','C223','C233','C123']
gc4list = ['C111','C222','C333','C112','C122','C113','C133','C223','C233','C123','D1111','D2222','D3333','D1112','D1222','D1113','D1333','D2223','D2333','D1122','D1133','D2233','D1123','D1223','D1233']

for atom in sorted(ParameterDict):
    CheckParams[atom] = {}
    for check in to_check:
         has_param = False
         CheckParams[atom][check] = {'bad':[],'good':[]}
         regcheck = check_dict[check]
         for param in ParameterDict[atom]:
            if match(regcheck,param):
                 has_param = True
                 value = abs(float(ParameterDict[atom][param][0]))
                 esd   = float(ParameterDict[atom][param][1])
                 if value < sigma * esd:
                     CheckParams[atom][check]['bad'].append((param,value,esd))
                 elif value >= sigma * esd:
                    CheckParams[atom][check]['good'].append(param)
         if has_param:
             if check == 'GC3':
                 shift_over_sigma = [(float(ParameterDict[atom][x][0])/float(ParameterDict[atom][x][1])) for x in gc3list]
             if check == 'GC4':
                 shift_over_sigma = [(float(ParameterDict[atom][x][0])/float(ParameterDict[atom][x][1])) for x in gc4list]
             with open(logfile,'a') as log:
                 print >> log, '{:^6} {:^4} {:^4} {:^4} {}'.format(atom,check,len(CheckParams[atom][check]['good']),len(CheckParams[atom][check]['bad']),[x[0] for x in CheckParams[atom][check]['bad']])
             with open(table, 'a') as tab:
                 tab.write('{}\t{}\n'.format('\t'.join([atom,check,str(len(CheckParams[atom][check]['good'])),str(len(CheckParams[atom][check]['bad']))]),'\t'.join(str('%.2f' % abs(i)) for i in shift_over_sigma)))
    
copy('xd{}.res'.format(worknum),'{}/xd.res'.format(XDcheckGC_dir))
copy('xd{}.mas'.format(worknum),'{}/xd.mas'.format(XDcheckGC_dir))

PARENT = getcwd()
chdir(XDcheckGC_dir)
atom_pdf = {}
for atom in AtomTable:
  if int(AtomTable[atom][0]) > 2:
    print 'xdpdf: {}\t\r'.format(atom),
    pdfout = 'xd{}_{}_pdf.out'.format(worknum,atom)
    #atom_pdf[atom] = []
    if not path.isfile(pdfout):
      XDPDF(atom)
      call(['xdpdf',XDName],stdout=FNULL)
      copy('xd_pdf.out',pdfout)
    with open(pdfout,'r') as file:
      rfile = file.readlines()
    MIN = []
    MAX = []
    for line in rfile:
      if ' Total integrated negative probability ' in line:
        INP = line.split()[-2]
      if ' Integrated volume for negative probability' in line or  'Itegrated volume for negative probability ' in line:
        VNP = line.split()[-2]
      if ' Total integrated positive probability' in line:
        IPP = line.split()[-2]
      if ' Integrated volume for positive probability' in line or ' Itegrated volume for positive probability ' in line:
        VPP = line.split()[-2]
      if ' Section ' in line:
        MIN.append(float(line.split()[7]))
        MAX.append(float(line.split()[9]))
    if len(MAX) > 0:
      atom_pdf[atom] = {'MAX':max(MAX),'MIN':min(MIN),'INP':INP,'VNP':VNP,'IPP':IPP,'VPP':VPP}
    #copy('xd_pdf.grd','{}_pdf.grd'.format(atom))
print 'xdpdf: done.\t'
chdir(PARENT)


with open(logfile,'a') as log:
  print >> log,'''
XDPDF SUMMARY
INP: Total integrated negative probability [%]
IPP: Total integrated positive probability [%]
MAX: maximum PDF value
MIN: minimum PDF value
VNP: Integrated volume for negative probability [Angstrom**3]
VPP: Integrated volume for positive probability [Angstrom**3]
'''

with open(pdf_table,'w') as tab:
    tab.write('Atom\tINP [%]\tIPP [%]\tMAX\tMin\tVNP\tVPP\n')

for a,b in sorted(atom_pdf.items()):
  for c,d in sorted(atom_pdf[a].items()):
    first = ''
    last = ''
    if c == 'INP':
        first = a
    elif c == 'VPP':
        last = '\n'
    with open(logfile,'a') as log:
      print >> log, '{:>5} {:>5} {:>10} {}'.format(first,c,d,last)
with open(logfile,'a') as log:
    for key in sorted(atom_pdf.keys()):
        log.write('{:>5} {:>5} {:>5} {:>10} {:>10} {:>10} {:>10}\n'.format(key,atom_pdf[key]['INP'],atom_pdf[key]['IPP'],atom_pdf[key]['MAX'],atom_pdf[key]['MIN'],atom_pdf[key]['VNP'],atom_pdf[key]['VPP']))
with open(pdf_table,'a') as tab:
    for key in sorted(atom_pdf.keys()):
        tab.write('{:>5}\t{:>5}\t{:>5}\t{:>10}\t{:>10}\t{:>10}\t{:>10}\n'.format(key,atom_pdf[key]['INP'],atom_pdf[key]['IPP'],atom_pdf[key]['MAX'],atom_pdf[key]['MIN'],atom_pdf[key]['VNP'],atom_pdf[key]['VPP']))


