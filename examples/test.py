x = [(3,2,1),(1,2,3)]
y = [(1,2,3),(3,2,1)]
z = [(1,2,3),(1,2,3), (4,5,6), (7,8,9)]
x.reverse()
xy = range(5+1)
xy.remove(0)
xy.remove(1)

seen = set()
uniq = []
common = []
for x in z:
    if x not in seen:
        uniq.append(x)
        seen.add(x)
    else:
        common.append(x)
        
print uniq
print seen
print common