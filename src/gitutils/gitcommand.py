import sys

import logging
# Setup Logger
logger = logging.getLogger('db_interface')
# Handler should already be taken care of
#logger.setLevel(logging.DEBUG)
#ch = logging.StreamHandler()
#ch.setLevel(level=logging.DEBUG)
#formatter = logging.Formatter(fmt="[%(levelname)s]: %(asctime)s - %(message)s")
#ch.setFormatter(fmt=formatter)
#logger.addHandler(hdlr=ch)
            logger.debug('git checkout %s%s' % (prefix,version))
            #print(out)
        logger.debug(f'git log -p --branches=* --all --date=iso-strict-local --function-context --since {since} --until {until}')
                                diffheader = diff

                                diffheader += line
                                    diffheader += next(lines)
                                    diffheader += diff
                                        diffheader += next(lines)
                                        diffheader += next(lines)
                                        diffheader += next(lines)
                                    diffheader += diff
                                    # while not (diff.startswith(b'+') or diff.startswith(b'-')) or (diff.startswith(b'+++') or diff.startswith(b'---')) :
                                    #     diff = next(lines)
                                    #diff = next(lines)
                                        if diff.startswith(b'diff'):

                                        # if (diff.startswith(b'+') or diff.startswith(b'-')):
                                        diffinfo.append(diff.decode("utf-8", errors='ignore'))

                                        # elif diff.startswith(b'diff'):
                                        #     break
                                        # elif len(diff) < 2:
                                        #     try:
                                        #         diff = next(lines)
                                        #         if len(diff) < 2:
                                        #             break
                                        #     except:
                                        #         break

                                    diffs.append({'filename':filename, 'diff':diffinfo, 'header':diffheader.decode("utf-8", errors='ignore')})
                                diffheader = diff 

                                diffheader += line
                                    diffheader += next(lines)
                                    diffheader += diff
                                        diffheader += next(lines)
                                        diffheader += next(lines)
                                        diffheader += next(lines)
                                    diffheader += diff
                                    diffs.append({'filename':filename, 'diff':diffinfo, 'header':diffheader.decode("utf-8", errors='ignore')})
def repoError(repodir,err):
    sys.stderr.write("***ERROR [gitutils.gitcommand]: %s %s" % (repodir,err))
     
