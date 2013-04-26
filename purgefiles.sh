files=$@
for file in $files; do
	git filter-branch -f --index-filter "git rm -rf --cached --ignore-unmatch $file" --prune-empty HEAD
done
 
# remove the temporary history git-filter-branch otherwise leaves behind for a long time
rm -rf .git/refs/original/ && git reflog expire --all &&  git gc --aggressive --prune 
