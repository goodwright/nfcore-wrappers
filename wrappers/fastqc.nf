#!/usr/bin/env nextflow

include { FASTQC } from "../modules/nf-core/fastqc/main"

workflow {

    ch_reads = [ [id:file(params.reads).baseName], file(params.reads, checkIfExists: true) ]

    FASTQC (
        ch_reads
    )

}
