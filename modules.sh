touch main.nf
touch nextflow.config
echo "repository_type: pipeline" >> .nf-core.yml

python3 -m nf_core modules $1 $2 $3

rm main.nf
rm nextflow.config
rm .nf-core.yml