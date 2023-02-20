nextflow.enable.dsl=2

include { FASTQC } from "../modules/nf-core/fastqc/main" 

workflow {

    ch_reads = [ id:params.reads.baseName, file(params.reads, checkIfExists: true) ]

    FASTQC (
        ch_reads
    )

}
