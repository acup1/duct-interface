def exlambda(fstr,pstr="",obj=[]):
    loc={}
    gl={}
    for i in range(len(obj)):
        gl[pstr.split(",")[i]]=obj[i]
    ex=f"""def __SFunc__():
{' '+fstr[2:]}"""
    exec(ex,gl,loc)
    return loc["__SFunc__"]
