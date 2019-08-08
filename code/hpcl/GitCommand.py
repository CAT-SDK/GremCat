        repo = url[url.rfind('/')+1:url.rfind('.')]
            #checkout the versions
    
        #git log -p # this will list all commits and the code additions in addition to dates and messages.
        retcode, out, err = Command.Command('git log -p').run()
        lines = iter(out.splitlines())

        current_author = ''
        for line in lines:


            #If the line is an author, then start to piece together the commit   
            #if line.startswith(b'Author: '):
            if line.startswith(b'commit'):

                commitid = line[7:len(line)]
                line = next(lines)

                            #next(lines)
                            #next(lines)
                            #next(lines)
                            filenameline = diff.decode("utf-8")
                            filename = filenameline[11:len(filenameline)]
                            #print('FILENAME '+ filename)
                     
                            line = next(lines)
                            #skip extra line if this line is seen
                            if line.startswith(b'new file mode'):
                                next(lines)
                            
                            if not line.startswith(b'deleted file mode') and not line.startswith(b'old mode'): 
                              
                                next(lines)
                                next(lines)

                                #skip ahead until see first + or -
                                while not (diff.startswith(b'+') or diff.startswith(b'-')) or (diff.startswith(b'+++') or diff.startswith(b'---')) :
                                    diff = next(lines)

                                diffinfo = []
                                while len(diff) >= 1:

                                    if (diff.startswith(b'+') or diff.startswith(b'-')):
                                        diffinfo.append(diff.decode("utf-8", errors='ignore')) 

                                    elif diff.startswith(b'diff') or len(diff) < 2:
                                        break
                                    
                                    try:
                                        diff = next(lines)
                                    except:
                                        break

                                diffs.append({'filename':filename, 'diff':diffinfo})
                                                            
                            #else:
                                #ignore deleted files for now   
                            try:
                                diff = next(lines)
                            except:
                                break
                    #print(diffs)
                    commits[current_author]['commits'].append({'id':commitid, 'date':date,'message':message, 'diffs':diffs})
                elif line.startswith(b'Merge: '):
                    #ignore merges
                    next(lines)
                    
            #else:
        #print(commits)