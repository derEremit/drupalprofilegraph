#! /usr/bin/python

import os, pydot
import argparse

def getDependency(line):
  if (line.count('dependencies[]') and not line.startswith(';')):
    dep = line.split('=')[1].strip().strip('"')
    if (dep != 'features' and dep != 'strongarm'):
      return dep
  return False

def main(profilepath, modulespath, outpath):
  profilename = profilepath.split('/')[-1]
  # create empty graph object
  graph = pydot.Dot(graph_type='digraph',aspect="1.4", root=profilename)
  modules = list()
  dependencies = list()
  profilepath = profilepath + '/' + profilename + '.info'
  f=open(profilepath, 'r')
  print "Processing file : " + f.name
  lines=f.readlines()
  f.close()
  profileName = f.name.split('/')[-1].split('.')[0]
  # add rootnode
  graph.add_node( pydot.Node(profileName, style="filled", fillcolor="green", root="true") )

  process = False

  for line in lines:
  #dependencies.append([(f.name.split('/')[-1], (getDependency(line))) for line in lines])
    if line.count("Custom modules") > 0:
      process = True
    if line.count("Development modules") > 0:
      process = False
    if process:
      temp = getDependency(line)
      dependencies.append(temp)
      if temp:
        graph.add_edge(pydot.Edge(profileName, temp))

  dependencies.append("uba_post_content")
  graph.add_edge(pydot.Edge(profileName, "uba_post_content"))
  
  for subdir, dirs, files in os.walk(modulespath):
    for file in files:
      if file.endswith(".info"):
        f=open(subdir + "/" + file, 'r')
        #print "Processing file : " + f.name
        lines=f.readlines()
        moduleName = f.name.split('/')[-1].split('.')[0]
        f.close()
        isCustom = False
        if subdir.count("/modules/custom/") > 0:
          isCustom = True
        isFeature = False
        for line in lines:
        #dependencies.append([(f.name.split('/')[-1], (getDependency(line))) for line in lines])
          if line.startswith("features["):
            isFeature = True
          temp = getDependency(line)
          if temp:
           dependencies.append(temp)
           graph.add_edge(pydot.Edge(moduleName, temp))
        module = {'name': moduleName, 'isCustom' : isCustom, 'isFeature' :isFeature}
        modules.append(module)
        print moduleName + " sub: " + subdir
        #print moduleName + " dirs: " + dirs

  for module in modules:
    if module['isFeature'] and module['name'] in dependencies:
      graph.add_node( pydot.Node(module['name'], style="filled", fillcolor="yellow") )
    elif module['isCustom'] and module['name'] in dependencies:
      graph.add_node( pydot.Node(module['name'], style="filled", fillcolor="red") )
      
  graph.write_png(outpath + profilename + '-graph.png')
  print ("Success!!");


if __name__ == '__main__':
  p = argparse.ArgumentParser(prog="drupalprofilegraph")
  p.add_argument('profilepath', help="path to profile directory")
  p.add_argument('modulespath', help="path to (custom) modules directory")
  p.add_argument('outpath', help="path, where output PNG will be put")
  arguments = p.parse_args()
  main(arguments.profilepath, arguments.modulespath, arguments.outpath)

