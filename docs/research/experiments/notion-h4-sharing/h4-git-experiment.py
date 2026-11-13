import os, subprocess, tempfile, json, pathlib
root=tempfile.mkdtemp(prefix='h4git_'); p=pathlib.Path(root)
def git(cwd,*args,check=True):
 r=subprocess.run(['git',*args],cwd=cwd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE); assert not check or r.returncode==0, r.stderr; return r

def write(repo,name,data):
 f=repo/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')

git(p,'init','--bare','remote.git');git(p,'clone','remote.git','a');a=p/'a';git(a,'config','user.name','test');git(a,'config','user.email','test@example.invalid');write(a,'elements/wall.json',{'id':'wall','height':3});write(a,'elements/door.json',{'id':'door','host':'wall'});git(a,'add','.');git(a,'commit','-m','base');git(a,'push','origin','HEAD:main');git(p,'clone','-b','main','remote.git','b');b=p/'b';git(b,'config','user.name','test');git(b,'config','user.email','test@example.invalid')
# A deletes wall, B adjusts door, independent paths merge yet invalid host
(a/'elements/wall.json').unlink();git(a,'add','-A');git(a,'commit','-m','delete wall');git(a,'push','origin','HEAD:main');write(b,'elements/door.json',{'id':'door','host':'wall','width':1.0});git(b,'add','-A');git(b,'commit','-m','edit door');rejected=git(b,'push','origin','HEAD:main',check=False).returncode;git(b,'fetch','origin','main');merge=git(b,'merge','--no-edit','origin/main',check=False).returncode;orphan=not (b/'elements/wall.json').exists() and json.loads((b/'elements/door.json').read_text())['host']=='wall'
# Same path divergent edits produce conflict
c=p/'c';git(p,'clone','-b','main','remote.git','c');git(c,'config','user.name','test');git(c,'config','user.email','test@example.invalid');write(c,'elements/door.json',{'id':'door','host':'wall','width':2.0});git(c,'add','-A');git(c,'commit','-m','door other');git(c,'push','origin','HEAD:main');git(b,'fetch','origin','main');git(b,'commit','--allow-empty','-m','merge saved',check=False);conf=git(b,'merge','--no-edit','origin/main',check=False).returncode
out={'git_version':git(p,'--version').stdout.strip(),'stale_push_exit_nonzero':rejected!=0,'disjoint_files_merge_exit':merge,'orphaned_host_after_clean_merge':orphan,'same_file_merge_exit_nonzero':conf!=0,'limitations':'local Git only; not GitHub API, app code, or production security'};print(json.dumps(out,indent=2)); pathlib.Path(__file__).with_name('h4-git-experiment-results.json').write_text(json.dumps(out,indent=2)+'\n')
