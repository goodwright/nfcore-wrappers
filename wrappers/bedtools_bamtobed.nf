#!/usr/bin/env nextflow

include { BEDTOOLS_BAMTOBED } from "../modules/nf-core/bedtools/bamtobed/main"

workflow {

    ch_bam = [ [id:file(params.bam).baseName], file(params.bam, checkIfExists: true) ]

    BEDTOOLS_BAMTOBED (
        ch_bam
    )

}
