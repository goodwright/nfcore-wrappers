touch main.nf
touch nextflow.config

nf-core modules $1 $2 $3

rm main.nf
rm nextflow.config