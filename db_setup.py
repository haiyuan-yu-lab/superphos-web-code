from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Float, String
import pandas as pd
from numpy import genfromtxt
#from models import Yeast

engine = create_engine('sqlite:///organisms.db', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
#df = pd.read_csv('./data/yeast_phosphosites_parsed.txt', sep='\t')
#df.to_sql(name=Yeast.__tablename__, con=engine, index_label='id', if_exists='replace')
class Yeast(Base):
    """"""
    __tablename__ = "yeast"

    id = Column(Integer, primary_key=True)
    #search_engine = Column(String)
    gene = Column(String)
    uniprot_id = Column(String)
    #systematic_gene_name = Column(String)
    #annotated_peptide = Column(String)
    spectral_count = Column(Integer)
    #site_clustering = Column(String)
    #multiple_site_remarks = Column(String)
    #best_localscore_by_xcorr = Column(Float)
    #best_prob_mq = Column(Float)
    #pep_by_percolator_q = Column(Float)
    #prob_annotated_peptide = Column(String)
    #best_scan_num = Column(Integer)
    #file_best_scan = Column(String)
    amino_acid = Column(String(1))
    modification = Column(String)
    position = Column(Integer)
    

#def Load_Data(file_name):
    #print(genfromtxt('./data/yeast_phosphosites_parsed_2.txt', delimiter=',', skip_header=1, converters={0: lambda s: str(s)}))
    #data = genfromtxt(file_name, delimiter=',', skip_header=1, converters={0: lambda s: str(s)})
    #return data.tolist()
    
def init_db():
    from models import Yeast
    Base.metadata.create_all(bind=engine)
    
    try:
        file_name = "./data/yeast_phosphosites_parsed_2.txt"
        #print(file_name)
        #data = Load_Data(file_name)
        data = pd.read_csv(file_name, delimiter=',')
        #print(data.shape)
        #engine = create_engine('sqlite:///organisms.db')#, convert_unicode=True)
        #Create the session
        #session = sessionmaker()
        #session.configure(bind=engine)
        #db_session = session()
        #print(data)
        #count = 0

        for i in range(data.shape[0]):
            #print(data.iloc[i]['PEP/PercolatorQvalue'],i)
            #i = i.strip('\"').strip('b').strip('\'')
            #i = i.split(',')
            record = Yeast(**{
                'id' : i,
                #'search_engine' : data.iloc[i]['Search_engine'],
                'gene' : data.iloc[i]['Gene(s)'],
                'uniprot_id' : data.iloc[i]['Uniprot_id'],
                #'systematic_gene_name' : data.iloc[i]['SystematicGeneName'],
                #'annotated_peptide' : data.iloc[i]['AnnotatedPeptide'],
                'spectral_count' : data.iloc[i]['#identifications'],
                #'site_clustering' : data.iloc[i]['SiteClustering'],
                #'multiple_site_remarks' : data.iloc[i]['MultipleSitesRemarks'],
                #'best_localscore_by_xcorr' : data.iloc[i]['Best-LocalizationScore/Xcorr'],
                #'best_prob_mq' : data.iloc[i]['Best-Probability_MQ'],
                #'pep_by_percolator_q' : data.iloc[i]['PEP/PercolatorQvalue'],
                #'prob_annotated_peptide' : data.iloc[i]['ProbabilityAnnotation'],
                #'best_scan_num' : data.iloc[i]['BestScanNumber'],
                #'file_best_scan' : data.iloc[i]['FileNameForBestScanNumber'],
                'amino_acid' : data.iloc[i]['AnnotatedPeptide'].split('(p)')[0][-1],
                'modification' : "phos",
                'position' : data.iloc[i]['Pos'].split(';')[0]


                #'uniprot_id' : i[0],#data['uniprot'].iloc[i],#data.loc[i,'uniprot'],
                #'position' : i[1],#data.loc[i,'Pos'],
                #'amino_acid' : i[2],#data.loc[i,'AA'],
                #'modification' : i[3],#data.loc[i,'Mod'],
                #'spectral_count' : i[4]#data.loc[i,'SpectralCount']
            })
            #count+=1
            #print(record.spectral_count, data.iloc[i]['#identifications'])
            #print(record, "record", i, "uniprot: ", i[0])#data.loc[i,'uniprot'])
            db_session.add(record) #Add all the records

        db_session.commit() #Attempt to commit all the records
        #print("Database finished loading")
    except:
        db_session.rollback() #Rollback the changes on error
    finally:
        #print("database finished loading")
        db_session.close() #Close the connection


#init_db()