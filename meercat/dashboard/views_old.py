import datetime
import json

import configparser

from django.http import HttpResponse
from django.template import loader
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import redirect, render
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

import pandas as pd

import re

import sys
sys.path.insert(1, '/shared/soft/ideas_db/ideas-uo/src')
sys.path.insert(1, '../src')
from gitutils.github_api import GitHubAPIClient

from database.models import Project, ProjectRole, Commit, Diff, Issue, PullRequest, PullRequestIssue, Comment, EventPayload, CommitTag
from database.utilities import comment_pullrequest

import subprocess
import os, warnings
warnings.filterwarnings('ignore')
from patterns.visualizer import Visualizer

def not_authorized(request):
    return render(request, 'dashboard/not_authorized.html')


# Index view - should list all projects
@login_required
def index(request):
    print("INDEX")

    pid = 30
    if request.GET.get('pid'):
        pid = int(request.GET.get('pid'))

    if request.user.is_staff:
        return redirect('staff_index')

    devProjects = getUserProjectsByRole(request.user, 'DEV') 
    devProjects = sorted(devProjects, key=lambda d: d.name, reverse=False)
    
    PMProjects = getUserProjectsByRole(request.user, 'PM')
    PMProjects = sorted(PMProjects, key=lambda d: d.name, reverse=False)
    
    context = {'devProjects': devProjects, 'PMProjects': PMProjects}
 
    return render(request, 'dashboard/index.html', context)

@login_required
def staff_index(request):
    print("STAFF INDEX")

    pid = 30
    if request.GET.get('pid'):
        pid = int(request.GET.get('pid'))

    projects = list(Project.objects.all())
    projects = sorted(projects, key=lambda d: d.name, reverse=False)

    return render(request, 'dashboard/staff_index.html', {'projects': projects})

@login_required
def whitelist(request, *args, **kwargs):
    pid = 30
    if kwargs['pk']:
        pid = int(kwargs['pk'])

    if not hasAccessToProject(request.user, pid):
        return redirect('not_authorized')

    project = Project.objects.get(id=pid)

    if ProjectRole.objects.filter(project=project, user=request.user).exists():
        project_role = ProjectRole.objects.get(project=project, user=request.user)
    else:
        messages.error('Sorry, we could not get your whitelist')
        return redirect('project', pk=pid)

    project_owner = project.source_url.split('/')[-2] #Owner always has index -2. HTTPS urls are of the form https://github.com/owner/repo.git
    whitelist = project_role.whitelist 

    if whitelist is None:
        whitelist = ""

    context = {'project_owner': project_owner, 'project': project, 'whitelist': whitelist}

    return render(request, 'dashboard/whitelist.html', context)

# Project view - should list general project info
def project(request, *args, **kwargs):
    print("PROJECT")
    print( kwargs['pk'] )


    pid = 30
    if kwargs['pk']:
        pid = int(kwargs['pk'])

    if not hasAccessToProject(request.user, pid):
        return redirect('not_authorized')

    template = loader.get_template('dashboard/project.html')

    project = list(Project.objects.all().filter(id=pid).all())[0]

    # chose wether to display whitelist button if user is staff
    show_whitelist = True
    if request.user.is_staff:
        has_project_role = ProjectRole.objects.filter(project=project, user=request.user).exists()
        if not has_project_role:
            show_whitelist = False

    prs = list(PullRequest.objects.all().filter(project=project).all())
    prs = sorted(prs, key=lambda d: d.number, reverse=True)

    commits = list(Commit.objects.all().filter(project=project).all())
    commits = sorted(commits, key=lambda d: d.datetime, reverse=True)

    issues = list(Issue.objects.all().filter(project=project).all())
    issues = sorted(issues, key=lambda d: d.number, reverse=True)

    print("Done loading db data.  Now checking repo contents...")

    # TODO: these are super slow for some projects (spack)

    pythonloc = countlinespython(r'../'+project.name)
    print(".")
    fortranloc = countlinesfortran(r'../'+project.name)
    print("..")
    cloc = countlinesc(r'../'+project.name)
    print("...")
    files = countfiles(r'../'+project.name)
    print("....")


    #TODO: should be able to remove this
    with open('../anl_test_repo/folder1/arithmetic.py', 'r') as f:
        lines = f.readlines()
        f.close()


    context = {'show_whitelist': show_whitelist, 'project':project,'prs':prs, 'commits':commits, 'issues':issues, 'pythonloc':pythonloc, 'fortranloc':fortranloc, 'cloc':cloc, 'files':files, 'file':''.join(lines).replace('\\','\\\\').replace('\n', '\\n').replace('\'','\\\'')}

    return HttpResponse(template.render(context, request))


# PR list view - list all the PRs for project
@login_required
def prlist(request, *args, **kwargs):
    print("PRLIST")
    template = loader.get_template('dashboard/prlist.html')

    pid = 30
    #if request.GET.get('pid'):
    #    pid = int(request.GET.get('pid'))
    if kwargs['pk']:
        pid = int(kwargs['pk'])

        
    if not hasAccessToProject(request.user, pid):
        return redirect('not_authorized')

    project = list(Project.objects.all().filter(id=pid).all())[0]

    prs = list(PullRequest.objects.all().filter(project=project).all())
    prs = sorted(prs, key=lambda d: d.number, reverse=True)

    context = {'project':project,'prs':prs}

    return HttpResponse(template.render(context, request))


# Pull Request view - show the assistant for specific PR
@login_required
def pr(request, *args, **kwargs):
    print("PR")
    template = loader.get_template('dashboard/pr.html')

    prid = 2250
    #if request.GET.get('pr'):
    #    prid = int(request.GET.get('pr'))
    if kwargs['pk']:
        prid = int(kwargs['pk'])

    if not hasAccessToPR(request.user, prid):
        return redirect('not_authorized')

    pr = list(PullRequest.objects.all().filter(id=prid).all())[0]

    commits = list(Commit.objects.all().filter(hash__in=[committag.sha for committag in pr.commits.all()]))

    issues = list(Issue.objects.all().filter(url__in=[pri.issue.url for pri in PullRequestIssue.objects.all().filter(pr=pr).all()]))


    #Find any issue that this PR closed
    closed_issue = None
    issue_number = re.search(r'#\d+', pr.description)
    if issue_number:
        print(issue_number.group())
        print( pr.project.source_url.replace('.git', '/issues/'+issue_number.group()[1:]) )
        closed_issue_list = list(Issue.objects.all().filter(url=pr.project.source_url.replace('.git', '/issues/'+issue_number.group()[1:])))
        if len(closed_issue_list) > 0:
            closed_issue = closed_issue_list[0]


    #issues = list(Issue.objects.all().filter(project=list(Project.objects.all().filter(name='FLASH5').all())[0], state='closed'))
    #for issue in issues:
    #    comments = list(Comment.objects.all().filter(issue=issue))

    diffs = list(Diff.objects.all().filter(commit__in=[c for c in commits]))
    filenames = [d.file_path for d in diffs]
    #get just unique filenames
    filenames_set = set(filenames)
    filenames = list(filenames_set)

    events = list(EventPayload.objects.all().filter(pr_number=pr.number))

    comments = list(Comment.objects.all().filter(pr=pr))

    


    context = {'pr':pr, 'commits':commits, 'issues':issues, 'filenames':filenames, 'events':events, 'comments':comments,'closed_issue':closed_issue}

    return HttpResponse(template.render(context, request))


# Pull Request view - show the assistant for specific PR
def archeology(request, *args, **kwargs):

    template = loader.get_template('dashboard/archeology.html')

    # Get PR id
    prid = 0
    if kwargs['pk']:
        prid = int(kwargs['pk'])

    if not hasAccessToPR(request.user, prid):
        return redirect('not_authorized')

    pr = list(PullRequest.objects.all().filter(id=prid).all())[0]

    # Get filename
    filename = ''
    if request.GET.get('filename'):
        filename = request.GET.get('filename')

    # Get diffs for file
    diffs = Diff.objects.all().filter(commit__project=pr.project, file_path=filename).all()

    # Get commits, authors for those (diffs)
    authors = set([d.commit.author for d in diffs])

    table = [{'author':author, 'type':'commit','link':'more info'} for author in authors]




    context = {'pr':pr, 'filename': filename, 'authors':table}

    return HttpResponse(template.render(context, request))


# Refresh the GIT and GitHub data for a project (INTENTIONALLY ONLY WORKS FOR PROJECT ID 30)
@login_required
def refreshProject(request):
    print("REFRESH")

    pid = 30
    if request.GET.get('pid'):
        pid = int(request.GET.get('pid'))

    if not hasAccessToProject(request.user, pid):
        return redirect('not_authorized')

    project = list(Project.objects.all().filter(id=pid).all())[0]

    username = settings.DATABASES['default']['USER']
    password = settings.DATABASES['default']['PASSWORD']

    cmd = f'cd .. ; export PYTHONPATH=. ; nohup python3 ./src/gitutils/update_database.py {username} {password} {pid}'
    os.system(cmd)
    result = subprocess.check_output(cmd, shell=True)
    #print(result)
    
    resultdata = {
        'status':'success'
    }

    return HttpResponse(
        json.dumps(resultdata),
        content_type='application/json'
    )


# Refresh the GIT and GitHub data for a project (INTENTIONALLY ONLY WORKS FOR PROJECT ID 30)
@login_required
def createPatch(request):
    print("CREATE PATCH")

    prid = 2250
    if request.POST.get('pr'):
        prid = int(request.POST.get('pr'))

    if not hasAccessToPR(request.user, prid):
        return redirect('not_authorized')

    filename = 'folder1/arithmetic.py'
    if request.POST.get('filename'):
        filename = request.POST.get('filename')

    print(filename)
    print(filename.rindex('/'))
    print(filename[filename.rindex('/')+1:])

    pr = list(PullRequest.objects.all().filter(id=prid).all())[0]

    #project = list(Project.objects.all().filter(id=pid).all())[0]


    #TODO pull name from request and project from pr id

    #with open('../ideas-uo/anl_test_repo/folder1/arithmetic.py', 'w') as f:
    with open('../'+pr.project.name+'/'+filename, 'w') as f:
        f.write(request.POST.get('filecontents'))
        f.close()
    
    #cmd = f'cd ../ideas-uo/anl_test_repo ; git diff folder1/arithmetic.py > arithmetic.py.patch'
    cmd = f'cd ../'+pr.project.name+' ; git diff '+filename+' > '+filename[filename.rindex('/')+1:]+'.patch'
    os.system(cmd)
    #result = subprocess.check_output(cmd, shell=True)

    #with open('../ideas-uo/anl_test_repo/arithmetic.py.patch', 'r') as f:
    with open('../'+pr.project.name+'/'+filename[filename.rindex('/')+1:]+'.patch', 'r') as f:
        lines = f.readlines()
        f.close()
    os.remove('../'+pr.project.name+'/'+filename[filename.rindex('/')+1:]+'.patch')    

    #cmd = f'cd ../ideas-uo/anl_test_repo ; git checkout -- folder1/arithmetic.py'
    cmd = f'cd ../'+pr.project.name+' ; git checkout -- '+filename
    os.system(cmd)


    resultdata = {
        'status':'success',
        'filename':filename[filename.rindex('/')+1:]+'.patch',
        'patch': ''.join(lines)
    }

    return HttpResponse(
        json.dumps(resultdata),
        content_type='application/json'
    )


# Retrieves commit data for a specific PR
@login_required
def diffCommitData(request):
    print("Diff Commit DATA")

    print(request.POST.get('pr'))

    prid = 2250
    if request.POST.get('pr'):
        prid = int(request.POST.get('pr'))

    if not hasAccessToPR(request.user, prid):
        return redirect('not_authorized')

    pr = list(PullRequest.objects.all().filter(id=prid).all())[0]

    #Find all changed files related to the PR by getting all diffs from all commits in PR    
    commits = list(Commit.objects.all().filter(hash__in=[committag.sha for committag in pr.commits.all()]))

    print("Commits: "+str(len(commits)))

    diffs = list(Diff.objects.all().filter(commit__in=[c for c in commits]))
    filenames = [d.file_path for d in diffs]
    #Get just unique filenames
    filenames_set = set(filenames)
    filenames = list(filenames_set)

    #Now find all commits and diffs for the changed files in the past 60 days
    #date = datetime.datetime.now() - datetime.timedelta(days=60)
    date = pr.created_at - datetime.timedelta(days=60)
    diffcommits = []

    filtereddiffs = Diff.objects.all().filter(commit__project=pr.project, commit__datetime__gte=date, commit__datetime__lte=pr.created_at)
    for filename in filenames:
        diffcommits.append( {'filename': filename, 'commits':[{'commit':d.commit.hash, 'diff':d.body} for d in filtereddiffs.filter(file_path=filename)]} )

    prcommits = []
    for commit in commits:
        prcommits.append({'hash':commit.hash})

    docstring_results = first_responder_function(pr.project, pr)

    linter_results = []
    for filename in filenames:
        if filename.endswith('.py'): 
            output = os.popen('export PYTHONPATH=${PYTHONPATH}:'+os.path.abspath('../'+pr.project.name)+' ; cd ../'+pr.project.name+' ; pylint --output-format=json '+filename).read()
            linter_results.append( {'filename': filename, 'results':json.loads(output)} )

    
    resultdata = {
        'diffcommits':diffcommits,
        'prcommits':prcommits,
        'docstring_results':docstring_results,
        'linter_results':linter_results,
        'source_url':pr.project.source_url[0:-4]
    }

    return HttpResponse(
        json.dumps(resultdata),
        content_type='application/json'
    )


@login_required
def getFile(request):

    print("Get File DATA")

    #print(request.POST.get('pr'))

    prid = 2250
    if request.POST.get('pr'):
        prid = int(request.POST.get('pr'))

    if not hasAccessToPR(request.user, prid):
        return redirect('not_authorized')

    filename = 'folder1/arithmetic.py'
    if request.POST.get('filename'):
        filename = request.POST.get('filename')

    pr = list(PullRequest.objects.all().filter(id=prid).all())[0]


    # Open and read the file
    with open('../'+pr.project.name+'/'+filename, 'r') as f:
        lines = f.readlines()
        f.close()

    # If python file or fortran file, get linter results
    linter_results = []
    #docstring_results = []

    if filename.endswith('.py'): 
        output = os.popen('export PYTHONPATH=${PYTHONPATH}:'+os.path.abspath('../'+pr.project.name)+' ; cd ../'+pr.project.name+' ; pylint --output-format=json '+filename).read()
        linter_results = json.loads(output)
        #docstring_results = first_responder_function(pr.project, pr)

    if filename.endswith('.F90'): 
        output = os.popen('fortran-linter ../'+pr.project.name+'/'+filename+' --syntax-only').read()
        linter_results = json.loads(output.split('../'+pr.project.name+'/'+filename))

    #print("LINTER RESULTS: "+str(linter_results))
    #print("DOC CHECKER RESULTS: "+str(docstring_results))



    resultdata = {
        'filecontents': ''.join(lines),
        'linter_results': linter_results
    }

    return HttpResponse(
        json.dumps(resultdata),
        content_type='application/json'
    )


@csrf_exempt
def githubBot(request):

    print("Callback from webhook bot on github")

    payload = json.loads(request.body)

    #print( str(payload) )

    print( "Action Type: " + str(payload['action']) )
    print( "Pull Request Number: " + str(payload['number']) )
    print( "Repository: " + str(payload['repository']['clone_url']) )

    project = list(Project.objects.all().filter(source_url=str(payload['repository']['clone_url'])).all())[0]
    pull_request = list(PullRequest.objects.all().filter(project=prid, number=int(str(payload['number']))).all())[0]

    #TODO: eventually only do this for new PRs (check payload for action type I think)

    if pull_request:

        comment = first_responder_function(pull_request.project, pull_request)[0]
        print("------------")
        if comment:
            comment_pullrequest(pull_request, comment)
            print("commented")
        else:
            event = EventLog(
                event_type=EventLog.EventTypeChoices.NO_NOTIFICATION,
                pull_request=pull_request,
                datetime=datetime.today()            
            )
            print("don't bug me")

        print("------------")


    return HttpResponse(
        json.dumps({'results':'success'}),
        content_type='application/json'
    )


# Uses the Visualizer code to generate a graph.
# Works just for FLASH5 at the moment, but can be made to be more generic.
@login_required
def patternGraph1(request):
    print("PATTERN DATA")

    print( request.GET.get('start') )

    startdate = request.GET.get('start')
    enddate = request.GET.get('end')

    if startdate: 
        startdate = datetime.datetime.strptime(startdate, '%Y-%m-%d')
    else:
        startdate = datetime.datetime.fromtimestamp(0)

    if enddate: 
        enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
    else:
        enddate = datetime.datetime.today()

    
    prid = 2250
    if request.GET.get('pr'):
        prid = int(request.GET.get('pr'))

    pr = list(PullRequest.objects.all().filter(id=prid).all())[0]
    commits = list(Commit.objects.all().filter(hash__in=[committag.sha for committag in pr.commits.all()]))
    diffs = list(Diff.objects.all().filter(commit__in=[c for c in commits]))
    filenames = [d.file_path for d in diffs]

    
    

    # Visualizer()
    # vis = Visualizer(project_name='FLASH5')
    # vis.get_data()

    #removed = vis.remove_external()
    # removed = vis.remove_files(filenames)

    # vis.hide_names = False

    #Setting year or range seems to break some graphs
    #if startdate.year == enddate.year:
    
    # TEMPORARILY VIEW ALL YEARS
    #vis.set_year(enddate.year)
    
    #vis.select_month_range()
    #else:    
    #    vis.select_year_range(startdate.year,enddate.year)

    #df = vis.plot_zone_heatmap(agg='mean')
    #df = vis.plot_top_N_heatmap(10, locc_metric='locc')
    
    # TEMPORARILY VIEW ALL YEARS
    #df = vis.plot_top_N_heatmap(10, time_range='year', locc_metric='change-size-cos')
    #df = vis.plot_top_N_heatmap(10, locc_metric='change-size-cos')

    resultdata = {
        #'filename': 'spack-zone-change-size-cos-map-Entire_project-mean.png',
        #'filename': 'FLASH5-top-10-locc-map-Entire_project.png',
        #'filename': 'FLASH5-top-10-change-size-cos-map-'+str(enddate.year)+'.png',
        'filename': 'FLASH5-top-10-change-size-cos-map-Entire_project.png',
    }

    return HttpResponse(
    	json.dumps(resultdata),
    	content_type='application/json'
    )


# Branches view (is this still needed)
@login_required
def branches(request):
    print("BRANCHES")
    template = loader.get_template('dashboard/branches.html')
    context = {}

    return HttpResponse(template.render(context, request))


# Returns branch data for anl_test_repo
# If this is still useful, need to make more generic
@login_required
def branchData(request):
    print("BRANCHES DATA")

    config = configparser.ConfigParser()
    config.read('../credentials.ini')

    GitHubAPIClient.set_credentials(username=config['github']['login'], token=config['github']['token'])

    GitHubAPIClient.check_credentials()

    data = GitHubAPIClient.fetch_events(owner='fickas', repository='anl_test_repo')

    df = pd.DataFrame(data)

    created_branches = []
    deleted_branches = []
    for i in range(len(df)):
        if df.loc[i, 'type'] == 'CreateEvent' and df.loc[i, 'payload']['ref_type'] == 'branch':
            created_branches.append(df.loc[i, 'payload']['ref'])
        if df.loc[i, 'type'] == 'DeleteEvent' and df.loc[i, 'payload']['ref_type'] == 'branch':
            deleted_branches.append(df.loc[i, 'payload']['ref'])

    open_branches = set(created_branches)-set(deleted_branches)
    feature_branches = list(open_branches-set(['main', 'development', 'staged']))



    branches = pd.DataFrame(columns=['Name', 'Author', 'Created', 'Deleted']).set_index('Name')

    for i in range(len(df)):
        if df.loc[i, 'type'] in ['CreateEvent', 'DeleteEvent'] and df.loc[i, 'payload']['ref_type'] == 'branch':
            name = df.loc[i, 'payload']['ref']
            author =  df.loc[i, 'actor']['login']
            date = df.loc[i, 'created_at']
            event_type = 'Created' if df.loc[i, 'type'] == 'CreateEvent' else 'Deleted'
            if name in branches.index.to_list():
                branches.loc[name, event_type] = date
                branches.loc[name, 'Author'] = author
            else:
                row = {'Author': author, 'Created': '', 'Deleted':''}
                branches.loc[name] = row
                branches.loc[name, event_type] = date

    #TODO: update this to only attempt to drop if keys exist, otherwise error is thrown.
    #branches = branches.drop(['main', 'staged', 'development']).fillna('None')

    #might be easier to use for javascript
    name_column = branches.index.to_list()
    author_column = branches['Author'].to_list()
    created_column = branches['Created'].to_list()
    deleted_column = branches['Deleted'].to_list()



    resultdata = {
        'open_branches': list(open_branches),
        'created_branches': created_branches,
        'deleted_branches': deleted_branches,
        'feature_branches': feature_branches,
        'name_column': name_column,
        'author_column': author_column,
        'created_column': created_column,
        'deleted_column': deleted_column
    }


    return HttpResponse(
    	json.dumps(resultdata),
    	content_type='application/json'
    )


def countlines(start, lines=0, header=True, begin_start=None):
    #if header:
    #    print('{:>10} |{:>10} | {:<20}'.format('ADDED', 'TOTAL', 'FILE'))
    #    print('{:->11}|{:->11}|{:->20}'.format('', '', ''))

    # TODO: Currently only counds python code.

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isfile(thing):
            if thing.endswith('.py'):
                with open(thing, 'r') as f:
                    newlines = f.readlines()
                    newlines = len(newlines)
                    lines += newlines

                    #if begin_start is not None:
                    #    reldir_of_thing = '.' + thing.replace(begin_start, '')
                    #else:
                    #    reldir_of_thing = '.' + thing.replace(start, '')

                    #print('{:>10} |{:>10} | {:<20}'.format(newlines, lines, reldir_of_thing))


    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isdir(thing):
            lines = countlines(thing, lines, header=False, begin_start=start)

    return lines


def countlinespython(start, lines=0, header=True, begin_start=None):

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isfile(thing):
            if thing.endswith('.py'):
                with open(thing, 'r') as f:
                    newlines = f.readlines()
                    newlines = len(newlines)
                    lines += newlines

    for thing in os.listdir(start):
        if not thing.startswith('.git') and not thing.startswith('repos'):
            thing = os.path.join(start, thing)
            if os.path.isdir(thing):
                lines = countlinespython(thing, lines, header=False, begin_start=start)

    return lines


def countlinesfortran(start, lines=0, header=True, begin_start=None):

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isfile(thing):
            if thing.endswith('.F90'):
                with open(thing, 'r') as f:
                    newlines = f.readlines()
                    newlines = len(newlines)
                    lines += newlines

    for thing in os.listdir(start):
        if not thing.startswith('.git') and not thing.startswith('repos'):
            thing = os.path.join(start, thing)
            if os.path.isdir(thing):
                lines = countlinesfortran(thing, lines, header=False, begin_start=start)

    return lines

def countlinesc(start, lines=0, header=True, begin_start=None):

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isfile(thing):
            if thing.endswith('.c') or thing.endswith('.h') or thing.endswith('.cpp'):
                with open(thing, 'r') as f:
                    try:
                        newlines = f.readlines()
                        newlines = len(newlines)
                        lines += newlines
                    except:
                        pass    

    for thing in os.listdir(start):
        if not thing.startswith('.git') and not thing.startswith('repos'):
            thing = os.path.join(start, thing)
            if os.path.isdir(thing):
                lines = countlinesc(thing, lines, header=False, begin_start=start)

    return lines

def countfiles(start, files=0, header=True, begin_start=None):

    # TODO: Counts all files

    for thing in os.listdir(start):
        thing = os.path.join(start, thing)
        if os.path.isfile(thing):
            files += 1

    for thing in os.listdir(start):
        if not thing.startswith('.git') and not thing.startswith('repos'):
            thing = os.path.join(start, thing)
            if os.path.isdir(thing):
                files = countfiles(thing, files, header=False, begin_start=start)

    return files

def getUserProjectsByRole(user, role):
    projectRoles = list(ProjectRole.objects.filter(user__id=user.id, role=role))
    projectIds = [role.project.id for role in projectRoles]
    projects = [Project.objects.get(id=projectId) for projectId in projectIds]

    return projects


def hasAccessToProject(user, project_id):
    if user.is_staff:
        return True

    return ProjectRole.objects.filter(user__id=user.id, project=project_id).exists()

def hasAccessToPR(user, pr_id):
    if user.is_staff:
        return True

    project_id = PullRequest.objects.get(id=pr_id).project.id
    return ProjectRole.objects.filter(user__id=user.id, project=project_id).exists()

#localhost:8080/dashboard/firstresponder/26?prid=17
def firstresponder(request, *args, **kwargs):

    #template = loader.get_template('dashboard/firstresponder.html')


    # Get PR id
    if kwargs['pk']:
        proj_id = int(kwargs['pk'])
    else:
        return HttpResponse(
            json.dumps('Missing project'),
            content_type='application/json'
            )

    project_info = get_project_info(proj_id)

    if project_info==None:
        return HttpResponse(
            json.dumps(f'Project id missing from project_info {proj_id}'),
            content_type='application/json'
            )

    proj_list = list(Project.objects.all().filter(id=proj_id).all())
    if not proj_list:
        return HttpResponse(
            json.dumps(f'Unknown project {proj_id}'),
            content_type='application/json'
            )

    proj_object = proj_list[0]

    #proj_name = 

    if request.GET.get('prid'):
        pr_id = request.GET.get('prid')
    else:
        return HttpResponse(
            json.dumps(f'Missing Pull Request number'),
            content_type='application/json'
            )

    pr_list = list(PullRequest.objects.all().filter(id=pr_id).all())
    if not pr_list:
        return HttpResponse(
            json.dumps(f'Illegal Pull Request number {pr_id}'),
            content_type='application/json'
            )

    pr_object = pr_list[0]

    pr_info = first_responder_function(proj_object, pr_object)

    return HttpResponse(
        json.dumps(pr_info),
        content_type='application/json'
        )

def first_responder_function(proj_object, pr_object):

    proj_name = proj_object.name  #get project name
    proj_id = proj_object.id
    project_info = get_project_info(proj_id)  #see functions at end
    assert project_info != None, f'Project id missing from project_info {proj_id}'
    docstring_kind = project_info['docstring_kind']  #None if does not exist

    #get set up on right feature branch
    commits_list = list(Commit.objects.all().filter(hash__in=[committag.sha for committag in pr_object.commits.all()]))
    assert commits_list, f'No commits found for {proj_id}'

    commit_messages = [c.message for c in commits_list]

    branch = commits_list[0].branch
    cmd = f'cd ../{proj_name} ; git checkout {branch}'
    try:
        os.system(cmd)
    except:
        assert False, f'Failure to checkout branch {cmd}'

    #get all files in PR
    diffs = list(Diff.objects.all().filter(commit__in=[c for c in commits_list]))
    filenames = [d.file_path for d in diffs]
    #Get just unique filenames
    filenames_set = set(filenames)
    filenames = list(filenames_set)
    print(filenames[0])
    file_lines = []
    assert 'filenames' in project_info, f'filenames missing from project_info {proj_id}'
    assert 'extensions' in project_info, f'extensions missing from project_info {proj_id}'
    for filename in filenames:
        name, extension = os.path.splitext(filename)
        if (extension and extension in project_info['extensions']) or (not extension and filename in project_info['filenames']):
            with open('../'+proj_name+'/'+filename, 'r') as f:
                lines = f.readlines()
                f.close()
            file_lines.append((filename, name,  extension, lines))
        else:
            print(f'Uncheckable currently: {filename}')
            file_lines.append((filename, name,  extension, None))

    #Gather info on each file in file_lines
    all_files = []
    for path, name, extension, lines in file_lines:

        if not lines:
            continue  #no lines to check for file

        #check by project - does not scale well :(

        if proj_id==26 or proj_id==35:  #Flash5 or Flash-X

            #check if non-code file first



            #Fortran, C, C++ all have comments preceding subroutine.

            function_info = []
            i = 0  #start at top of file
            while i<len(lines):
                #compute values for sig_name, sig_params, (doc, doc_start, doc_end, fields, doc_params), test_info, all_issues

                #look for robodoc docstring  (*if* says internal)
                if lines[i].startswith('!!****f*') or lines[i].startswith('!!****if*'):
                    doc_start = i
                    i, sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues = get_f90_robodoc_string_plus_sig(lines, i)  #parses out both docstring and signature, i last line of doc
                    function_info.append((sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues))

                #look for doxygen. Not so easy. We cannot tell if doxygen comment is for subroutine or something else. robodoc actually flags it in header.
                #So search past comment to see if find subroutine. If not, ignore the comment (for now).
                elif lines[i].startswith('!>'):
                    doc_start = i
                    #check if comment goes with subroutine
                    while i<len(lines) and (lines[i].startswith('!') or lines[i].strip()==''):
                        i+=1

                    if i>=len(lines):
                        break  #done with file

                    #we ran into a line that not comment or blank that follows the doxygen comment. See if subroutine.
                    if not lines[i].startswith('subroutine '):
                        i+=1
                        continue  #comment is for something other than subroutine

                    #found comment and subroutine
                    i, sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues = get_f90_doxygen_string_plus_sig(lines, doc_start)  #parses out both docstring and signature, i last line of doc
                    function_info.append((sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues))
                    
                #look for subroutine with missing docstring
                elif lines[i].startswith('subroutine '):
                    doc_params = []
                    params_start = 0
                    doc_lines = []
                    doc_fields = []
                    doc_start = 0
                    doc_end = 0
                    #found subroutine while looking for docstring - so missing docstring
                    sub_start = i
                    nodoc_issue = [[f'No docstring for subroutine', sub_start]]

                    #deal with multi-line signature - uses & as line continuation
                    while lines[i].find(')') == -1:
                        i += 1
                        if i >= len(lines):
                            i -= 1
                            lines[i] += ')'  #bit of kludge - adding missing closing paren
                            break

                    #looks good!
                    raw_sig = ' '.join(lines[sub_start:i+1]).strip('\n').replace('&', ' ')[10:]
                    sig_name = raw_sig[:raw_sig.find('(')].strip()
                    sig_params = raw_sig[raw_sig.find('(')+1:raw_sig.find(')')].strip().split(',')
                    function_info.append((sig_name, sig_params, doc_lines, doc_start, doc_end, doc_fields, doc_params, params_start, nodoc_issue))  #no doc string

                i+=1  #keep looking through file

            #done looking for docstrings and subroutines in file. Now work on docstring alignment and mandatory fields

            extended_info = []
            for sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, issues in function_info:

                #if no doc no reason to check matching
                if not doc:
                    extended_info.append((sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, issues))  #no doc string found
                    continue

                #found docstring
                mandatories = project_info['docstring_mandatory']
                param_issues = check_param_match(sig_params, doc_params, params_start)
                mandatory_issues  = check_mandatory(mandatories, doc_fields, doc_start)
                all_issues = issues + param_issues + mandatory_issues
                print(f'all_issues: {all_issues}')
                extended_info.append((sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, all_issues))  #add in new issues

            file_table = [{'signature_name': sig_name,
                          'signature_params': sig_params,
                          'docstring': ''.join(doc),
                          'doc_fields': doc_fields,
                          'doc_start': doc_start,
                          'params_start': params_start,
                          'test_info': [],
                          'result': issues} for sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, issues in extended_info]


        elif proj_id==30:  #anl_test_repo
            function_info = []  #find all the functions in the file and record info on each of them
            i = 0

            #Python uses dostring that follows function. There is an alternative with doxygen where the comments
            #can precede, but it is frowned upon. Not handling Doxygen preceding comments currently.

            #find function signature then look for docstring following
            while i<len(lines):
                sig_start = i
                i, sig_name, sig_params = get_py_signature(lines,i)
                if not sig_name:
                    i += 1  #move on and keep searching
                    continue

                #is signature line - check for doc string currently only in numpy format. Adding Google style on todo list. Ditto Doxygen as docstring.
                sig_end = i
                doc, doc_start, doc_end, fields, doc_params, params_start, issues = get_py_doc_string(lines, sig_end+1)
                
                #after demo, pass in sig_params to check. test_info will have to expand.
                test_info = find_pytest_files(proj_name, path, sig_name)  #returns list of triples (path, file_name, i)

                #get ready to move test function to repo
                #cd '..'
                #proj_name in os.listdir()

                #import importlib
                #proj = importlib.import_module(proj_name, '')

                #proj.bin.meercat_test_functions.find_pytest_files(proj_name, path, sig_name)

                mandatories = project_info['docstring_mandatory']
                param_issues = check_param_match(sig_params, doc_params, params_start) if doc else []
                mandatory_issues  = check_mandatory(mandatories, fields, doc_start) if doc else []
                all_issues = issues + param_issues + mandatory_issues
                function_info.append((sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, test_info, all_issues))
                #print(f'function_info: {function_info}')

                i += 1  #move beyond docstring

            #done with py and numpy parsing case
        else:
            print(f'failed on {docstring_kind} and {extension}')
            file_table.append(dict())  #can't handle project yet

        file_table = [{'signature_name': sig_name,
                          'signature_params': sig_params,
                          'docstring': ''.join(doc),
                          'doc_fields': doc_fields,
                          'doc_start': doc_start,
                          'params_start': params_start,
                          'test_info': test_info,
                          'result': issues} for sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, test_info, issues in function_info]

        all_files.append((name+extension, file_table))

    #finished with all files in PR

    #all_files:
    #   name, file_table
    #       {'signature_name': sig, 'signature_params':params, 'docstring': doc_info, 'result': all_issues}
    #       {'signature_name': sig, 'signature_params':params, 'docstring': doc_info, 'result': all_issues}
    #       ...
    #       where doc_info = (doc, doc_start, doc_end, fields, doc_params)
    if all_files:
        k = 0
        n = len(all_files)
        for name,ft in all_files:
            for sig_dict in ft:
                if sig_dict['result']:
                    k += 1
                    break

        message = f'''## The MeerCat Pull-Request Assistant has information for you

    ### {k} out of {n} files in this PR were found to have issues.

    ### We have suggestions for adding tags.

    ### We have suggestions for adding more people to the discussion.

    [Please see the Pull-Request Assistant page for more detail.](http://sansa.cs.uoregon.edu:8888/dashboard/pr/{pr_object.id})
    '''
    else:
        message = f'''## The MeerCat Pull-Request Assistant has information for you

    ### No files in this PR were analyzed.

    ### We have suggestions for adding tags.

    ### We have suggestions for adding more people to the discussion.

    [Please see the Pull-Request Assistant page for more detail.](http://sansa.cs.uoregon.edu:8888/dashboard/pr/{pr_object.id})
    '''
    return [message, all_files]


#### Simulating global data about projects

def get_project_info(project_id):
    #simulate project info
    project_info = {
        26: {'docstring_kind': 'robodoc',
             'docstring_mandatory': [],
            'testing_kind': 'custom',
             'main':'master',
            'filenames':[],
            'code_quality': '',
            'supports_callgraph': False,
            'supports_test_hunt': False,
            'extensions':['.F90']},  #flash5

        35: {'docstring_kind': 'robodoc',
             'docstring_mandatory': [],
            'testing_kind': 'custom',
             'main':'master',
            'filenames':['test'],
            'code_quality': '',
            'supports_callgraph': False,
            'supports_test_hunt': False,
            'extensions':['.F90', 'toml']},  #flash-x

        32: {'docstring_kind': 'robodoc',
             'docstring_mandatory': [],
            'testing_kind': 'custom',
             'main':'master',
            'filenames':[],
            'code_quality': '',
            'supports_callgraph': False,
            'supports_test_hunt': False,
            'extensions':['.F90']},  #hypre

        30: {'docstring_kind': 'numpy',
             'docstring_mandatory':['Parameters', 'Returns', 'Raises'],
            'testing_kind': 'pytest',
             'main':'main',
            'filenames':[],
            'code_quality': 'CodeQL',
            'supports_callgraph': True,
            'supports_test_hunt': True,
            'extensions':['.py', '.F90']}     #anl_test_repo
    }
    return project_info[project_id] if project_id in project_info else None

# File explorer
#localhost:8080/dashboard/filex/25?branch=master&filename=path  where 25 is test_anl id and path is to file
def file_explorer(request, *args, **kwargs):

    template = loader.get_template('dashboard/file_explorer.html')

    # Get PR id
    if kwargs['pk']:
        proj_id = int(kwargs['pk'])
    else:
        return HttpResponse(
            json.dumps('Missing project'),
            content_type='application/json'
            )

    proj_list = list(Project.objects.all().filter(id=proj_id).all())
    if not proj_list:
        return HttpResponse(
            json.dumps(f'Unknown project {proj_id}'),
            content_type='application/json'
            )


    # Get branch
    if request.GET.get('branch'):
        branch = request.GET.get('branch')
    else:
        return HttpResponse(
            json.dumps(f'Missing branch'),
            content_type='application/json'
            )

    # Get filename
    if request.GET.get('filename'):
        filename = request.GET.get('filename')
    else:
        return HttpResponse(
            json.dumps(f'Missing filename'),
            content_type='application/json'
            )

    project_info = get_project_info(proj_id)
    if project_info==None:
        return HttpResponse(
            json.dumps(f'Project id missing from project_info {proj_id}'),
            content_type='application/json'
            )

    proj_object = proj_list[0]

    context = file_explorer_function(proj_id, proj_object, project_info, branch, filename)
    '''
    context = {'file':filename,
             'project': project,
             'language': extension,
             'documentation': docstring_kind,
             'branch':branch,
             'authors':dev_table,
             'authors_len': len(dev_table),
             'functions_supported': True if function_table else False,
             'functions':function_table,
             'prs':prs_table
             }
    '''

    return HttpResponse(template.render(context, request))

def file_explorer_function(proj_id, project_object, project_info, branch, filename):

    proj_name = project_object.name
    name, extension = os.path.splitext(filename)
    if (extension and extension in project_info['extensions']) or (not extension and filename in project_info['filenames']):
            with open('../'+proj_name+'/'+filename, 'r') as f:
                lines = f.readlines()
                f.close()
    else:
        print(f'Uncheckable currently: {filename}')
        lines = []

    if lines:

        if proj_id==26 or proj_id==35:  #Flash5 or Flash-X

            #Fortran, C, C++ all have comments preceding subroutine.

            function_info = []
            i = 0  #start at top of file
            while i<len(lines):
                #compute values for sig_name, sig_params, (doc, doc_start, doc_end, fields, doc_params), test_info, all_issues

                #look for robodoc docstring  (*if* says internal)
                if lines[i].startswith('!!****f*') or lines[i].startswith('!!****if*'):
                    doc_start = i
                    i, sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues = get_f90_robodoc_string_plus_sig(lines, i)  #parses out both docstring and signature, i last line of doc
                    function_info.append((sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues))

                #look for doxygen. Not so easy. We cannot tell if doxygen comment is for subroutine or something else. robodoc actually flags it in header.
                #So search past comment to see if find subroutine. If not, ignore the comment (for now).
                elif lines[i].startswith('!>'):
                    doc_start = i
                    #check if comment goes with subroutine
                    while i<len(lines) and (lines[i].startswith('!') or lines[i].strip()==''):
                        i+=1

                    if i>=len(lines):
                        break  #done with file

                    #we ran into a line that not comment or blank that follows the doxygen comment. See if subroutine.
                    if not lines[i].startswith('subroutine '):
                        i+=1
                        continue  #comment is for something other than subroutine

                    #found comment and subroutine
                    i, sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues = get_f90_doxygen_string_plus_sig(lines, doc_start)  #parses out both docstring and signature, i last line of doc
                    
                    callers =  get_callers(proj_id, sig_name, filename)

                    function_info.append((sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, callers, [], issues))
                    
                #look for subroutine with missing docstring
                elif lines[i].startswith('subroutine '):
                    doc_params = []
                    params_start = 0
                    doc_lines = []
                    doc_fields = []
                    doc_start = 0
                    doc_end = 0
                    #found subroutine while looking for docstring - so missing docstring
                    sub_start = i
                    nodoc_issue = [[f'No docstring for subroutine', sub_start]]

                    #deal with multi-line signature - uses & as line continuation
                    while lines[i].find(')') == -1:
                        i += 1
                        if i >= len(lines):
                            i -= 1
                            lines[i] += ')'  #bit of kludge - adding missing closing paren
                            break

                    #looks good!
                    raw_sig = ' '.join(lines[sub_start:i+1]).strip('\n').replace('&', ' ')[10:]
                    sig_name = raw_sig[:raw_sig.find('(')].strip()
                    sig_params = raw_sig[raw_sig.find('(')+1:raw_sig.find(')')].strip().split(',')

                    callers =  get_callers(proj_id, sig_name, filename)

                    function_info.append((sig_name, sig_params, doc_lines, doc_start, doc_end, doc_fields, doc_params, params_start, callers, [], nodoc_issue))  #no doc string

                i+=1  #keep looking through file

            #done looking for docstrings and subroutines in file. Now work on docstring alignment and mandatory fields

            extended_info = []
            for sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, callers, test_info, issues in function_info:

                #if no doc no reason to check matching
                if not doc:
                    extended_info.append((sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, callers, test_info, issues))  #no doc string found
                    continue

                #found docstring
                mandatories = project_info['docstring_mandatory']
                param_issues = check_param_match(sig_params, doc_params, params_start)
                mandatory_issues  = check_mandatory(mandatories, doc_fields, doc_start)
                all_issues = issues + param_issues + mandatory_issues
                #print(f'all_issues: {all_issues}')
                extended_info.append((sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, callers, [], all_issues))  #add in new issues

            file_table = [{'signature_name': sig_name,
                          'signature_params': sig_params,
                          'full_signature': f"{sig_name}({','.join(sig_params)})",
                          'docstring': ''.join(doc),
                          'doc_fields': doc_fields,
                          'doc_start': doc_start,
                          'params_start': params_start,
                          'test_info': test_info,
                          'callers': callers,
                          'result': issues} for sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, callers, test_info, issues in extended_info]


        elif proj_id==30:  #anl_test_repo
            function_info = []  #find all the functions in the file and record info on each of them
            i = 0

            #Python uses dostring that follows function. There is an alternative with doxygen where the comments
            #can precede, but it is frowned upon. Not handling Doxygen preceding comments currently.

            #find function signature then look for docstring following
            while i<len(lines):
                sig_start = i
                i, sig_name, sig_params = get_py_signature(lines,i)
                if not sig_name:
                    i += 1  #move on and keep searching
                    continue

                #is signature line - check for doc string currently only in numpy format. Adding Google style on todo list. Ditto Doxygen as docstring.
                sig_end = i
                doc, doc_start, doc_end, fields, doc_params, params_start, issues = get_py_doc_string(lines, sig_end+1)
                
                #after demo, pass in sig_params to check. test_info will have to expand.
                test_info = find_pytest_files(proj_name, filename, sig_name)  if project_info['supports_test_hunt'] else [] #returns list of triples (path, file_name, i)

                mandatories = project_info['docstring_mandatory']
                param_issues = check_param_match(sig_params, doc_params, params_start) if doc else []
                mandatory_issues  = check_mandatory(mandatories, fields, doc_start) if doc else []
                all_issues = issues + param_issues + mandatory_issues

                callers =  get_callers(proj_id, sig_name, filename) if project_info['supports_callgraph'] else []

                function_info.append((sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, callers, test_info, all_issues))
                #print(f'function_info: {function_info}')

                i += 1  #move beyond docstring

            file_table = [{'signature_name': sig_name,
                          'signature_params': sig_params,
                          'full_signature': f"{sig_name}({','.join(sig_params)})",
                          'docstring': ''.join(doc),
                          'doc_fields': doc_fields,
                          'doc_start': doc_start,
                          'params_start': params_start,
                          'test_info': test_info,
                          'callers': callers,
                          'result': issues} for sig_name, sig_params, doc, doc_start, doc_end, doc_fields, doc_params, params_start, callers, test_info, issues in function_info]
        else:
            print(f'Project has no parser yet: {proj_id}')
            file_table = []  #can't handle file yet
    else:
        print(f'failed on {docstring_kind} and {extension}')
        file_table = []  #can't handle file yet
    print('====================')
    for d in file_table:
        print(d['signature_name'], d['test_info'], d['callers'])
        print()
    # Build developer table

    diffs = Diff.objects.all().filter(commit__project=project_object, file_path=filename).all()

    #print(diffs)
    author_loc = {}

    for d in diffs:
        body = d.body
        author = d.commit.author
        loc_count = body.count('\n+') + body.count('\n-')
        if author in author_loc:
            author_loc[author] += loc_count 
        else:
            author_loc[author] = loc_count

    # Get commits, authors for those (diffs)

    info = [(d.commit.datetime, d.commit.author, d.commit.hash) for d in diffs]
    commit_messages = [d.commit.message for d in diffs]
    commit_hashes = [d.commit.hash for d in diffs]

    tags = CommitTag.objects.all().filter(sha__in=commit_hashes)

    prs = list(set(PullRequest.objects.all().filter(commits__in=tags)))  #all prs that go with file commits

    pr_messages = [(pr.number, pr.url, pr.title, pr.description) for pr in prs]

    '''
    print('pr_messages', '\n')
    for n, u, title, desc in pr_messages:
        print(n, ' ', u)
        print(title, ' ::: ', desc, '\n')
    '''
    pr_comments = list(Comment.objects.all().filter(pr__in=prs))

    #print('comments','\n')
    for com in pr_comments:
        print(com.author, ' ', com.body, '\n')

    issues = list(Issue.objects.all().filter(url__in=[pri.issue.url for pri in PullRequestIssue.objects.all().filter(pr__in=prs).all()]))

    #print('issues', issues, '\n')

    #issue_number = re.search(r'#\d+', pr.description)

    #closed_issue_list = list(Issue.objects.all().filter(url=project.source_url.replace('.git', '/issues/'+issue_number.group()[1:])))

    #issue_messsages = [(iss.title, iss.description) for iss in closed_issue_list]

    #issue_comments = list(Comment.objects.all().filter(issue__in=closed_issue_list))

    #print('issue comments', issue_comments)
    author_count = {}
    for date, author, link in info:
        if author in author_count:
            author_count[author] += 1
        else:
            author_count[author] = 1

    new_info = []
    authors = []
    for date, author, link in sorted(info, reverse=False):
        if author in authors: continue
        new_info.append((date, author, author_count[author], author_loc[author], link))
        authors.append(author)


    #see here for avoiding author alisases: https://towardsdatascience.com/string-matching-with-fuzzywuzzy-e982c61f8a84
    #combine counts for same author with different aliases.

    dev_table = [{'author':author, 'number_commits': count, 'lines': loc, 'most_recent_commit':date,'commit_link':link} for date, author, count, loc, link in new_info]

    def compute_issue_url(pr):
        issue_tags = ['issue', 'close', 'closes', 'closed', 'fix', 'fixes', 'fixed', 'resolve', 'resolves', 'resolved']
        description = pr.description.strip()
        for tag in issue_tags:
            i = description.find(tag+' #')
            i = description.find(tag+'#') if i==-1 else i
            if i==-1: continue  #did not find tag

            #found tag
            partial = description[i:]
            j = partial.find('#')
            raw_issnum = partial[j+1:]
            issnum = raw_issnum[:raw_issnum.find(' ')].strip()
            try:
                issnum = int(issnum)
                issue_list = list(Issue.objects.all().filter(url=project.source_url.replace('.git', '/issues/'+issnum.group()[1:])))
                issue_url = issue_list[0].url
                return [tag, issue_url]
            except:
                continue

        #Look for #number without tag
        if '#' in description:
            i = description.find('#')
            raw_issnum = description[i+1:]
            issnum = raw_issnum[:raw_issnum.find(' ')].strip()  #not necessarily a number
            try:
                n = int(issnum)
                issue_list = list(Issue.objects.all().filter(url=project.source_url.replace('.git', '/issues/'+n.group()[1:])))
                issue_url = issue_list[0].url
                return ["Missing tag", issue_url]
            except:
                pass
        return 'None found'

    prs_table = sorted([{'number':pr.number, 'url':pr.url, 'issue_url': compute_issue_url(pr), 'notes': ["WiP"], 'notes_kind':'WiP' } for pr in prs], key=lambda d: d['number'])


    context = {'file':filename,
                 'project': project_object,
                 'branch':branch,
                 'authors':dev_table,
                 'authors_len': len(dev_table),
                 'functions_supported': True if file_table else False,
                 'supports_callgraph': project_info['supports_callgraph'],
                 'supports_test_hunt': project_info['supports_test_hunt'],
                 'functions':file_table,
                 'prs':prs_table
                 }
    return context


#call with, e.g., 'anl_test_repo', 'folder1/arithmetic.py', 'sub'
def find_pytest_files(proj_name, file_path, function_name):
    #for full pytest dir setup see https://docs.pytest.org/en/7.1.x/explanation/goodpractices.html#conventions-for-python-test-discovery
    #here just assuming test files are in folder on file_path
    import os
    full_path = f'../{proj_name}/{file_path}'
    found_asserts = []
    while(True):
        head,tail = os.path.split(full_path)  #head now has containing dir for file
        if not head: break
        if tail==proj_name: break  #don't check above the repo
        all = os.listdir(head)  #files and folders
        #look for pytest files in dir
        for item in all:
            if os.path.isdir(item): continue  #skip over dirs
            name,extension = os.path.splitext(item)
            if 'test' in name and extension=='.py':
                print(f'found: {head}, {name}')
                with open(head+'/'+name+extension, 'r') as f:
                    lines = f.readlines()
                    f.close()
                i = 0
                while i<len(lines):
                    if lines[i].startswith('def test_'):
                        i+=1
                        while i<len(lines) and lines[i] != '\n':
                            if lines[i].strip().startswith('assert') and f' {function_name}(' in lines[i]:
                                j = head.find(f'{proj_name}/')
                                path = head[j+len(proj_name)+1:]
                                found_asserts.append((path, name+extension, i))
                            i += 1
                    i+=1
        full_path = head
    return found_asserts

def get_callers(proj_id, sig_name, filename):
    project_callers =  {30:
            {
             ('check_fum', 'folder1/arithmetic.py'): [],
             ('concat',    'folder2/strings.py'): [('folder2/test_strings.py', 'test_concat')],
             ('count',     'folder2/strings.py'): [],
             ('foo',       'folder3/more_functions.py'): [('folder2/strings.py', 'fum')],
             ('fum',       'folder2/strings.py'): [('folder1/arithmetic.py', 'check_fum')],
             ('list_sub',  'folder1/arithmetic.py'): [],
             ('sub',       'folder1/arithmetic.py'): [('folder1/arithmetic.py', 'list_sub'),
                                                     ('folder1/test_arithmetic.py', 'test_sub')],
             ('test_concat', 'folder2/test_strings.py'): [],
             ('test_sub', 'folder1/test_arithmetic.py'): []
             }
        }
    if proj_id not in project_callers:
        print(f'No calling info for {proj_id}')
        return []
    if (sig_name, filename) not in project_callers[proj_id]:
        print(f'get_callers warning: did not find {(sig_name,filename)} in {proj_id}')
        return []
    return project_callers[proj_id][(sig_name, filename)]

#### Utility functions for parsing files and other things
def get_py_signature(lines, i):
    '''!
    @param lines - a file as a list of strings
    @param i - the line to check within lines (0 origin)
    @return returns a triple of values: i is last line of signature (same as input if no signature); string name, empty if no signature found; list of params
    @details looks for line starting with "def ". If found then keeps moving through lines looking for closing colon, i.e., ":". The name and list of params returned has
     the def and colon removed. If the : is not found before reachining end of the file (lines) then the function will be ignored, i.e.,
     an empty string will be returned and the value of i will be one past the last line.
    @callgraph
    @callergraph
    '''
    if not lines[i].startswith('def '): return i, '', []
    j=i
    while not lines[i].strip().endswith(':'):
        i += 1
        if i >= len(lines):
            print(f'get_signature warning: no colon found for {lines[j]}')
            return i, '', []
    raw = ''.join([line for line in lines[j:i+1]]).strip('\n')[4:]
    full = ' '.join(raw.split())
    name = raw[:raw.find('(')].strip()
    args = raw[raw.find('(')+1:raw.find(')')].strip().split(',')
    return i, name, args

def get_py_doc_string(lines, i):
    #return doc, doc_start, doc_end, fields, doc_params, params_start, issues
    #skip over white space
    while lines[i].strip()=='':
        i+=1
    #check for triple quotes
    if lines[i].strip() not in ["'''", '"""']: return '', i, i, [], [], i, [['No docstring found',i]]  #did not find
    doc_start = i
    fields = []
    params = []
    params_start = i
    i+=1  #move beyond opening quotes
    issues = []
    numpy_fields = ['Parameters', 'Returns', 'Yields', 'Raises', 'See Also', 'Notes', 'Examples']
    while i<len(lines):
        if lines[i].strip() in ["'''", '"""']:
            doc_end = i
            break  #found end

        #check for field
        if lines[i].strip() in numpy_fields and i+1 < len(lines) and all([c=='-' for c in lines[i+1].strip()]):
            field = lines[i].strip()
            fields.append(field)
            i += 2  #skip over field and -------

            #check for Parameters field in particular
            if field == 'Parameters':
                params_start = i-2
                while i<len(lines):

                    if lines[i].strip() in numpy_fields and i+1 < len(lines) and all([c=='-' for c in lines[i+1].strip()]):
                        break  #found next field

                    if lines[i].strip() in ["'''", '"""']:
                        break  #found end

                    if ':' in lines[i]:
                        param = lines[i].strip()[:lines[i].find(':')].replace(':','').strip()
                        params.append(param)
                        i += 1
                        continue

                    if lines[i].strip().isalnum() and lines[i].strip()[0].isalpha():
                        param = lines[i].strip()
                        params.append(param)
                        i += 1
                        continue

                    i += 1  #keep looking

                if i>=len(lines):
                    issues.append([f'Missing end to docstring', doc_start])
                    doc = lines[doc_start:]
                    return doc, doc_start, i-1, fields, params, params_start, issues
                else:
                    continue  #broke out
        i += 1

    #end outer while
    if i >= len(lines):
        #fell out of while
        issues.append([f'Missing end to docstring', doc_start])
        doc_end = i

    doc = lines[doc_start:doc_end+1]

    return doc, doc_start, doc_end, fields, params, params_start, issues

def check_param_match(sig_args, doc_args, doc_start):
    issue = []
    #check if 2 lists match up
    residue1 = [x for x in doc_args if x not in sig_args]  #more params than arg names?
    residue2 = [x for x in sig_args if x not in doc_args]  #more args than param names?
    if residue1:
        issue.append([f'Bogus doc arguments: {residue1}', doc_start])
    if residue2:
        issue.append([f'actual arguments missing doc arguments: {residue2}', doc_start])
    return issue


def check_mandatory(mandatories, fields, doc_start):
    residue1 = [x for x in mandatories if x not in fields]  #more params than arg names?
    issues = [[f'mandatory fields missing: {residue1}', doc_start]] if residue1 else []
    return issues

def get_f90_robodoc_string_plus_sig(lines, i):
    #returns i, sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues
    assert lines[i].startswith('!!****if*')  or lines[i].startswith('!!****f*')#assumes lines[i] is beginning of docstring

    doc_start = i
    i+=1  #move past header
    #Look for fields
    fields = []
    params = []
    params_start = doc_start
    while not lines[i].startswith('!!**') and lines[i].startswith('!!') and i < len(lines):
        line = lines[i][2:].strip()
        if not line.isalpha() and not line.isupper(): continue
        #found field
        fields.append(line)

        if line=='ARGUMENTS':
            params_start = i
            #found ARGUMENTS section - now get arguments
            all_headers = ['NAME','SYNOPSIS','DESCRIPTION','RESULT','EXAMPLE','SIDE EFFECTS', 'NOTES','SEE ALSO']
            i += 1  #move beyond ARGUMENTS line
            while i<len(lines):

                #check if ends by a non-comment line
                if not lines[i].startswith('!!'):
                    doc_end = i-1
                    break

                #check if get to new section (so end of ARGUMENTS)
                line = doc_lines[j][2:].strip()  #remove !! and padding
                if line in all_headers:
                    fields.append(line)
                    break

                #check if - or : in line. If so, argument name is defined
                hyphen = line.find(' - ')
                index = line.find(' : ') if hyphen == -1 else hyphen  #try colon if do not find hyphen 

                #if not found, keep moving along
                if index == -1:
                    i += 1
                    continue

                #record arg name(s) found
                arg_name = line[:index].strip()
                for aname in arg_name.split(','):  #can have more than one name preceding hyphen
                    params.append(aname)
                i += 1

            #figure out how dropped out of while loop collecting args

            if i>=len(lines):
                #did not find closing of doc string
                return i, '', [], lines[doc_start:i], doc_start, 0, fields, params, params_start, [[f'No end found for docstring starting at {doc_start}', doc_start]]

            if line in all_headers:
                #got to next section - keep going
                i += 1

            if not lines[i].startswith('!!'):
                #ready to look for subroutine
                break



    #found non comment line - assume ending
    doc_end = i-1
    doc = lines[doc_start:i]

    #now look for subroutine
    while not lines[i].startswith('subroutine '):
        i += 1
        if i >= len(lines):
            #missing subroutine
            return i, '', [], lines[doc_start:i], doc_start, 0, fields, params, params_start, [[f'No subroutine for docstring starting at {doc_start}', doc_start]]
    j = i
    while lines[i].find(')') == -1:
        i += 1
        if i >= len(lines):
            return i, '', [], lines[doc_start:i], doc_start, doc_end, fields, params, params_start, [[f'No ) for for subroutine starting at {j}', j]]

    #looks good!
    raw_sig = ' '.join(lines[j:i+1]).strip('\n').replace('&', ' ')[10:]
    sig_name = raw_sig[:raw_sig.find('(')].strip()
    sig_params = raw_sig[raw_sig.find('(')+1:raw_sig.find(')')].strip().split(',')

    return i+1, sig_name, sig_params, doc, doc_start, doc_end, fields, params, params_start, []

'''
!> A generic assertion, tests a given logical expression. (The short, concise description)

!> If it evaluates to .false.,
!> print the fail message and possibly stop execution. (A more detailed description)
!> 
!> @param test The logical expression to test. (Explanation of individual arguments)
!> @param failmsg The message to print on fail. If omitted, a generic message is printed.
!> Can be modified with a prefix (see assertSetMsgPrefix)
!> @param doStop Controls whether to stop execution. If doStop .true., 
!> the program is stopped. If .false., only the fail message is printed
!> and bookkeeping is done for delayed stopping (see assertStopOnFailed).
!> If given, overrides the default behaviour  set by assertSetStopMode.

!> @see assertStopOnFailed (References to other routines)
!> @see assertSetStopMode
!> @see assertSetMsgPrefix

!> @author H.-J. Klingshirn (Author information)
!> @version 1.0 (Version information)
 OR Python

## @package pyexample
#  Documentation for this module.
#
#  More details.
 
## Documentation for a function.
#
#  More details.
def func():
    pass
'''

def get_doxygen_string_plus_sig(lines, i, language):
    #returns i, sig_name, sig_params, doc, doc_start, doc_end, fields, doc_params, params_start, issues

    doc_start = i
    fields = []
    params = []
    params_start = doc_start
    language_mapping ={'F90': {'comment': '!'},
                        'py': {'comment': '#'}
                      }
    comment_char = language_mapping[language]['comment']
    while (lines[i].startswith(comment_char) or lines[i].strip()=='') and i<len(lines):

        if lines[i].strip()=='':
            i+=1
            continue

        j = lines[i].find('@')
        if j==-1:
            i+=1
            continue

        #found field
        raw_field = lines[i][j+1:]
        k = raw_field.find(' ')  #space before name
        field = raw_field[:k].strip()
        fields.append(field)

        if field=='param':
            raw_name = raw_field[k+1:]
            params.append(raw_name[:raw_name.find(' ')])

    #either found sub or run out of lines
    if i>=len(lines):
        return i, '', [], lines[doc_start:i], doc_start, 0, list(set(fields)), params, params_start, [[f'No subroutine for docstring starting at {doc_start}', doc_start]]
    doc_end = i-1
    doc = lines[doc_start:i]




    return i+1, sig_name, sig_params, doc, doc_start, doc_end, list(set(fields)), params, params_start, []


def parse_f90_subroutine(lines, i):
    #now look for subroutine
    while not lines[i].startswith('subroutine '):
        i += 1
        if i >= len(lines):
            #missing subroutine
            return i, '', [], lines[doc_start:i], doc_start, 0, list(set(fields)), params, params_start, [[f'No subroutine for docstring starting at {doc_start}', doc_start]]
    j = i
    while lines[i].find(')') == -1:
        i += 1
        if i >= len(lines):
            return i, '', [], lines[doc_start:i], doc_start, doc_end, list(set(fields)), params, params_start, [[f'No ) for for subroutine starting at {j}', j]]

    #looks good!
    raw_sig = ' '.join(lines[j:i+1]).strip('\n').replace('&', ' ')[10:]
    sig_name = raw_sig[:raw_sig.find('(')].strip()
    sig_params = raw_sig[raw_sig.find('(')+1:raw_sig.find(')')].strip().split(',')
def write_pr_info_to_file(proj_id):
    return []






