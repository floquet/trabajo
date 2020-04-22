#!/bin/bash
printf "%s\n" "$(date), $(tput bold)${BASH_SOURCE[0]}$(tput sgr0)"

# counts steps in batch process
export counter=0
export SECONDS=0
function new_step(){
    counter=$((counter+1))
    echo ""
    echo "Step ${counter}: ${1}"
}

new_step "Set environment variables"

export OMP_NUM_THREADS=10
export LD_LIBRARY_PATH="/usr/lib64":"$(pwd)":"${LD_LIBRARY_PATH}"

echo "ulimit = $(ulimit)"
echo "\${OMP_NUM_THREADS} = ${OMP_NUM_THREADS}"
echo "\${LD_LIBRARY_PATH} = ${LD_LIBRARY_PATH}"

new_step "cd ${trabajo}"
          cd ${trabajo}

new_step "export mom=$PWD"
          export mom=$PWD

new_step 'export exe="${mom}/bin/MMoM_4.1.12"'
          export exe="${mom}/MMoM_4.1.12"

new_step "Identify source files"
export stem="B-20A"
facets="${stem}-S-1000m ${stem}-S-0100m ${stem}-S-0050m"
echo "\${facets} = ${facets}"

new_step 'export target="${mom}-${stem}-output"'
          export target="${mom}-${stem}-output"

new_step "mkdir -p  ${mom}-${stem}-output"
          mkdir -p "${mom}-${stem}-output"

new_step "cd  ${mom}-${stem}-output"
          cd "${mom}-${stem}-output"

new_step 'export sink="${mom}-${stem}-output"'
          export sink="${mom}-${stem}-output"

for f in ${facets}; do
	new_step "Run ${f}"
	cp ${stem}/template-${stem}.geo ${sink}/${f}.geo
	cp ${stem}/${f}.facet .
	sed -i 's/FILE_A/'${f}'/'       ${f}.geo
	sed -i 's/FILE_B/'${f}'.facet/' ${f}.geo
	echo "./${exe} ${f}.geo > ${sink}/${f}-run.out"
	      ./${exe} ${f}.geo > ${sink}/${f}-run.out
	mv ${f}.geo      ${sink}/${stem}/.
	mv ${f}.4112.txt ${sink}/${stem}/.
	rm ${f}.facet
done

new_step "Exit"
echo "time used = ${SECONDS} s"
date
