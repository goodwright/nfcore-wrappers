nextflow.enable.dsl=2

include { BOWTIE_BUILD } from "../modules/nf-core/bowtie/build/main" 

workflow {

    ch_fasta = file(params.fasta, checkIfExists: true)

    BOWTIE_BUILD (
        ch_fasta
    )

}
