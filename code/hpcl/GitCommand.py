import datetime

        os.chdir(self.tmpdir)

        os.chdir(self.tmpdir)
        if not os.path.exists(filepath):
            return '',getYears(reponame)
    #Get all the versions of a repo since data (default: utc epoch)
    def getRepoCommitData(self, reponame, since=datetime.datetime.utcfromtimestamp(0).isoformat()):
        for version in versions:


        # function-context for python just adds all the surrounding lines of code to the diff output
        #retcode, out, err = Command.Command('git log -p --date=iso-strict-local --function-context').run()
        retcode, out, err = Command.Command(f'git log -p --since={since}').run()
            #If the line is an author, then start to piece together the commit
                #print(line)
                    else:
                    #print(rawdate)

                    #print(m)
                        message += (m + b'\n').decode("utf-8")
                        try:
                            m = next(lines)
                        except StopIteration:
                            m = ''
                    #this code will iterate over the lines trying to pull just the +/- info from the diff output
                    while len(diff) > 0 and diff.startswith(b'\\') == False:

                                diff = next(lines)
                                if diff.startswith(b'diff'): 
                                    break
                                #skip just one line if this line is seen
                                if line.startswith(b'new file mode'):
                                    next(lines)

                                else:
                                    next(lines)
                                    next(lines)
                                        diffinfo.append(diff.decode("utf-8", errors='ignore'))
                                    elif diff.startswith(b'diff'):
                                    elif len(diff) < 2:
                                        try:
                                            diff = next(lines)
                                            if len(diff) < 2:
                                                break
                                        except:
                                            break


                                #ignore deleted files for now

                #ignore anything else until next author line
