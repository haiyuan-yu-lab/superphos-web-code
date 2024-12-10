from flask_table import Table, Col
 
class Results(Table):
    id = Col('ID')
    gene = Col('Gene Name', show=False)
    uniprot_id = Col('Protein ID', show=False)
    spectral_count = Col('Spectral Count')
    amino_acid = Col('AA')
    modification = Col('Modification')
    position = Col('Position')
