class TreeNode:
    def __init__(self):
        self.children = {}
        self.files = []

    def add_file(self, fileIn):
        if fileIn[0].startswith('-'):
            return
        if len(fileIn) == 1:
            self.files.append(fileIn[0])
        else:
            if fileIn[0] not in self.children:
                self.children[fileIn[0]] = TreeNode()
            self.children[fileIn[0]].add_file(fileIn[1:])

    def __str__(self):
        return str(self.children)+" "+str(self.files)

def TreeTraveller(tree_in):
    '''
    yields the files of a directory with their path and how many directories were rendered before its level
    '''
    visited = [(0, [list(tree_in.children.keys())[0]], tree_in)] #number of rendered folders deep, current folder, TreeNode of folder

    while len(visited)>0:
        file = visited.pop(0)
        fileNode = file[2]
        depth = file[0]
        if len(fileNode.files)>0:
            depth+=1
        for i in fileNode.files:
            yield file[0], file[1][1:], i
        for i in fileNode.children:
            newNode = (depth, file[1]+[i], fileNode.children[i])
            visited.insert(0, newNode)
            
