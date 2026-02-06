for d in data/*; do
    for f in $d/*.in; do 
        python3 submissions/accepted/solution.py < $f > $d/`basename $f .in`.ans; 
    done
done
