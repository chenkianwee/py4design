import ntpath
path = "a/b/c.heat"
head,tail = ntpath.split(path)
print tail.split(".")[0]