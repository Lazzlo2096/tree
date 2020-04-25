#!/usr/bin/env python3
import os
import sys
import json

'''Python 3 remiplementation of the linux 'tree' utility'''

chars = {
    'nw': '\u2514',
    'nws': '\u251c',
    'ew': '\u2500',
    'ns': '\u2502'
}

strs = [
    chars['ns'] + '   ',
    chars['nws'] + chars['ew']*2 + ' ',
    chars['nw'] + chars['ew']*2 + ' ',
    '    '
]

class colors:
    blue = '\033[01;34m'
    green = '\033[01;32m'
    cyan = '\033[01;36m'
    red = '\033[40;31;01m'
    default = '\033[00m'

    #dir =  blue
    #exec = green
    #link = cyan
    #deadlink = red
    #end = default

    by_type = {
        'link': cyan,
        'deadlink': red,
        'directory': blue,
        'file': default, # or do nothing
        'executable': green,
    }

def colorwrap(string, color):
    return color+string+colors.default

def colorwrap_by_type(string, filetype):
    return colorwrap(string, colors.by_type[filetype])

def colorize(path, full = False):
    file = path if full else os.path.basename(path)

    if os.path.islink(path):
        return colors.link + file + colors.end + ' -> ' + colorize(os.readlink(path), True)

    if os.path.isdir(path):
        return colors.dir + file + colors.end

    if os.access(path, os.X_OK):
        return colors.exec + file + colors.end

    return file

def build_tree(dir, opts):
    tree = []
    dirs = 0
    files = 0

    for filename in sorted(os.listdir(dir), key = str.lower):
        if filename[0] == '.' and not opts['show_hidden']:
            continue
        path = os.path.join(dir, filename)
        node = {'name': filename}
        if opts['show_size']: 
            node['size'] = os.path.getsize(path)
        if os.path.islink(path):
            node['type'] = 'link'
            node['target'] = os.readlink(path)
            node['contents'] = []
            if os.path.isdir(path):
                if opts['follow_symlinks']:
                    node['contents'], d, f = build_tree(path, opts)
                    dirs += d + 1
                    files += f
                else:
                    dirs += 1
            else:
                files += 1
        elif False: # is deadlink (?)
            node['type'] = 'deadlink'
        elif os.path.isdir(path):
            node['type'] = 'directory'
            node['contents'], d, f = build_tree(path, opts)
            dirs += d + 1
            files += f
        elif os.access(path, os.X_OK): # is executable
            node['type'] = 'executable'
            files += 1
        else: # if regular file
            node['type'] = 'file'
            files += 1

        tree.append(node)

    return tree, dirs, files

def print_tree(tree, level=0, opts = {}):
    dir_len = len(tree) - 1
    for i, file_node in enumerate(tree):
        pre = ""
        if level!=0:  # we assume that zero level is always this dir (".")
            pre = strs[3]*(level-1) + strs[2 if (i == dir_len) else 1]   # *(level-1) - dirty hack
        print( pre + colorwrap_by_type(file_node['name'], file_node['type']) )

    if file_node['type'] == 'directory' :
        print_tree(file_node['contents'], level+1)

def print_dir(dir, pre = '', opts = {}):
    dirs = 0
    files = 0
    size = 0

    if pre == '': print(colors.dir + dir + colors.end)

    dir_len = len(os.listdir(dir)) - 1
    for i, file in enumerate(sorted(os.listdir(dir), key = str.lower)):
        path = os.path.join(dir, file)
        if file[0] == '.' and not opts['show_hidden']: continue
        if os.path.isdir(path):
            print(pre + strs[2 if 1 == dir_len else 1] + colorize(path))
            if os.path.islink(path):
                dirs += 1
            else:
                d, f, s = print_dir(path, pre + strs[3 if i == dir_len else 0], opts = opts)
                dirs += d + 1
                files += f
                size += s
        else:
            files += 1
            size += os.path.getsize(path)
            print(pre + strs[2 if i == dir_len else 1] + ('[{:>11}]  '.format(size) if opts['show_size'] else '') + colorize(path))

    return (dirs, files, size)

def print_report(report):
    dirs = report['directories']
    files = report['files']
    print('{} director{}, {} file{}'.format(dirs, 'ies' if dirs != 1 else 'y', files, 's' if files != 1 else ''))

if __name__ == '__main__':
    dirs = 0
    files = 0

    opts = {
        'show_hidden': False,
        'show_size': False,
        'follow_symlinks': False
    }

    tree, dirs, files = build_tree('.', opts)
    init_tree_point = [{
        'name': '.'
        ,'type': 'directory'
        ,'contents': tree
    }]

    #print(json.dumps(init_tree_point, sort_keys = True))
    print_tree(init_tree_point)

    jreport = {
        'type': 'report',
        'directories': dirs,
        'files': files
    }
    print()
    print_report(jreport)
