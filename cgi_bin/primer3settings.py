#!/usr/bin/env python
print """\
Content-Type: text/html\n
<html><body>
<p> </p>
</body></html>

Primer3 File - http://primer3.sourceforge.net
P3_FILE_TYPE=settings

<p> <input type="number" name="PRIMER_FIRST_BASE_INDEX" value=1</p>
<p> <input type="number" name="PRIMER_TASK" value=generic</p>
P3_FILE_ID=Settings for PCR amplification followed by Sanger sequencing on both strands using PCR primers
<p> <input type="number" name="PRIMER_MIN_THREE_PRIME_DISTANCE" value=3</p>
<p> <input type="number" name="PRIMER_EXPLAIN_FLAG" value=1</p>

# Put something reasonable for PRIMER_MISPRIMING_LIBRARY depending
# on the species you are designing primers for.
PRIMER_MISPRIMING_LIBRARY=
<p> <input type="number" name="PRIMER_MAX_LIBRARY_MISPRIMING"" value=12.00<p>
<p> <input type="number" name="PRIMER_PAIR_MAX_LIBRARY_MISPRIMING" value=20.00</p>

<p> <input type="number" name="PRIMER_PRODUCT_SIZE_RANGE" value=150-250 100-300 301-400 401-500 501-600 601-700 701-850 851-1000</p>
<p> <input type="number" name="PRIMER_NUM_RETURN" value=5</p>
<p> <input type="number" name="PRIMER_MAX_END_STABILITY" value=9.0</p>
#
<p> <input type="number" name="PRIMER_MAX_SELF_ANY_TH" value=45.00</p>
<p> <input type="number" name="PRIMER_MAX_SELF_END_TH" value=35.00</p>
<p> <input type="number" name="PRIMER_PAIR_MAX_COMPL_ANY_TH" value=45.00</p>
<p> <input type="number" name="PRIMER_PAIR_MAX_COMPL_END_TH" value=35.00</p>

<p> <input type="number" name="PRIMER_MAX_HAIRPIN_TH" value=24.00</p>
<p> <input type="number" name="PRIMER_MAX_TEMPLATE_MISPRIMING_TH" value=40.00</p>
<p> <input type="number" name="PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING_TH" value=70.00</p>
<p> <input type="number" name="PRIMER_MIN_SIZE" value=18</p>
<p> <input type="number" name="PRIMER_OPT_SIZE" value=20</p>
<p> <input type="number" name="PRIMER_MAX_SIZE" value=23</p>
<p> <input type="number" name="PRIMER_MIN_TM" value=57.0</p>
<p> <input type="number" name="PRIMER_OPT_TM" value=59.0</p>
<p> <input type="number" name="PRIMER_MAX_TM" value=62.0</p>
<p> <input type="number" name="PRIMER_PAIR_MAX_DIFF_TM" value=5.0</p>
# PRIMER_TM_FORMULA=1 means use the SantaLucia parameters (Proc Natl Acad Sci 95:1460-65)
<p> <input type="number" name="PRIMER_TM_FORMULA" value=1</p>
<p> <input type="number" name="PRIMER_SALT_MONOVALENT" value=50.0</p>
# PRIMER_SALT_CORRECTIONS=1 means use the salt correction in SantaLucia et al 1998
<p> <input type="number" name="PRIMER_SALT_CORRECTIONS" value=1</p>
# Millimolar conc of MgCl+2
<p> <input type="number" name="PRIMER_SALT_DIVALENT" value=1.5</p>
# Millimolar conc of dNTPs
<p> <input type="number" name="PRIMER_DNTP_CONC" value=0.6</p>
<p> <input type="number" name="PRIMER_DNA_CONC" value=50.0</p>
<p> <input type="number" name="PRIMER_THERMODYNAMIC_OLIGO_ALIGNMENT" value=1</p>
<p> <input type="number" name="PRIMER_THERMODYNAMIC_TEMPLATE_ALIGNMENT" value=0</p>
<p> <input type="number" name="PRIMER_LOWERCASE_MASKING" value=0</p>
#
<p> <input type="number" name="PRIMER_MIN_GC" value=30.0</p>
<p> <input type="number" name="PRIMER_MAX_GC" value=70.0</p>
<p> <input type="number" name="PRIMER_MAX_NS_ACCEPTED" value=0</p>
<p> <input type="number" name="PRIMER_MAX_POLY_X" value=4</p>
<p> <input type="number" name="PRIMER_OUTSIDE_PENALTY" value=0</p>
<p> <input type="number" name="PRIMER_GC_CLAMP" value=0</p>
<p> <input type="number" name="PRIMER_LIBERAL_BASE" value=1</p>
<p> <input type="number" name="PRIMER_LIB_AMBIGUITY_CODES_CONSENSUS" value=0</p>
<p> <input type="number" name="PRIMER_PICK_ANYWAY" value=1</p>

<p> <input type="number" name="PRIMER_WT_TM_LT" value=1.0</p>
<p> <input type="number" name="PRIMER_WT_TM_GT" value=1.0</p>
<p> <input type="number" name="PRIMER_WT_SIZE_LT" value=1.0</p>
<p> <input type="number" name="PRIMER_WT_SIZE_GT" value=1.0</p>
<p> <input type="number" name="PRIMER_WT_GC_PERCENT_LT" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_GC_PERCENT_GT" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_SELF_ANY_TH" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_SELF_END_TH" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_HAIRPIN_TH" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_NUM_NS" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_LIBRARY_MISPRIMING" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_SEQ_QUAL" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_END_QUAL" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_POS_PENALTY" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_END_STABILITY" value=0.0</p>
<p> <input type="number" name="PRIMER_WT_TEMPLATE_MISPRIMING_TH" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_PRODUCT_SIZE_LT" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_PRODUCT_SIZE_GT" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_PRODUCT_TM_LT" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_PRODUCT_TM_GT" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_DIFF_TM" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_COMPL_ANY_TH" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_COMPL_END_TH" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_LIBRARY_MISPRIMING" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_PR_PENALTY" value=1.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_IO_PENALTY" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_TEMPLATE_MISPRIMING" value=0.0</p>

<p> <input type="number" name="PRIMER_INTERNAL_WT_SIZE_LT" value=1.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_END_QUAL" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_SELF_END" value=12.00</p>
<p> <input type="number" name="PRIMER_QUALITY_RANGE_MIN" value=0</p>
<p> <input type="number" name="PRIMER_PAIR_MAX_COMPL_END" value=3.00</p>
<p> <input type="number" name="PRIMER_PRODUCT_MAX_TM" value=1000000.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_SIZE" value=27</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_SELF_ANY" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_POLY_X" value=5</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_SIZE_GT" value=1.0</p>
<p> <input type="number" name="PRIMER_SEQUENCING_ACCURACY" value=20</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_TM_GT" value=1.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_LIBRARY_MISHYB" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_GC" value=80.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_COMPL_ANY" value=0.0</p>
<p> <input type="number" name="PRIMER_PICK_INTERNAL_OLIGO" value=0</p>
<p> <input type="number" name="PRIMER_MAX_SELF_END" value=3.00</p>
<p> <input type="number" name="PRIMER_QUALITY_RANGE_MAX" value=100</p>
<p> <input type="number" name="PRIMER_INTERNAL_DNTP_CONC" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MIN_SIZE" value=18</p>
<p> <input type="number" name="PRIMER_INTERNAL_MIN_QUALITY" value=0</p>
<p> <input type="number" name="PRIMER_SEQUENCING_INTERVAL" value=250</p>
<p> <input type="number" name="PRIMER_INTERNAL_SALT_DIVALENT" value=1.5</p>
<p> <input type="number" name="PRIMER_MAX_SELF_ANY" value=8.00</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_SEQ_QUAL" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_WT_COMPL_END" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_OPT_TM" value=60.0</p>
<p> <input type="number" name="PRIMER_SEQUENCING_SPACING" value=500</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_SELF_ANY" value=12.00</p>
<p> <input type="number" name="PRIMER_MIN_END_QUALITY" value=0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MIN_TM" value=57.0</p>
<p> <input type="number" name="PRIMER_PAIR_MAX_COMPL_ANY" value=8.00</p>
<p> <input type="number" name="PRIMER_SEQUENCING_LEAD" value=50</p>
<p> <input type="number" name="PRIMER_PICK_LEFT_PRIMER" value=1</p>
<p> <input type="number" name="PRIMER_INTERNAL_OPT_SIZE" value=20</p>
<p> <input type="number" name="PRIMER_WT_TEMPLATE_MISPRIMING" value=0.0</p>
<p> <input type="number" name="PRIMER_MAX_END_GC" value=5</p>
<p> <input type="number" name="PRIMER_MIN_QUALITY" value=0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_LIBRARY_MISHYB" value=12.00</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_GC_PERCENT_GT" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_NS_ACCEPTED" value=0</p>
<p> <input type="number" name="PRIMER_WT_SELF_ANY" value=0.0</p>
<p> <input type="number" name="PRIMER_MAX_TEMPLATE_MISPRIMING" value=12.00</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_NUM_NS" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_SELF_END" value=0.0</p>
<p> <input type="number" name="PRIMER_PRODUCT_OPT_SIZE" value=0</p>
<p> <input type="number" name="PRIMER_PRODUCT_OPT_TM" value=0.0</p>
<p> <input type="number" name="PRIMER_PAIR_MAX_TEMPLATE_MISPRIMING" value=24.00</p>
<p> <input type="number" name="PRIMER_INSIDE_PENALTY" value=-1.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_MIN_GC" value=20.0</p>
<p> <input type="number" name="PRIMER_PRODUCT_MIN_TM" value=-1000000.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_SALT_MONOVALENT" value=50.0</p>
<p> <input type="number" name="PRIMER_WT_SELF_END" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_DNA_CONC" value=50.0</p>
<p> <input type="number" name="PRIMER_PICK_RIGHT_PRIMER" value=1</p>
<p> <input type="number" name="PRIMER_INTERNAL_MAX_TM" value=63.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_GC_PERCENT_LT" value=0.0</p>
<p> <input type="number" name="PRIMER_INTERNAL_WT_TM_LT" value=1.0></p>
=
"""
