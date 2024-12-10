from app import db

class Yeast(db.Model):
    """"""
    __tablename__ = "yeast"

    id = db.Column(db.String, primary_key=True)
    #search_engine = db.Column(db.String)
    gene = db.Column(db.String)
    uniprot_id = db.Column(db.String)
    #systematic_gene_name = db.Column(db.String)
    #annotated_peptide = db.Column(db.String)
    spectral_count = db.Column(db.Integer)
    #site_clustering = db.Column(db.String)
    #multiple_site_remarks = db.Column(db.String)
    #best_localscore_by_xcorr = db.Column(db.Float)
    #best_prob_mq = db.Column(db.Float)
    #pep_by_percolator_q = db.Column(db.String)
    #prob_annotated_peptide = db.Column(db.Float)
    #best_scan_num = db.Column(db.Integer)
    #file_best_scan = db.Column(db.String)
    amino_acid = db.Column(db.String(1))
    modification = db.Column(db.String)
    position = db.Column(db.Integer)
    #name = db.Column(db.String)
    #uniprot_id = db.Column(db.String)
    #position = db.Column(db.Integer)
    #amino_acid = db.Column(db.String(1))
    #modification = db.Column(db.String)
    #spectral_count = db.Column(db.Integer)

    #def __init__(self, name):
    #    """"""
    #    self.name = name

    #def __repr__(self):
    #    return "<Protein: {}>".format(self.name)