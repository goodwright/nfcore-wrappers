#!/usr/bin/env nextflow

include { STAR_GENOMEGENERATE } from "../modules/nf-core/star/genomegenerate/main"

workflow {

    ch_fasta = file(params.fasta, checkIfExists: true)
    ch_gtf = file(params.gtf, checkIfExists: true)

    STAR_GENOMEGENERATE (
        ch_fasta,
        ch_gtf
    )

}
