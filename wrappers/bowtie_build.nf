nextflow.enable.dsl=2

include { BOWTIE_BUILD } from "../modules/nf-core/bowtie/build/main"

workflow {

    BOWTIE_BUILD ( file(params.fasta) )

}
