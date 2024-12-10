from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from app import db

engine = create_engine('sqlite:///organisms.db', echo=True)
Base = declarative_base()


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
    #prob_annotated_peptide = db.Column(db.String)
    #best_scan_num = db.Column(db.Integer)
    #file_best_scan = db.Column(db.String)
    amino_acid = db.Column(db.String(1))
    modification = db.Column(db.String)
    position = db.Column(db.Integer)
    #uniprot_id = db.Column(db.String)
    #position = db.Column(db.Integer)
    #amino_acid = db.Column(db.String(1))
    #modification = db.Column(db.String)
    #spectral_count = db.Column(db.Integer)

    def __init__(self, name):
        """"""
        self.name = name

    def __repr__(self):
        return "<Protein: {}>".format(self.name)


# create tables
Base.metadata.create_all(engine)