#!/usr/bin/env nextflow

include { TRIMGALORE } from "../modules/nf-core/trimgalore/main"

workflow {

    ch_reads = [ [id:file(params.reads).baseName, single_end: true], file(params.reads, checkIfExists: true) ]

    TRIMGALORE (
        ch_reads
    )

}
