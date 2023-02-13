nextflow.enable.dsl=2

include { TRIMGALORE } from "../modules/nf-core/trimgalore/main"

workflow {

    meta = [id:file(params.fastq).name, single_end: true]

    TRIMGALORE ( [meta, file(params.fastq)] )

}
