## GenoMEL pipelines in Bionimbus

Workon:

* Variant calling workflow

Complete:

* Novoalign harmonization workflow optimization

  > 10-12X faster than original workflow (Same logic/workflow, new tools and merged steps)

  > BWA mem harmonization workflow ready for comparison (Generally 3-5X faster than novoalign workflow after optimization)

  > internal scatter for cwl engine + multiple read groups WGS

* Indelrealignment workflow

  > Based on GATK3.7

  > BQSR workflow ready for comparison
