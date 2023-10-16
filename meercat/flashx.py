# -*- coding: utf-8 -*-
"""anl_meercat_library_flashx.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1_0Y_1cAb84sUZIaEqhmxKEL7HHb7cBtk

# First we will bring in one of the GremCat libraries

This is the library that provides the `get_commits` function, which will translate a portion of a project database into a pandas `DataFrame`.

%%capture
!pip install uo-puddles
from uo_puddles.gremcat_df import *
"""

import os, sys

def splitall(path):
    allparts = []
    while 1:
        head, tail = os.path.split(path)
        if head == path:  # sentinel for absolute paths
            allparts.insert(0, head)
            break
        elif tail == path: # sentinel for relative paths
            allparts.insert(0, tail)
            break
        else:
            path = head
            allparts.insert(0, tail)
    return allparts

"""# Units are the major (subfolder) division of the Flash-X repo

Many unit folder reside directly under `source/` although some are buried deeper.

Documentation is focused on units. By convention, file names reflect the unit they are part of by starting with the unit name.

Files direclty in a unit folder are called stubs.

Files deeper in a unit folder structure are called implementations.

Complicating this can be the presence of a folder under a unit call localAPI. Files in this folder are private to the unit and are stubs: you will find implementations of them in other unit subfolders. Private files do **not** start with the unit name.

If a private file is found without a stub in localAPI, it is considered private to its containing subfolder, i.e., it is **not** available throughout the unit the way a stubbed private file is.
"""

#global for now - probably could move into check_file_documentation
units = [
    "Driver",
    "Grid",
    "Multispecies",
    "Particles",
    "PhysicalConstants",
    "RuntimeParameters",
    "Simulation",
    "MoL",
    "IO",
    "Eos",
    "Gravity",
    "HeatAD",
    "Hydro",
    "ImBound",
    "IncompNS",
    "Multiphase",
    "RadTrans",
]

doc_extensions_to_check = ['.F90', '.dox']  #might add more types later, e.g., .md files
filenames_to_check = []

#Auxilliary function used by check_file_documentation.
#General idea is that some files do not have checking unabled so skip over them.
#Returns one of two tuples:
#   (True, '') meaning it is checkable or
#   (False, msg:str) meaning not checkable with msg description of why

def is_file_documentation_checkable(lines:list, path:str) -> tuple:
  assert isinstance(lines, list)
  assert all([isinstance(x,str) for x in lines])
  assert isinstance(path,str)

  global doc_extensions_to_check
  global filenames_to_check

  try:
    the_file = os.path.split(path)[1]  #the tail has the file name
  except:
    return (False, f'path not parsable: {path}')
  
  if the_file=='':
    return (False, f'path does not include file: {path}')

  try:
    name, extension = os.path.splitext(the_file)
  except:
    return (False, f'file not parsable: {the_file}')

  #first check extension and possibly filename as being listed as checkable
  if extension:
    if extension in doc_extensions_to_check:
      pass
    else:
      return (False, f'File of type {extension} currently not checkable')
  elif name in filenames_to_check:
    pass  #no extension but filename listed as checkable
  else:
    return (False, f"No extension and specific file name {name} not checkable.")

  #Below is Flash-X specific

  if extension=='.dox': return (True, '')  #currently no restrictions on dox files
  
  if extension == '.F90':
    '''
    There are 4 types of F90 files that we will eventually want to check in Flash-X:
      1. Single subroutine per file
      2. Multiple subroutines per file
      3. Module(s)
      4. Mixture of subroutines and modules

    At moment, only dealing with the first, a file with a single subroutine defined.
    Will add more cases later.
    '''
    subs = [line for line in lines if line.startswith('subroutine ')]  #list subroutines in file
    mods = [line for line in lines if line.startswith('module ')]      #list modules in file
    return (False, f'Only checking files with a single subroutine currently') if (len(subs) != 1 or len(mods) != 0) else (True, '')

  #checks for other things eventually here, e.g., md, config or toml files.

  return (True, '')

"""#Need directory structure for checking private files

Assume MeerCat calls this function.

#Directory Structure

For some projects, it may be necessary to find files or folders not directly on the file path. It is expected that MeerCat will call this function and pass in a portion of the repo directory structure. Not the content, just folder and file names in a tree like structure.

If this function is not called, then it is assumed that checking a specific project's documentation does not require knowing more than what is on the path. In this case, `dir_struct` defaults to `None`.
"""

dir_struct = None  #assume MeerCat will set this with function below if needed by a project

#One of two public functions
def set_directory_structure(structure):
  global dir_struct
  dir_struct = structure
  return None

def find_file_or_folder(starting_folder:list , target:str, the_type:str):
  assert starting_folder
  assert the_type in ['file', 'folder']

  def iterative_search(current_folder, path_so_far):
        for the_dict in current_folder:
          if the_type=='folder':
            if the_dict['isFile']==False and the_dict['name']==target:
              return (current_folder, path_so_far)
          else:
            if the_dict['isFile']==True and the_dict['name']==target:
              return (current_folder, path_so_far)

        #did not find in this folder. Do search.
        for the_dict in current_folder:
          if the_dict['isFile']==False:
            answer = iterative_search(the_dict['contents'], f'{path_so_far}/{the_dict["name"]}')
            if answer[0]: return answer
            continue
        return ([], '')  #not found on path_so_far
  
  answer = iterative_search(starting_folder, '')
  return answer

test_struct = [
    {'isFile':True, 'name':'file1'},
    {'isFile':True, 'name':'file2'},
    {'isFile':False, 'name':'source', 'contents':[
        {'isFile':True, 'name':'file3'},
        {'isFile':True, 'name':'file4'},
        {'isFile':False, 'name':'Foo', 'contents':[
            {'isFile':True, 'name':'file7'}
        ]},
        {'isFile':False, 'name':'Fum', 'contents':[
            {'isFile':True, 'name':'file8'},
            {'isFile':False, 'name':'Fie', 'contents':[
              {'isFile':True, 'name':'file9'}
            ]},
        ]},
    ]},
    {'isFile':False, 'name':'folder1', 'contents':[
        {'isFile':True, 'name':'file5'},
        {'isFile':True, 'name':'file6'},
        {'isFile':False, 'name':'Foe', 'contents':[
            {'isFile':True, 'name':'file10'},
            {'isFile':False, 'name':'Fud', 'contents':[
              {'isFile':True, 'name':'file11'}
            ]},
      ]},
    ]},
]


def contains_folder(dir_struct, folder):
  return find_file_or_folder(dir_struct, folder, 'folder')

def contains_file(dir_struct, file):
  return find_file_or_folder(dir_struct, file, 'file')

"""##Look for end of path, assumed to be folder"""

def find_folder_on_path(root_structure:list, path:str):
  components = splitall(path)
  current_structure = root_structure
  path_so_far = ''
  for dir in components:
    folder,path = contains_folder(current_structure, dir)
    if not folder:
      #the current dir is not in current_structure
      return (current_structure, path_so_far)
    else:
      #the current dir is in current_structure so find it
      path_so_far += f'/{dir}'
      for the_dict in folder:
        if the_dict['isFile']==False and the_dict['name']==dir:
          current_structure = the_dict['contents']
          break
      else: assert False, 'Should not get here.'
  return (current_structure, path_so_far)


"""# Main checking function

Input is simply file, in form of a list of lines/strings and the path to the file, starting with `source/`.

The return value is a dictionary of following form:

<pre>
'file_status': 'checkable' or 'uncheckable: msg' or 'checkable but no documentation'
'missing_fields': list of fields as strings
'problem_fields' = [(msg:str, line:str, line_number:int),  ...] where msg describes problem.
'bogus_fields': e.g., [('@internal', line:str, line_number:int), ...] where @internal should not be in this file.
</pre>

For the MeerCat message that goes along with `'uncheckable: msg'` or `'checkable but no documentation'`, might use something like *"Please see Flash-X/docs/doxygen/UnitTemplate/ for templates on setting up Doxygen documentation."*
"""

#This is one of two public functions that make up library API
def check_file_documentation(lines:list, path:str):
  assert isinstance(lines, list)
  assert all([isinstance(x,str) for x in lines])
  assert isinstance(path,str)

  return check_file_documentation_aux(dir_struct, lines, path)  #adds dir_struct

def check_file_documentation_aux(dir_struct, lines:list, path:str):
  assert isinstance(lines, list)
  assert all([isinstance(x,str) for x in lines])
  assert isinstance(path,str)

  global units  #list of known units in Flash-X

  results_dict = {
      'file_status': 'checkable',
      'missing_fields': [],
      'problem_fields': [],
      'bogus_fields': [],
  }

  checkable, msg = is_file_documentation_checkable(lines, path)  #returns tuple: (bool, msg)
  if not checkable:
    results_dict['file_status'] = f'uncheckable: {msg}'
    return results_dict

  path_components = splitall(path)  #list of all pieces in path, e.g., ['source', 'numericalTools', 'MoL', 'MoL_advance.F90']
  the_unit = [unit for unit in units if unit in path_components]
  if len(the_unit)>1:
    #weird case - 2+ units on branch
    results_dict['file_status'] = f'uncheckable: more_than_one_unit_on_path {path}'
    return results_dict

  name, extension = os.path.splitext(path_components[-1])  #e.g., ('MoL_advance', '.F90') notice dot included
  if extension == '.F90':
      #need to figure out if stub or implementation or private
      the_file = os.path.basename(path)
      the_header = os.path.dirname(path)
      
      if not the_unit:
        #weird case - F90 file on path that does not include a unit name
        results_dict['file_status'] = f'uncheckable: no unit on path {path}'
        return results_dict

      unit_name = the_unit[0]

      #check for stub - file directly under a unit folder and startswith unit name
      if the_header.endswith(unit_name) and name.startswith(unit_name):
          results = check_implementation_stub(lines, path, name, unit_name)
          for key in results:
            results_dict[key] = results[key]
          return results_dict

      #not stub - check for stubbed implementation - file not under unit folder but does start with unit name
      if name.startswith(unit_name):
        results = check_implementation(lines, path, name, unit_name)
        for key in results:
          results_dict[key] = results[key]
        return results_dict

      #not stubbed implementation - must be private
      results = check_private_file(dir_struct, lines, path, name, unit_name)
      for key in results:
        results_dict[key] = results[key]
      return results_dict

  #not F90 file. Check if dox file.
  if extension == '.dox':

    #dox files can appear above a unit folder, e.g., source/numericalTools/numericalTools.dox
    if not the_unit:
      results_dict['file_status'] = f'checkable but currently not checking dox files above unit folder.'
      return results_dict
    #could replace above with checker later if wanted

    #single unit found on path
    unit_name = the_unit[0]
    results = check_unit_dox(lines, path, name, unit_name)
    for key in results:
      results_dict[key] = results[key]
    return results

  results_dict['file_status'] = f'checkable but no checkers found'
  return results_dict

"""###Public or Private stub

An F90 stub can be for either a public function or a private function. The fields are the same except for `@ingroup`, which is slightly different for each.
"""

def check_implementation_stub(lines, path, file_name, unit, public=True):
  required_fields = ['@copyright',
                    '@licenseblock',
                    '@file',
                    '@brief',
                    '@ingroup',
                    '@details',
                    '@anchor',
                    #'@param',  #depends if parameters exist
  ]

  bogus_fields = ['@defgroup', '@stubref']  #probably others
  
  path_components = splitall(path)

  problems = dict(file_status = f"checkable {'public' if public else 'private'} stub",
                  bogus_fields=[],  #fields that appear but should not appear in the file
                  missing_fields = [],  #missing fields that should appear
                  problem_fields = [])  #appropriate fields but with a problem in content
  
  #check for bogus fields
  for i,line in enumerate(lines):
    for field in bogus_fields:
      if field in line: problems['bogus_fields'] += [(f'{field} should not appear in stub file', line, i)]

  found_fields = []
  for i,line in enumerate(lines):
    for field in required_fields:
      if field in line: found_fields.append((field, line, i))
    if '@param' in line:  #Check for param separately, else it will be counted missing.
      found_fields.append(('@param', line, i))  

  if not found_fields:
    problems['file_status'] = f"{problems['file_status']} but no documentation"
    return problems

  missing_fields = (set(required_fields) - set([f for f,l,i in found_fields]))

  if missing_fields:
    problems['missing_fields'] = list(missing_fields)

  params_found = []

  for field, line, i in found_fields:
    if field == '@brief':
      if '<insert ' in line.lower():
        problems['problem_fields'] += [('@brief has place holder', line, i)]
      continue

    if field == '@ingroup' and public:
      if not line.strip().endswith(unit):
        problems['problem_fields'] += [(f'@ingroup should name containing unit {unit}', line, i)]
      continue

    if field == '@ingroup' and not public:
      if not line.strip().endswith(f'{path_components[-3]}Private'):
        problems['problem_fields'] += [(f'@ingroup should name containing folder {path_components[-3]}Private', line, i)]
      continue

    if field == '@details':
      if '<insert ' in line.lower():
        problems['problem_fields'] += [('@details has place holder', line, i)]
      continue

    if field == '@anchor':
      if not line.strip().endswith(file_name+'_stub'):
        problems['problem_fields'] += [(f'Expecting @anchor {file_name}_stub', line, i)]
      continue

    if field == '@param':
      components = line[line.find('@param'):].split(' ')
      params_found.append(components[1])
      if '<insert ' in line.lower():
        problems['problem_fields'] += [('@param has place holder', line, i)]
      continue

  #Now check if @params missing altogether. First find actual params.

  i = 0
  while not lines[i].startswith("subroutine "):
      i += 1
      if i >= len(lines):
        problems['file_status'] = f"{problems['file_statuc']} but no subroutine in file: {path}"
        return problems
  j = i
  while lines[i].find(")") == -1:
      i += 1
      if i >= len(lines):
        problems['problem_fields'] += [('No closing found for subroutine.', line, i)]
        return problems

  #Now get params
  raw_sig = " ".join(lines[j : i + 1]).strip("\n").replace("&", " ")[10:]
  sig_params = raw_sig[raw_sig.find("(") + 1 : raw_sig.find(")")].strip().split(",")
  sig_params = [sp.strip() for sp in sig_params]

  #Now know actual params. Is there a @param for each?
  for param in sig_params:
    if param in params_found: 
      continue
    else:
      problems['missing_fields'].append(f'@param {param}')

  return problems

def check_implementation(lines, path, file_name, unit, public=True):
  required_fields = ['@copyright',
                    '@licenseblock',
                    '@file',
                    '@brief',
                    '@ingroup',
                    '@details',
                    '@stubref',
  ]

  bogus_fields = ['@defgroup', '@anchor']

  problems = dict(file_status = f"checkable {'public' if public else 'private'} stub implementation",
                  bogus_fields=[],  #fields that appear but should not appear in the file
                missing_fields = [],  #missing fields that should appear
                problem_fields = [])  #appropriate fields but with a problem in content

  path_components = splitall(path)

  #check for bogus fields
  for i,line in enumerate(lines):
    for field in bogus_fields:
      if field in line: problems['bogus_fields'] += [(f'{field} should not appear in stub implementation', line, i)]

  found_fields = []
  for i,line in enumerate(lines):
    for field in required_fields:
      if field in line: found_fields.append((field, line, i))

  if not found_fields:
    problems['file_status'] = f"{problems['file_status']} but no documentation"
    return problems

  missing_fields = (set(required_fields) - set([f for f,l,i in found_fields]))

  if missing_fields:
    problems['missing_fields'] = list(missing_fields)

  for field, line, i in found_fields:
    if field == '@brief':
      if '<insert ' in line.lower():
        problems['problem_fields'] += [('@brief has place holder', line, i)]
      continue

    if field == '@ingroup':
      if not line.strip().endswith(path_components[-2]):
        problems['problem_fields'] += [(f'@ingroup should name containing folder {path_components[-2]}', line, i)]
      continue

    if field == '@details':
      if '<insert ' in line.lower():
        problems['problem_fields'] += [('@details has place holder', line, i)]
      continue

    if field == '@stubref':
      name, extension = os.path.splitext(path_components[-1])
      if not line.strip().endswith('{'+name+'}'):
        problems['problem_fields'] += [('@stubref should end with {'+name+'}', line, i)]
      continue

  return problems

def check_private_file(dir_struct, lines, path, file_name, unit):
  '''
  Private files are ones that do not start with the unit name. There are 2 types of private files:
    1. files that are available to any other subfolder in the unit. These must have a stub that appears in the folder localApi.
       They can be implemented in any other subfolder under the unit.
    2. files that are available only in the containing subfolder. These will not have a stub, i.e., will not appear in localApi.

  Need to sort out which we are looking at.
  '''

  #First check if we are in localApi folder.
  path_components = splitall(path)  #list of all pieces in path, e.g., ['source', 'numericalTools', 'MoL', 'MoL_advance.F90']
  if path_components[-2] == 'localAPI':
    return check_implementation_stub(lines, path, file_name, unit, public=False)

  #No, not in localAPI. Is there a stub for the file in localApi folder?
  if not dir_struct:
    return {'file_status': f'checkable but directory structure has not been set - necessary to check private implementation'}

  #dir_struct is set so we can see if can find localAPI.
  #first build path to unit.
  unit_path = []
  for item in path_components:
    if item == unit:
      unit_path.append(item)
      break
    unit_path.append(item)

  #check if localApi exists under unit
  localAPI_path = '/'.join(unit_path) + '/localAPI'
  folder, path = find_folder_on_path(dir_struct, localAPI_path)
  if path != localAPI_path:
    #No localApi folder so must be non_stubbed
    return check_private_nonstubbed_implementation(lines, path, file_name, unit)

  #localAPI does exist. check if stub in localAPI
  if not contains_file(folder, file_name):
    #localApi folder but no stub
    return check_private_nonstubbed_implementation(lines, path, file_name, unit)

  #stub exists so must be implementation of stub
  return check_implementation(lines, path, file_name, unit, public=False)  #same as normal stubbed implementation

def check_private_nonstubbed_implementation(lines, path, file_name, unit):
  return {'file_status': f'Checkable but not checking non-stubbed private files. Either no localAPI folder or {file_name} not found in that folder'}


"""# Check dox file

There are two types:

1. dox files with a unit in the path.
2. dox files without a unit in the path, where sits above unit folder, e.g.,  `source/numericalTools/numericalTools.dox`.
"""

def check_unit_dox(lines, path, file_name, unit):
  required_fields = ['@copyright',
                    '@par License',
                    '@parblock',
                    '@endparblock',
                    #'@internal',  only in internal folders
                    '@brief',
                    #'@ingroup',  #folder above but complicated
                    '@details',
                    '@defgroup', #containing folder
  ]

  path_components = splitall(path)

  problems = dict(bogus_fields=[],  #fields that appear but should not appear in the file
                  no_required_fields = False,
                  missing_fields = [],  #missing fields that should appear
                  problem_fields = [])  #appropriate fields but with a problem in content

  '''
  Fairly complicated structure. If you are looking at a path

     source/foo/Fum/Fie/...

  then you would expect following:
     1. foo (not a unit) may optinally have a file foo.dox. It will have a @defgroup foo. It will not have
        an @internal nor an @ingroup. Currently  this function will never be called with source/foo/foo.dox. It is caught earlier.
        However, have to be careful with source/foo/Fum/Fum.dox. It may or may not reference foo given foo.dox is optional at moment.
     2. Assume Fum is a unit. It will have a file Fum.dox with @defgroup Fum. It may have an @ingroup foo. It will not have
        an @internal.
    3. Fie is a folder under a unit. It will have a file Fie.dox with @defgroup Fie. It will have an @ingroup Fum. It will
       have an @internal.

  The code below attempts to check all this. Make sure correct fields are in required list and make sure fields that should not be there are not.
  '''

  #check if top-level, e.g., Fum in above example
  if path_components[-2] != unit:
    #not the unit dox file in path so must be in a group below, e.g., Fie
    required_fields.append('@ingroup')
    required_fields.append('@internal')
  else:
    #yes, under unit so .../Fum/Fum.dox
    for i,line in enumerate(lines):
      #checking for source/foo/Fum/Fum.dox. Only legit use of @ingroup is if it points to foo.
      if '@ingroup' in line and not path_components[-3] in line:
        problems['bogus_fields'] += [('@ingroup', line, i)]
      if '@internal' in line:
        problems['bogus_fields'] += [('@internal', line, i)]

  #done checking for @ingroup and @internal usage

  found_fields = []
  for i,line in enumerate(lines):
    for field in required_fields:
      if field in line: found_fields.append((field, line, i))

  if not found_fields:
    problems['no_required_fields'] = True
    return problems

  missing_fields = (set(required_fields) - set([f for f,l,i in found_fields]))
  if missing_fields:
    problems['missing_fields'] = list(missing_fields)

  for field, line, i in found_fields:
    if field == '@brief':
      if '<insert ' in line.lower():
        problems['problem_fields'] += [('@brief has place holder', line, i)]
      continue

    if field == '@ingroup':
      if not line.strip().endswith(path_components[-3]):
        problems['problem_fields'] += [(f'@ingroup should name {path_components[-3]}', line, i)]
      continue

    if field == '@details':
      if '<insert ' in line.lower():
        problems['problem_fields'] += [('@details has place holder', line, i)]
      continue

    #a bit complicated. Determine if dox for public or dox for private.
    if field == '@defgroup':
      if path_components[-1].startswith(unit):
        #file name starts with unit
        if path_components[-2] not in line:
          problems['problem_fields'] += [(f'Expecting @defgroup {path_components[-2]}', line, i)]
      else:
        #file name does not start with unit so must be private
        if f'{unit}Private' not in line:
          problems['problem_fields'] += [(f'Expecting @defgroup {unit}Private', line, i)]
      continue

  return problems
