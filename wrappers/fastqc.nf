nextflow.enable.dsl=2

include { FASTQC } from "../modules/nf-core/fastqc/main"

workflow {

    meta = [id:file(params.fastq).name, single_end: true]

    FASTQC ( [meta, file(params.fastq)] )

}