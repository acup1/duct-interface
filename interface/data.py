def lastNotNullIndex(a,dy=0):
    for i in list(range(len(a)))[::-1]:
        if a[i]>dy:
            return i

def maxX(x,y,dy):
    if len(x)<len(y):return 0
    else:
        return x[lastNotNullIndex(y,dy)]


if __name__=="__main__":
    y=[0,0,0,1,2,3,4,5,0,0,0,0,0]
    x=list(range(len(y)))

    print("\t".join(list(map(str,x))))
    print("\t".join(list(map(str,y))))

    print(maxX(x,y))
